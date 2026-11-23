# Puesta en marcha

Necesitas **dos cosas**: una cuenta de GitHub (para el Codespace) y una clave gratuita de Gemini (para el modelo).
Hazlo antes de la sesión: son unos 15 minutos.

## 1. Clave gratuita de Gemini (Google AI Studio)

1. Entra en <https://aistudio.google.com> con una **cuenta personal de Google** (hay que ser mayor de 18 años).
   Las cuentas de empresa o universidad a veces tienen AI Studio desactivado: si te pasa, usa tu cuenta personal.
2. Acepta los términos de uso.
3. Ve a **Get API key** → **Create API key**. Si te pide un proyecto, crea uno nuevo (por ejemplo, `cunef-agentes`).
4. Comprueba que el proyecto está en el **plan gratuito** (*Free*). Si aparece un plan de pago, ese proyecto tiene
   facturación activada: crea otro proyecto sin facturación. Así es imposible que te cobren nada.
5. Copia la clave (empieza por `AIza…`) y guárdala en un lugar seguro, como tu gestor de contraseñas.

> **Sobre tus datos:** en el Espacio Económico Europeo, el uso gratuito de la API de Gemini se rige por las mismas
> condiciones de datos que el plan de pago: Google no usa tus peticiones para entrenar sus modelos. Aun así, envía
> solo lo necesario: trabajarás con tu CV, pero sin teléfono, dirección ni DNI.

**Límites del plan gratuito** (pueden cambiar): unas 10 llamadas por minuto y unas 500 al día por cada modelo. La
cuota diaria se reinicia a las 09:00 (hora de Madrid). Los tres labs gastan unas 25 llamadas, y cada candidatura en la
webapp, unas 12 más.

## 2. Abre el Codespace con tu clave

**Opción A (recomendada).** Pulsa el botón **Open in GitHub Codespaces** del [README](../README.md). En la
pantalla *Create codespace* verás el campo **GEMINI_API_KEY**: pega tu clave y pulsa **Create new codespace**. GitHub
la guarda como *secret* personal, cifrado, y la inyecta como variable de entorno solo en tus Codespaces de este
repositorio.

**Opción B.** Si ya has creado el Codespace sin la clave, ve a <https://github.com/settings/codespaces> →
**Codespaces secrets** → **New secret** (o edita el que ya tengas):

- Nombre: `GEMINI_API_KEY`
- Valor: tu clave
- Repository access: `gerardsl/cunef-ia-agentica` (o tu *fork*)

Después recarga el Codespace (GitHub te lo ofrecerá) o detenlo y vuelve a abrirlo.

**Opción C (último recurso).** En el Codespace, copia `.env.example` como `.env` y pega la clave en la línea
`GEMINI_API_KEY=`. El fichero `.env` está en `.gitignore`, así que no se sube a GitHub.

La primera vez, el Codespace tarda unos minutos en instalar las dependencias. Al terminar verás en el terminal
`✅ Clave configurada…` y `✅ Paquetes del curso instalados`. Si VS Code abre en *Restricted Mode* y pregunta
*Do you trust the authors of the files in this folder?*, pulsa **Trust Folder & Continue**: sin eso no arrancan ni el
terminal ni los notebooks.

## 3. Comprueba que todo funciona

En un terminal (menú ☰ → *Terminal* → *New Terminal*):

```bash
python -c "import mucdia; mucdia.comprobar()"
```

Debes ver tres ✅: la clave, los paquetes y la respuesta del modelo. Después abre
[`sesion2/lab2a_leer_la_oferta.ipynb`](../sesion2/lab2a_leer_la_oferta.ipynb) y elige el kernel: **Select Kernel** →
**Python Environments** → **Python 3.12** (`/usr/local/bin/python`; no *Create Python Environment*, aunque ponga
*Recommended*).

## Buenas prácticas con el Codespace

- **Detenlo al terminar**: **F1** → *Codespaces: Stop Current Codespace* (o en <https://github.com/codespaces>, ⋯ →
  *Stop codespace*). Si no, se detiene solo tras 30 minutos sin uso. Así no gastas tus horas gratuitas.
- **Tus cambios se guardan en el Codespace**, aunque lo detengas: no hace falta hacer *commit*. Si quieres llevarte
  un notebook, descárgalo (clic derecho sobre el fichero → *Download*) o guárdalo en un *fork* tuyo.
- **Materiales nuevos** (las soluciones, el día después de la clase): en un terminal, `git pull`.

## Alternativa: en tu ordenador (sin Codespaces)

Necesitas Python 3.12, Git y VS Code con las extensiones de Python y Jupyter.

```bash
git clone https://github.com/gerardsl/cunef-ia-agentica.git
cd cunef-ia-agentica
python -m venv .venv
# Windows: .venv\Scripts\activate      macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env        # Windows: copy .env.example .env   → y pega tu clave en .env
python -c "import mucdia; mucdia.comprobar()"
```

En VS Code, elige el intérprete `.venv` como kernel de los notebooks. En Windows con procesador ARM, si algún paquete
no se instala, usa un Python 3.12 de 64 bits x64. La webapp se lanza con el entorno activado
(`python sesion2/webapp.py`): si `python` no es el del entorno, verás `No module named 'fastapi'`.

## ¿Y si no puedo tener clave?

Puedes seguir la sesión con las respuestas grabadas (`mucdia.usar_modo("replay")`) y trabajando con tu equipo en el
portátil de otra persona. Cada uno usa su propia clave: **nunca compartáis claves**.

## Otros proveedores (opcional)

El paquete `mucdia` funciona con cualquier servicio compatible con la API de OpenAI (Azure OpenAI, OpenAI, Ollama,
LM Studio…). En `.env`:

```
PROVEEDOR=openai
OPENAI_API_KEY=...
OPENAI_BASE_URL=http://localhost:11434/v1     # p. ej. Ollama
MODELO=llama3.2
```

Los resultados y las herramientas pueden variar según el modelo. La sesión está probada con `gemini-3.5-flash-lite`.
