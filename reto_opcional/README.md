# Reto opcional: el agente de tu equipo, de verdad

Opcional y no evaluable. Si te ha picado el gusanillo, aquí tienes un reto para llevar el agente de tu equipo un poco
más lejos. Puedes hacerlo solo o con tu equipo, en cualquier momento después de la sesión 3.

## La misión

El comité de dirección de Almansa quiere un **agente investigador** que responda preguntas abiertas de negocio
combinando datos y documentos, con cifras, fuentes y recomendaciones. Elige **dos** de estos misterios:

1. ¿Por qué cayeron las ventas de Hogar en Andalucía en el tercer trimestre de 2026?
2. ¿Qué producto preocupa más por sus reseñas y devoluciones en 2026? ¿Desde cuándo y qué habría que hacer?
3. ¿Qué pasó con las incidencias de envío en la campaña de Navidad de 2025? ¿Qué cambiarías para el Black Friday de
   2026?
4. ¿Qué campaña de marketing de 2026 tuvo peor retorno? ¿Merece la pena repetirla?
5. ¿Qué peso tiene ya la app en las ventas online y cómo ha evolucionado? ¿Qué implica para el marketing?

Contrasta lo que diga tu agente con tus propias consultas SQL: ¿ha acertado? ¿Ha citado documentos vigentes?

## Niveles

**🥉 Bronce: un buen agente.**
- Parte del agente de tu equipo (lab 1b o lab 2c) y añade al menos **una herramienta propia** bien descrita.
- Escribe **5 preguntas de prueba con su respuesta esperada** (en un dict o un CSV) y mide cuántas acierta.

**🥈 Plata: un agente fiable.**
- Convierte las preguntas de prueba en una **evaluación automática** (inspírate en `sesion3/evaluacion.py`):
  comprobaciones deterministas (¿usó la herramienta correcta? ¿aparece la cifra?) y, si quieres, un modelo como juez.
- Añade **una acción con aprobación humana** (por ejemplo, "programar una campaña" simulada) y prueba que no se
  ejecuta sin permiso.
- Comprueba que una reseña o un ticket con instrucciones maliciosas no consigue manipularlo.

**🥇 Oro: un agente listo para enseñar.**
- Compara **dos orquestaciones** (por ejemplo, un único agente frente al equipo secuencial, o *handoff* o
  *magentic*) en calidad, número de llamadas y coste (`almansa.uso()`).
- Publícalo en DevUI o expón sus herramientas como un servidor MCP y úsalo desde GitHub Copilot.
- Rellena el [Agent Canvas](../docs/agent_canvas.md) final con lo que has medido: ¿lo pondrías en producción?

## Entrega (si quieres feedback)

Haz un *fork* del repositorio, trabaja en una carpeta `reto_opcional/<tu_equipo>/` con un `README.md` corto
(qué has construido, cómo se ejecuta y tus resultados) y envía el enlace por LinkedIn
([linkedin.com/in/gerardsl](https://www.linkedin.com/in/gerardsl)).

**Recuerda:** nada de claves en el código ni en el repositorio, y solo datos sintéticos.
