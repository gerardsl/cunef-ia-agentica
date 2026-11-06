"""Gestión de la cuota gratuita: limitador de llamadas por minuto, reintentos y contador de uso."""

import asyncio
import json
import re
import threading
import time
from collections import deque
from datetime import datetime
from zoneinfo import ZoneInfo

from . import config

# Precio orientativo del plan de pago (USD por millón de tokens: entrada, salida) para hablar de costes/ROI.
PRECIOS_USD = {
    "gemini-3.5-flash-lite": (0.30, 2.50),
    "gemini-3.1-flash-lite": (0.25, 1.50),
    "gemini-3.6-flash": (0.75, 3.75),
}
LIMITE_DIARIO_GRATIS = 500


class CuotaDiariaAgotada(RuntimeError):
    pass


class ClaveNoValida(RuntimeError):
    pass


class SinGrabacion(RuntimeError):
    pass


MENSAJE_CUOTA = (
    "⛔ Has agotado la cuota GRATUITA diaria de Gemini para el modelo {modelo}. "
    "Se reinicia a medianoche (hora del Pacífico), las 09:00 en Madrid.\n"
    "Opciones: 1) sigue en el portátil de otra persona de tu equipo; "
    "2) cambia de modelo (cada modelo tiene su propia cuota), p. ej. almansa.usar_modelo('gemini-3.1-flash-lite'); "
    "3) usa respuestas grabadas: almansa.usar_modo('replay')."
)
MENSAJE_CLAVE = (
    "🔑 No hay una clave válida para el modelo. Revisa docs/setup.md: en Codespaces, la clave va en el secret "
    "GEMINI_API_KEY; en local, en el fichero .env. Mientras tanto puedes usar almansa.usar_modo('replay')."
)


def dia_de_cuota() -> str:
    return datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()


class Uso:
    """Contador de llamadas, tokens y esperas (de este proceso y del día de cuota)."""

    def __init__(self):
        self._lock = threading.Lock()
        self.reiniciar()

    def reiniciar(self):
        self.llamadas = self.replay = self.reintentos = 0
        self.tokens_entrada = self.tokens_salida = 0
        self.espera_s = 0.0

    def registrar(self, uso: dict | None, replay: bool = False):
        with self._lock:
            if replay:
                self.replay += 1
                return
            self.llamadas += 1
            if uso:
                self.tokens_entrada += int(uso.get("input_token_count") or uso.get("prompt_tokens") or 0)
                self.tokens_salida += int(uso.get("output_token_count") or uso.get("completion_tokens") or 0)
        self._sumar_diario()

    def _sumar_diario(self):
        try:
            config.DIR_USO.mkdir(parents=True, exist_ok=True)
            ruta = config.DIR_USO / "uso_diario.json"
            datos = json.loads(ruta.read_text()) if ruta.exists() else {}
            clave = f"{dia_de_cuota()}|{config.modelo()}"
            datos[clave] = datos.get(clave, 0) + 1
            ruta.write_text(json.dumps(datos))
        except Exception:
            pass

    def llamadas_hoy(self) -> int:
        ruta = config.DIR_USO / "uso_diario.json"
        try:
            return json.loads(ruta.read_text()).get(f"{dia_de_cuota()}|{config.modelo()}", 0)
        except Exception:
            return 0

    def coste_equivalente_usd(self) -> float:
        pe, ps = PRECIOS_USD.get(config.modelo(), (0.30, 2.50))
        return (self.tokens_entrada * pe + self.tokens_salida * ps) / 1_000_000

    def resumen(self) -> str:
        hoy = self.llamadas_hoy()
        lineas = [
            f"Modelo: {config.modelo()}  ·  modo: {config.modo()}",
            f"Llamadas al modelo en esta sesión: {self.llamadas}  (respuestas grabadas: {self.replay}, reintentos: {self.reintentos})",
            f"Tokens: {self.tokens_entrada:,} de entrada · {self.tokens_salida:,} de salida".replace(",", "."),
            f"Coste si fuera de pago: {self.coste_equivalente_usd():.4f} USD (gratis en el plan gratuito)",
            f"Llamadas hoy en este equipo con este modelo: {hoy} de ~{LIMITE_DIARIO_GRATIS} gratuitas",
        ]
        if self.espera_s:
            lineas.append(f"Tiempo esperando por el límite por minuto: {self.espera_s:.0f} s")
        return "\n".join(lineas)


USO = Uso()


class Limitador:
    """Ventana deslizante de 60 s: como mucho MAX_RPM llamadas por minuto en este proceso."""

    def __init__(self):
        self._lock = threading.Lock()
        self._marcas: deque[float] = deque()

    def _espera(self) -> float:
        with self._lock:
            ahora = time.monotonic()
            while self._marcas and ahora - self._marcas[0] >= 60:
                self._marcas.popleft()
            if len(self._marcas) < config.max_rpm():
                self._marcas.append(ahora)
                return 0.0
            return 60 - (ahora - self._marcas[0]) + 0.2

    def esperar(self):
        while (s := self._espera()) > 0:
            _aviso_espera(s)
            time.sleep(s)

    async def esperar_async(self):
        while (s := self._espera()) > 0:
            _aviso_espera(s)
            await asyncio.sleep(s)


LIMITADOR = Limitador()
_ultimo_aviso = [0.0]


def _aviso_espera(segundos: float):
    USO.espera_s += segundos
    if time.monotonic() - _ultimo_aviso[0] > 20:
        _ultimo_aviso[0] = time.monotonic()
        print(f"⏳ Límite de {config.max_rpm()} llamadas/minuto: espero {segundos:.0f} s…", flush=True)


def texto_error(e: BaseException) -> str:
    partes, vistos = [], set()
    while e is not None and id(e) not in vistos:
        vistos.add(id(e))
        partes.append(f"{type(e).__name__}: {e}")
        for atributo in ("code", "status_code", "status"):
            valor = getattr(e, atributo, None)
            if valor:
                partes.append(str(valor))
        for atributo in ("body", "details", "response_json"):
            valor = getattr(e, atributo, None)
            if valor:
                partes.append(json.dumps(valor, default=str, ensure_ascii=False)[:3000])
        e = e.__cause__ or e.__context__
    return " | ".join(partes)


def clasificar(e: BaseException) -> str:
    """Devuelve 'diaria', 'minuto', 'temporal', 'clave' u 'otro'."""
    if isinstance(e, CuotaDiariaAgotada):
        return "diaria"
    if isinstance(e, ClaveNoValida):
        return "clave"
    t = texto_error(e)
    if re.search(r"429|RESOURCE_EXHAUSTED|rate.?limit|too many requests|quota", t, re.I):
        return "diaria" if re.search(r"PerDay|per.day|daily", t, re.I) else "minuto"
    if re.search(r"API.?key|API_KEY_INVALID|UNAUTHENTICATED|PERMISSION_DENIED|\b401\b|\b403\b", t, re.I):
        return "clave"
    if re.search(r"\b50[0234]\b|UNAVAILABLE|overloaded|INTERNAL|timed?.?out|timeout|connection", t, re.I):
        return "temporal"
    return "otro"


def segundos_reintento(e: BaseException, intento: int) -> float:
    m = re.search(r"retry(?:Delay| in| after)[\"']?\s*[:=]?\s*[\"']?(\d+(?:\.\d+)?)\s*s", texto_error(e), re.I)
    if m:
        return min(float(m.group(1)) + 1.0, 65.0)
    return min(5.0 * 2 ** intento, 60.0)


def error_amigable(e: BaseException, tipo: str) -> BaseException:
    if tipo == "diaria":
        return CuotaDiariaAgotada(MENSAJE_CUOTA.format(modelo=config.modelo()))
    if tipo == "clave":
        return ClaveNoValida(MENSAJE_CLAVE)
    return e
