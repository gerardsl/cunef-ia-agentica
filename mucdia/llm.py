"""Clientes de modelo para el curso.

- cliente():         cliente de Microsoft Agent Framework (Gemini por defecto) con limitador, reintentos,
                     contador de uso y replay ya integrados como *middleware*.
- cliente_openai():  cliente con la interfaz del SDK de OpenAI (chat.completions.create) apuntando al
                     endpoint compatible de Gemini; lo usamos para programar el bucle agéntico "a mano".
"""

import asyncio
import logging
import time
from types import SimpleNamespace

from agent_framework import ChatContext, ChatMiddleware, ChatResponse

from . import config, replay
from .cuota import LIMITADOR, USO, SinGrabacion, clasificar, error_amigable, segundos_reintento

MAX_INTENTOS = 6
logging.getLogger("google_genai.types").setLevel(logging.ERROR)


def _uso_dict(usage) -> dict | None:
    if usage is None:
        return None
    if isinstance(usage, dict):
        return usage
    return getattr(usage, "model_dump", lambda: dict(usage))()


class MiddlewareCurso(ChatMiddleware):
    """Se ejecuta en cada llamada al modelo: replay → límite por minuto → reintentos → contador."""

    async def process(self, context: ChatContext, call_next):
        if context.stream:
            await LIMITADOR.esperar_async()
            context.stream_result_transforms.append(self._contar)
            await call_next()
            return

        clave = replay.clave_maf(context.messages, context.options)
        if replay.debe_reproducir():
            if self._reproducir(context, clave):
                return
            raise SinGrabacion("No hay respuesta grabada para este paso. Ejecútalo en vivo (con tu clave) o "
                               "comprueba que no has cambiado el código del ejemplo.")

        for intento in range(MAX_INTENTOS):
            await LIMITADOR.esperar_async()
            try:
                await call_next()
                break
            except Exception as e:  # noqa: BLE001
                tipo = clasificar(e)
                if tipo == "minuto" and intento < MAX_INTENTOS - 1:
                    espera = segundos_reintento(e, intento)
                    USO.reintentos += 1
                    USO.espera_s += espera
                    print(f"⏳ Límite por minuto alcanzado; reintento en {espera:.0f} s…", flush=True)
                    await asyncio.sleep(espera)
                    continue
                if tipo == "temporal" and intento < 3:
                    USO.reintentos += 1
                    await asyncio.sleep(3 * (intento + 1))
                    continue
                if tipo in ("diaria", "clave") and config.modo() == "auto":
                    replay.ESTADO.solo_replay = True
                    if self._reproducir(context, clave):
                        print("⚠️  Sin cuota o sin clave: continúo con respuestas grabadas.", flush=True)
                        return
                amigable = error_amigable(e, tipo)
                if amigable is e:
                    raise
                raise amigable from e

        if isinstance(context.result, ChatResponse):
            USO.registrar(_uso_dict(context.result.usage_details))
            if config.modo() == "record":
                replay.guardar(clave, "maf", context.result.to_dict())

    @staticmethod
    def _contar(respuesta):
        USO.registrar(_uso_dict(getattr(respuesta, "usage_details", None)))
        return respuesta

    @staticmethod
    def _reproducir(context: ChatContext, clave: str) -> bool:
        datos = replay.cargar(clave)
        if datos is None:
            return False
        context.result = ChatResponse.from_dict(datos)
        USO.registrar(None, replay=True)
        return True


def cliente(modelo: str | None = None, **kwargs):
    """Devuelve un cliente de chat de Agent Framework listo para usar en un Agent."""
    modelo = modelo or config.modelo()
    middleware = [MiddlewareCurso(), *kwargs.pop("middleware", [])]
    if config.proveedor() == "openai":
        from agent_framework.openai import OpenAIChatCompletionClient

        return OpenAIChatCompletionClient(model=modelo, api_key=config.clave() or "sin-clave",
                                          base_url=config.url_base(), middleware=middleware, **kwargs)
    from agent_framework.gemini import GeminiChatClient

    return GeminiChatClient(api_key=config.clave() or "sin-clave", model=modelo, middleware=middleware, **kwargs)


# ---------------------------------------------------------------------------------------------
# Cliente con interfaz OpenAI (sesión 1: bucle agéntico desde cero)
# ---------------------------------------------------------------------------------------------

class _Completions:
    def __init__(self, real):
        self._real = real

    def create(self, **kwargs):
        from openai.types.chat import ChatCompletion

        clave = replay.clave_openai(kwargs)
        if replay.debe_reproducir():
            datos = replay.cargar(clave)
            if datos is not None:
                USO.registrar(None, replay=True)
                return ChatCompletion.model_validate(datos)
            raise SinGrabacion("No hay respuesta grabada para este paso. Ejecútalo en vivo (con tu clave).")

        for intento in range(MAX_INTENTOS):
            LIMITADOR.esperar()
            try:
                respuesta = self._real.chat.completions.create(**kwargs)
                break
            except Exception as e:  # noqa: BLE001
                tipo = clasificar(e)
                if tipo == "minuto" and intento < MAX_INTENTOS - 1:
                    espera = segundos_reintento(e, intento)
                    USO.reintentos += 1
                    USO.espera_s += espera
                    print(f"⏳ Límite por minuto alcanzado; reintento en {espera:.0f} s…", flush=True)
                    time.sleep(espera)
                    continue
                if tipo == "temporal" and intento < 3:
                    USO.reintentos += 1
                    time.sleep(3 * (intento + 1))
                    continue
                if tipo in ("diaria", "clave") and config.modo() == "auto":
                    replay.ESTADO.solo_replay = True
                    datos = replay.cargar(clave)
                    if datos is not None:
                        print("⚠️  Sin cuota o sin clave: continúo con respuestas grabadas.", flush=True)
                        USO.registrar(None, replay=True)
                        return ChatCompletion.model_validate(datos)
                amigable = error_amigable(e, tipo)
                if amigable is e:
                    raise
                raise amigable from e

        USO.registrar(_uso_dict(respuesta.usage))
        if config.modo() == "record":
            replay.guardar(clave, "openai", respuesta.model_dump(mode="json"))
        return respuesta


class ClienteOpenAI:
    """Imita al cliente oficial de OpenAI: cliente.chat.completions.create(model=..., messages=..., tools=...)."""

    def __init__(self):
        from openai import OpenAI

        self._real = OpenAI(api_key=config.clave() or "sin-clave", base_url=config.url_base(), max_retries=0)
        self.chat = SimpleNamespace(completions=_Completions(self._real))


def cliente_openai() -> ClienteOpenAI:
    return ClienteOpenAI()
