"""Acceso de solo lectura a la base de datos de Almansa y al buscador de documentos."""

import re
import sqlite3

import pandas as pd

from . import config

_PROHIBIDO = re.compile(r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|reindex)\b", re.I)


def conexion() -> sqlite3.Connection:
    """Conexión de SOLO LECTURA (mode=ro): aunque alguien lo intente, no se puede modificar la base de datos."""
    return sqlite3.connect(f"file:{config.DB.as_posix()}?mode=ro", uri=True, check_same_thread=False)


def consultar(sql: str, params: tuple | dict = ()) -> pd.DataFrame:
    with conexion() as con:
        return pd.read_sql_query(sql, con, params=params)


def a_texto(df: pd.DataFrame, limite: int = 50) -> str:
    """Convierte un DataFrame en texto compacto (CSV) para que lo lea un modelo."""
    if df.empty:
        return "(sin resultados)"
    texto = df.head(limite).to_csv(index=False, float_format="%.2f", lineterminator="\n").strip()
    if len(df) > limite:
        texto += f"\n... ({len(df)} filas en total; se muestran {limite}. Agrega o filtra más.)"
    return texto


def sql_seguro(sql: str, limite: int = 50) -> str:
    """Ejecuta una consulta SELECT con salvaguardas y devuelve el resultado como texto."""
    s = (sql or "").strip().rstrip(";").strip()
    if not re.match(r"(?is)^(select|with)\b", s):
        return "ERROR: solo se permiten consultas de lectura (SELECT o WITH)."
    if ";" in s:
        return "ERROR: envía una sola sentencia SQL."
    if _PROHIBIDO.search(s):
        return "ERROR: la consulta contiene operaciones no permitidas."
    try:
        return a_texto(consultar(s), limite)
    except Exception as e:  # noqa: BLE001
        return f"ERROR SQL: {e}"


def esquema() -> str:
    """Tablas y vistas con sus columnas, más las notas del diccionario de datos."""
    with conexion() as con:
        objetos = con.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') "
                              "AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'documentos_%' ORDER BY type DESC, name").fetchall()
        notas = {}
        for tabla, columna, desc in con.execute("SELECT tabla, columna, descripcion FROM diccionario"):
            notas.setdefault(tabla, []).append(desc if columna == "*" else f"{columna}: {desc}")
        lineas = []
        for nombre, tipo in objetos:
            if nombre in ("diccionario", "documentos"):
                continue
            cols = ", ".join(r[1] for r in con.execute(f"PRAGMA table_info('{nombre}')"))
            lineas.append(f"- {nombre} ({'vista' if tipo == 'view' else 'tabla'}): {cols}")
            lineas += [f"    · {n}" for n in notas.get(nombre, [])]
    return "\n".join(lineas)


def buscar_documentos(consulta: str, k: int = 4) -> list[dict]:
    """Búsqueda de texto completo (BM25) sobre los documentos internos. No consume cuota del modelo."""
    palabras = [p for p in re.findall(r"\w+", consulta or "", re.UNICODE) if len(p) > 2]
    if not palabras:
        return []
    expresion = " OR ".join(f'"{p}"' for p in palabras)
    with conexion() as con:
        filas = con.execute(
            "SELECT d.doc, d.titulo, d.seccion, m.estado, m.fecha, d.texto FROM documentos d "
            "JOIN documentos_meta m ON m.doc = d.doc WHERE documentos MATCH ? ORDER BY bm25(documentos) LIMIT ?",
            (expresion, k)).fetchall()
    return [dict(doc=f[0], titulo=f[1], seccion=f[2], estado=f[3], fecha=f[4], texto=f[5][:1500]) for f in filas]
