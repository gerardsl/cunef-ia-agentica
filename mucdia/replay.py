"""Grabación y reproducción de respuestas del modelo ("replay").

Si se agota la cuota gratuita (o no hay clave), los pasos guiados de los notebooks pueden seguir
funcionando con respuestas grabadas previamente por el profesor. La clave de cada grabación es un
hash de la conversación (mensajes, herramientas disponibles, instrucciones y, si se fijan, parámetros de
muestreo como la temperatura), sin identificadores aleatorios, para que el mismo código produzca la misma clave.

Una misma clave puede guardar varias MUESTRAS (por ejemplo, la misma pregunta repetida 5 veces para medir la
variabilidad): en modo replay, la n-ésima llamada con esa clave devuelve la n-ésima muestra (y vuelve a empezar).
Cada muestra guarda también cuánto tardó la llamada original, para poder analizar la latencia sin gastar cuota.

También se graba la salida del código que ejecutan los agentes programadores (mucdia.codigo): la siguiente
llamada al modelo depende de ella, y no debe cambiar por la velocidad de la máquina (un límite de tiempo) ni por
diferencias mínimas de redondeo entre sistemas.
"""

import base64
import hashlib
import json
import os
import zlib
from typing import Any

from . import config

MUESTREO = ("temperature", "top_p", "top_k", "seed")


class Estado:
    solo_replay = False
    avisado = False

    def __init__(self):
        self.usos: dict[str, int] = {}       # cuántas veces se ha reproducido cada clave en este proceso
        self.grabadas: set[str] = set()      # claves grabadas en este proceso (las siguientes se añaden como muestras)


ESTADO = Estado()


def _hash(obj: Any) -> str:
    texto = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:24]


def _args(argumentos: Any) -> Any:
    if isinstance(argumentos, str):
        try:
            return json.loads(argumentos)
        except json.JSONDecodeError:
            return argumentos.strip()
    return argumentos


def clave_maf(mensajes, opciones) -> str:
    conversacion = []
    for m in mensajes:
        partes = []
        for c in m.contents or []:
            if c.type == "text" and (c.text or "").strip():
                partes.append(["t", c.text.strip()])
            elif c.type == "function_call":
                partes.append(["c", c.name, _args(c.arguments)])
            elif c.type == "function_result":
                partes.append(["r", str(c.result)[:4000]])
        if partes:
            conversacion.append([str(m.role), partes])
    opciones = dict(opciones or {})
    herramientas = sorted(getattr(h, "name", str(h)) for h in (opciones.get("tools") or []))
    formato = opciones.get("response_format")
    datos = {"m": conversacion, "h": herramientas, "i": opciones.get("instructions"),
             "f": getattr(formato, "__name__", str(formato) if formato else None)}
    # Solo si se fijan: así las claves de las llamadas sin parámetros de muestreo no cambian.
    if muestreo := {k: opciones[k] for k in MUESTREO if opciones.get(k) is not None}:
        datos["s"] = muestreo
    return _hash(datos)


def clave_codigo(codigo: str, segundos: int, max_caracteres: int) -> str:
    """Clave de la salida de un código ejecutado por un agente (ver mucdia.codigo)."""
    return _hash({"codigo": codigo, "segundos": segundos, "max": max_caracteres})


def _valor(obj, campo):
    return obj.get(campo) if isinstance(obj, dict) else getattr(obj, campo, None)


def clave_openai(kwargs: dict) -> str:
    conversacion = []
    for m in kwargs.get("messages", []):
        llamadas = [[_valor(_valor(t, "function"), "name"), _args(_valor(_valor(t, "function"), "arguments"))]
                    for t in (_valor(m, "tool_calls") or [])]
        contenido = _valor(m, "content")
        conversacion.append([_valor(m, "role"), contenido.strip() if isinstance(contenido, str) else contenido, llamadas])
    herramientas = sorted(_valor(_valor(t, "function"), "name") for t in (kwargs.get("tools") or []))
    datos = {"m": conversacion, "h": herramientas, "f": str(kwargs.get("response_format"))}
    if muestreo := {k: kwargs[k] for k in MUESTREO if kwargs.get(k) is not None}:
        datos["s"] = muestreo
    return _hash(datos)


def _registrar(clave: str) -> None:
    """Si MUCDIA_REGISTRO_REPLAY apunta a un fichero, anota la clave usada (para publicar las grabaciones por sesión)."""
    registro = os.getenv("MUCDIA_REGISTRO_REPLAY")
    if registro:
        with open(registro, "a", encoding="utf-8") as f:
            f.write(clave + "\n")


def _comprimir(respuesta: dict) -> str:
    # Comprimido (zlib + base64): el repo es público y las grabaciones del reto de la sesión 3 no deben
    # poder leerse con un simple buscador de texto.
    datos = zlib.compress(json.dumps(respuesta, ensure_ascii=False, default=str).encode("utf-8"), 9)
    return base64.b64encode(datos).decode("ascii")


def _descomprimir(z: str) -> dict:
    return json.loads(zlib.decompress(base64.b64decode(z)).decode("utf-8"))


def guardar(clave: str, tipo: str, respuesta: dict, ms: float | None = None):
    """Graba una respuesta. Si la misma clave ya se grabó en este proceso, la añade como una muestra más."""
    config.DIR_REPLAYS.mkdir(parents=True, exist_ok=True)
    ruta = config.DIR_REPLAYS / f"{clave}.json"
    muestras, tiempos = [], []
    if clave in ESTADO.grabadas and ruta.exists():
        entrada = json.loads(ruta.read_text(encoding="utf-8"))
        muestras = entrada["z"] if isinstance(entrada.get("z"), list) else [entrada["z"]]
        tiempos = entrada.get("ms") or [None] * len(muestras)
    muestras.append(_comprimir(respuesta))
    tiempos.append(None if ms is None else round(ms))
    ruta.write_text(json.dumps({"tipo": tipo, "z": muestras, "ms": tiempos}), encoding="utf-8")
    ESTADO.grabadas.add(clave)
    _registrar(clave)


def cargar(clave: str) -> tuple[dict, float | None] | None:
    """Devuelve (respuesta, milisegundos que tardó la llamada original) o None si no hay grabación."""
    ruta = config.DIR_REPLAYS / f"{clave}.json"
    if not ruta.exists():
        return None
    _registrar(clave)
    if not ESTADO.avisado and config.modo() != "completar":
        ESTADO.avisado = True
        print("🎞️  Usando respuestas GRABADAS (modo replay): el resultado es el que obtuvo el profesor.", flush=True)
    entrada = json.loads(ruta.read_text(encoding="utf-8"))
    if "respuesta" in entrada:                      # formato antiguo, sin comprimir
        return entrada["respuesta"], None
    muestras = entrada["z"] if isinstance(entrada["z"], list) else [entrada["z"]]
    tiempos = entrada.get("ms") or [None] * len(muestras)
    i = ESTADO.usos.get(clave, 0)
    ESTADO.usos[clave] = i + 1
    return _descomprimir(muestras[i % len(muestras)]), tiempos[i % len(tiempos)]


def existe(clave: str) -> bool:
    return (config.DIR_REPLAYS / f"{clave}.json").exists()


def debe_reproducir(clave: str | None = None) -> bool:
    """replay: siempre · auto: sin clave o sin cuota · completar: si ya había una grabación de esta clave
    (las claves grabadas en este mismo proceso siguen en vivo, para poder añadir muestras)."""
    modo = config.modo()
    if modo == "completar":
        return clave is not None and clave not in ESTADO.grabadas and existe(clave)
    return modo == "replay" or (modo == "auto" and (ESTADO.solo_replay or not config.clave()))
