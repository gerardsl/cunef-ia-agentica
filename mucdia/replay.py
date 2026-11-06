"""Grabación y reproducción de respuestas del modelo ("replay").

Si se agota la cuota gratuita (o no hay clave), los pasos guiados de los notebooks pueden seguir
funcionando con respuestas grabadas previamente por el profesor. La clave de cada grabación es un
hash de la conversación (mensajes, herramientas disponibles e instrucciones), sin identificadores
aleatorios, para que el mismo código produzca la misma clave.
"""

import base64
import hashlib
import json
import os
import zlib
from typing import Any

from . import config


class Estado:
    solo_replay = False
    avisado = False


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
    return _hash({"m": conversacion, "h": herramientas, "i": opciones.get("instructions"),
                  "f": getattr(formato, "__name__", str(formato) if formato else None)})


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
    return _hash({"m": conversacion, "h": herramientas, "f": str(kwargs.get("response_format"))})


def _registrar(clave: str) -> None:
    """Si MUCDIA_REGISTRO_REPLAY apunta a un fichero, anota la clave usada (para publicar las grabaciones por sesión)."""
    registro = os.getenv("MUCDIA_REGISTRO_REPLAY")
    if registro:
        with open(registro, "a", encoding="utf-8") as f:
            f.write(clave + "\n")


def guardar(clave: str, tipo: str, respuesta: dict):
    config.DIR_REPLAYS.mkdir(parents=True, exist_ok=True)
    ruta = config.DIR_REPLAYS / f"{clave}.json"
    # Comprimido (zlib + base64): el repo es público y las grabaciones del reto de la sesión 3 no deben
    # poder leerse con un simple buscador de texto.
    datos = zlib.compress(json.dumps(respuesta, ensure_ascii=False, default=str).encode("utf-8"), 9)
    ruta.write_text(json.dumps({"tipo": tipo, "z": base64.b64encode(datos).decode("ascii")}), encoding="utf-8")
    _registrar(clave)


def cargar(clave: str) -> dict | None:
    ruta = config.DIR_REPLAYS / f"{clave}.json"
    if not ruta.exists():
        return None
    _registrar(clave)
    if not ESTADO.avisado:
        ESTADO.avisado = True
        print("🎞️  Usando respuestas GRABADAS (modo replay): el resultado es el que obtuvo el profesor.", flush=True)
    entrada = json.loads(ruta.read_text(encoding="utf-8"))
    if "z" in entrada:
        return json.loads(zlib.decompress(base64.b64decode(entrada["z"])).decode("utf-8"))
    return entrada["respuesta"]


def debe_reproducir() -> bool:
    modo = config.modo()
    return modo == "replay" or (modo == "auto" and (ESTADO.solo_replay or not config.clave()))
