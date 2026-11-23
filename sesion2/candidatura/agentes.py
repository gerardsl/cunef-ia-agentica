"""Los agentes del equipo: qué les pedimos (instrucciones) y qué deben devolver (esquemas).

    editor_cv     → adapta tu CV con el servidor MCP «mi-carrera» (sin inventar nada) y lo guarda
    investigador  → decide qué tienes que preparar sobre la empresa y lo prepara con fuentes
    coach         → un plan de 4 semanas para cerrar huecos y tu pitch de 3 frases

Tus instrucciones (labs 2b y 2c) sustituyen a las de referencia: ver candidatura.piezas.
"""

from typing import Literal

from pydantic import BaseModel, Field

from . import investigacion, piezas


# ------------------------------------------------------------------------------------------------ editor de CV
class Encaje(BaseModel):
    requisito: str = Field(description="El requisito de la oferta, tal cual")
    estado: Literal["cubierto", "parcial", "hueco"] = Field(
        description="cubierto: hay una prueba clara en el CV, el grado o el máster; parcial: hay algo relacionado pero "
                    "no es exactamente lo que piden (o está en curso); hueco: no hay ninguna prueba")
    evidencia: str = Field(description="Dónde está la prueba (sección del CV, asignatura del máster o competencia del "
                                       "grado). Vacío si es un hueco")


class Cambio(BaseModel):
    que: str = Field(description="Qué has cambiado en el CV, en una frase")
    por_que: str = Field(description="Para qué requisito o palabra clave de la oferta")


class CVAdaptado(BaseModel):
    archivo: str = Field(description="La ruta que devolvió guardar_cv al guardar el CV, o vacío si no se pudo guardar")
    palabras_clave: list[str] = Field(description="Las palabras clave de la oferta que has escrito TAL CUAL en el CV "
                                                  "porque describen con verdad el perfil")
    cambios: list[Cambio] = Field(description="Los cambios principales respecto al CV original (entre 3 y 8)")
    encaje: list[Encaje] = Field(description="Un elemento por cada requisito imprescindible de la oferta")
    huecos: list[str] = Field(description="Lo que la oferta pide y la persona no puede demostrar todavía. NO va en el "
                                          "CV: va al plan de preparación")


INSTRUCCIONES_EDITOR = """Eres el editor de CV de una persona que busca empleo en datos e IA. Adaptas su CV a UNA oferta
sin inventar nada: un CV con una mentira es peor que un CV peor escrito.

Cómo trabajas:
1. Lee el CV con leer_cv y el estado del máster con plan_de_estudios.
2. Para cada requisito técnico de la oferta, busca pruebas con buscar_competencias.
3. Antes de escribir, repasa las palabras clave de la oferta una a una: «la uso» si describe con verdad algo que la
   persona ha hecho o está estudiando (análisis de datos para quien ha analizado datos, por ejemplo), o «hueco» si no.
   Un filtro automático (ATS) busca esas palabras EXACTAS: escribe tal cual las que uses.
4. Reescribe el CV COMPLETO en Markdown, con su formato (nombre como título, contacto y secciones) y en el idioma de la
   oferta. Adáptalo de verdad, no lo copies:
   - Un único perfil de 2 o 3 líneas orientado al puesto, con las palabras clave que uses.
   - Ordena secciones, logros y proyectos para que lo más relevante para la oferta salga primero. No añadas logros
     nuevos: reescribe y reordena los que hay.
   - Sin inflar: 1.200 reseñas no son «grandes conjuntos de datos», y unas prácticas no son «un equipo
     multidisciplinar y ágil» si el CV no lo dice.
   - Bajo el máster, añade las asignaturas EN CURSO que más encajen con la oferta (como formación en curso) y, si
     encajan, las masterclasses ya HECHAS. Nunca las pendientes.
   - Prohibido inventar o inflar experiencia, cifras, títulos, herramientas o niveles que no consten en el CV, el grado
     o el máster.
5. Guarda el CV con guardar_cv. Si devuelve ERROR, quita o reescribe lo que señala y vuelve a guardarlo (como mucho,
   3 intentos).
6. Responde con el archivo que devolvió guardar_cv, las palabras clave usadas, los cambios, el encaje de cada requisito
   imprescindible y los huecos. Sé exigente con el encaje: «cubierto» solo si la prueba cumple el requisito tal como
   lo pide la oferta; si se parece o es discutible, «parcial». Lo que pongas en huecos no puede estar «cubierto». Un
   diagnóstico honesto sirve más que uno amable."""


# ------------------------------------------------------------------------------------------------ investigador
class Tema(BaseModel):
    tema: str = Field(description="Qué preparar, en pocas palabras")
    por_que: str = Field(description="Por qué importa para ESTA oferta y ESTE puesto")
    prioridad: Literal["alta", "media", "baja"]


class Seccion(BaseModel):
    titulo: str = Field(description="El tema que prepara esta sección")
    contenido: str = Field(description="Lo que hay que saber, en 3 a 6 frases, solo con lo que dicen las fuentes")
    fuentes: list[str] = Field(description="Las URL de las que sale cada dato (las que devolvieron las herramientas)")


class Dossier(BaseModel):
    empresa: str
    que_preparar: list[Tema] = Field(description="Entre 4 y 6 temas, de más a menos prioritario")
    secciones: list[Seccion] = Field(description="Una sección por cada tema que hayas podido investigar")
    preguntas_probables: list[str] = Field(description="5 o 6 preguntas que probablemente le harán: técnicas (por los "
                                                       "requisitos) y de motivación (por la empresa)")
    preguntas_para_ellos: list[str] = Field(description="3 preguntas inteligentes para hacer al final de la entrevista")
    no_encontrado: list[str] = Field(description="Lo que convendría saber y no aparece en las fuentes consultadas")


INSTRUCCIONES_INVESTIGADOR = """Eres investigador de empresas y preparas a una persona para la entrevista de ESTA oferta.
1. Decide qué tiene que preparar (entre 4 y 6 temas, con prioridad y por qué): qué hace la empresa y cómo gana
   dinero, sus cifras clave, noticias recientes, su estrategia de datos e IA, el área del puesto, su cultura o sus
   competidores… lo que más pese para este puesto.
2. Investiga con las herramientas: ficha_empresa primero; después noticias; y leer_web para la web oficial o una
   noticia clave. Como mucho, 6 llamadas.
3. Prepara el dossier: una sección por tema, solo con lo que digan las fuentes y con la URL de cada dato. Si algo no
   lo encuentras, ponlo en no_encontrado: no lo inventes ni lo completes con lo que «suele» pasar.
4. Añade las preguntas que probablemente le harán y 3 preguntas inteligentes para hacerles a ellos.
Responde en español."""


# ------------------------------------------------------------------------------------------------ coach
class Semana(BaseModel):
    semana: int = Field(description="1, 2, 3 o 4")
    objetivo: str = Field(description="El hueco o tema que cierra esta semana")
    acciones: list[str] = Field(description="2 o 3 acciones concretas (unas 5 horas en total)")
    prueba: str = Field(description="El entregable verificable que demuestra el avance: un repositorio, un cuaderno, un "
                                    "informe, un certificado…")


class PlanYPitch(BaseModel):
    plan: list[Semana] = Field(description="Exactamente 4 semanas")
    pitch: list[str] = Field(description="EXACTAMENTE 3 frases: por qué encaja en este puesto, con pruebas reales de su "
                                         "CV y una referencia concreta a la empresa")


INSTRUCCIONES_COACH = """Eres coach de carrera. Con la oferta, el encaje del CV y lo que hay que preparar sobre la
empresa, escribes:
1. Un plan de 4 semanas desde la fecha que te dan para cerrar los huecos más importantes. Cada semana: un objetivo, 2 o
   3 acciones concretas y una PRUEBA verificable (las empresas contratan pruebas, no promesas). Sé realista: quien cursa
   un máster a tiempo completo tiene unas 5 horas a la semana.
2. Un pitch de exactamente 3 frases, en primera persona: por qué encaja en este puesto, con una referencia concreta a
   la empresa. Cada hecho que cites debe aparecer TAL CUAL en el CV adaptado: no mezcles logros distintos ni atribuyas
   a un logro herramientas que no usó. No subas niveles ni conviertas tareas en responsabilidades: «nivel intermedio»
   no es «dominio» y «coordinar turnos de voluntarios» no es «coordinar equipos interdisciplinares». Sin superlativos
   («perfectamente», «experta»): que hablen las pruebas.
Responde en español."""


# ------------------------------------------------------------------------------------------------ fábricas
def _replay() -> bool:
    """Con respuestas grabadas se usan las instrucciones de referencia: son las que se grabaron."""
    try:
        from mucdia import replay

        return replay.debe_reproducir()
    except ImportError:
        return False


def instrucciones_editor() -> str:
    return INSTRUCCIONES_EDITOR if _replay() else piezas.instrucciones("editor_cv", INSTRUCCIONES_EDITOR)


def instrucciones_investigador() -> str:
    return INSTRUCCIONES_INVESTIGADOR if _replay() else piezas.instrucciones("investigador", INSTRUCCIONES_INVESTIGADOR)


def editor_cv(cliente, servidor_mcp, middleware=None, instrucciones: str | None = None):
    from agent_framework import Agent

    return Agent(client=cliente, name="editor_cv", instructions=instrucciones or instrucciones_editor(),
                 tools=[servidor_mcp], middleware=middleware or [])


def investigador(cliente, middleware=None, instrucciones: str | None = None):
    from agent_framework import Agent

    return Agent(client=cliente, name="investigador", instructions=instrucciones or instrucciones_investigador(),
                 tools=investigacion.HERRAMIENTAS, middleware=middleware or [])


def coach(cliente, middleware=None):
    from agent_framework import Agent

    return Agent(client=cliente, name="coach", instructions=INSTRUCCIONES_COACH, middleware=middleware or [])


def describir_oferta(oferta) -> str:
    """La oferta estructurada, en texto, para pasársela a otro agente."""
    requisitos = "\n".join(f"- [{r.tipo} · {r.categoria}] {r.texto}" for r in oferta.requisitos)
    return (f"Puesto: {oferta.puesto} · Empresa: {oferta.empresa} · {oferta.ubicacion} · {oferta.modalidad} · "
            f"nivel {oferta.nivel}\nResumen: {oferta.resumen}\nTareas:\n" + "\n".join(f"- {t}" for t in oferta.tareas)
            + f"\nRequisitos:\n{requisitos}\nPalabras clave: {', '.join(oferta.palabras_clave)}")
