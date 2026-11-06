# Agent Canvas

Una página para diseñar un agente **antes** de programarlo. Rellenadlo en equipo al final de la sesión 1 (10
minutos) y revisadlo en las sesiones 2 y 3. Copiad este fichero (por ejemplo, `docs/canvas_equipo07.md`) o
rellenadlo en papel.

**Equipo:** … · **Área:** Finanzas · Marketing · Operaciones y Clientes · Documentación y Compliance

| # | Bloque | Preguntas guía | Vuestra respuesta |
|---|---|---|---|
| 1 | **Problema** | ¿Qué tarea resuelve? ¿Para quién? ¿Con qué frecuencia? ¿Cómo se hace hoy? | |
| 2 | **Éxito** | ¿Cómo sabréis que funciona? Un KPI medible (tiempo, errores, satisfacción, €). | |
| 3 | **Herramientas** | ¿Qué datos necesita leer? ¿Qué acciones puede ejecutar? ¿Alguna ya existe en `mucdia.negocio`? | |
| 4 | **Autonomía** | ¿Qué hace solo? ¿Qué necesita aprobación humana? ¿Qué no debe hacer nunca? | |
| 5 | **Riesgos** | ¿Qué puede salir mal (datos erróneos, fuga de información, acciones indebidas)? ¿A quién afecta? | |
| 6 | **Supervisión** | ¿Quién revisa sus resultados? ¿Cuándo interviene una persona? ¿Qué se registra? | |
| 7 | **Coste y valor** | Coste por tarea frente al tiempo ahorrado (ver la calculadora de abajo). | |
| 8 | **Regulación** | ¿Interactúa con personas (debe decir que es una IA)? ¿Toma decisiones sobre personas (empleo, crédito…)? ¿Trata datos personales? | |

## ¿Workflow o agente?

Antes de seguir, comprobad que de verdad necesitáis un agente:

- Si los pasos son **siempre los mismos**, basta con un *workflow* (o con un script): es más barato, rápido y
  predecible.
- Un agente compensa cuando **el camino depende de lo que va encontrando**: elegir qué datos mirar, en qué orden y
  cuándo parar.
- Cuanta más autonomía, más evaluación, supervisión y controles necesitará (lo veremos en la sesión 3).

## Calculadora de ROI

```
Valor mensual  = tareas al mes × minutos ahorrados por tarea / 60 × coste por hora de la persona
Coste del modelo = tareas al mes × llamadas por tarea × coste por llamada
Coste total    = coste del modelo + desarrollo e integración (prorrateados) + supervisión + mantenimiento
ROI            = (valor mensual − coste total mensual) / coste total mensual
```

**Ejemplo (sesión 1):** 400 informes al mes × 20 minutos ahorrados × 35 €/h ≈ **4.700 € al mes** de valor. El
modelo cuesta unos 0,003 $ por pregunta (≈ 1,2 $ al mes). Lo caro no es el modelo, sino construirlo, supervisarlo
y equivocarse.

Usad `mucdia.uso()` después de probar vuestro agente: os da las llamadas y los tokens reales y lo que costaría en
el plan de pago.

## Lista de comprobación antes de "ponerlo en producción" (sesión 3)

- [ ] Tiene un conjunto de casos de prueba con el resultado esperado y una puntuación mínima.
- [ ] Solo tiene las herramientas y los permisos imprescindibles (mínimo privilegio).
- [ ] Las acciones con impacto (enviar, pagar, borrar, descontar) requieren aprobación humana.
- [ ] El contenido externo (emails, reseñas, webs, documentos) se trata como no confiable.
- [ ] No hay secretos en las instrucciones.
- [ ] Se registran trazas, coste y latencia (observabilidad).
- [ ] Se informa a las personas de que hablan con una IA (art. 50 del AI Act), si aplica.
- [ ] Alguien es responsable del agente y sabe cuándo apagarlo.
