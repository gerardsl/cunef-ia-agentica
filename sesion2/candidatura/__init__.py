"""Tu agente de candidaturas (sesión 2): las piezas que usan los notebooks, el servidor MCP y la webapp.

    import sys, mucdia
    sys.path.insert(0, str(mucdia.config.RAIZ / "sesion2"))
    import candidatura as C

    C.oferta.leer_oferta(url)              # paso 1 · leer la oferta (robots.txt, JSON-LD…)
    C.carrera.buscar_competencias("SQL")   # paso 2 · tu carrera como datos (lo usa el servidor MCP)
    C.investigacion.noticias("BBVA")       # paso 3 · investigar la empresa con fuentes
    from candidatura import flujo          # todo junto, como en la webapp

Este fichero no importa nada pesado: el servidor MCP también usa el paquete y debe arrancar rápido.
"""

from . import agentes, carrera, investigacion, oferta, piezas, web

__all__ = ["agentes", "carrera", "investigacion", "oferta", "piezas", "web", "fmt"]


def fmt(numero) -> str:
    """1497 → «1.497» (separador de miles español)."""
    return f"{numero:,}".replace(",", ".")
