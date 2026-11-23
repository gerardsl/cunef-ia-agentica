"""Todo junto: el flujo que usa la webapp (y el último paso del lab 2c).

Es un *flujo* (workflow): los pasos y su orden los fija el código; en cada paso que necesita juicio trabaja un agente.

    1 · Leer la oferta (código: robots.txt, JSON-LD…) → estructurarla (agente analista)
    2 · Adaptar el CV por MCP (agente editor)  ‖  investigar la empresa (agente investigador)      ← en paralelo
    3 · Plan de 4 semanas y pitch de 3 frases (agente coach)

    resultado = await preparar(url="https://…")             # o preparar(texto="…la oferta pegada…")
    resultado = await preparar(url, emitir=print)            # cada paso y cada herramienta, en directo

Cada evento es un diccionario con «tipo»: inicio, paso, pagina, herramienta, resultado_herramienta, resultado, aviso,
necesito_texto, error y fin. La webapp los envía al navegador según ocurren.
"""

import asyncio
import json
import re
import time
from collections.abc import Callable

from agent_framework import FunctionInvocationContext, function_middleware

import mucdia
from mucdia.cuota import USO

from . import agentes, carrera, oferta, piezas

Emisor = Callable[[dict], None]
PASOS = {"oferta": "Leer la oferta", "cv": "Adaptar tu CV (MCP)", "empresa": "Investigar la empresa",
         "plan": "Plan y pitch"}


def _imprimir(evento: dict) -> None:
    tipo = evento["tipo"]
    if tipo == "paso":
        print(f"{'▶' if evento['estado'] == 'inicio' else '✔'} {PASOS[evento['paso']]}", flush=True)
    elif tipo == "herramienta":
        print(f"   🔧 {evento['agente']} → {evento['nombre']}({evento['args']})", flush=True)
    elif tipo == "resultado_herramienta" and not evento["ok"]:
        print(f"   ⚠️  {evento['nombre']}: {evento['resumen']}", flush=True)
    elif tipo in ("aviso", "error", "necesito_texto"):
        print(f"   {'⚠️' if tipo == 'aviso' else '❌'} {evento.get('mensaje') or evento.get('texto')}", flush=True)


def _texto_resultado(resultado) -> str:
    if resultado is None:
        return ""
    if isinstance(resultado, str):
        return resultado
    if isinstance(resultado, (list, tuple)):
        return "\n".join(_texto_resultado(r) for r in resultado)
    return getattr(resultado, "text", None) or str(resultado)


def _argumentos(argumentos) -> dict:
    if argumentos is None:
        return {}
    datos = argumentos.model_dump() if hasattr(argumentos, "model_dump") else dict(argumentos)
    return {k: (v if len(str(v)) <= 90 else f"{str(v)[:87]}…") for k, v in datos.items()}


def vigilar_herramientas(agente: str, emitir: Emisor, registro: dict):
    """Middleware: avisa de cada herramienta que usa el agente (antes y después) y anota el CV guardado."""

    @function_middleware
    async def vigilar(context: FunctionInvocationContext, call_next):
        nombre = context.function.name
        emitir({"tipo": "herramienta", "agente": agente, "nombre": nombre, "args": _argumentos(context.arguments)})
        await call_next()
        texto = _texto_resultado(context.result).strip()
        ok = not texto.upper().startswith("ERROR")
        emitir({"tipo": "resultado_herramienta", "agente": agente, "nombre": nombre, "ok": ok,
                "resumen": texto[:240]})
        if nombre == "guardar_cv" and ok and (m := re.search(r"Guardado: (\S+\.md)", texto)):
            registro["archivo"] = m.group(1)
        registro.setdefault("llamadas", []).append(nombre)

    return vigilar


async def _adaptar_cv(cliente, of, yo: dict, emitir: Emisor) -> dict:
    registro: dict = {}
    servidor = mucdia.servidor_mcp()
    try:
        editor = agentes.editor_cv(cliente, servidor, middleware=[vigilar_herramientas("editor_cv", emitir, registro)])
        r = await editor.run("Adapta mi CV a esta oferta:\n\n" + agentes.describir_oferta(of),
                             options={"response_format": agentes.CVAdaptado})
        adaptado = r.value
    finally:
        await servidor.close()
    archivo = registro.get("archivo") or (adaptado.archivo if adaptado else "")
    ruta = carrera.S2.parent / archivo if archivo else None
    if ruta is None or not ruta.exists():
        raise RuntimeError("El editor no ha conseguido guardar un CV sin afirmaciones inventadas (guardar_cv lo ha "
                           "rechazado o no lo ha llamado). Prueba otra vez o revisa sus instrucciones.")
    cv_nuevo = ruta.read_text(encoding="utf-8")
    return {
        "archivo": ruta.relative_to(carrera.S2.parent).as_posix(),
        "word": ruta.with_suffix(".docx").relative_to(carrera.S2.parent).as_posix(),
        "markdown": cv_nuevo,
        "cambios": [c.model_dump() for c in adaptado.cambios],
        "encaje": [e.model_dump() for e in adaptado.encaje],
        "huecos": adaptado.huecos,
        "cobertura_antes": carrera.cobertura(of.palabras_clave, yo["cv"]),
        "cobertura_despues": carrera.cobertura(of.palabras_clave, cv_nuevo),
        "sin_respaldo": carrera.afirmaciones_sin_respaldo(cv_nuevo),
        "intentos_de_guardar": registro.get("llamadas", []).count("guardar_cv"),
    }


async def _investigar(cliente, of, emitir: Emisor) -> dict:
    investigador = agentes.investigador(cliente, middleware=[vigilar_herramientas("investigador", emitir, {})])
    r = await investigador.run(f"Hoy es {carrera.fecha_referencia():%d-%m-%Y}. Prepárame para la entrevista de esta "
                               f"oferta:\n\n{agentes.describir_oferta(of)}",
                               options={"response_format": agentes.Dossier})
    return r.value.model_dump()


async def _plan(cliente, of, cv: dict | None, dossier: dict | None) -> dict:
    partes = [agentes.describir_oferta(of), f"Fecha de hoy: {carrera.fecha_referencia():%d-%m-%Y}"]
    if cv:
        partes.append("Encaje del CV:\n" + "\n".join(f"- {e['requisito']}: {e['estado']} ({e['evidencia']})"
                                                     for e in cv["encaje"]))
        partes.append("Huecos: " + "; ".join(cv["huecos"]))
        partes.append("CV adaptado:\n" + cv["markdown"])
    if dossier:
        partes.append("Qué preparar sobre la empresa:\n" + "\n".join(f"- [{t['prioridad']}] {t['tema']}: {t['por_que']}"
                                                                     for t in dossier["que_preparar"]))
    r = await agentes.coach(cliente).run("\n\n".join(partes), options={"response_format": agentes.PlanYPitch})
    return r.value.model_dump()


def dossier_markdown(dossier: dict) -> str:
    lineas = [f"# Dossier: {dossier['empresa']}", "", "## Qué preparar"]
    lineas += [f"- **{t['tema']}** ({t['prioridad']}): {t['por_que']}" for t in dossier["que_preparar"]]
    for s in dossier["secciones"]:
        lineas += ["", f"## {s['titulo']}", s["contenido"], *[f"- Fuente: {f}" for f in s["fuentes"]]]
    lineas += ["", "## Preguntas que probablemente te harán", *[f"- {p}" for p in dossier["preguntas_probables"]]]
    lineas += ["", "## Preguntas para hacerles", *[f"- {p}" for p in dossier["preguntas_para_ellos"]]]
    if dossier["no_encontrado"]:
        lineas += ["", "## No encontrado en las fuentes", *[f"- {p}" for p in dossier["no_encontrado"]]]
    return "\n".join(lineas) + "\n"


async def preparar(url: str = "", texto: str = "", emitir: Emisor | None = None, cliente=None,
                   pagina: dict | None = None) -> dict:
    """Prepara la candidatura completa para una oferta (su enlace, su texto o la página ya leída en el lab 2a).
    Devuelve un diccionario con la oferta, el CV adaptado, el dossier de la empresa y el plan; y lo guarda en
    sesion2/trabajo/<empresa>-<puesto>/."""
    emitir = emitir or _imprimir
    cliente = cliente or mucdia.cliente()
    t0 = time.perf_counter()
    uso0 = (USO.llamadas, USO.replay, USO.tokens_entrada, USO.tokens_salida)
    yo = carrera.perfil()
    resultado: dict = {"ok": False, "perfil": yo["origen"], "piezas": piezas.estado()}
    emitir({"tipo": "inicio", "perfil": yo["origen"], "piezas": resultado["piezas"], "modelo": mucdia.config.modelo(),
            "modo": mucdia.config.modo()})

    # 1 · Leer la oferta
    emitir({"tipo": "paso", "paso": "oferta", "estado": "inicio"})
    if pagina is None:
        pagina = oferta.desde_texto(texto, url) if texto.strip() else await asyncio.to_thread(oferta.leer_oferta, url)
    resultado["pagina"] = {k: v for k, v in pagina.items() if k != "texto"}
    if not pagina["ok"]:
        emitir({"tipo": "necesito_texto", **resultado["pagina"]})
        return resultado
    emitir({"tipo": "pagina", "fuente": pagina["fuente"], "robots": pagina["robots"], "url": pagina["url"],
            "caracteres": len(pagina["texto"])})
    try:
        of = await oferta.analizar_oferta(cliente, pagina)
    except Exception as e:  # noqa: BLE001
        emitir({"tipo": "error", "texto": f"No he podido analizar la oferta: {e}"})
        return resultado
    resultado["oferta"] = of.model_dump()
    emitir({"tipo": "resultado", "clave": "oferta", "datos": resultado["oferta"]})
    emitir({"tipo": "paso", "paso": "oferta", "estado": "fin"})

    # 2 · CV y empresa, en paralelo
    emitir({"tipo": "paso", "paso": "cv", "estado": "inicio"})
    emitir({"tipo": "paso", "paso": "empresa", "estado": "inicio"})
    cv, dossier = await asyncio.gather(_adaptar_cv(cliente, of, yo, emitir), _investigar(cliente, of, emitir),
                                       return_exceptions=True)
    for clave, valor in (("cv", cv), ("empresa", dossier)):
        if isinstance(valor, BaseException):
            emitir({"tipo": "error", "paso": clave, "texto": f"{PASOS[clave]}: {valor}"})
        else:
            resultado[clave] = valor
            emitir({"tipo": "resultado", "clave": clave, "datos": valor})
        emitir({"tipo": "paso", "paso": clave, "estado": "fin"})

    # 3 · Plan y pitch
    emitir({"tipo": "paso", "paso": "plan", "estado": "inicio"})
    try:
        resultado["plan"] = await _plan(cliente, of, resultado.get("cv"), resultado.get("empresa"))
        # El mismo guardarraíl que el CV: ¿cita el pitch cifras o herramientas que no constan?
        resultado["plan"]["pitch_sin_respaldo"] = carrera.afirmaciones_sin_respaldo(" ".join(resultado["plan"]["pitch"]))
        emitir({"tipo": "resultado", "clave": "plan", "datos": resultado["plan"]})
    except Exception as e:  # noqa: BLE001
        emitir({"tipo": "error", "paso": "plan", "texto": f"{PASOS['plan']}: {e}"})
    emitir({"tipo": "paso", "paso": "plan", "estado": "fin"})

    # Guardar y medir
    carpeta = carrera.TRABAJO / f"{carrera.slug(of.empresa, 25)}-{carrera.slug(of.puesto, 35)}"
    carpeta.mkdir(parents=True, exist_ok=True)
    resultado["ok"] = all(k in resultado for k in ("cv", "empresa", "plan"))
    resultado["medidas"] = {
        "segundos": round(time.perf_counter() - t0),
        "llamadas": (USO.llamadas - uso0[0]) + (USO.replay - uso0[1]),
        "grabadas": USO.replay - uso0[1],
        "tokens": (USO.tokens_entrada - uso0[2]) + (USO.tokens_salida - uso0[3]),
    }
    (carpeta / "resultado.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2, default=str),
                                            encoding="utf-8")
    if "empresa" in resultado:
        (carpeta / "dossier.md").write_text(dossier_markdown(resultado["empresa"]), encoding="utf-8")
    resultado["carpeta"] = carpeta.relative_to(carrera.S2.parent).as_posix()
    emitir({"tipo": "fin", "ok": resultado["ok"], "carpeta": resultado["carpeta"], **resultado["medidas"]})
    return resultado
