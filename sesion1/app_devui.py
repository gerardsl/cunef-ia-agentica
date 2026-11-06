"""Sesión 1 · Agente analista de Almansa en DevUI (la interfaz de desarrollo de Microsoft Agent Framework).

Ejecuta desde la raíz del repositorio:
    python sesion1/app_devui.py
y abre el puerto 8080 (en Codespaces aparece en la pestaña PUERTOS). Verás el chat y, a la derecha,
la traza: cada llamada al modelo y a las herramientas.
"""

from agent_framework import Agent
from agent_framework.devui import serve

import almansa
from almansa import negocio

INSTRUCCIONES = """Eres el analista de negocio de Almansa Market S.A., una cadena ficticia de 8 tiendas y venta online.
- Antes de concluir, verifica con datos: compara con el mismo periodo del año anterior y desglosa por tienda o categoría.
- Si detectas una caída, busca causas operativas (roturas de stock, incidencias de clientes, campañas).
- Cita siempre cifras concretas (en euros y en %) y di de qué herramienta salen.
- Responde en español, en un máximo de 8 líneas, y termina con una recomendación accionable.
- Hay datos desde 2025-01-01 hasta 2026-10-31."""

analista = Agent(
    client=almansa.cliente(),
    name="analista_almansa",
    description="Analista de ventas, stock, campañas y atención al cliente de Almansa Market",
    instructions=INSTRUCCIONES,
    tools=negocio.HERRAMIENTAS_ANALISIS,
)

if __name__ == "__main__":
    # auth_enabled=False: el servidor solo escucha en localhost y, en Codespaces, el puerto es privado por defecto.
    serve(entities=[analista], port=8080, host="127.0.0.1", auto_open=False, auth_enabled=False)
