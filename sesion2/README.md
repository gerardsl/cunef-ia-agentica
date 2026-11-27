# Sesión 2 · Agentes conectados: un agente que prepara tu candidatura

**Miércoles 25 de noviembre de 2026 · 19:30-21:00**

Me mandasteis, a mano, una oferta real, lo que haríais en un mes para ser buenos candidatos y tres
frases para que os fichara. Hoy construís **el agente que lo hace con vosotros**: le pasas el enlace de la oferta y

1. **lee la oferta** respetando las reglas de la web (robots.txt) y la estructura con el modelo;
2. **adapta tu CV** a través de un **servidor MCP** con tu perfil (tu CV, tu grado y tu máster), **sin inventar
   nada**: un guardarraíl en código rechaza cualquier cifra o herramienta que no conste;
3. **decide qué tienes que preparar sobre la empresa y lo prepara**, con fuentes que se pueden citar;
4. te propone un **plan de cuatro semanas** y tu **pitch de tres frases**…

…y todo eso, en **tu webapp**. Cada lab termina con un número.

| Lab | Notebook | Tiempo | Qué aprenderás |
|---|---|---|---|
| **2a** | [`lab2a_leer_la_oferta.ipynb`](lab2a_leer_la_oferta.ipynb) | 15' | Leer la web con educación (robots.txt), JSON-LD de schema.org y salidas estructuradas |
| **2b** | [`lab2b_tu_cv_por_mcp.ipynb`](lab2b_tu_cv_por_mcp.ipynb) | 20' | MCP por dentro, un servidor con mínimo privilegio y un guardarraíl que no deja inventar |
| **2c** | [`lab2c_empresa_y_webapp.ipynb`](lab2c_empresa_y_webapp.ipynb) | 15' | Investigar con fuentes, un flujo con agentes en paralelo y tu webapp |

**Los notebooks están resueltos**: solo tienes que pegar el enlace de tu oferta en la primera celda del lab 2a
(`MI_OFERTA`) y ejecutar los tres labs en orden. Las celdas ✏️ son las piezas del agente: tienen comprobación
automática y **las usa tu webapp** (se guardan en `sesion2/mis_piezas/`).

## Antes de empezar

1. Abre tu Codespace con el botón del [README](../README.md) y elige el kernel **Python 3.12** en cada notebook.
   Ver [problemas frecuentes](../docs/problemas_frecuentes.md) si algo se queja.
2. Ten a mano **el enlace de la oferta** que me mandaste y **tu CV** (PDF, Word o texto).
3. ¿Tu oferta es de LinkedIn, Indeed o InfoJobs? Esas webs no dejan que las lean programas: copia su texto en el
   navegador y pégalo cuando el agente te lo pida.

## Tu perfil (`sesion2/mi_perfil/`)

El agente solo puede usar lo que conste aquí. **Esta carpeta no se sube nunca a GitHub** (está en `.gitignore`).

| Fichero | Qué es |
|---|---|
| `cv.md` | Tu CV en Markdown. Súbelo desde la webapp o conviértelo en el lab 2b: `C.carrera.importar_cv(…)` |
| `grado.md` | Lo que aprendiste en tu grado (asignaturas, trabajos y prácticas que puedas demostrar) |
| `master.md` | Lo que llevas hecho en el máster (prácticas, proyectos) |

Si aún no has puesto tu CV, el agente usa el de **Lucía Martín**, ficticia ([`ejemplo/`](ejemplo/)), que también
sirve de plantilla. Tu perfil y el de ejemplo nunca se mezclan. El plan de estudios oficial del MUCD-IA (BOE de 19 de
febrero de 2026) está en [`datos/plan_mucdia.json`](datos/plan_mucdia.json), con el estado de cada asignatura según la
fecha: lo **en curso** se cita como formación en curso; lo **pendiente**, nunca.

> **Tu CV es un dato personal: envía solo lo necesario.** Desde el Espacio Económico Europeo (España incluida), aunque
> uses la cuota gratuita, Google aplica las condiciones de pago: no usa lo que envías a Gemini para mejorar sus
> productos y solo lo guarda un tiempo limitado para detectar abusos ([Términos adicionales de la API de
> Gemini](https://ai.google.dev/gemini-api/terms), vigentes desde el 23 de marzo de 2026). Aun así, el teléfono, la
> dirección o el DNI no ayudan a adaptar un CV: quítalos de `cv.md` y añádelos al final en el Word. Y si algún día
> publicas la webapp para otras personas del EEE, esos mismos términos exigen el plan de pago.

## El servidor MCP «mi-carrera»

[`servidor_mcp_carrera.py`](servidor_mcp_carrera.py) pone tu carrera al alcance de cualquier cliente MCP (el agente
de la webapp, GitHub Copilot, Claude…), con **mínimo privilegio**: solo lee tu perfil y solo escribe versiones nuevas
en `sesion2/trabajo/cv/`.

| Tipo | Nombre | Para qué |
|---|---|---|
| Herramienta | `leer_cv` | Tu CV original, en Markdown |
| Herramienta | `plan_de_estudios` | Las asignaturas del MUCD-IA con su estado hoy y las masterclasses |
| Herramienta | `buscar_competencias` | Dónde aprendiste algo: tu grado, tu máster, el plan o las masterclasses |
| Herramienta | `guardar_cv` | Guarda el CV adaptado (Markdown y Word)… si no tiene cifras ni herramientas sin respaldo |
| Recursos | `carrera://cv` · `carrera://grado` · `carrera://master` · `carrera://plan` | Lo mismo, para leerlo sin modelo |
| Prompt | `adaptar_cv` | Plantilla para pedir a cualquier asistente que adapte tu CV a una oferta |

Pruébalo:

```bash
python sesion2/servidor_mcp_carrera.py     # se queda esperando por stdio: sal con Ctrl+C
mcp dev sesion2/servidor_mcp_carrera.py    # inspector web oficial de MCP (requiere Node.js)
```

**El mismo servidor en GitHub Copilot.** [`.vscode/mcp.json`](../.vscode/mcp.json) lo registra como `mi-carrera`.
Abre Copilot Chat en modo **Agent**, actívalo en el icono de herramientas y pídele: *«Adapta mi CV a esta oferta:
…»*. Mismo servidor, mismo guardarraíl, otro cliente.

## Tu webapp

```bash
python sesion2/webapp.py      # en Codespaces se abre sola; si no: pestaña PUERTOS → 8000 → 🌐
```

Pega tu oferta (o su texto), sube tu CV si quieres y mira trabajar al equipo en directo: qué herramienta usa cada
agente, qué rechaza el guardarraíl y cuánto cuesta (segundos, llamadas y tokens). Descarga tu CV en Word y revísalo:
**el guardarraíl comprueba cifras y herramientas, no el tono; el CV lo firmas tú**. Sin clave o sin cuota, la oferta de
ejemplo funciona con respuestas grabadas.

## Cómo está hecho

```
sesion2/
├─ candidatura/            el paquete del agente
│  ├─ web.py               leer la web con educación: robots.txt, una petición identificada, muros y grabaciones
│  ├─ oferta.py            paso 1 · JSON de Workday, JSON-LD, microdatos o texto → Oferta (Pydantic)
│  ├─ carrera.py           paso 2 · tu perfil, el plan del máster, competencias, guardarraíl, Word y cobertura
│  ├─ investigacion.py     paso 3 · Wikipedia y Wikidata, Bing Noticias y la web de la empresa
│  ├─ agentes.py           instrucciones y esquemas del editor, el investigador y el coach
│  ├─ flujo.py             el flujo completo, con eventos en directo
│  └─ piezas.py            tus piezas de los labs (mis_piezas/) o las de referencia
├─ servidor_mcp_carrera.py el servidor MCP «mi-carrera»
├─ webapp.py · web/        la webapp (FastAPI + una página HTML)
├─ datos/plan_mucdia.json  el plan de estudios oficial del MUCD-IA
└─ ejemplo/                el perfil ficticio de Lucía (y tus plantillas)
```

**¿Por qué no «buscar en Google» desde el modelo?** La búsqueda integrada de Gemini no entra en el plan gratuito, y
Google Noticias prohíbe en su robots.txt que la lean programas. El agente usa fuentes gratuitas que sí lo permiten:
la API de Wikipedia y Wikidata (con sus condiciones de uso: identificarse y pocas peticiones), el RSS de Bing Noticias
y la web oficial de la empresa si su robots.txt lo permite.

## Para saber más

- Model Context Protocol: <https://modelcontextprotocol.io>
- Robots Exclusion Protocol (RFC 9309): <https://www.rfc-editor.org/rfc/rfc9309>
- schema.org `JobPosting`: <https://schema.org/JobPosting>
- *Building effective agents* (Anthropic, 2024): flujos frente a agentes <https://www.anthropic.com/engineering/building-effective-agents>
- Microsoft Agent Framework: <https://learn.microsoft.com/agent-framework/>
