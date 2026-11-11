"""Ejecutar el código Python que escribe un agente (sesión 1, lab 1b).

Cada ejecución corre en un PROCESO APARTE con:
  - un límite de tiempo (si el código se cuelga, se corta),
  - las variables de entorno sin claves ni tokens (el código no puede leer tu GEMINI_API_KEY),
  - la base de datos de MUCDIA en solo lectura (`consultar(sql)` devuelve un DataFrame),
  - la salida recortada (para no llenar el contexto del modelo).

⚠️ Esto NO es un sandbox de producción: el proceso puede leer ficheros y abrir conexiones. Es suficiente para
tu propio Codespace con tus propias preguntas; en la sesión 3 veremos por qué no lo expondrías a un cliente.
"""

import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from . import config, replay

PRELUDIO = '''\
import warnings
warnings.filterwarnings("ignore")
import sqlite3
import numpy as np
import pandas as pd
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)
pd.set_option("display.max_rows", 40)


def consultar(sql, params=()):
    """Ejecuta una consulta SQL de solo lectura sobre la base de datos de MUCDIA y devuelve un DataFrame."""
    with sqlite3.connect("file:{db}?mode=ro", uri=True) as con:
        return pd.read_sql_query(sql, con, params=params)

'''
_SECRETO = re.compile(r"KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL", re.I)


def _limpiar_error(texto: str, script: Path, lineas_preludio: int) -> str:
    """Resume el error: la línea del código del agente donde falló (si la hay) y la excepción final, sin rutas
    locales (así el modelo recibe lo esencial y el resultado es igual en Windows, macOS y Linux)."""
    texto = texto.replace(str(script), "<codigo>")
    lineas = [l for l in texto.strip().splitlines() if l.strip()]
    resumen = []
    for i, linea in enumerate(lineas):
        if m := re.search(r'"<codigo>", line (\d+)', linea):
            n = int(m.group(1)) - lineas_preludio
            if n > 0:
                codigo = lineas[i + 1].strip() if i + 1 < len(lineas) else ""
                resumen = [f"línea {n} de tu código: {codigo}"]
    return "\n".join(resumen + lineas[-1:])


def ejecutar_codigo(codigo: str, segundos: int = 20, max_caracteres: int = 3000) -> str:
    """Ejecuta `codigo` en un proceso aparte y devuelve lo que imprime (o el error), recortado.

    En modo replay devuelve la salida que se grabó para ese mismo código (si la hay), para que la reproducción no
    dependa de la velocidad de cada máquina."""
    clave = replay.clave_codigo(codigo, segundos, max_caracteres)
    if replay.debe_reproducir(clave) and (grabacion := replay.cargar(clave)) is not None:
        return grabacion[0]["salida"]
    t0 = time.perf_counter()
    salida = _ejecutar(codigo, segundos, max_caracteres)
    if config.graba():
        replay.guardar(clave, "codigo", {"salida": salida}, ms=(time.perf_counter() - t0) * 1000)
    return salida


def _ejecutar(codigo: str, segundos: int, max_caracteres: int) -> str:
    preludio = PRELUDIO.format(db=config.DB.as_posix())
    lineas_preludio = preludio.count("\n")
    entorno = {k: v for k, v in os.environ.items() if not _SECRETO.search(k)}
    entorno["PYTHONIOENCODING"] = "utf-8"
    with tempfile.TemporaryDirectory(prefix="agente_") as carpeta:
        script = Path(carpeta) / "codigo_del_agente.py"
        script.write_text(preludio + codigo, encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=segundos, env=entorno, cwd=carpeta)
        except subprocess.TimeoutExpired:
            return f"ERROR: el código ha tardado más de {segundos} s y se ha detenido. Simplifícalo o agrega antes."
        salida = r.stdout.strip()
        if r.returncode != 0:
            salida = (salida + "\n" if salida else "") + "ERROR:\n" + _limpiar_error(r.stderr, script, lineas_preludio)
    if not salida:
        return "(el código no ha impreso nada: usa print() para mostrar el resultado)"
    if len(salida) > max_caracteres:
        salida = salida[:max_caracteres] + f"\n… (salida recortada: {len(salida):,} caracteres en total)".replace(",", ".")
    return salida
