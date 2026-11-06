"""Servidor MCP de Almansa Market: da acceso de SOLO LECTURA a la base de datos y a los documentos internos.

Cualquier cliente MCP puede usarlo: un agente de Microsoft Agent Framework, GitHub Copilot en VS Code,
Claude Desktop, etc. Se comunica por stdio (entrada/salida estándar), así que no hace falta abrir puertos.

Probarlo con el inspector oficial:   mcp dev sesion2/servidor_mcp_almansa.py
Lanzarlo a mano (se queda esperando): python sesion2/servidor_mcp_almansa.py
"""

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from almansa import datos, negocio

SOLO_LECTURA = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)

mcp = MCPServer(
    "almansa-datos",
    instructions=(
        "Datos comerciales de Almansa Market S.A. (empresa ficticia): ventas, productos, clientes, campañas, "
        "inventario, tickets de soporte y reseñas, más un buscador de documentos internos. Todo es de solo lectura. "
        "Llama primero a describir_datos para conocer las tablas antes de escribir SQL."
    ),
)


@mcp.tool(annotations=SOLO_LECTURA)
def describir_datos() -> str:
    """Lista las tablas y vistas de la base de datos con sus columnas y las notas del diccionario de datos.
    Llámala antes de escribir SQL."""
    return datos.esquema()


@mcp.tool(annotations=SOLO_LECTURA)
def consultar_sql(sql: str) -> str:
    """Ejecuta UNA consulta SQL de solo lectura (SELECT o WITH, dialecto SQLite) y devuelve hasta 50 filas en CSV.
    Usa preferentemente las vistas v_ventas_lineas y v_ventas_mensuales. Las ventas reales son las de estado = 'completada'."""
    return datos.sql_seguro(sql)


@mcp.tool(annotations=SOLO_LECTURA)
def buscar_documentos(consulta: str) -> str:
    """Busca en los documentos internos (políticas, actas del comité, contratos, informes, FAQ) y devuelve los
    fragmentos más relevantes con su fuente, su fecha y su estado (vigente u obsoleto)."""
    return negocio.buscar_en_documentos(consulta)


@mcp.resource("almansa://diccionario", name="Diccionario de datos", mime_type="text/plain")
def diccionario() -> str:
    """Esquema y notas de la base de datos de Almansa."""
    return datos.esquema()


@mcp.prompt(title="Informe de área")
def informe_de_area(area: str, pregunta: str) -> str:
    """Plantilla para pedir un informe de negocio sobre un área (Finanzas, Marketing, Operaciones...)."""
    return (
        f"Actúa como analista del área de {area} de Almansa Market. Pregunta: {pregunta}\n"
        "1) Explora los datos con describir_datos y consultar_sql. 2) Busca contexto en los documentos internos. "
        "3) Responde con cifras concretas, cita las fuentes (tabla o documento) y termina con una recomendación."
    )


if __name__ == "__main__":
    mcp.run()
