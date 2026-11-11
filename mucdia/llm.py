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

from . import config, replay, telemetria
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
    """Se ejecuta en cada llamada al modelo: replay → límite por minuto → reintentos → contador y telemetría."""

    async def process(self, context: ChatContext, call_next):
        if context.stream:
            await LIMITADOR.esperar_async()
            context.stream_result_transforms.append(self._contar)
            await call_next()
            return

        clave = replay.clave_maf(context.messages, context.options)
        if replay.debe_reproducir(clave):
            if self._reproducir(context, clave):
                return
            raise SinGrabacion("No hay respuesta grabada para este paso. Ejecútalo en vivo (con tu clave) o "
                               "comprueba que no has cambiado el código del ejemplo.")

        for intento in range(MAX_INTENTOS):
            await LIMITADOR.esperar_async()
            t0 = time.perf_counter()
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
        ms = (time.perf_counter() - t0) * 1000

        if isinstance(context.result, ChatResponse):
            uso = _uso_dict(context.result.usage_details)
            USO.registrar(uso)
            telemetria.registrar(cliente="maf", modelo=config.modelo(), grabada=False, uso=uso, ms=ms,
                                 herramientas=telemetria.herramientas_maf(context.result),
                                 mensajes=len(context.messages or []))
            if config.graba():
                replay.guardar(clave, "maf", context.result.to_dict(), ms=ms)

    @staticmethod
    def _contar(respuesta):
        USO.registrar(_uso_dict(getattr(respuesta, "usage_details", None)))
        return respuesta

    @staticmethod
    def _reproducir(context: ChatContext, clave: str) -> bool:
        grabacion = replay.cargar(clave)
        if grabacion is None:
            return False
        datos, ms = grabacion
        context.result = ChatResponse.from_dict(datos)
        uso = _uso_dict(context.result.usage_details)
        USO.registrar(uso, replay=True)
        telemetria.registrar(cliente="maf", modelo=config.modelo(), grabada=True, uso=uso, ms=ms,
                             herramientas=telemetria.herramientas_maf(context.result),
                             mensajes=len(context.messages or []))
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

    @staticmethod
    def _desde_grabacion(grabacion, kwargs):
        from openai.types.chat import ChatCompletion

        datos, ms = grabacion
        respuesta = ChatCompletion.model_validate(datos)
        uso = _uso_dict(respuesta.usage)
        USO.registrar(uso, replay=True)
        telemetria.registrar(cliente="openai", modelo=kwargs.get("model") or config.modelo(), grabada=True, uso=uso,
                             ms=ms, herramientas=telemetria.herramientas_openai(respuesta),
                             mensajes=len(kwargs.get("messages") or []))
        return respuesta

    def create(self, **kwargs):
        clave = replay.clave_openai(kwargs)
        if replay.debe_reproducir(clave):
            grabacion = replay.cargar(clave)
            if grabacion is not None:
                return self._desde_grabacion(grabacion, kwargs)
            raise SinGrabacion("No hay respuesta grabada para este paso. Ejecútalo en vivo (con tu clave).")

        for intento in range(MAX_INTENTOS):
            LIMITADOR.esperar()
            t0 = time.perf_counter()
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
                    grabacion = replay.cargar(clave)
                    if grabacion is not None:
                        print("⚠️  Sin cuota o sin clave: continúo con respuestas grabadas.", flush=True)
                        return self._desde_grabacion(grabacion, kwargs)
                amigable = error_amigable(e, tipo)
                if amigable is e:
                    raise
                raise amigable from e
        ms = (time.perf_counter() - t0) * 1000

        uso = _uso_dict(respuesta.usage)
        USO.registrar(uso)
        telemetria.registrar(cliente="openai", modelo=kwargs.get("model") or config.modelo(), grabada=False, uso=uso,
                             ms=ms, herramientas=telemetria.herramientas_openai(respuesta),
                             mensajes=len(kwargs.get("messages") or []))
        if config.graba():
            replay.guardar(clave, "openai", respuesta.model_dump(mode="json"), ms=ms)
        return respuesta


class ClienteOpenAI:
    """Imita al cliente oficial de OpenAI: cliente.chat.completions.create(model=..., messages=..., tools=...)."""

    def __init__(self):
        from openai import OpenAI

        self._real = OpenAI(api_key=config.clave() or "sin-clave", base_url=config.url_base(), max_retries=0)
        self.chat = SimpleNamespace(completions=_Completions(self._real))


def cliente_openai() -> ClienteOpenAI:
    return ClienteOpenAI()
