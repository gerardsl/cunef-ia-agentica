"""Servidor MCP «mi-carrera»: tu CV y lo que has aprendido, al alcance de cualquier agente… con reglas.

Cualquier cliente MCP puede usarlo: el agente de la webapp (Microsoft Agent Framework), GitHub Copilot en VS Code
(ver .vscode/mcp.json), Claude Desktop… Se comunica por stdio (entrada/salida estándar): no abre ningún puerto.

    Herramientas: leer_cv · plan_de_estudios · buscar_competencias · guardar_cv
    Recursos:     carrera://cv · carrera://grado · carrera://master · carrera://plan
    Prompt:       adaptar_cv

Mínimo privilegio: lee tu perfil (sesion2/mi_perfil/, o el ejemplo ficticio si aún no has puesto el tuyo) y solo
escribe versiones nuevas en sesion2/trabajo/cv/. Nunca modifica tu CV original. Y guardar_cv tiene un guardarraíl en
código (el tuyo del lab 2b, si lo has escrito): ningún cliente puede guardar un CV con cifras o herramientas sin
respaldo, por mucho que se lo pida al modelo.

Probarlo con el inspector oficial:   mcp dev sesion2/servidor_mcp_carrera.py
Lanzarlo a mano (se queda esperando): python sesion2/servidor_mcp_carrera.py
"""

from typing import Annotated

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from candidatura import carrera

LECTURA = {"annotations": ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False),
           "structured_output": False}
ESCRITURA = {"annotations": ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True,
                                            openWorldHint=False),
             "structured_output": False}

mcp = MCPServer(
    "mi-carrera",
    instructions=(
        "Perfil profesional de una persona que estudia el Máster en Ciencia de Datos e IA de CUNEF: su CV, lo que "
        "aprendió en su grado y en el máster, y las masterclasses de IA agéntica. Lee siempre el CV (leer_cv) antes de "
        "proponer cambios. guardar_cv solo guarda versiones nuevas y rechaza cifras o herramientas que no consten."
    ),
)


@mcp.tool(**LECTURA)
def leer_cv() -> str:
    """Devuelve el CV de la persona en Markdown, tal como está ahora (su versión original)."""
    yo = carrera.perfil()
    aviso = ("(CV de EJEMPLO, ficticio: la persona todavía no ha puesto el suyo en sesion2/mi_perfil/cv.md)\n\n"
             if yo["origen"] == "ejemplo" else "")
    return aviso + (yo["cv"] or "ERROR: el CV está vacío.")


@mcp.tool(**LECTURA)
def plan_de_estudios() -> str:
    """Asignaturas oficiales del máster (MUCD-IA, CUNEF) con su estado a día de hoy (cursada, en curso o pendiente), y
    las masterclasses de IA agéntica. Úsala para saber qué formación puede citarse y cómo."""
    return carrera.plan_texto()


@mcp.tool(**LECTURA)
def buscar_competencias(
    consulta: Annotated[str, "Competencia, herramienta o tema que pide la oferta, p. ej. «Power BI» o «series temporales»"],
) -> str:
    """Busca dónde ha aprendido la persona algo que pide la oferta: en su grado, en lo que ha hecho en el máster, en el
    plan de estudios y en las masterclasses. Devuelve cada resultado con su origen y su estado."""
    return carrera.buscar_competencias(consulta)


@mcp.tool(**ESCRITURA)
def guardar_cv(
    empresa: Annotated[str, "Empresa de la oferta"],
    puesto: Annotated[str, "Puesto de la oferta"],
    cv_markdown: Annotated[str, "El CV adaptado COMPLETO, en Markdown"],
) -> str:
    """Guarda una versión del CV adaptada a una oferta (Markdown y Word) en sesion2/trabajo/cv/. No modifica el CV
    original. Antes comprueba que todas las cifras y herramientas del CV nuevo constan en el CV original, el grado, el
    máster o las masterclasses: si no, NO lo guarda y devuelve un ERROR con lo que hay que corregir."""
    if len(cv_markdown.strip()) < 300:
        return "ERROR: ese CV está casi vacío. Pásame el CV adaptado completo en Markdown."
    sin_respaldo = carrera.afirmaciones_sin_respaldo(cv_markdown)
    if sin_respaldo:
        return ("ERROR: no lo guardo. Estas afirmaciones no constan en el CV original, el grado, el máster ni las "
                f"masterclasses: {', '.join(sin_respaldo)}. Quítalas o reescríbelas con lo que sí consta y vuelve a "
                "llamar a guardar_cv.")
    ruta = carrera.guardar_version(empresa, puesto, cv_markdown)
    relativa = ruta.relative_to(carrera.S2.parent).as_posix()
    return f"Guardado: {relativa} (y su versión en Word, .docx). {len(cv_markdown.split())} palabras."


@mcp.resource("carrera://cv", name="CV", mime_type="text/markdown")
def recurso_cv() -> str:
    """El CV original de la persona."""
    return carrera.perfil()["cv"]


@mcp.resource("carrera://grado", name="Competencias del grado", mime_type="text/markdown")
def recurso_grado() -> str:
    """Lo que la persona aprendió en su grado (lo escribe ella)."""
    return carrera.perfil()["grado"] or "(vacío)"


@mcp.resource("carrera://master", name="Lo hecho en el máster", mime_type="text/markdown")
def recurso_master() -> str:
    """Prácticas y proyectos que la persona ha hecho en el máster (lo escribe ella)."""
    return carrera.perfil()["master"] or "(vacío)"


@mcp.resource("carrera://plan", name="Plan de estudios del MUCD-IA", mime_type="text/plain")
def recurso_plan() -> str:
    """El plan oficial del máster con el estado de cada asignatura."""
    return carrera.plan_texto()


@mcp.prompt(title="Adaptar el CV a una oferta")
def adaptar_cv(oferta: str) -> str:
    """Plantilla para pedir a cualquier asistente que adapte el CV a una oferta (pega la oferta o su enlace)."""
    return (
        f"Adapta mi CV a esta oferta:\n\n{oferta}\n\n"
        "1) Lee mi CV con leer_cv y el estado de mi máster con plan_de_estudios. 2) Busca con buscar_competencias "
        "dónde aprendí lo que pide la oferta. 3) Reescribe el CV completo en Markdown sin inventar nada: ni cifras, ni "
        "herramientas, ni experiencia. 4) Guárdalo con guardar_cv y dime qué has cambiado y qué huecos me quedan."
    )


if __name__ == "__main__":
    mcp.run()
