"""Paquete de apoyo del curso de IA agéntica (CUNEF · MUCDIA).

Uso típico en un notebook:

    import mucdia
    mucdia.comprobar()               # entorno, datos y clave
    cliente = mucdia.cliente()       # cliente de chat para Microsoft Agent Framework
    mucdia.uso()                     # llamadas, tokens y coste equivalente
    mucdia.traza_df()                # una fila por llamada al modelo: tokens, latencia y herramientas
"""

import importlib.util
import os

from . import config, lab
from .codigo import ejecutar_codigo
from .conectores import servidor_mcp
from .cuota import USO, ClaveNoValida, CuotaDiariaAgotada, SinGrabacion
from .datos import buscar_documentos, consultar, esquema, sql_seguro
from .llm import cliente, cliente_openai
from .simulado import ClienteSimulado
from .telemetria import reiniciar_traza, traza_df
from .traza import mostrar_traza

__all__ = ["config", "lab", "cliente", "cliente_openai", "ClienteSimulado", "consultar", "sql_seguro", "esquema",
           "buscar_documentos", "ejecutar_codigo", "mostrar_traza", "traza_df", "reiniciar_traza", "servidor_mcp",
           "uso", "usar_modelo", "usar_modo", "comprobar", "CuotaDiariaAgotada", "ClaveNoValida", "SinGrabacion"]

# Paquetes que se añadieron al curso después de crear algunos Codespaces (sesiones 2 y 3).
PAQUETES_EXTRA = {"sklearn": "scikit-learn", "fastembed": "fastembed"}


def uso() -> None:
    """Muestra cuántas llamadas y tokens llevas y cuánto costaría en el plan de pago."""
    print(USO.resumen())


def usar_modelo(modelo: str) -> None:
    """Cambia el modelo para los clientes que crees a partir de ahora (p. ej. 'gemini-3.1-flash-lite')."""
    os.environ["MODELO"] = modelo
    print(f"Modelo activo: {modelo}. Vuelve a crear el cliente: cliente = mucdia.cliente()")


def usar_modo(modo: str) -> None:
    """auto (por defecto) | live | replay | record."""
    os.environ["MODO_LLM"] = modo
    from .replay import ESTADO

    ESTADO.solo_replay = modo == "replay"
    print(f"Modo del modelo: {config.modo()}")


def comprobar(llamar_al_modelo: bool = True) -> bool:
    """Comprueba el entorno: datos, clave y (opcionalmente) una llamada real al modelo."""
    ok = True
    if config.DB.exists():
        n = consultar("SELECT COUNT(*) AS n FROM ventas")["n"][0]
        print(f"✅ Base de datos encontrada ({n:,} pedidos)".replace(",", "."))
    else:
        print("❌ No encuentro data/mucdia.db. Ejecuta: python data/generar_datos.py")
        ok = False
    if config.clave():
        print(f"✅ Clave configurada para el proveedor '{config.proveedor()}' (modelo {config.modelo()})")
    else:
        print("⚠️  No hay clave configurada: solo funcionarán las respuestas grabadas (replay). Ver docs/setup.md")
        ok = False
    if faltan := [pip for modulo, pip in PAQUETES_EXTRA.items() if importlib.util.find_spec(modulo) is None]:
        print(f"⚠️  Faltan paquetes del curso ({', '.join(faltan)}). En un terminal:\n"
              "     pip install --user -r requirements.txt")
    if llamar_al_modelo and config.clave():
        try:
            r = cliente_openai().chat.completions.create(
                model=config.modelo(), messages=[{"role": "user", "content": "Responde solo con la palabra: listo"}])
            print(f"✅ El modelo responde: {r.choices[0].message.content.strip()!r}")
        except Exception as e:  # noqa: BLE001
            print(f"❌ El modelo no responde: {e}")
            ok = False
    return ok
