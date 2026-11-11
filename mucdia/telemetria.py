"""Telemetría por llamada al modelo: tokens, latencia y herramientas pedidas en cada paso.

Cada llamada (en vivo o reproducida desde una grabación) deja un registro. Con ellos se responde a las preguntas
de un científico de datos sobre un agente: ¿cuántos pasos da?, ¿cómo crece el contexto?, ¿cuánto cuesta?,
¿cuánto tarda?

    mucdia.traza_df()          # DataFrame con una fila por llamada al modelo
    mucdia.reiniciar_traza()   # empieza a medir desde cero
"""

import threading
import time

import pandas as pd

_lock = threading.Lock()
_registros: list[dict] = []


def registrar(*, cliente: str, modelo: str, grabada: bool, uso: dict | None, ms: float | None,
              herramientas: list[str], mensajes: int) -> None:
    uso = uso or {}
    entrada = int(uso.get("input_token_count") or uso.get("prompt_tokens") or 0)
    salida = int(uso.get("output_token_count") or uso.get("completion_tokens") or 0)
    with _lock:
        _registros.append({
            "llamada": len(_registros) + 1,
            "hora": time.strftime("%H:%M:%S"),
            "cliente": cliente,
            "modelo": modelo,
            "grabada": grabada,
            "mensajes": mensajes,
            "tokens_entrada": entrada,
            "tokens_salida": salida,
            "ms": None if ms is None else round(ms),
            "herramientas": ", ".join(herramientas),
        })


def traza_df() -> pd.DataFrame:
    """Una fila por llamada al modelo desde el último reinicio (las grabadas llevan grabada=True)."""
    with _lock:
        df = pd.DataFrame(_registros)
    if df.empty:
        return pd.DataFrame(columns=["llamada", "hora", "cliente", "modelo", "grabada", "mensajes", "tokens_entrada",
                                     "tokens_salida", "ms", "herramientas"])
    return df.set_index("llamada")


def reiniciar_traza() -> None:
    with _lock:
        _registros.clear()


def herramientas_openai(respuesta) -> list[str]:
    try:
        return [t.function.name for t in (respuesta.choices[0].message.tool_calls or [])]
    except (AttributeError, IndexError):
        return []


def herramientas_maf(respuesta) -> list[str]:
    nombres = []
    for m in getattr(respuesta, "messages", None) or []:
        for c in m.contents or []:
            if c.type == "function_call":
                nombres.append(c.name)
    return nombres
