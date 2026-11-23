"""Paso 2 · Tu carrera como datos: el CV, el grado, el máster… y un guardarraíl para no inventar nada.

    perfil()                          → tu CV, tu grado y tu máster (o los del EJEMPLO ficticio si aún no has puesto los tuyos)
    plan_texto()                      → el plan oficial del MUCD-IA, con el estado de cada asignatura a día de hoy
    buscar_competencias("Power BI")   → dónde aprendiste algo: grado, máster o masterclasses
    afirmaciones_sin_respaldo(cv)     → cifras y herramientas del CV nuevo que no constan en ninguna fuente
    guardar_version(empresa, puesto, cv_markdown) → sesion2/trabajo/cv/<empresa>-<puesto>.md y .docx
    cobertura(palabras_clave, texto)  → qué palabras clave de la oferta aparecen en un CV (lo que mira un ATS)

No importa `mucdia` a propósito: lo usa también el servidor MCP, que arranca en su propio proceso y debe ser ligero.
"""

import json
import os
import re
import unicodedata
from datetime import date
from pathlib import Path

from . import piezas

S2 = Path(__file__).resolve().parent.parent
EJEMPLO = S2 / "ejemplo"
PERFIL = S2 / "mi_perfil"
TRABAJO = S2 / "trabajo"
PLAN = S2 / "datos" / "plan_mucdia.json"
FECHA_DE_CLASE = date(2026, 11, 25)


# ------------------------------------------------------------------------------------------------ el perfil
def origen() -> str:
    """«tuyo» si existe sesion2/mi_perfil/cv.md; si no (o si CANDIDATURA_PERFIL=ejemplo, o en modo replay), «ejemplo».
    Nunca se mezclan: con tu CV se usan solo tu grado y tu máster, aunque estén vacíos."""
    if os.getenv("CANDIDATURA_PERFIL", "").lower() == "ejemplo" or os.getenv("MODO_LLM", "").lower() == "replay":
        return "ejemplo"
    return "tuyo" if (PERFIL / "cv.md").exists() else "ejemplo"


def _leer(ruta: Path) -> str:
    return ruta.read_text(encoding="utf-8").strip() if ruta.exists() else ""


def perfil() -> dict:
    carpeta = PERFIL if origen() == "tuyo" else EJEMPLO
    return {"origen": origen(), "cv": _leer(carpeta / "cv.md"), "grado": _leer(carpeta / "grado.md"),
            "master": _leer(carpeta / "master.md"), "carpeta": carpeta}


def fecha_referencia() -> date:
    """Hoy… salvo al grabar o reproducir respuestas (o con CANDIDATURA_FECHA): entonces, el día de la clase, para que
    las respuestas grabadas coincidan."""
    if fijada := os.getenv("CANDIDATURA_FECHA"):
        return date.fromisoformat(fijada)
    if os.getenv("MODO_LLM", "").lower() in ("replay", "record", "completar"):
        return FECHA_DE_CLASE
    return date.today()


# ------------------------------------------------------------------------------------------------ el plan de estudios
def plan() -> dict:
    return json.loads(PLAN.read_text(encoding="utf-8"))


def estado_asignatura(cuatrimestre: int, hoy: date | None = None) -> str:
    hoy = hoy or fecha_referencia()
    tramo = plan()["calendario"][str(cuatrimestre)]
    if hoy < date.fromisoformat(tramo["inicio"]):
        return "pendiente"
    return "en curso" if hoy <= date.fromisoformat(tramo["fin"]) else "cursada"


def estado_sesion(fecha: str, hoy: date | None = None) -> str:
    return "hecha" if (hoy or fecha_referencia()) >= date.fromisoformat(fecha) else "pendiente"


def plan_texto() -> str:
    p, hoy = plan(), fecha_referencia()
    lineas = [f"{p['titulo']} · {p['universidad']} · curso {p['curso']} · estado a {hoy:%d-%m-%Y}",
              f"Fuentes: {'; '.join(p['fuentes'])}.", f"Aviso: {p['aviso']}", ""]
    for a in p["asignaturas"]:
        lineas.append(f"- {a['nombre']} ({a['ects']} ECTS, {a['cuatrimestre']}.º cuatrimestre, {a['caracter']}): "
                      f"{estado_asignatura(a['cuatrimestre'], hoy).upper()}")
        if a["contenidos"]:
            lineas.append(f"  contenidos: {'; '.join(a['contenidos'])}")
        if a["herramientas"]:
            lineas.append(f"  herramientas habituales (orientativo, solo valen si constan en tu CV o en tu máster): "
                          f"{', '.join(a['herramientas'])}")
    m = p["masterclasses"]
    lineas += ["", m["nombre"] + ":"]
    for s in m["sesiones"]:
        lineas.append(f"- {s['fecha']} · {s['nombre']}: {estado_sesion(s['fecha'], hoy).upper()} · "
                      f"{'; '.join(s['contenidos'])}" + (f" · herramientas: {', '.join(s['herramientas'])}"
                                                          if s["herramientas"] else ""))
    lineas += ["", "Regla: lo EN CURSO se presenta como formación en curso (no como dominio); lo PENDIENTE no se pone en "
                   "el CV."]
    return "\n".join(lineas)


# ------------------------------------------------------------------------------------------------ buscar competencias
_VACIAS = set("de la el en y a los las del un una con por para que o al se su sus lo como mas es sobre entre the and of "
              "to in for with on an".split())
SINONIMOS = {
    "machine learning": "aprendizaje automatico", "deep learning": "aprendizaje profundo redes neuronales",
    "dashboard": "cuadro mando visualizacion power bi", "cuadro de mando": "dashboard visualizacion power bi",
    "visualization": "visualizacion", "storytelling": "comunicar visualizacion", "nlp": "lenguaje natural",
    "natural language": "lenguaje natural", "llm": "modelos lenguaje", "genai": "ia generativa",
    "generative": "generativa", "etl": "extraccion transformacion carga", "pipeline": "flujo datos etl",
    "forecasting": "prevision series temporales", "prevision": "series temporales", "time series": "series temporales",
    "statistics": "estadistica", "statistical": "estadistica", "database": "bases datos sql",
    "data quality": "calidad datos", "ethics": "etica", "gdpr": "rgpd privacidad", "privacy": "privacidad",
    "ai act": "reglamento europeo inteligencia artificial", "agents": "agentes", "agentic": "agentes",
    "regression": "regresion", "classification": "clasificacion", "experimentation": "experimentos",
    "a/b": "experimentos contrastes", "english": "ingles", "communication": "comunicar", "finance": "finanzas",
    "risk": "riesgo", "marketing": "marketing", "customer": "clientes", "ml": "aprendizaje automatico",
}


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def _tokens(texto: str) -> set[str]:
    palabras = re.findall(r"[a-z0-9+#/]+", normalizar(texto))
    return {p.rstrip("s") if len(p) > 4 else p for p in palabras if p not in _VACIAS and len(p) > 1}


def _elementos() -> list[tuple[str, str, str]]:
    """(etiqueta, texto para buscar, texto para mostrar) de todo lo que sabes: plan del máster, tu grado, tu máster y
    las masterclasses."""
    p, hoy, yo = plan(), fecha_referencia(), perfil()
    elementos = []
    for a in p["asignaturas"]:
        texto = " ".join([a["nombre"], *a["contenidos"], *a["competencias"], *a["herramientas"]])
        mostrar = (f"contenidos: {'; '.join(a['contenidos'])}"
                   + (f" · competencias: {'; '.join(a['competencias'])}" if a["competencias"] else "")
                   + (f" · herramientas habituales (orientativo): {', '.join(a['herramientas'])}"
                      if a["herramientas"] else ""))
        elementos.append((f"máster (plan oficial) · {a['nombre']} · {estado_asignatura(a['cuatrimestre'], hoy)}", texto,
                          mostrar))
    for s in p["masterclasses"]["sesiones"]:
        texto = " ".join([s["nombre"], *s["contenidos"], *s["competencias"], *s["herramientas"]])
        mostrar = f"contenidos: {'; '.join(s['contenidos'])}" + (
            f" · herramientas: {', '.join(s['herramientas'])}" if s["herramientas"] else "")
        elementos.append((f"masterclasses de IA agéntica · {s['nombre']} · {estado_sesion(s['fecha'], hoy)}", texto,
                          mostrar))
    for fuente, nombre in (("grado", "tu grado"), ("master", "tu máster (lo que has hecho)")):
        for linea in yo[fuente].splitlines():
            linea = linea.strip().lstrip("-*• ").strip()
            if linea and not linea.startswith(("#", ">")) and len(linea) > 3:
                elementos.append((nombre, linea, linea))
    return elementos


def buscar_competencias(consulta: str, maximo: int = 8) -> str:
    """Dónde has aprendido algo: busca en el plan del máster, en tu grado, en lo que has hecho en el máster y en las
    masterclasses. Devuelve los resultados con su origen y su estado (cursada, en curso, pendiente)."""
    q = normalizar(consulta)
    extra = " ".join(v for k, v in SINONIMOS.items() if k in q)
    buscadas = _tokens(f"{consulta} {extra}")
    if not buscadas:
        return "ERROR: escribe qué competencia buscas (por ejemplo, «Power BI», «series temporales» o «SQL»)."
    puntuados = []
    for etiqueta, texto, mostrar in _elementos():
        comunes = buscadas & _tokens(texto)
        if comunes:
            puntuados.append((len(comunes) + (2 if q in normalizar(texto) else 0), etiqueta, mostrar))
    if not puntuados:
        return (f"No encuentro «{consulta}» ni en tu grado, ni en tu máster, ni en el plan de estudios. Si no consta, no "
                "lo pongas en el CV: es un hueco para tu plan de preparación.")
    puntuados.sort(key=lambda x: -x[0])
    lineas = [f"Competencias relacionadas con «{consulta}» (de más a menos relevante):"]
    for i, (_, etiqueta, mostrar) in enumerate(puntuados[:maximo], start=1):
        lineas.append(f"{i}. [{etiqueta}] {mostrar[:400]}")
    lineas.append("Recuerda: lo «en curso» va como formación en curso; lo «pendiente» no va en el CV; las herramientas "
                  "del plan son orientativas y solo valen si constan en tu CV o en tu máster.")
    return "\n".join(lineas)


# ------------------------------------------------------------------------------------------------ guardarraíl
TECNOLOGIAS = {  # nombre → patrón (sin distinguir mayúsculas, salvo los que empiezan por (?-i:...))
    "Python": r"python", "R": r"(?-i:\bR\b)(?![-/])", "SQL": r"\bsql\b", "NoSQL": r"nosql", "Excel": r"excel",
    "Power BI": r"power ?bi", "Power Query": r"power ?query", "DAX": r"(?-i:\bDAX\b)", "VBA": r"\bvba\b",
    "Tableau": r"tableau", "Looker": r"looker", "Qlik": r"qlik", "SAS": r"(?-i:\bSAS\b)", "SPSS": r"spss",
    "Stata": r"\bstata\b", "MATLAB": r"matlab", "Java": r"\bjava\b", "JavaScript": r"javascript",
    "TypeScript": r"typescript", "Scala": r"\bscala\b", "C++": r"c\+\+", "Spark": r"\bspark\b", "PySpark": r"pyspark",
    "Hadoop": r"hadoop", "Databricks": r"databricks", "Snowflake": r"snowflake", "BigQuery": r"big ?query",
    "Redshift": r"redshift", "AWS": r"\baws\b|amazon web services", "Azure": r"\bazure\b",
    "Google Cloud": r"\bgcp\b|google cloud", "Docker": r"docker", "Kubernetes": r"kubernetes|\bk8s\b",
    "Airflow": r"airflow", "dbt": r"\bdbt\b", "Kafka": r"kafka", "Git": r"\bgit\b", "GitHub": r"github",
    "GitLab": r"gitlab", "Jira": r"\bjira\b", "scikit-learn": r"scikit[- ]?learn|sklearn", "XGBoost": r"xgboost",
    "LightGBM": r"lightgbm", "CatBoost": r"catboost", "TensorFlow": r"tensorflow", "Keras": r"\bkeras\b",
    "PyTorch": r"pytorch", "Hugging Face": r"hugging ?face", "LangChain": r"langchain", "LangGraph": r"langgraph",
    "LlamaIndex": r"llama ?index", "MLflow": r"mlflow", "FastAPI": r"fastapi", "Flask": r"\bflask\b",
    "Django": r"django", "Streamlit": r"streamlit", "pandas": r"\bpandas\b", "NumPy": r"numpy", "Polars": r"\bpolars\b",
    "matplotlib": r"matplotlib", "seaborn": r"seaborn", "Plotly": r"plotly", "statsmodels": r"statsmodels",
    "SAP": r"(?-i:\bSAP\b)", "Salesforce": r"salesforce", "PostgreSQL": r"postgre", "MySQL": r"mysql",
    "MongoDB": r"mongo", "Oracle": r"\boracle\b", "SQL Server": r"sql server", "SQLite": r"sqlite",
    "Linux": r"\blinux\b", "Bash": r"\bbash\b", "Google Analytics": r"google analytics", "Figma": r"figma",
    "Terraform": r"terraform", "Neo4j": r"neo4j", "Elasticsearch": r"elasticsearch", "OpenAI": r"openai",
    "ChatGPT": r"chatgpt", "Copilot": r"copilot", "MCP": r"(?-i:\bMCP\b)|model context protocol",
    "Microsoft Agent Framework": r"agent framework", "Pydantic": r"pydantic", "BeautifulSoup": r"beautiful ?soup",
}


def fuentes_de_respaldo(yo: dict | None = None) -> str:
    """Todo lo que acredita lo que pones en el CV: tu CV, tu grado, tu máster, los nombres y contenidos oficiales del
    plan y las masterclasses ya hechas. (Las herramientas orientativas del plan NO cuentan.)"""
    yo = yo or perfil()
    p, hoy = plan(), fecha_referencia()
    oficial = [f"{a['nombre']} {' '.join(a['contenidos'])}" for a in p["asignaturas"]]
    sesiones = [f"{s['nombre']} {' '.join(s['contenidos'])} {' '.join(s['herramientas'])}"
                for s in p["masterclasses"]["sesiones"] if estado_sesion(s["fecha"], hoy) == "hecha"]
    return "\n".join([yo["cv"], yo["grado"], yo["master"], p["titulo"], p["universidad"], *oficial,
                      p["masterclasses"]["nombre"], *sesiones])


def cifras_sin_respaldo(cv_nuevo: str, fuentes: str) -> list[str]:
    """Cifras del CV nuevo que no aparecen en ninguna fuente («1.200» y «1200» cuentan como la misma)."""
    def cifras(texto):
        return re.findall(r"\d+(?:[.,]\d+)*", texto)

    normalizar_cifra = lambda c: re.sub(r"[.,]", "", c)  # noqa: E731
    conocidas = {normalizar_cifra(c) for c in cifras(fuentes)}
    nuevas = []
    for c in cifras(cv_nuevo):
        if normalizar_cifra(c) not in conocidas and c not in nuevas:
            nuevas.append(c)
    return nuevas


def tecnologias_sin_respaldo(cv_nuevo: str, fuentes: str) -> list[str]:
    """Herramientas conocidas que aparecen en el CV nuevo y no en las fuentes."""
    return [nombre for nombre, patron in TECNOLOGIAS.items()
            if re.search(patron, cv_nuevo, re.I) and not re.search(patron, fuentes, re.I)]


def afirmaciones_sin_respaldo(cv_nuevo: str, fuentes: str | None = None) -> list[str]:
    """El guardarraíl: cifras y herramientas del CV nuevo sin respaldo. Usa TU cifras_sin_respaldo (lab 2b,
    sesion2/mis_piezas/guardarrail.py) si la has escrito; si no, la de referencia."""
    fuentes = fuentes if fuentes is not None else fuentes_de_respaldo()
    detector_cifras = piezas.cargar("guardarrail", "cifras_sin_respaldo", cifras_sin_respaldo)
    try:
        cifras = list(detector_cifras(cv_nuevo, fuentes))
    except Exception:  # noqa: BLE001 — si tu función falla, mejor la de referencia que ningún control
        cifras = cifras_sin_respaldo(cv_nuevo, fuentes)
    return [f"cifra «{c}»" for c in cifras] + [f"herramienta «{t}»" for t in tecnologias_sin_respaldo(cv_nuevo, fuentes)]


# ------------------------------------------------------------------------------------------------ guardar versiones
def slug(texto: str, maximo: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", normalizar(texto)).strip("-")
    return s[:maximo].strip("-") or "oferta"


def guardar_version(empresa: str, puesto: str, cv_markdown: str) -> Path:
    """Guarda el CV adaptado en sesion2/trabajo/cv/<empresa>-<puesto>.md y .docx. Nunca toca tu CV original."""
    carpeta = TRABAJO / "cv"
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{slug(empresa, 25)}-{slug(puesto, 35)}.md"
    ruta.write_text(cv_markdown.strip() + "\n", encoding="utf-8")
    markdown_a_docx(cv_markdown, ruta.with_suffix(".docx"))
    return ruta


def ultimo_cv() -> Path:
    """El CV adaptado más reciente de sesion2/trabajo/cv/."""
    versiones = sorted((TRABAJO / "cv").glob("*.md"), key=lambda r: r.stat().st_mtime)
    if not versiones:
        raise FileNotFoundError("No hay ningún CV adaptado en sesion2/trabajo/cv/: el editor no ha llegado a guardarlo.")
    return versiones[-1]


def _runs(parrafo, texto: str):
    for i, trozo in enumerate(re.split(r"\*\*(.+?)\*\*", texto)):
        if trozo:
            trozo = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", trozo).replace("*", "")
            parrafo.add_run(trozo).bold = i % 2 == 1


def markdown_a_docx(markdown: str, ruta: Path) -> Path:
    """Un Word sencillo y limpio a partir del Markdown del CV (títulos, viñetas y negritas)."""
    from docx import Document
    from docx.shared import Pt

    doc = Document()
    estilo = doc.styles["Normal"]
    estilo.font.name, estilo.font.size = "Calibri", Pt(10.5)
    for linea in markdown.splitlines():
        texto = linea.strip()
        if not texto:
            continue
        if texto.startswith("#"):
            nivel = min(len(texto) - len(texto.lstrip("#")), 3)
            doc.add_heading(texto.lstrip("#").strip(), level=0 if nivel == 1 else nivel - 1)
        elif re.match(r"^[-*•] ", texto):
            _runs(doc.add_paragraph(style="List Bullet"), texto[2:].strip())
        elif texto.startswith(">"):
            p = doc.add_paragraph()
            _runs(p, texto.lstrip("> ").strip())
            for r in p.runs:
                r.italic = True
        else:
            _runs(doc.add_paragraph(), texto)
    doc.save(ruta)
    return ruta


# ------------------------------------------------------------------------------------------------ medir
def cobertura(palabras_clave: list[str], texto: str) -> dict:
    """Qué palabras clave de la oferta aparecen en un CV: lo que comprobaría un filtro automático (ATS)."""
    t = normalizar(texto)
    presentes, ausentes = [], []
    for clave in dict.fromkeys(k.strip() for k in palabras_clave if k.strip()):
        n = normalizar(clave)
        palabras = [p for p in re.findall(r"[a-z0-9+#]+", n) if len(p) > 2 and p not in _VACIAS]
        encontrada = n in t or (len(palabras) > 1 and all(re.search(rf"\b{re.escape(p)}", t) for p in palabras))
        (presentes if encontrada else ausentes).append(clave)
    total = len(presentes) + len(ausentes)
    return {"porcentaje": round(100 * len(presentes) / total) if total else 0, "presentes": presentes,
            "ausentes": ausentes}


# ------------------------------------------------------------------------------------------------ importar tu CV
def _leer_texto(ruta: Path) -> str:
    """Un .md o .txt en la codificación con que se guardara: UTF-8 (con o sin BOM), UTF-16 (el «Unicode» del Bloc de
    notas) o ANSI (Windows-1252)."""
    datos = ruta.read_bytes()
    if datos.startswith((b"\xff\xfe", b"\xfe\xff")):
        return datos.decode("utf-16")
    try:
        return datos.decode("utf-8-sig")
    except UnicodeDecodeError:
        return datos.decode("cp1252", errors="replace")


def _texto_docx(ruta: Path) -> str:
    """Párrafos y tablas en su orden: muchas plantillas de CV maquetan con tablas."""
    from docx import Document
    from docx.table import Table

    lineas = []
    for bloque in Document(str(ruta)).iter_inner_content():
        if isinstance(bloque, Table):
            for fila in bloque.rows:
                celdas = list(dict.fromkeys(c.text.strip() for c in fila.cells if c.text.strip()))
                if celdas:
                    lineas.append(" · ".join(celdas))
            continue
        if not bloque.text.strip():
            continue
        estilo = (bloque.style.name or "").lower() if bloque.style is not None else ""
        if estilo.startswith(("heading", "título", "title")):
            lineas.append(f"\n## {bloque.text.strip()}")
        elif "list" in estilo or "lista" in estilo:
            lineas.append(f"- {bloque.text.strip()}")
        else:
            lineas.append(bloque.text.strip())
    return "\n".join(lineas)


def importar_cv(ruta: str | Path, nombre_original: str = "") -> Path:
    """Convierte tu CV (PDF, Word, Markdown o texto) a Markdown y lo guarda en sesion2/mi_perfil/cv.md.
    Revísalo después: la extracción de un PDF puede desordenar columnas."""
    ruta = Path(ruta)
    extension = Path(nombre_original or ruta.name).suffix.lower()
    if extension in (".md", ".markdown", ".txt"):
        texto, minimo, problema = _leer_texto(ruta), 20, "El fichero está prácticamente vacío."
    elif extension == ".docx":
        texto, minimo = _texto_docx(ruta), 50
        problema = ("Apenas he podido extraer texto del Word (¿está en cuadros de texto?). Prueba con el PDF o pega el "
                    "texto en sesion2/mi_perfil/cv.md.")
    elif extension == ".pdf":
        from pypdf import PdfReader

        texto, minimo = "\n\n".join((pagina.extract_text() or "") for pagina in PdfReader(str(ruta)).pages), 200
        problema = ("Apenas he podido extraer texto del PDF (¿está escaneado como imagen?). Prueba con el Word o pega "
                    "el texto en sesion2/mi_perfil/cv.md.")
    else:
        raise ValueError("Formato no admitido: usa PDF, Word (.docx), Markdown (.md) o texto (.txt).")
    texto = re.sub(r"\n{3,}", "\n\n", texto.replace("\r\n", "\n")).strip()
    if len(re.sub(r"\s", "", texto)) < minimo:
        raise ValueError(problema)
    PERFIL.mkdir(parents=True, exist_ok=True)
    destino = PERFIL / "cv.md"
    destino.write_text(texto + "\n", encoding="utf-8")
    return destino
