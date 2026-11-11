"""Configuración del curso: variables de entorno y fichero .env en la raíz del repositorio.

Variables admitidas (todas opcionales salvo la clave):
    GEMINI_API_KEY   clave gratuita de Google AI Studio (en Codespaces, como secret)
    PROVEEDOR        gemini (por defecto) | openai  (cualquier endpoint compatible con OpenAI: Azure, Ollama...)
    MODELO           por defecto gemini-3.5-flash-lite
    OPENAI_API_KEY, OPENAI_BASE_URL   solo si PROVEEDOR=openai
    MAX_RPM          llamadas por minuto que nos permitimos (por defecto 9; el plan gratuito admite 10)
    MODO_LLM         auto (por defecto) | live | replay | record | completar
                     (completar: reproduce lo que ya está grabado y graba solo lo que falta; para el profesor)
"""

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env", override=False)
load_dotenv(Path.home() / ".mucdia" / ".env", override=False)

DB = RAIZ / "data" / "mucdia.db"
# Las demos del profesor usan su propia carpeta de grabaciones para no mezclarlas con las del repositorio público.
DIR_REPLAYS = Path(os.getenv("MUCDIA_DIR_REPLAYS") or RAIZ / "replays")
DIR_USO = Path.home() / ".mucdia"
GEMINI_OPENAI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
MODELO_POR_DEFECTO = "gemini-3.5-flash-lite"


def _var(nombre: str, defecto: str = "") -> str:
    return (os.getenv(nombre) or defecto).strip()


def proveedor() -> str:
    return _var("PROVEEDOR", "gemini").lower()


def modelo() -> str:
    return _var("MODELO", MODELO_POR_DEFECTO)


def modo() -> str:
    m = _var("MODO_LLM", "auto").lower()
    return m if m in ("auto", "live", "replay", "record", "completar") else "auto"


def graba() -> bool:
    """¿Hay que guardar las respuestas nuevas? (modos record y completar)"""
    return modo() in ("record", "completar")


def max_rpm() -> int:
    try:
        return max(1, int(_var("MAX_RPM", "9")))
    except ValueError:
        return 9


def clave() -> str:
    if proveedor() == "openai":
        return _var("OPENAI_API_KEY")
    return _var("GEMINI_API_KEY") or _var("GOOGLE_API_KEY")


def url_base() -> str | None:
    if proveedor() == "openai":
        return _var("OPENAI_BASE_URL") or None
    return GEMINI_OPENAI_URL
