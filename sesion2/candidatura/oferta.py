"""Paso 1 · Leer la oferta: lo exacto, en código; el juicio, en el modelo.

    pagina = leer_oferta(url)             # robots.txt → JSON público (Workday) → JSON-LD → microdatos → texto
    pagina = desde_texto(texto_pegado)    # si la web no deja leerla (LinkedIn, InfoJobs…), la persona pega el texto
    oferta = await analizar_oferta(cliente, pagina)   # el modelo la estructura: requisitos, tareas, palabras clave…

Muchas webs de empleo incrustan la oferta en un bloque JSON-LD con el vocabulario de schema.org (`JobPosting`): es lo
que leen Google y los portales para indexarla. Si está, no hace falta adivinar dónde está cada cosa en el HTML.
"""

import json
import re
import urllib.parse
from typing import Literal

from pydantic import BaseModel, Field

from . import piezas, web

MIN_CARACTERES = 300
OFERTA_DE_EJEMPLO = "https://carreras.kpmg.es/job/Madrid-Consultora-Data-Analytics-&-IA-28046/1441848633/"
CONSEJO_PEGAR = ("Abre la oferta en tu navegador, selecciona y copia su texto (puesto, empresa, funciones y requisitos) y "
                 "pégalo en el cuadro «o pega el texto de la oferta».")


def elegir(url: str = "") -> str:
    """Tu oferta… o la de ejemplo (KPMG) si no has pegado ninguna o si sigues el lab con respuestas grabadas."""
    from mucdia import replay

    if replay.debe_reproducir():
        print("🎞️  Respuestas grabadas: uso la oferta de ejemplo (KPMG, consultoría de datos e IA, júnior).")
        return OFERTA_DE_EJEMPLO
    if not (url or "").strip():
        print("ℹ️  No has pegado tu oferta: uso la de ejemplo (KPMG). Pega la tuya en MI_OFERTA cuando quieras.")
        return OFERTA_DE_EJEMPLO
    return url.strip()


# ------------------------------------------------------------------------------------------------ JSON-LD (schema.org)
def extraer_jobposting(html: str) -> dict | None:
    """Busca en el HTML los bloques <script type="application/ld+json"> y devuelve el primer objeto de tipo
    JobPosting (un diccionario), o None si no hay. Los bloques pueden ser un objeto, una lista o un @graph."""
    from bs4 import BeautifulSoup

    sopa = BeautifulSoup(html or "", "html.parser")
    for script in sopa.find_all("script", type="application/ld+json"):
        try:
            datos = json.loads(script.string or script.get_text() or "", strict=False)
        except json.JSONDecodeError:
            continue
        pendientes = [datos]
        while pendientes:
            d = pendientes.pop(0)
            if isinstance(d, list):
                pendientes.extend(d)
            elif isinstance(d, dict):
                tipo = d.get("@type")
                if tipo == "JobPosting" or (isinstance(tipo, list) and "JobPosting" in tipo):
                    return d
                if "@graph" in d:
                    pendientes.append(d["@graph"])
    return None


def _texto(valor) -> str:
    """Un campo de schema.org puede ser texto, HTML, una lista o un objeto con «name»/«description»."""
    if valor is None:
        return ""
    if isinstance(valor, list):
        return "; ".join(t for t in (_texto(v) for v in valor) if t)
    if isinstance(valor, dict):
        return _texto(valor.get("name") or valor.get("description") or valor.get("value") or "")
    texto = str(valor)
    return web.html_a_texto(texto, todo=True) if "<" in texto and ">" in texto else texto.strip()


def _lugar(jp: dict) -> str:
    lugares = jp.get("jobLocation") or []
    lugares = lugares if isinstance(lugares, list) else [lugares]
    textos = []
    for lugar in lugares:
        direccion = lugar.get("address", {}) if isinstance(lugar, dict) else {}
        if isinstance(direccion, dict):
            partes = [direccion.get(k) for k in ("addressLocality", "addressRegion", "addressCountry")]
            partes = [_texto(p) for p in partes if p]
            textos.append(", ".join(dict.fromkeys(partes)))
        elif direccion:
            textos.append(str(direccion))
    if jp.get("jobLocationType") == "TELECOMMUTE":
        textos.append("teletrabajo")
    return " · ".join(t for t in textos if t)


def _salario(jp: dict) -> str:
    s = jp.get("baseSalary")
    if not isinstance(s, dict):
        return _texto(s)
    valor = s.get("value", {})
    if isinstance(valor, dict):
        cifras = [valor.get("minValue"), valor.get("maxValue")] if valor.get("minValue") else [valor.get("value")]
        unidad = valor.get("unitText", "")
    else:
        cifras, unidad = [valor], ""
    cifras = " – ".join(str(c) for c in cifras if c not in (None, ""))
    return f"{cifras} {s.get('currency', '')} {unidad}".strip() if cifras else ""


def jobposting_a_texto(jp: dict) -> tuple[str, str, str]:
    """(título, empresa, texto) a partir de un JobPosting de schema.org."""
    titulo = _texto(jp.get("title"))
    empresa = _texto(jp.get("hiringOrganization"))
    campos = [("Empresa", empresa), ("Ubicación", _lugar(jp)), ("Tipo de empleo", _texto(jp.get("employmentType"))),
              ("Publicada", _texto(jp.get("datePosted"))), ("Válida hasta", _texto(jp.get("validThrough"))),
              ("Salario", _salario(jp))]
    lineas = [f"# {titulo}"] + [f"{k}: {v}" for k, v in campos if v]
    lineas += ["", _texto(jp.get("description"))]
    for campo, nombre in (("responsibilities", "Responsabilidades"), ("qualifications", "Requisitos"),
                          ("skills", "Competencias"), ("experienceRequirements", "Experiencia"),
                          ("educationRequirements", "Formación")):
        if valor := _texto(jp.get(campo)):
            lineas += ["", f"## {nombre}", valor]
    return titulo, empresa, "\n".join(lineas).strip()


# ------------------------------------------------------------------------------------------------ otras fuentes
def _microdatos(html: str) -> tuple[str, str, str] | None:
    """Ofertas marcadas con microdatos de schema.org (itemprop="title", itemprop="description"…)."""
    from bs4 import BeautifulSoup

    sopa = BeautifulSoup(html or "", "html.parser")
    descripcion = sopa.find(attrs={"itemprop": "description"})
    if descripcion is None:
        return None
    titulo = sopa.find(attrs={"itemprop": "title"})
    empresa = sopa.find(attrs={"itemprop": "hiringOrganization"})
    lugar = sopa.find(attrs={"itemprop": "jobLocation"})
    titulo = titulo.get_text(" ", strip=True) if titulo else web.titulo_de(html)
    empresa = empresa.get_text(" ", strip=True) if empresa else ""
    lugar = lugar.get_text(" ", strip=True) if lugar else ""
    lineas = [f"# {titulo}"] + ([f"Empresa: {empresa}"] if empresa else []) + ([f"Ubicación: {lugar}"] if lugar else [])
    lineas += ["", web.html_a_texto(str(descripcion), todo=True)]
    return titulo, empresa, "\n".join(lineas)


_WORKDAY = re.compile(r"^(?P<inquilino>[\w-]+)\.wd\d+\.myworkdayjobs\.com$", re.I)


def _workday(url: str) -> tuple[str, str, str] | None:
    """Las webs de empleo de Workday (BBVA, AstraZeneca…) se pintan con JavaScript: el HTML viene casi vacío. Pero la
    propia web carga la oferta de un JSON público (/wday/cxs/…), que robots.txt permite leer. Usamos ese JSON."""
    partes = urllib.parse.urlsplit(url)
    m = _WORKDAY.match(partes.netloc)
    trozos = [t for t in partes.path.split("/") if t]
    if not m or "job" not in trozos:
        return None
    if re.fullmatch(r"[a-z]{2}-[A-Z]{2}", trozos[0]):  # /es-ES/…
        trozos = trozos[1:]
    api = f"{partes.scheme}://{partes.netloc}/wday/cxs/{m['inquilino']}/{trozos[0]}/{'/'.join(trozos[1:])}"
    datos = json.loads(web.obtener(api, aceptar="application/json").texto)
    info = datos.get("jobPostingInfo") or {}
    if not info.get("jobDescription"):
        return None
    empresa = (datos.get("hiringOrganization") or {}).get("name", "")
    campos = [("Empresa", empresa), ("Ubicación", info.get("location")), ("Modalidad", info.get("remoteType")),
              ("Jornada", info.get("timeType")), ("Publicada", info.get("startDate")), ("Fin del plazo", info.get("endDate"))]
    lineas = [f"# {info.get('title', '')}"] + [f"{k}: {v}" for k, v in campos if v]
    lineas += ["", web.html_a_texto(info["jobDescription"], todo=True)]
    return info.get("title", ""), empresa, "\n".join(lineas)


def _fallo(url: str, motivo: str, mensaje: str) -> dict:
    return {"ok": False, "url": url, "motivo": motivo, "mensaje": mensaje, "consejo": CONSEJO_PEGAR}


def _leer(url: str, extractor) -> dict:
    try:
        url = web.validar_url(url)
        ok, explicacion = web.permitido(url)
        if not ok:
            return _fallo(url, "robots", f"No leo esta página: {explicacion}. Respetamos esa decisión de la web.")
        if (wd := _workday(url)) is not None:
            titulo, empresa, texto = wd
            return {"ok": True, "url": url, "fuente": "Workday (JSON público de su web de empleo)", "titulo": titulo,
                    "empresa": empresa, "texto": texto, "robots": explicacion}
        respuesta = web.obtener(url)
    except web.ErrorWeb as e:
        return _fallo(url, e.motivo, str(e))
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return _fallo(url, "formato", f"La web ha respondido algo que no sé interpretar ({type(e).__name__}).")

    html = respuesta.texto
    if (jp := extractor(html)) is not None:
        titulo, empresa, texto = jobposting_a_texto(jp)
        fuente = "JSON-LD (schema.org JobPosting)"
    elif (md := _microdatos(html)) is not None:
        titulo, empresa, texto = md
        fuente = "microdatos (schema.org)"
    else:
        titulo, empresa, texto = web.titulo_de(html), "", web.html_a_texto(html)
        fuente = "texto de la página"
    if web.parece_un_muro(texto):
        return _fallo(respuesta.url, "muro", "La web me enseña un muro (captcha, «activa JavaScript» o acceso denegado) "
                                             "en vez de la oferta: no es para programas.")
    if len(texto) < MIN_CARACTERES:
        return _fallo(respuesta.url, "corto", f"Solo he encontrado {len(texto)} caracteres de texto: la página se genera "
                                              "con JavaScript o la oferta ya no está publicada.")
    # El título de la página y la web dicen a menudo quién contrata aunque el texto de la oferta no lo nombre.
    contexto = f"Página: {web.titulo_de(html)} · web: {urllib.parse.urlsplit(respuesta.url).netloc}"
    return {"ok": True, "url": respuesta.url, "fuente": fuente, "titulo": titulo, "empresa": empresa,
            "texto": f"{contexto}\n\n{texto}", "robots": explicacion}


@web.grabable("leer_oferta")
def _leer_grabable(url: str) -> dict:
    return _leer(url, piezas.cargar("oferta", "extraer_jobposting", extraer_jobposting))


def leer_oferta(url: str, extractor=None) -> dict:
    """Lee una oferta pública respetando robots.txt. Devuelve un diccionario:
    ok=True  → url, fuente, titulo, empresa, texto, robots
    ok=False → motivo («robots», «bloqueo», «muro», «corto», «no_existe»…), mensaje y consejo (pegar el texto).

    extractor: tu función extraer_jobposting (lab 2a). Si no la pasas, se usa la de sesion2/mis_piezas/oferta.py o,
    si no existe, la de referencia."""
    if extractor is None:
        return _leer_grabable(url)
    return _leer(url, extractor)


def desde_texto(texto: str, url: str = "") -> dict:
    """La oferta pegada a mano (cuando la web no deja que un programa la lea)."""
    texto = (texto or "").strip()
    if len(texto) < MIN_CARACTERES:
        return _fallo(url, "corto", f"El texto pegado es muy corto ({len(texto)} caracteres): copia la oferta completa.")
    return {"ok": True, "url": url, "fuente": "texto pegado por ti", "titulo": texto.splitlines()[0][:120], "empresa": "",
            "texto": texto[:15000], "robots": "no aplica"}


# ------------------------------------------------------------------------------------------------ el modelo la estructura
class Requisito(BaseModel):
    texto: str = Field(description="El requisito, resumido en una línea y fiel a la oferta")
    tipo: Literal["imprescindible", "deseable"] = Field(
        description="imprescindible si la oferta lo exige (requisitos, «se requiere», «must have»); deseable si solo lo "
                    "valora («se valorará», «plus», «nice to have»)")
    categoria: Literal["técnica", "negocio", "idioma", "formación", "experiencia", "personal"] = Field(
        description="técnica: herramientas y métodos; negocio: conocimiento del sector o de la función; idioma; "
                    "formación: títulos; experiencia: años o puestos previos; personal: competencias transversales")


class Oferta(BaseModel):
    empresa: str = Field(description="Nombre comercial de la empresa que contrata (no el del portal de empleo)")
    puesto: str = Field(description="Nombre del puesto tal como lo anuncia la oferta")
    ubicacion: str = Field(description="Ciudad o ciudades; «no consta» si no lo dice")
    modalidad: Literal["presencial", "híbrido", "remoto", "no consta"] = Field(description="Modalidad de trabajo")
    nivel: Literal["prácticas", "júnior", "intermedio", "sénior", "no consta"] = Field(
        description="Nivel según la experiencia que pide: prácticas o beca; júnior (0-2 años); intermedio (3-5); sénior (más)")
    salario: str = Field(description="Banda salarial solo si la oferta la indica; si no, «no consta». Nunca la estimes")
    resumen: str = Field(description="Qué hará la persona y para qué, en dos frases")
    tareas: list[str] = Field(description="Las funciones principales del puesto, una por línea")
    requisitos: list[Requisito] = Field(description="Todos los requisitos de la oferta, imprescindibles y deseables")
    palabras_clave: list[str] = Field(
        description="Herramientas, técnicas, títulos e idiomas que un filtro automático (ATS) buscaría en el CV, escritos "
                    "como en la oferta (p. ej. «Python», «SQL», «Power BI», «inglés C1», «análisis de datos»); entre 8 y "
                    "20. Ni el nombre de la empresa, ni el de equipos internos, ni palabras sueltas genéricas («Data», «IA»)")


INSTRUCCIONES_ANALISTA = """Eres analista de ofertas de empleo. Estructuras la oferta que te pasan, sin inventar nada:
- Si un dato no aparece en la oferta, escribe «no consta». Nunca estimes el salario ni la experiencia.
- Distingue lo que la oferta EXIGE (imprescindible) de lo que solo VALORA (deseable).
- Responde en español aunque la oferta esté en inglés, pero conserva los nombres de las herramientas.
- La empresa es la que contrata, no el portal de empleo ni la consultora de selección (salvo que contrate ella)."""


async def analizar_oferta(cliente, pagina: dict, esquema=Oferta, instrucciones: str = INSTRUCCIONES_ANALISTA,
                          middleware=None):
    """Convierte el texto de la oferta en un objeto `esquema` (Pydantic) con el modelo."""
    from agent_framework import Agent

    analista = Agent(client=cliente, name="analista_oferta", instructions=instrucciones, middleware=middleware or [])
    entrada = f"Oferta ({pagina.get('fuente', '')}{' · ' + pagina['url'] if pagina.get('url') else ''}):\n\n{pagina['texto']}"
    respuesta = await analista.run(entrada, options={"response_format": esquema})
    return respuesta.value


# ------------------------------------------------------------------------------------------------ de un lab al siguiente
def _trabajo():
    from .carrera import TRABAJO

    TRABAJO.mkdir(parents=True, exist_ok=True)
    return TRABAJO


def guardar_oferta(oferta, pagina: dict) -> None:
    """Guarda la oferta estructurada y la página leída en sesion2/trabajo/ (los labs 2b y 2c las recuperan)."""
    (_trabajo() / "oferta.json").write_text(oferta.model_dump_json(indent=2), encoding="utf-8")
    (_trabajo() / "pagina.json").write_text(json.dumps(pagina, ensure_ascii=False, indent=2), encoding="utf-8")


def cargar_oferta() -> Oferta:
    ruta = _trabajo() / "oferta.json"
    if not ruta.exists():
        raise FileNotFoundError("Aún no hay oferta: ejecuta antes el lab 2a (lab2a_leer_la_oferta.ipynb).")
    return Oferta.model_validate_json(ruta.read_text(encoding="utf-8"))


def cargar_pagina() -> dict:
    ruta = _trabajo() / "pagina.json"
    if not ruta.exists():
        raise FileNotFoundError("Aún no hay oferta: ejecuta antes el lab 2a (lab2a_leer_la_oferta.ipynb).")
    return json.loads(ruta.read_text(encoding="utf-8"))
