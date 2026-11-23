"""Leer la web con educación: robots.txt, una sola petición, identificándonos y con límites.

    permitido(url)            → (True/False, motivo): ¿nos deja robots.txt leer esa página?
    obtener(url)              → Respuesta(estado, url, texto, tipo); lanza ErrorWeb si no se puede
    html_a_texto(html)        → el texto legible de una página (sin menús, scripts ni pies)
    @grabable("nombre")       → graba la salida de una herramienta web para reproducirla sin red (modo replay)

Dos reglas del curso:
- **Páginas web**: solo si robots.txt lo permite a nuestro agente. Si lo prohíbe (LinkedIn, por ejemplo), no se lee:
  se pide a la persona que pegue el texto.
- **APIs públicas documentadas** (Wikipedia, Wikidata): las rigen sus condiciones de uso, no robots.txt (que es para
  rastreadores). Las cumplimos: nos identificamos con un User-Agent con contacto y hacemos pocas peticiones.
"""

import functools
import re
import time
import urllib.parse
import urllib.robotparser
from dataclasses import dataclass

import httpx

NOMBRE_AGENTE = "CUNEF-agente-candidaturas"
USER_AGENT = f"Mozilla/5.0 (compatible; {NOMBRE_AGENTE}/1.0; +https://github.com/gerardsl/cunef-ia-agentica)"
CABECERAS = {"User-Agent": USER_AGENT, "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"}
SEGUNDOS = 20
MAX_BYTES = 3_000_000

# Señales de que no hemos recibido la página, sino un muro (captcha, «activa JavaScript», acceso denegado…)
SENALES_DE_MURO = (
    "captcha", "no podemos identificar tu navegador", "enable javascript", "activa javascript", "habilita javascript",
    "cookies and javascript", "pardon our interruption", "access denied", "acceso denegado", "just a moment",
    "attention required", "verify you are human", "are you a robot", "unusual traffic", "request blocked",
    "inicia sesión para ver", "sign in to view", "authwall",
)
ESTADOS_DE_BLOQUEO = {401: "pide iniciar sesión", 403: "nos deniega el acceso", 429: "nos limita por exceso de peticiones",
                      451: "no está disponible por motivos legales", 503: "no está disponible o filtra a los programas"}


class ErrorWeb(Exception):
    """No se ha podido leer la página. `motivo` es corto («robots», «bloqueo», «red»…) y el mensaje, para personas."""

    def __init__(self, mensaje: str, motivo: str = "red"):
        super().__init__(mensaje)
        self.motivo = motivo


@dataclass
class Respuesta:
    estado: int
    url: str
    texto: str
    tipo: str


_ROBOTS: dict[str, tuple[urllib.robotparser.RobotFileParser | None, str]] = {}


def _robots(url: str) -> tuple[urllib.robotparser.RobotFileParser | None, str]:
    partes = urllib.parse.urlsplit(url)
    base = f"{partes.scheme}://{partes.netloc}"
    if base not in _ROBOTS:
        try:
            r = httpx.get(base + "/robots.txt", headers=CABECERAS, timeout=SEGUNDOS, follow_redirects=True)
        except httpx.HTTPError as e:
            # RFC 9309: si robots.txt no responde (error de red o 5xx), hay que asumir que todo está prohibido.
            _ROBOTS[base] = (None, f"no he podido leer {base}/robots.txt ({type(e).__name__}): por prudencia, no entro")
            return _ROBOTS[base]
        if r.status_code >= 500:
            _ROBOTS[base] = (None, f"{base}/robots.txt da error {r.status_code}: por prudencia, no entro")
        elif r.status_code >= 400:  # RFC 9309: si no existe (4xx), se puede acceder
            rp = urllib.robotparser.RobotFileParser()
            rp.allow_all = True
            _ROBOTS[base] = (rp, f"{base} no publica robots.txt")
        else:
            rp = urllib.robotparser.RobotFileParser()
            rp.parse(r.text.splitlines())
            _ROBOTS[base] = (rp, f"{base}/robots.txt")
    return _ROBOTS[base]


def permitido(url: str) -> tuple[bool, str]:
    """¿Permite robots.txt que nuestro agente lea `url`? Devuelve (sí o no, explicación)."""
    rp, origen = _robots(url)
    if rp is None:
        return False, origen
    if rp.can_fetch(NOMBRE_AGENTE, url):
        return True, f"permitido por {origen}"
    return False, f"prohibido por {origen} para programas como este agente"


def validar_url(url: str) -> str:
    url = (url or "").strip()
    partes = urllib.parse.urlsplit(url)
    if partes.scheme not in ("http", "https") or not partes.netloc:
        raise ErrorWeb(f"«{url[:80]}» no es una dirección web (debe empezar por http:// o https://).", "url")
    return url


def obtener(url: str, *, api: bool = False, aceptar: str = "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.5",
            parametros: dict | None = None) -> Respuesta:
    """UNA petición GET, identificada y con límite de tiempo y tamaño.

    api=False (páginas): antes, comprueba robots.txt; si prohíbe, lanza ErrorWeb(motivo="robots").
    api=True (APIs públicas documentadas, como Wikipedia): se rigen por sus condiciones de uso."""
    url = validar_url(url)
    if not api:
        ok, motivo = permitido(url)
        if not ok:
            raise ErrorWeb(f"No leo {urllib.parse.urlsplit(url).netloc}: {motivo}.", "robots")
    try:
        with httpx.stream("GET", url, params=parametros, headers={**CABECERAS, "Accept": aceptar}, timeout=SEGUNDOS,
                          follow_redirects=True) as r:
            datos = b""
            for trozo in r.iter_bytes():
                datos += trozo
                if len(datos) > MAX_BYTES:
                    break
            texto = datos.decode(r.encoding or "utf-8", errors="replace")
            respuesta = Respuesta(r.status_code, str(r.url), texto, r.headers.get("content-type", ""))
    except httpx.HTTPError as e:
        raise ErrorWeb(f"No he podido conectar con {urllib.parse.urlsplit(url).netloc} ({type(e).__name__}).", "red") from e
    if respuesta.estado in ESTADOS_DE_BLOQUEO:
        raise ErrorWeb(f"{urllib.parse.urlsplit(url).netloc} {ESTADOS_DE_BLOQUEO[respuesta.estado]} "
                       f"(HTTP {respuesta.estado}).", "bloqueo")
    if respuesta.estado == 404:
        raise ErrorWeb("La página no existe (HTTP 404): ¿ha caducado la oferta o falta un trozo del enlace?", "no_existe")
    if respuesta.estado >= 400:
        raise ErrorWeb(f"La web responde con un error (HTTP {respuesta.estado}).", "error")
    return respuesta


def parece_un_muro(texto: str) -> bool:
    """Texto corto con señales de captcha, «activa JavaScript», acceso denegado…: no es la página que queríamos."""
    t = texto.lower()
    return len(t) < 2500 and any(s in t for s in SENALES_DE_MURO)


# ------------------------------------------------------------------------------------------------ HTML → texto
_FUERA = ["script", "style", "noscript", "svg", "iframe", "button", "select", "template"]
_MARCO = ["nav", "header", "footer"]       # menús y pies de la web (fuera de <main> o <article>)
_BLOQUES = ["p", "div", "section", "article", "main", "ul", "ol", "table", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
            "br", "li", "dd", "dt", "blockquote"]
_PISTAS_CONTENIDO = re.compile(r"job|descrip|description|oferta|vacan|posting|content|detalle|detail", re.I)


def _contenedor_principal(sopa):
    """El trozo de la página con el contenido: <main>, <article> o el bloque con más texto cuyo id/clase lo sugiere."""
    for selector in ("main", "article", "[role=main]"):
        nodo = sopa.select_one(selector)
        if nodo and len(nodo.get_text(" ", strip=True)) > 400:
            return nodo
    candidatos = [n for n in sopa.find_all(["div", "section"])
                  if _PISTAS_CONTENIDO.search(" ".join([n.get("id") or "", *(n.get("class") or [])]))]
    candidatos = [n for n in candidatos if len(n.get_text(" ", strip=True)) > 400]
    if candidatos:
        return max(candidatos, key=lambda n: len(n.get_text(" ", strip=True)))
    return sopa.body or sopa


def html_a_texto(html: str, max_caracteres: int = 15000, todo: bool = False) -> str:
    """Texto legible de un HTML: quita scripts, menús y pies; respeta párrafos, títulos y viñetas."""
    from bs4 import BeautifulSoup

    sopa = BeautifulSoup(html or "", "html.parser")
    for etiqueta in sopa.find_all(_FUERA):
        etiqueta.decompose()
    for etiqueta in sopa.find_all(_MARCO):
        if not etiqueta.decomposed and not etiqueta.find_parent(["main", "article"]):
            etiqueta.decompose()
    nodo = sopa if todo else _contenedor_principal(sopa)
    for li in nodo.find_all("li"):
        li.insert_before("\n- ")
    for h in nodo.find_all(["h1", "h2", "h3", "h4"]):
        h.insert_before("\n\n## " if h.name in ("h1", "h2") else "\n\n### ")
        h.insert_after("\n")
    for b in nodo.find_all(_BLOQUES):
        b.insert_after("\n")
    texto = nodo.get_text("")
    texto = re.sub(r"[ \t\u00a0]+", " ", texto)
    texto = re.sub(r" *\n *", "\n", texto)
    texto = re.sub(r"\n- *\n", "\n- ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto).strip()
    if len(texto) > max_caracteres:
        texto = texto[:max_caracteres] + "\n… (texto recortado)"
    return texto


def titulo_de(html: str) -> str:
    import html as html_lib

    m = re.search(r"<title[^>]*>(.*?)</title>", html or "", re.S | re.I)
    return html_lib.unescape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else ""


# ------------------------------------------------------------------------------------------------ grabar y reproducir
def grabable(nombre: str):
    """Graba la salida de una herramienta que lee la web y la reproduce en modo replay.

    Así, quien se queda sin cuota sigue el lab con las respuestas grabadas: la conversación con el modelo incluye lo que
    devolvieron las herramientas, y debe ser idéntica para que la grabación coincida (la web cambia cada día)."""

    def decorador(funcion):
        @functools.wraps(funcion)
        def envoltorio(*args, **kwargs):
            from mucdia import config, replay  # aquí y no arriba: el servidor MCP importa este paquete y debe ser ligero

            clave = replay._hash({"web": nombre, "args": [str(a) for a in args],
                                  "kwargs": {k: str(v) for k, v in sorted(kwargs.items())}})
            if replay.debe_reproducir(clave) and (grabacion := replay.cargar(clave)) is not None:
                return grabacion[0]["salida"]
            t0 = time.perf_counter()
            salida = funcion(*args, **kwargs)
            if config.graba():
                replay.guardar(clave, "web", {"salida": salida}, ms=(time.perf_counter() - t0) * 1000)
            return salida

        return envoltorio

    return decorador
