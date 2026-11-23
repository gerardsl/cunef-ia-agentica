"""Tu agente de candidaturas, en una webapp.

    python sesion2/webapp.py                  # y abre http://127.0.0.1:8000
    python sesion2/webapp.py --puerto 8001

En GitHub Codespaces: al arrancar, VS Code avisa de que el puerto 8000 está disponible → «Abrir en el navegador»
(o pestaña PUERTOS → 8000 → icono del globo). Para pararla: Ctrl+C en el terminal.

Por dentro (FastAPI):
    GET  /                    la página (sesion2/web/index.html)
    GET  /api/estado          tu perfil, tus piezas y el modelo
    POST /api/preparar        {url} o {texto} → eventos del flujo, uno por línea (NDJSON), según ocurren
    POST /api/cv?nombre=…     sube tu CV (PDF, Word, Markdown o texto) → sesion2/mi_perfil/cv.md
    POST /api/cv/ejemplo      vuelve al CV de ejemplo (tu CV se guarda como mi_perfil/cv_anterior.md)
    GET  /descargas/…         los ficheros que genera (CV en Markdown y Word, dossier…), solo de sesion2/trabajo/
"""

import argparse
import asyncio
import json
import sys
import tempfile
from pathlib import Path

S2 = Path(__file__).resolve().parent
sys.path.insert(0, str(S2))

import uvicorn  # noqa: E402
from fastapi import FastAPI, HTTPException, Request  # noqa: E402
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse  # noqa: E402
from markdown_it import MarkdownIt  # noqa: E402
from pydantic import BaseModel  # noqa: E402

import mucdia  # noqa: E402
from candidatura import carrera, flujo, oferta, piezas  # noqa: E402

OFERTA_DE_EJEMPLO = oferta.OFERTA_DE_EJEMPLO
MAX_CV_BYTES = 5_000_000

app = FastAPI(title="Tu agente de candidaturas", docs_url=None, redoc_url=None)
markdown = MarkdownIt("commonmark", {"html": False})  # sin HTML crudo: lo que escribe el modelo no puede inyectar código
EN_MARCHA = asyncio.Lock()
_TAREAS: set[asyncio.Task] = set()


class Peticion(BaseModel):
    url: str = ""
    texto: str = ""


@app.get("/", response_class=HTMLResponse)
def portada() -> str:
    return (S2 / "web" / "index.html").read_text(encoding="utf-8")


@app.get("/api/estado")
def estado() -> dict:
    yo = carrera.perfil()
    primera = next((l.lstrip("# ").strip() for l in yo["cv"].splitlines() if l.strip()), "")
    return {"perfil": yo["origen"], "nombre": primera, "grado": bool(yo["grado"]), "master": bool(yo["master"]),
            "piezas": piezas.estado(), "modelo": mucdia.config.modelo(), "modo": mucdia.config.modo(),
            "clave": bool(mucdia.config.clave()), "ejemplo": OFERTA_DE_EJEMPLO,
            "cv_html": markdown.render(yo["cv"])}


def _para_la_web(evento: dict) -> dict:
    """Añade el HTML del CV adaptado (renderizado aquí, con el HTML crudo desactivado)."""
    if evento.get("tipo") == "resultado" and evento.get("clave") == "cv":
        evento = {**evento, "datos": {**evento["datos"], "html": markdown.render(evento["datos"]["markdown"])}}
    return evento


@app.post("/api/preparar")
async def preparar(peticion: Peticion) -> StreamingResponse:
    if not (peticion.url.strip() or peticion.texto.strip()):
        raise HTTPException(400, "Pega el enlace de la oferta o su texto.")
    if EN_MARCHA.locked():
        raise HTTPException(409, "Ya hay una candidatura en marcha: espera a que termine.")
    cola: asyncio.Queue = asyncio.Queue()

    async def ejecutar():
        async with EN_MARCHA:
            try:
                await flujo.preparar(url=peticion.url.strip(), texto=peticion.texto, emitir=cola.put_nowait)
            except Exception as e:  # noqa: BLE001 — se lo contamos a la persona, con el mensaje amable de mucdia
                cola.put_nowait({"tipo": "error", "texto": f"{type(e).__name__}: {e}"})
            finally:
                cola.put_nowait(None)

    tarea = asyncio.create_task(ejecutar())
    _TAREAS.add(tarea)
    tarea.add_done_callback(_TAREAS.discard)

    async def eventos():
        while (evento := await cola.get()) is not None:
            yield json.dumps(_para_la_web(evento), ensure_ascii=False, default=str) + "\n"

    return StreamingResponse(eventos(), media_type="application/x-ndjson")


@app.post("/api/cv")
async def subir_cv(request: Request, nombre: str) -> dict:
    datos = await request.body()
    if not datos or len(datos) > MAX_CV_BYTES:
        raise HTTPException(400, "Sube un fichero de hasta 5 MB.")
    mio = carrera.PERFIL / "cv.md"
    previo = mio.read_bytes() if mio.exists() else None
    with tempfile.TemporaryDirectory() as carpeta:
        temporal = Path(carpeta) / "cv"
        temporal.write_bytes(datos)
        try:  # importar_cv valida antes de escribir: si falla, tu CV anterior sigue intacto
            ruta = carrera.importar_cv(temporal, nombre_original=nombre)
        except ValueError as e:
            raise HTTPException(400, str(e)) from e
        except Exception as e:  # noqa: BLE001 — un PDF o un Word dañado, protegido con contraseña…
            raise HTTPException(400, f"No he podido leer «{nombre}» ({type(e).__name__}). ¿Está dañado o protegido "
                                     "con contraseña? Prueba con otro formato o pega el texto en sesion2/mi_perfil/cv.md.") from e
    if previo is not None and previo != ruta.read_bytes():
        (carrera.PERFIL / "cv_anterior.md").write_bytes(previo)
    return {"ok": True, "ruta": ruta.relative_to(S2.parent).as_posix(), **estado()}


@app.post("/api/cv/ejemplo")
def usar_ejemplo() -> dict:
    mio = carrera.PERFIL / "cv.md"
    if mio.exists():
        mio.replace(carrera.PERFIL / "cv_anterior.md")
    return estado()


@app.get("/descargas/{ruta:path}")
def descargar(ruta: str) -> FileResponse:
    fichero = (S2.parent / ruta).resolve()
    if not fichero.is_relative_to(carrera.TRABAJO.resolve()) or not fichero.is_file():
        raise HTTPException(404, "No existe (solo se descargan ficheros de sesion2/trabajo/).")
    return FileResponse(fichero, filename=fichero.name)


def main() -> None:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--puerto", type=int, default=8000)
    argumentos.add_argument("--host", default="127.0.0.1", help="127.0.0.1 = solo desde esta máquina (lo seguro)")
    a = argumentos.parse_args()
    print(f"🚀 Tu agente de candidaturas: http://{a.host}:{a.puerto}  (en Codespaces: pestaña PUERTOS → {a.puerto})")
    print(f"   Perfil: {carrera.origen()} · modelo: {mucdia.config.modelo()} · modo: {mucdia.config.modo()} · Ctrl+C para parar")
    uvicorn.run(app, host=a.host, port=a.puerto, log_level="warning")


if __name__ == "__main__":
    main()
