# Problemas frecuentes

Busca el mensaje que ves (o algo parecido). Si no se resuelve, avisa en clase: casi todo tiene arreglo en un minuto.

## Clave y cuota

**`🔑 No hay una clave válida para el modelo…`**
La variable `GEMINI_API_KEY` no llega al Codespace o la clave no es válida.
1. Comprueba que existe sin mostrarla entera: en un terminal, `echo ${GEMINI_API_KEY:0:6}` (debe salir `AIza…`).
2. Si no sale nada: revisa el *secret* en <https://github.com/settings/codespaces> (nombre exacto `GEMINI_API_KEY`
   y acceso a este repositorio) y **recarga el Codespace**. Los *secrets* solo se cargan al arrancar.
3. Si sale pero falla: genera una clave nueva en AI Studio y sustitúyela.
4. Después, en el notebook: **Restart** del kernel y vuelve a ejecutar.

**`⏳ Límite de 9 llamadas/minuto: espero N s…`**
Es normal: el plan gratuito permite unas 10 llamadas por minuto y el paquete espera solo. Un agente que usa tres
herramientas hace cuatro o cinco llamadas al modelo.

**`⛔ Has agotado la cuota GRATUITA diaria…`**
Se reinicia a las 09:00 (hora de Madrid). Mientras tanto:
- sigue en el portátil de otra persona de tu equipo (con su clave, nunca compartáis claves);
- cambia de modelo, porque cada uno tiene su propia cuota: `almansa.usar_modelo("gemini-3.1-flash-lite")` y vuelve a
  crear el cliente (`cliente = almansa.cliente()`);
- o usa las respuestas grabadas: `almansa.usar_modo("replay")`.

**`⚠️ Sin cuota o sin clave: continúo con respuestas grabadas.`** /
**`🎞️ Usando respuestas GRABADAS (modo replay)`**
No es un error: ves lo que obtuvo el profesor al ejecutar ese mismo paso. Para volver al modelo en vivo:
`almansa.usar_modo("auto")`.

**`SinGrabacion: No hay respuesta grabada para este paso`**
Solo hay grabaciones de los pasos guiados tal y como vienen en el notebook. Si has cambiado la pregunta, las
instrucciones o las herramientas, ese paso necesita el modelo en vivo (con cuota).

**`503 UNAVAILABLE` / `The model is overloaded`**
Saturación temporal de Google. El paquete reintenta solo varias veces; si persiste, espera un minuto o cambia de
modelo.

## Notebooks y Codespace

**El notebook pide un kernel o no ejecuta nada.**
**Select Kernel** (arriba a la derecha) → **Python Environments** → **Python 3.12** (`/usr/local/bin/python`).

**`ModuleNotFoundError: No module named 'almansa'` (o `agent_framework`).**
La instalación inicial no terminó. En un terminal, desde la raíz del repositorio:
`pip install --user -r requirements.txt && pip install --user -e .` y reinicia el kernel.

**`SyntaxError: 'await' outside function` al copiar código a un `.py`.**
En los notebooks se puede usar `await` directamente; en un script, mete el código en `async def main()` y ejecútalo
con `asyncio.run(main())`.

**DevUI no se abre.**
Lanza `python sesion1/app_devui.py` en un terminal y espera al mensaje de que el servidor está listo. Abre la pestaña
**PUERTOS** (*Ports*), busca el **8080** y pulsa el globo 🌐. Si dice `address already in use`, ya tienes otra DevUI
abierta: ciérrala con **Ctrl+C** en su terminal (o `pkill -f devui`).

**Lab 1a: `400 … thought_signature` o `Function call is missing a thought_signature`.**
Al guardar el mensaje del modelo en la conversación, añádelo **tal cual** (`mensajes.append(mensaje)`). Si lo
reconstruyes a mano se pierde la "firma de razonamiento" que Gemini 3 necesita para continuar.

**El agente se inventa cifras o no usa las herramientas.**
Revisa las instrucciones ("usa las herramientas y no inventes datos"), que la herramienta esté en `tools=[...]` y su
*docstring*: el modelo decide qué herramienta usar solo a partir del nombre, la descripción y los parámetros.

**Sesión 2 · el servidor MCP no arranca o se queda colgado.**
Pruébalo solo: `python sesion2/servidor_mcp_almansa.py` (debe quedarse esperando sin errores; sal con **Ctrl+C**).
En el notebook, usa siempre `almansa.servidor_mcp()`, que ya trae la configuración correcta.

## Git y materiales nuevos

**¿Cómo consigo los materiales de la sesión siguiente?**
En un terminal: `git pull`. Si trabajas en un *fork*, pulsa antes **Sync fork** en GitHub.

**`git pull` dice que tus cambios locales se sobrescribirían.**
Guarda tu versión con otro nombre, descarta los cambios del original y vuelve a intentarlo:

```bash
cp sesion1/lab1a_bucle_agentico.ipynb sesion1/mi_lab1a.ipynb
git checkout -- sesion1/lab1a_bucle_agentico.ipynb
git pull
```

**He borrado o roto un notebook.**
`git checkout -- ruta/del/notebook.ipynb` lo deja como estaba en el repositorio.

## En tu ordenador (sin Codespaces)

- **Windows: `python` no se reconoce.** Prueba con `py -3.12`, o instala Python 3.12 desde python.org marcando
  *Add python.exe to PATH*.
- **Error al instalar paquetes en Windows ARM.** Usa un Python 3.12 x64 (de 64 bits para Intel/AMD): se ejecuta en
  emulación sin problemas.
- **Error de red o de proxy al instalar.** Prueba desde otra red (algunas redes corporativas bloquean PyPI) o usa el
  Codespace.
