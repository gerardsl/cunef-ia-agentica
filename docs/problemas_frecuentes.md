# Problemas frecuentes

Busca el mensaje que ves (o algo parecido). Si no se resuelve, avisa en clase: casi todo tiene arreglo en un minuto.

## Clave y cuota

**`🔑 No hay una clave válida para el modelo…`**
La variable `GEMINI_API_KEY` no llega al Codespace o la clave no es válida.
1. Comprueba que existe sin mostrarla entera: en un terminal, `echo ${GEMINI_API_KEY:0:6}` (debe salir `AIza…`).
2. Si no sale nada: revisa el *secret* en <https://github.com/settings/codespaces> (nombre exacto `GEMINI_API_KEY`
   y acceso a este repositorio, `gerardsl/cunef-ia-agentica`; si lo creaste para otro, añádelo en
   *Repository access*) y **recarga el Codespace**. Los *secrets* solo se cargan al arrancar.
3. Si sale pero falla: genera una clave nueva en AI Studio y sustitúyela.
4. Después, en el notebook: **Restart** del kernel y vuelve a ejecutar.

**`⏳ Límite de 9 llamadas/minuto: espero N s…`**
Es normal: el plan gratuito permite unas 10 llamadas por minuto y el paquete espera solo. Un agente que usa tres
herramientas hace cuatro o cinco llamadas al modelo.

**`⛔ Has agotado la cuota GRATUITA diaria…`**
Se reinicia a las 09:00 (hora de Madrid). Mientras tanto:
- sigue en el portátil de otra persona de tu equipo (con su clave, nunca compartáis claves);
- cambia de modelo, porque cada uno tiene su propia cuota: `mucdia.usar_modelo("gemini-3.1-flash-lite")` y vuelve a
  crear el cliente (`cliente = mucdia.cliente()`);
- o usa las respuestas grabadas: `mucdia.usar_modo("replay")`.

**`⚠️ Sin cuota o sin clave: continúo con respuestas grabadas.`** /
**`🎞️ Usando respuestas GRABADAS (modo replay)`**
No es un error: ves lo que obtuvo el profesor al ejecutar ese mismo paso. Para volver al modelo en vivo:
`mucdia.usar_modo("auto")`.

**`SinGrabacion: No hay respuesta grabada para este paso`**
Solo hay grabaciones de los pasos guiados tal y como vienen en el notebook. Si has cambiado la pregunta, las
instrucciones o las herramientas, ese paso necesita el modelo en vivo (con cuota).

**`⏳ El modelo está saturado o no responde; reintento en N s…` / `503 UNAVAILABLE`**
Saturación temporal de Google (pasa en los picos de demanda). El paquete reintenta solo durante unos 45 segundos; si
persiste, espera un par de minutos, cambia de modelo (`mucdia.usar_modelo("gemini-3.1-flash-lite")`) o sigue con
respuestas grabadas (`mucdia.usar_modo("replay")`).

## Notebooks y Codespace

**VS Code dice «Restricted Mode» o pregunta «Do you trust the authors of the files in this folder?».**
Pasa en los Codespaces nuevos. Pulsa **Trust Folder & Continue** (en español, *Confiar en la carpeta y continuar*):
el repositorio es el del curso. Sin eso no arrancan ni el terminal ni los notebooks.

**El notebook pide un kernel o no ejecuta nada.**
**Select Kernel** (arriba a la derecha) → **Python Environments** → **Python 3.12** (`/usr/local/bin/python`). No
elijas **Create Python Environment**, aunque ponga *Recommended*: crea un entorno vacío, sin las librerías del curso.
Tampoco el Python 3.11 (`/usr/bin/python3`). Si ya creaste un `.venv`, mira la pregunta siguiente.

**`pip` dice `Can not perform a '--user' install. User site-packages are not visible in this virtualenv`, el
terminal empieza por `(.venv)` o `mucdia.comprobar()` avisa de un `.venv`.**
VS Code ha creado un entorno virtual `.venv` (con *Create Python Environment*) y lo usa en lugar del Python del
Codespace, que es el que tiene todas las librerías. Ese `.venv` sobra y no tiene nada tuyo. En un terminal:

```bash
rm -rf .venv
```

Después, en cada notebook, **Select Kernel → Python Environments → Python 3.12** (`/usr/local/bin/python`); en
**Ctrl+Shift+P → Python: Select Interpreter**, el mismo Python 3.12; y cierra los terminales (🗑) y abre uno nuevo.
No hace falta ningún `pip install`: el Codespace ya lo trae todo.

**`ModuleNotFoundError: No module named 'mucdia'` (o `agent_framework`, `bs4`, `docx` o `pypdf`), o
`mucdia.comprobar()` avisa de que faltan paquetes.**
Casi siempre es el kernel: comprueba que sea **Python 3.12** (`/usr/local/bin/python`) y no un `.venv` (ver arriba).
Si lo es, la instalación inicial no terminó. En un terminal, desde la raíz del repositorio:
`pip install --user -r requirements.txt && pip install --user -e .` y reinicia el kernel.

**`SyntaxError: 'await' outside function` al copiar código a un `.py`.**
En los notebooks se puede usar `await` directamente; en un script, mete el código en `async def main()` y ejecútalo
con `asyncio.run(main())`.

**El agente se inventa cifras o no usa las herramientas.**
Revisa las instrucciones ("usa las herramientas y no inventes datos"), que la herramienta esté en `tools=[...]` y su
*docstring*: el modelo decide qué herramienta usar solo a partir del nombre, la descripción y los parámetros.

## Tu agente de candidaturas

**El servidor MCP no arranca o se queda colgado.**
Pruébalo solo: `python sesion2/servidor_mcp_carrera.py` (debe quedarse esperando sin errores; sal con **Ctrl+C**).
En el notebook, usa siempre `mucdia.servidor_mcp()`, que ya trae la configuración correcta. Sus errores quedan en
`~/.mucdia/mcp_servidor.log`.

**«No leo esta página: prohibido por robots.txt» (LinkedIn), «nos deniega el acceso (HTTP 403)» (Indeed) o
«la web me enseña un muro» (InfoJobs).**
No es un fallo: esas webs no dejan que las lean programas y el agente lo respeta. Abre la oferta en tu navegador,
copia su texto y pégalo (en la webapp, en «¿La web no deja leerla? Pega aquí su texto»; en el lab 2a, en
`TEXTO_OFERTA`). Si la oferta está también en la web de empleo de la empresa, prueba con ese enlace.

**El agente usa el CV de ejemplo (Lucía) y no el mío.**
Tu CV debe estar en `sesion2/mi_perfil/cv.md`. Súbelo desde la webapp (PDF, Word o Markdown) o, en el lab 2b,
`C.carrera.importar_cv("sesion2/mi_perfil/mi_cv.pdf")`. Revisa el resultado: un PDF a dos columnas se extrae
desordenado (si pasa, pega el texto a mano en `cv.md`). Con respuestas grabadas (sin cuota) siempre se usa el ejemplo.

**`guardar_cv` devuelve «ERROR: no lo guardo…».**
Es el guardarraíl: el CV nuevo tenía una cifra o una herramienta que no consta en tu CV, tu grado (`grado.md`) ni tu
máster (`master.md`). El agente debe corregirlo solo; si de verdad sabes usar esa herramienta, añádela a tu perfil.

**La webapp no se abre o dice `address already in use`.**
Lánzala con `python sesion2/webapp.py` en un terminal y abre la pestaña **Ports** (*Puertos*): en la fila
«Tu agente de candidaturas» (puerto **8000**), pulsa el globo 🌐. No se abre sola. Si el puerto está ocupado (otra
webapp abierta), ciérrala con **Ctrl+C** o usa `python sesion2/webapp.py --puerto 8001`.

**La página dice «Esta página necesita su servidor» (no sube el CV ni arranca la oferta de ejemplo).**
Has abierto `sesion2/web/index.html` como fichero (o desde otro servidor): esa página es solo la cara de la webapp.
Arráncala con `python sesion2/webapp.py`, con el entorno del curso, y entra en <http://127.0.0.1:8000>.

## Git y el Codespace

**Mi Codespace de antes no se actualiza (`git pull` dice `refusing to merge unrelated histories` o no encuentra el
repositorio).**
Este repositorio es nuevo: crea un Codespace nuevo con el botón del [README](../README.md). Si quieres, borra el
antiguo en <https://github.com/codespaces> (⋯ → *Delete*) para no gastar espacio.

**No puedo crear el Codespace.**
El repositorio es público, pero los Codespaces necesitan una cuenta de GitHub: inicia sesión y ábrelo desde
<https://github.com/gerardsl/cunef-ia-agentica>. Si GitHub dice que has agotado tus horas gratuitas, sigue en el
portátil de otra persona de tu equipo (cada uno con su clave) o en tu ordenador ([setup](setup.md)).

**`git pull` dice que tus cambios locales se sobrescribirían.**
Guarda tu versión con otro nombre, descarta los cambios del original y vuelve a intentarlo:

```bash
cp sesion2/lab2a_leer_la_oferta.ipynb sesion2/mi_lab2a.ipynb
git checkout -- sesion2/lab2a_leer_la_oferta.ipynb
git pull
```

**He borrado o roto un notebook.**
`git checkout -- ruta/del/notebook.ipynb` lo deja como estaba en el repositorio.

**He tocado varios notebooks y `git pull` no me deja actualizar.**
`git stash` aparta todos tus cambios de una vez (los recuperas con `git stash pop`); después, `git pull`.

## En tu ordenador (sin Codespaces)

- **Windows: `python` no se reconoce.** Prueba con `py -3.12`, o instala Python 3.12 desde python.org marcando
  *Add python.exe to PATH*.
- **Error al instalar paquetes en Windows ARM.** Usa un Python 3.12 x64 (de 64 bits para Intel/AMD): se ejecuta en
  emulación sin problemas.
- **Error de red o de proxy al instalar.** Prueba desde otra red (algunas redes corporativas bloquean PyPI) o usa el
  Codespace.
