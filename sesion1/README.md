# Sesión 1 · Del LLM al agente

**Miércoles 18 de noviembre de 2026 · 19:30-21:00**

Hoy abrirás un agente por dentro: lo programarás a mano, lo probarás sin gastar cuota con un modelo simulado y lo
medirás (tokens, coste, variabilidad). Después harás lo mismo, y más, con un framework profesional, incluido un agente
que escribe y ejecuta su propio código. Cada lab termina con un número.

| Lab | Notebook | Tiempo | Qué aprenderás |
|---|---|---|---|
| **1a** | [`lab1a_bucle_agentico.ipynb`](lab1a_bucle_agentico.ipynb) | 22' | Siguiente token y temperatura, el JSON Schema de una herramienta, el bucle agéntico con telemetría y cómo se rompe |
| **1b** | [`lab1b_primer_agente_maf.ipynb`](lab1b_primer_agente_maf.ipynb) | 24' | Microsoft Agent Framework: instrucciones, tu herramienta, un agente que programa, salida estructurada, memoria y DevUI |

Las celdas marcadas con ✏️ son tuyas y tienen una **comprobación automática**. Si llevas más de 3 minutos atascado:

```python
mucdia.lab.pista("bucle")      # una pista: "esquema", "bucle" o "codigo"
mucdia.lab.solucion("bucle")   # la solución, para seguir adelante
```

Lo importante es entender y medir el agente, no escribir cada línea. Los apartados ⭐ son opcionales, para quien vaya
rápido.

## Lab 1a · Un agente desde cero

Sin frameworks: el modelo, tres herramientas en Python sobre las ventas de MUCDIA y un bucle de unas 20 líneas.

1. Un modelo sin herramientas… y la temperatura (¿da siempre la misma respuesta?).
2. Las herramientas son funciones normales.
3. ✏️ De función a herramienta: genera el JSON Schema a partir de la firma, como hace un framework.
4. El modelo *pide* una herramienta (no la ejecuta)… y cada descripción cuesta tokens.
5. ✏️ El bucle agéntico con telemetría, probado primero con un modelo simulado (sin gastar cuota).
6. Mide tu agente: tokens por paso y coste por pregunta.
7. Rómpelo: una pregunta ambigua, una herramienta que falla, una descripción engañosa y un solo paso para pensar.

⭐ ¿Da siempre la misma respuesta? Repite 5 veces una pregunta y compara.

## Lab 1b · Agent Framework y un agente que programa

1. El mismo agente en 10 líneas, con su telemetría (`mucdia.traza_df()`).
2. ✏️ El puesto de trabajo (instrucciones) y una herramienta SQL para el área de tu equipo.
3. ✏️ Un agente que escribe y ejecuta código Python para responder lo que las herramientas fijas no saben.
   ¿Revisarías su código antes de llevar la cifra a un comité?
4. Salida estructurada con Pydantic.
5. Memoria con sesiones y **DevUI**:

   ```bash
   python sesion1/app_devui.py
   ```

   Abre la pestaña **PUERTOS** → **8080** → 🌐. A la izquierda conversas; a la derecha ves cada llamada al modelo y
   a las herramientas.

⭐ Pide al agente que programa un modelo predictivo: ¿lo valida bien?

> ⚠️ `mucdia.ejecutar_codigo()` ejecuta el código del agente en un proceso aparte, con límite de tiempo, sin tus claves
> y con la base de datos en solo lectura. **No es un sandbox de producción**: úsalo solo en tu Codespace y con tus
> propias preguntas. En la sesión 3 veremos por qué.

## ¿Creaste tu Codespace antes del 16 de noviembre?

Actualízalo antes de clase. En un terminal, desde la raíz del repositorio:

```bash
git stash                                # solo si has tocado algún notebook: aparta tus cambios
git pull
pip install --user -r requirements.txt   # paquetes nuevos (scikit-learn, fastembed)
```

Después, `00_comprobacion.ipynb` debe salir en verde.

## Reto de equipo y Agent Canvas

Para casa: el [Agent Canvas](../docs/agent_canvas.md) del agente de vuestra área (Finanzas, Marketing, Operaciones y
Clientes, o Documentación y Compliance), con el coste por pregunta que habéis medido hoy. En la sesión 2 lo
conectaréis a datos, a vuestros modelos y a documentos.

## Para saber más

- *Building effective agents* (Anthropic): <https://www.anthropic.com/engineering/building-effective-agents>
- *ReAct: Synergizing Reasoning and Acting in Language Models* (Yao et al.): <https://arxiv.org/abs/2210.03629>
- *Executable Code Actions Elicit Better LLM Agents* (CodeAct, Wang et al.): <https://arxiv.org/abs/2402.01030>
- *Measuring AI Ability to Complete Long Tasks* (METR): <https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/>
- Documentación de Microsoft Agent Framework: <https://learn.microsoft.com/agent-framework/>
- Llamadas a funciones con Gemini: <https://ai.google.dev/gemini-api/docs/function-calling>
