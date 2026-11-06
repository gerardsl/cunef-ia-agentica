# Sesión 1 · Del LLM al agente

**Miércoles 18 de noviembre de 2026 · 19:30-21:00**

Hoy entenderás qué hay dentro de un agente programando el bucle a mano y después harás lo mismo, y más, con un
framework profesional.

| Lab | Notebook | Tiempo | Qué aprenderás |
|---|---|---|---|
| **1a** | [`lab1a_bucle_agentico.ipynb`](lab1a_bucle_agentico.ipynb) | 20' | *Tool calling*, el bucle razonar → actuar → observar y por qué puede fallar |
| **1b** | [`lab1b_primer_agente_maf.ipynb`](lab1b_primer_agente_maf.ipynb) | 25' | Microsoft Agent Framework: instrucciones, herramientas propias, memoria, salida estructurada y DevUI |

Las celdas marcadas con ✏️ tienen huecos (`TODO`) para completar. Si te atascas más de 3 minutos, pregunta a tu
equipo o al profesor: lo importante es entender el bucle, no escribir cada línea.

## Lab 1a · Un agente desde cero

Sin frameworks: el modelo, tres herramientas en Python sobre las ventas de MUCDIA y un bucle de unas 20 líneas.

1. Un modelo sin herramientas (¿se inventa la cifra?).
2. Las herramientas son funciones normales.
3. Describirlas al modelo con JSON Schema ✏️.
4. El modelo *pide* una herramienta… pero no la ejecuta.
5. El bucle agéntico ✏️.
6. Rómpelo: una pregunta ambigua, una herramienta que falla, una descripción engañosa y un solo paso para pensar.

## Lab 1b · Tu primer agente con Microsoft Agent Framework

1. Un agente en 10 líneas (y su traza).
2. Las instrucciones definen el "puesto de trabajo" ✏️.
3. Crea una herramienta para el área de tu equipo ✏️.
4. Memoria de conversación con sesiones.
5. Salida estructurada (un informe con campos fijos).
6. Mira dentro del agente con **DevUI**:

   ```bash
   python sesion1/app_devui.py
   ```

   Abre la pestaña **PUERTOS** → **8080** → 🌐. A la izquierda conversas; a la derecha ves cada llamada al modelo y
   a las herramientas.

## Reto de equipo y Agent Canvas

En el lab 1b, cada equipo crea una herramienta para su área (Finanzas, Marketing, Operaciones y Clientes, o
Documentación y Compliance). En el cierre de la sesión empezaréis el [Agent Canvas](../docs/agent_canvas.md) del
agente de vuestra área (5 minutos) y lo terminaréis en casa: en la sesión 2 lo conectaréis a datos y documentos.

## Para saber más

- *Building effective agents* (Anthropic): <https://www.anthropic.com/engineering/building-effective-agents>
- Documentación de Microsoft Agent Framework: <https://learn.microsoft.com/agent-framework/>
- Llamadas a funciones con Gemini: <https://ai.google.dev/gemini-api/docs/function-calling>
