"""Paso 3 · Investigar la empresa con fuentes que se pueden citar (y sin claves de pago).

    ficha_empresa("KPMG")      → resumen de Wikipedia y datos de Wikidata (sector, sede, plantilla…), con enlaces
    noticias("KPMG")           → titulares recientes (Bing Noticias, RSS), con fecha, medio y enlace
    leer_web("https://…")      → el texto de una página (si su robots.txt lo permite) y sus enlaces principales

¿Por qué no «buscar en Google» desde el modelo? La búsqueda integrada de Gemini no entra en el plan gratuito (responde
429) y Google Noticias prohíbe en su robots.txt que la lean programas. Estas tres fuentes son gratuitas y lo permiten.
"""

import html
import re
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Annotated

from . import web

WIKIPEDIA = "https://{idioma}.wikipedia.org"
PROPIEDADES = {  # Wikidata: propiedad → etiqueta
    "P452": "sector", "P159": "sede", "P17": "país", "P571": "fundación", "P1128": "plantilla",
    "P2139": "ingresos", "P169": "consejero delegado", "P749": "matriz", "P414": "cotiza en", "P856": "web oficial",
}


def _json(url: str, **parametros) -> dict:
    import json

    return json.loads(web.obtener(url, api=True, aceptar="application/json", parametros=parametros or None).texto)


def _wikipedia(nombre: str, idioma: str) -> dict | None:
    base = WIKIPEDIA.format(idioma=idioma)
    paginas = _json(f"{base}/w/rest.php/v1/search/page", q=nombre, limit=1).get("pages", [])
    if not paginas:
        return None
    resumen = _json(f"{base}/api/rest_v1/page/summary/{urllib.parse.quote(paginas[0]['key'])}")
    if resumen.get("type") == "disambiguation":
        return None
    return resumen


def _valor(dato: dict, etiquetas: dict) -> str:
    valor = dato.get("mainsnak", {}).get("datavalue", {}).get("value")
    if isinstance(valor, dict) and "id" in valor:
        return etiquetas.get(valor["id"], valor["id"])
    if isinstance(valor, dict) and "time" in valor:
        return valor["time"].lstrip("+")[:4]
    if isinstance(valor, dict) and "amount" in valor:
        unidad = valor.get("unit", "").rsplit("/", 1)[-1]
        cantidad = f"{float(valor['amount']):,.0f}".replace(",", ".")
        return f"{cantidad} {etiquetas.get(unidad, '') if unidad.startswith('Q') else ''}".strip()
    return str(valor) if valor is not None else ""


def _fecha_del_dato(dato: dict) -> str:
    calificadores = dato.get("qualifiers", {}).get("P585", [])
    return calificadores[0]["datavalue"]["value"]["time"].lstrip("+")[:10] if calificadores else ""


def _wikidata(qid: str) -> list[str]:
    entidad = _json(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json")["entities"][qid]
    datos = {p: entidad.get("claims", {}).get(p, []) for p in PROPIEDADES}
    ids = set()
    for lista in datos.values():
        for d in lista:
            v = d.get("mainsnak", {}).get("datavalue", {}).get("value")
            if isinstance(v, dict) and "id" in v:
                ids.add(v["id"])
            if isinstance(v, dict) and "unit" in v and v["unit"].rsplit("/", 1)[-1].startswith("Q"):
                ids.add(v["unit"].rsplit("/", 1)[-1])
    etiquetas = {}
    if ids:
        respuesta = _json("https://www.wikidata.org/w/api.php", action="wbgetentities", ids="|".join(sorted(ids)[:50]),
                          props="labels", languages="es|en", format="json")
        for i, e in respuesta.get("entities", {}).items():
            etiquetas[i] = (e.get("labels", {}).get("es") or e.get("labels", {}).get("en") or {}).get("value", i)
    lineas = []
    for p, nombre in PROPIEDADES.items():
        lista = [d for d in datos[p] if d.get("rank") != "deprecated"]
        if not lista:
            continue
        if p in ("P1128", "P2139"):  # plantilla e ingresos: el dato más reciente, con su fecha
            d = max(lista, key=_fecha_del_dato)
            fecha = _fecha_del_dato(d)
            lineas.append(f"- {nombre}: {_valor(d, etiquetas)}{f' (dato de {fecha[:4]})' if fecha else ''}")
        else:
            valores = list(dict.fromkeys(v for v in (_valor(d, etiquetas) for d in lista[:4]) if v))
            lineas.append(f"- {nombre}: {', '.join(valores)}")
    return lineas


@web.grabable("ficha_empresa")
def ficha_empresa(nombre: Annotated[str, "Nombre comercial de la empresa, p. ej. «BBVA» o «Inditex»"]) -> str:
    """Ficha de una empresa con fuentes: resumen de Wikipedia y datos de Wikidata (sector, sede, fundación, plantilla,
    ingresos, consejero delegado, web oficial). Úsala primero para entender qué hace la empresa y dónde está su web."""
    try:
        resumen = _wikipedia(nombre, "es") or _wikipedia(nombre, "en")
        if resumen is None:
            return f"No encuentro «{nombre}» en Wikipedia. Prueba con otro nombre (el comercial o el de la matriz)."
        lineas = [f"# {resumen.get('title', nombre)}", resumen.get("extract", ""),
                  f"Fuente: {resumen.get('content_urls', {}).get('desktop', {}).get('page', '')}"]
        if qid := resumen.get("wikibase_item"):
            if datos := _wikidata(qid):
                lineas += ["", "Datos (Wikidata):", *datos, f"Fuente: https://www.wikidata.org/wiki/{qid}"]
        return "\n".join(lineas)
    except web.ErrorWeb as e:
        return f"ERROR al consultar Wikipedia: {e}"


def _enlace_real(enlace: str) -> str:
    """Bing envuelve cada enlace en un redireccionamiento: sacamos la URL del medio."""
    consulta = urllib.parse.parse_qs(urllib.parse.urlsplit(enlace).query)
    return consulta.get("url", [enlace])[0]


@web.grabable("noticias")
def noticias(empresa: Annotated[str, "Empresa (y, si ayuda, un tema: «BBVA inteligencia artificial»)"],
             maximo: Annotated[int, "Número máximo de titulares (hasta 10)"] = 8) -> str:
    """Titulares recientes sobre una empresa en Bing Noticias (España), del más nuevo al más antiguo, con fecha, medio y
    enlace. Solo son titulares: para contar algo más, lee la noticia con leer_web."""
    try:
        r = web.obtener("https://www.bing.com/news/search", aceptar="application/rss+xml,application/xml",
                        parametros={"q": empresa, "format": "rss", "setlang": "es", "cc": "ES"})
        raiz = ET.fromstring(r.texto.encode("utf-8"))
    except web.ErrorWeb as e:
        return f"ERROR al buscar noticias: {e}"
    except ET.ParseError:
        return "ERROR: Bing Noticias no ha devuelto un RSS válido."
    hace_un_anio = datetime.now(timezone.utc) - timedelta(days=365)
    items = []
    for item in raiz.iter("item"):
        campos = {hijo.tag.rsplit("}", 1)[-1]: (hijo.text or "").strip() for hijo in item}
        try:
            fecha = parsedate_to_datetime(campos.get("pubDate", ""))
        except (TypeError, ValueError):
            continue
        if fecha >= hace_un_anio:
            items.append((fecha, html.unescape(campos.get("title", "")), campos.get("Source", ""),
                          _enlace_real(campos.get("link", ""))))
    if not items:
        return f"No hay titulares del último año sobre «{empresa}» en Bing Noticias."
    items.sort(key=lambda x: x[0], reverse=True)
    lineas = [f"Titulares sobre «{empresa}» (Bing Noticias, último año):"]
    for fecha, titulo, medio, enlace in items[:max(1, min(maximo, 10))]:
        lineas.append(f"- {fecha:%d-%m-%Y} · {medio} · {titulo} · {enlace}")
    return "\n".join(lineas)


@web.grabable("leer_web")
def leer_web(url: Annotated[str, "Dirección completa de la página, empezando por https://"]) -> str:
    """Lee una página web (la web oficial de la empresa, su sala de prensa o una noticia) si su robots.txt lo permite.
    Devuelve su título, su texto (recortado) y sus enlaces principales para seguir navegando."""
    try:
        r = web.obtener(url)
    except web.ErrorWeb as e:
        return f"ERROR: {e}"
    if "html" not in r.tipo and "xml" not in r.tipo:
        return f"ERROR: {url} no es una página web (es {r.tipo or 'otro formato'})."
    texto = web.html_a_texto(r.texto, max_caracteres=6000)
    if web.parece_un_muro(texto):
        return f"ERROR: {url} muestra un muro (captcha o acceso denegado) en vez de su contenido."
    from bs4 import BeautifulSoup

    base = urllib.parse.urlsplit(r.url)
    enlaces = []
    for a in BeautifulSoup(r.texto, "html.parser").find_all("a", href=True):
        destino = urllib.parse.urljoin(r.url, a["href"]).split("#")[0]
        etiqueta = re.sub(r"\s+", " ", a.get_text(" ", strip=True))[:60]
        if urllib.parse.urlsplit(destino).netloc == base.netloc and etiqueta and destino != r.url:
            enlaces.append(f"- {etiqueta}: {destino}")
    enlaces = list(dict.fromkeys(enlaces))[:15]
    return "\n".join([f"# {web.titulo_de(r.texto)}", f"Fuente: {r.url}", "", texto,
                      *(["", "Enlaces de la misma web:", *enlaces] if enlaces else [])])


HERRAMIENTAS = [ficha_empresa, noticias, leer_web]
