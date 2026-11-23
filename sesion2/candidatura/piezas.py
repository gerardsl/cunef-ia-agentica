"""Tus piezas: lo que escribes en los notebooks (celdas ✏️) es lo que usa tu webapp.

Cada celda ✏️ guarda su código en sesion2/mis_piezas/ (con %%writefile) o tus instrucciones en
sesion2/mis_piezas/instrucciones.json. Si una pieza no existe todavía, se usa la de referencia.

    cargar("oferta", "extraer_jobposting", defecto)   # tu función, si la has escrito; si no, la de referencia
    instrucciones("editor_cv", defecto)                # tus instrucciones para un agente
    guardar_instrucciones("editor_cv", texto)
    estado()                                           # qué piezas son tuyas
"""

import importlib.util
import json
import sys
from pathlib import Path

CARPETA = Path(__file__).resolve().parent.parent / "mis_piezas"
INSTRUCCIONES = CARPETA / "instrucciones.json"
PIEZAS = {  # pieza → (fichero, nombre, lab)
    "lector JSON-LD": ("oferta.py", "extraer_jobposting", "2a"),
    "guardarraíl de cifras": ("guardarrail.py", "cifras_sin_respaldo", "2b"),
    "instrucciones del editor de CV": ("instrucciones.json", "editor_cv", "2b"),
    "instrucciones del investigador": ("instrucciones.json", "investigador", "2c"),
}


def cargar(modulo: str, nombre: str, defecto=None):
    """Importa `nombre` de sesion2/mis_piezas/<modulo>.py cada vez (así se ven tus cambios sin reiniciar)."""
    ruta = CARPETA / f"{modulo}.py"
    if not ruta.exists():
        return defecto
    try:
        spec = importlib.util.spec_from_file_location(f"mis_piezas_{modulo}", ruta)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001
        # A stderr: en el servidor MCP, stdout es el canal del protocolo.
        print(f"⚠️  sesion2/mis_piezas/{modulo}.py tiene un error ({type(e).__name__}: {e}); uso la pieza de referencia.",
              file=sys.stderr)
        return defecto
    return getattr(mod, nombre, defecto)


def _leer_instrucciones() -> dict:
    try:
        return json.loads(INSTRUCCIONES.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def instrucciones(agente: str, defecto: str) -> str:
    texto = _leer_instrucciones().get(agente, "")
    return texto if texto.strip() and "TODO" not in texto else defecto


def guardar_instrucciones(agente: str, texto: str) -> Path:
    datos = _leer_instrucciones()
    datos[agente] = texto.strip()
    CARPETA.mkdir(parents=True, exist_ok=True)
    INSTRUCCIONES.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    return INSTRUCCIONES


def estado() -> dict[str, bool]:
    """{pieza: True si es tuya}."""
    instr = _leer_instrucciones()
    resultado = {}
    for pieza, (fichero, nombre, _) in PIEZAS.items():
        if fichero.endswith(".json"):
            resultado[pieza] = bool(instr.get(nombre, "").strip()) and "TODO" not in instr.get(nombre, "")
        else:
            resultado[pieza] = cargar(fichero[:-3], nombre) is not None
    return resultado
