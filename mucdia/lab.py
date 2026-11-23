"""Comprobaciones automáticas, pistas y soluciones de respaldo de los labs de la sesión 2.

    mucdia.lab.comprobar_jobposting(...) · comprobar_oferta(...) · comprobar_respaldo(...)   # ✅ o ❌ con lo que falla
    mucdia.lab.comprobar_editor(texto) · comprobar_investigador(texto)
    mucdia.lab.pista("jobposting")                 # una pista
    mucdia.lab.solucion("jobposting")              # la solución (si te has atascado: cópiala y sigue)
"""

import typing

PISTAS: dict[str, list[str]] = {}
SOLUCIONES: dict[str, str] = {}


def pista(clave: str) -> None:
    """Muestra las pistas de un ejercicio: 'jobposting', 'oferta', 'respaldo', 'editor' o 'investigador'."""
    for i, texto in enumerate(PISTAS.get(clave, ["No hay pistas con ese nombre."]), start=1):
        print(f"💡 {i}. {texto}")


def solucion(clave: str) -> None:
    """Imprime la solución de un ejercicio para que puedas copiarla y seguir."""
    print(SOLUCIONES.get(clave, "No hay solución con ese nombre."))


def _fallo(mensaje: str, clave: str) -> bool:
    print(f"❌ {mensaje}\n   Pista: mucdia.lab.pista({clave!r})  ·  Atascado: mucdia.lab.solucion({clave!r})")
    return False


PISTAS.update({
    "jobposting": [
        "Con BeautifulSoup: `sopa = BeautifulSoup(html, \"html.parser\")` y "
        "`sopa.find_all(\"script\", type=\"application/ld+json\")`.",
        "El texto de cada bloque es `script.string`; conviértelo con `json.loads(..., strict=False)` dentro de un "
        "`try` (si un bloque no es JSON válido, `continue`).",
        "Un bloque puede ser un diccionario, una LISTA de diccionarios o un diccionario con la clave \"@graph\" (otra "
        "lista): recórrelos todos.",
        "Devuelve el primer diccionario cuyo `d.get(\"@type\")` sea \"JobPosting\" (o una lista que lo contenga). Si "
        "no hay ninguno, `return None`.",
    ],
    "oferta": [
        "El modelo lee las descripciones (`Field(description=...)`): son sus instrucciones campo a campo.",
        "tipo: di cuándo es «imprescindible» (la oferta lo exige: «requisitos», «se requiere», «must have») y cuándo "
        "«deseable» (lo valora: «se valorará», «plus», «nice to have»).",
        "salario: que lo copie solo si la oferta lo dice; si no, «no consta». Nunca que lo estime.",
        "palabras_clave: herramientas, técnicas, títulos e idiomas que buscaría un filtro automático (ATS), escritos "
        "como en la oferta; sin el nombre de la empresa ni palabras sueltas genéricas.",
    ],
    "respaldo": [
        "Las cifras de un texto: `re.findall(r\"\\d+(?:[.,]\\d+)*\", texto)` (encuentra 5, 1.200, 0,74…).",
        "Normaliza quitando puntos y comas: `re.sub(r\"[.,]\", \"\", cifra)` (así «1.200» y «1200» son la misma).",
        "Guarda en un conjunto las cifras normalizadas de las fuentes y recorre las del CV nuevo: si su versión "
        "normalizada no está, añádela (tal como aparece en el CV) a la lista, sin repetir.",
    ],
    "editor": [
        "Dile cómo trabajar: leer_cv y plan_de_estudios primero; buscar_competencias para cada requisito técnico; "
        "guardar_cv al final.",
        "La regla de oro, explícita: no inventar ni inflar experiencia, cifras, herramientas, títulos o niveles.",
        "El máster: las asignaturas en curso van como formación en curso; las pendientes, nunca.",
        "Qué hacer si guardar_cv devuelve ERROR: corregir lo que señala y volver a guardar (con un límite de intentos).",
    ],
    "investigador": [
        "Primero, que DECIDA qué preparar para esta oferta (4-6 temas con prioridad y por qué).",
        "Después, que investigue con ficha_empresa, noticias y leer_web, con un límite de llamadas.",
        "Que cite la URL de cada dato y ponga en no_encontrado lo que no encuentre: nada de rellenar con lo que «suele» "
        "pasar.",
    ],
})

SOLUCIONES.update({
    "jobposting": '''\
%%writefile "{PIEZAS}/oferta.py"
import json

from bs4 import BeautifulSoup


def extraer_jobposting(html: str) -> dict | None:
    """Devuelve el primer objeto JobPosting de los bloques JSON-LD del HTML, o None si no hay."""
    sopa = BeautifulSoup(html or "", "html.parser")
    for script in sopa.find_all("script", type="application/ld+json"):
        try:
            datos = json.loads(script.string or "", strict=False)
        except json.JSONDecodeError:
            continue                                   # un bloque roto no debe romper la lectura
        pendientes = [datos]
        while pendientes:
            d = pendientes.pop(0)
            if isinstance(d, list):
                pendientes.extend(d)                   # una lista de objetos
            elif isinstance(d, dict):
                tipo = d.get("@type")
                if tipo == "JobPosting" or (isinstance(tipo, list) and "JobPosting" in tipo):
                    return d
                if "@graph" in d:                      # un grafo con varios objetos
                    pendientes.append(d["@graph"])
    return None''',
    "oferta": '''\
class Requisito(BaseModel):
    texto: str = Field(description="El requisito, resumido en una línea y fiel a la oferta")
    tipo: Literal["imprescindible", "deseable"] = Field(
        description="imprescindible si la oferta lo exige (requisitos, «se requiere», «must have»); deseable si solo lo "
                    "valora («se valorará», «plus», «nice to have»)")
    categoria: Literal["técnica", "negocio", "idioma", "formación", "experiencia", "personal"] = Field(
        description="técnica: herramientas y métodos; negocio: sector o función; idioma; formación: títulos; "
                    "experiencia: años o puestos previos; personal: competencias transversales")


class Oferta(BaseModel):
    empresa: str = Field(description="Nombre comercial de la empresa que contrata (no el del portal de empleo)")
    puesto: str = Field(description="Nombre del puesto tal como lo anuncia la oferta")
    ubicacion: str = Field(description="Ciudad o ciudades; «no consta» si no lo dice")
    modalidad: Literal["presencial", "híbrido", "remoto", "no consta"] = Field(description="Modalidad de trabajo")
    nivel: Literal["prácticas", "júnior", "intermedio", "sénior", "no consta"] = Field(
        description="Nivel según la experiencia que pide: prácticas; júnior (0-2 años); intermedio (3-5); sénior (más)")
    salario: str = Field(description="Banda salarial solo si la oferta la indica; si no, «no consta». Nunca la estimes")
    resumen: str = Field(description="Qué hará la persona y para qué, en dos frases")
    tareas: list[str] = Field(description="Las funciones principales del puesto, una por línea")
    requisitos: list[Requisito] = Field(description="Todos los requisitos de la oferta, imprescindibles y deseables")
    palabras_clave: list[str] = Field(
        description="Herramientas, técnicas, títulos e idiomas que un filtro automático (ATS) buscaría en el CV, escritos "
                    "como en la oferta; entre 8 y 20. Ni el nombre de la empresa, ni el de equipos internos, ni "
                    "palabras sueltas genéricas («Data», «IA»)")''',
    "respaldo": '''\
%%writefile "{PIEZAS}/guardarrail.py"
import re


def cifras_sin_respaldo(cv_nuevo: str, fuentes: str) -> list[str]:
    """Cifras del CV nuevo que no aparecen en ninguna fuente («1.200» y «1200» cuentan como la misma)."""
    def normalizar(cifra):
        return re.sub(r"[.,]", "", cifra)

    conocidas = {normalizar(c) for c in re.findall(r"\\d+(?:[.,]\\d+)*", fuentes)}
    nuevas = []
    for cifra in re.findall(r"\\d+(?:[.,]\\d+)*", cv_nuevo):
        if normalizar(cifra) not in conocidas and cifra not in nuevas:
            nuevas.append(cifra)
    return nuevas''',
    "editor": '''\
INSTRUCCIONES_EDITOR = C.agentes.INSTRUCCIONES_EDITOR   # la de referencia; léela con print(INSTRUCCIONES_EDITOR)''',
    "investigador": '''\
INSTRUCCIONES_INVESTIGADOR = C.agentes.INSTRUCCIONES_INVESTIGADOR   # léela con print(INSTRUCCIONES_INVESTIGADOR)''',
})


# ------------------------------------------------------------------------------------------- lab 2a · JSON-LD
def _ld(*bloques: str) -> str:
    scripts = "".join(f'<script type="application/ld+json">{b}</script>' for b in bloques)
    return f"<html><head><title>Oferta</title>{scripts}</head><body><h1>Oferta</h1></body></html>"


def comprobar_jobposting(extraer_jobposting) -> bool:
    oferta = '{"@context": "https://schema.org", "@type": "JobPosting", "title": "Data Analyst Junior", ' \
             '"hiringOrganization": {"@type": "Organization", "name": "Ejemplo S.A."}, "description": "<p>SQL</p>"}'
    empresa = '{"@context": "https://schema.org", "@type": "Organization", "name": "Ejemplo S.A."}'
    casos = [
        ("un bloque con la oferta", _ld(oferta), "Data Analyst Junior"),
        ("la oferta dentro de una lista", _ld(f"[{empresa}, {oferta}]"), "Data Analyst Junior"),
        ("la oferta dentro de un @graph", _ld('{"@context": "https://schema.org", "@graph": [' + empresa + ", " + oferta + "]}"),
         "Data Analyst Junior"),
        ("un bloque roto antes de la oferta", _ld("{esto no es JSON", oferta), "Data Analyst Junior"),
        ("solo la ficha de la empresa (sin oferta)", _ld(empresa), None),
        ("una página sin JSON-LD", "<html><body><p>Hola</p></body></html>", None),
    ]
    for nombre, html, esperado in casos:
        try:
            r = extraer_jobposting(html)
        except Exception as error:  # noqa: BLE001
            return _fallo(f"Con {nombre}, tu función lanza {type(error).__name__}: {error}. Un bloque raro no debe "
                          "romper la lectura: usa try/except y sigue con el siguiente.", "jobposting")
        obtenido = r.get("title") if isinstance(r, dict) else r
        if obtenido != esperado:
            return _fallo(f"Con {nombre} debería devolver {'el JobPosting' if esperado else 'None'} y devuelve "
                          f"{str(r)[:120]!r}.", "jobposting")
    print("✅ Tu lector de JSON-LD funciona en los 6 casos (objeto, lista, @graph, bloque roto, sin oferta y sin JSON-LD).\n"
          "   Es lo que leen Google y los portales: título, empresa, ubicación, fecha, salario y descripción, sin adivinar "
          "dónde está cada cosa en el HTML.")
    return True


# ------------------------------------------------------------------------------------------- lab 2a · esquema
def comprobar_oferta(Oferta) -> bool:  # noqa: N803
    from pydantic import BaseModel

    if not (isinstance(Oferta, type) and issubclass(Oferta, BaseModel)):
        return _fallo("Oferta debe ser una clase de Pydantic (class Oferta(BaseModel): ...).", "oferta")
    campos = Oferta.model_fields
    for nombre in ("empresa", "puesto", "salario", "requisitos", "palabras_clave"):
        if nombre not in campos:
            return _fallo(f"A Oferta le falta el campo {nombre!r}.", "oferta")
    sin_describir = [n for n, c in campos.items() if not (c.description or "").strip() or "TODO" in (c.description or "")]
    if sin_describir:
        return _fallo(f"Describe estos campos (sin TODO): {sin_describir}. El modelo lee las descripciones: son sus "
                      "instrucciones.", "oferta")
    if "no consta" not in (campos["salario"].description or "").lower():
        return _fallo("En salario, di qué hacer si la oferta no lo indica («no consta»): si no, el modelo lo estimará.",
                      "oferta")
    try:
        requisito = typing.get_args(campos["requisitos"].annotation)[0]
        tipo = requisito.model_fields["tipo"]
    except (IndexError, AttributeError, KeyError):
        return _fallo("requisitos debe ser list[Requisito], y Requisito, tener un campo tipo.", "oferta")
    if set(typing.get_args(tipo.annotation)) != {"imprescindible", "deseable"}:
        return _fallo('Requisito.tipo debe ser Literal["imprescindible", "deseable"]: así no puede inventarse otro valor.',
                      "oferta")
    if not (tipo.description or "").strip() or "TODO" in (tipo.description or ""):
        return _fallo("Describe Requisito.tipo: cuándo es imprescindible y cuándo deseable.", "oferta")
    print("✅ Tu esquema es un contrato: tipos que validan (Literal) y descripciones que el modelo lee como instrucciones.")
    return True


# ------------------------------------------------------------------------------------------- lab 2b · guardarraíl
def comprobar_respaldo(cifras_sin_respaldo) -> bool:
    casos = [
        ("Ahorré 5 horas a la semana.", "pasó de 5 horas a 1 hora", []),
        ("Analicé 1.200 reseñas.", "clasifiqué 1200 reseñas", []),
        ("AUC de 0,74.", "un AUC de 0,74", []),
        ("Subí las ventas un 20 % en 8 tiendas.", "el informe de las 8 tiendas", ["20"]),
        ("3 años de SQL y 3 proyectos con 7 personas.", "SQL", ["3", "7"]),
    ]
    for cv, fuentes, esperado in casos:
        try:
            r = cifras_sin_respaldo(cv, fuentes)
        except Exception as error:  # noqa: BLE001
            return _fallo(f"cifras_sin_respaldo({cv!r}, …) lanza {type(error).__name__}: {error}", "respaldo")
        if not isinstance(r, list) or [str(x) for x in r] != esperado:
            return _fallo(f"Con el CV {cv!r} y las fuentes {fuentes!r} debería devolver {esperado} y devuelve {r!r}.",
                          "respaldo")
    print("✅ Tu guardarraíl funciona. Ya vive dentro del servidor MCP: guardar_cv lo usa antes de guardar, así que "
          "ningún cliente (este agente, Copilot o Claude) puede guardar un CV con una cifra inventada.")
    return True


# ------------------------------------------------------------------------------------------- labs 2b y 2c · instrucciones
def _revisar(texto: str, requisitos: dict[str, tuple[str, ...]], clave: str) -> bool:
    if not isinstance(texto, str) or len(texto.strip()) < 200 or "TODO" in texto:
        return _fallo("Escribe las instrucciones completas (sin TODO): son el puesto de trabajo del agente.", clave)
    t = texto.lower()
    faltan = [que for que, palabras in requisitos.items() if not any(p in t for p in palabras)]
    if faltan:
        return _fallo("A tus instrucciones les falta: " + "; ".join(faltan) + ".", clave)
    print("✅ Tus instrucciones cubren lo esencial: cómo trabajar, con qué herramientas y qué no debe hacer. Ojo: el "
          "modelo las sigue… casi siempre. Lo que no puede fallar va en código (como el guardarraíl de guardar_cv).")
    return True


def comprobar_editor(texto: str) -> bool:
    return _revisar(texto, {
        "cómo leer el CV (leer_cv)": ("leer_cv",),
        "cómo buscar pruebas (buscar_competencias)": ("buscar_competencias",),
        "cómo guardar el resultado (guardar_cv) y qué hacer si da ERROR": ("guardar_cv",),
        "la regla de no inventar": ("invent", "inflar"),
        "qué hacer con las asignaturas en curso o pendientes": ("en curso", "pendiente"),
    }, "editor")


def comprobar_investigador(texto: str) -> bool:
    return _revisar(texto, {
        "decidir qué preparar para ESTA oferta": ("prepar",),
        "qué herramientas usar (ficha_empresa, noticias, leer_web)": ("ficha_empresa", "noticias", "leer_web"),
        "citar las fuentes (URL)": ("fuente", "url"),
        "qué hacer si no encuentra algo (sin inventar)": ("no_encontrado", "invent", "no lo encuentr"),
    }, "investigador")
