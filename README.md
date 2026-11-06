# IA agéntica: del LLM al agente en producción

Materiales prácticos de las masterclasses de **IA agéntica** del Máster Universitario en Ciencia de Datos e IA
(MUCDIA) de **CUNEF Universidad**, curso 2026-27.

[![Abrir en GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/gerardsl/cunef-ia-agentica?quickstart=1)

| Sesión | Fecha | Qué construimos |
|---|---|---|
| **1 · Del LLM al agente** | miércoles 18-nov-2026 · 19:30-21:00 | Un bucle agéntico desde cero y tu primer agente con Microsoft Agent Framework |
| **2 · Agentes conectados** | miércoles 25-nov-2026 · 19:30-21:00 | Un servidor MCP, RAG agéntico sobre documentos internos y un equipo de agentes |
| **3 · De la demo a producción** | miércoles 2-dic-2026 · 19:30-21:00 | Evaluar, atacar (*red team*), blindar… y analizar el agente con el AI Act |

Los materiales de cada sesión se publican poco antes de la clase; las soluciones y las diapositivas (PDF), al día
siguiente, en `soluciones/` y `diapositivas/`.

## El caso: MUCDIA S.A.

Una cadena **ficticia** de 8 tiendas y venta online (sí, se llama como vuestro máster) con dos años de actividad
(enero de 2025 a octubre de 2026): 147.115 pedidos, 4.200 clientes, 108 productos, campañas, inventario, tickets de
soporte, reseñas, cuentas mensuales y 13 documentos internos (políticas, actas, contratos…). **Todos los datos son
sintéticos.** Detalles en [data/README.md](data/README.md).

Durante las tres sesiones seréis su equipo de analistas: primero con un agente, después con un equipo de agentes
conectado a sus datos y, al final, decidiendo si eso puede llegar a producción.

## Antes de la primera sesión (15 minutos)

1. **Cuenta de GitHub** (gratuita). Con ella tienes horas de Codespaces gratis cada mes, de sobra para el curso.
2. **Clave gratuita de Gemini** en Google AI Studio (hay que ser mayor de 18 años). Sigue
   [docs/setup.md](docs/setup.md): la clave debe ser de un proyecto **sin facturación**, así nunca pagarás nada.
3. **Abre el Codespace** con el botón de arriba y, en la pantalla de creación, pega tu clave en el campo
   `GEMINI_API_KEY`. La primera vez tarda unos minutos en prepararse.
4. Abre [`00_comprobacion.ipynb`](00_comprobacion.ipynb), elige el kernel de Python y ejecuta todas las celdas.
   Si todo sale ✅, ya estás listo.

¿Algo falla? Consulta [docs/problemas_frecuentes.md](docs/problemas_frecuentes.md) y, si no se resuelve, ven 10
minutos antes a la primera sesión.

## Qué hay en el repositorio

```
├─ 00_comprobacion.ipynb   comprobación del entorno, la clave y la cuota
├─ sesion1/                bucle agéntico desde cero · primer agente con Microsoft Agent Framework · DevUI
├─ sesion2/                servidor MCP · RAG agéntico · equipo de agentes        (se publica antes de la sesión 2)
├─ sesion3/                red team y blindaje · evaluación · observabilidad     (se publica antes de la sesión 3)
├─ mucdia/                paquete de apoyo: cliente del modelo, cuota, datos y herramientas de negocio
├─ data/                   base de datos SQLite, CSV y documentos internos de MUCDIA (sintéticos)
├─ docs/                   instalación, problemas frecuentes, chuleta y Agent Canvas
├─ reto_opcional/          reto para casa (opcional, no evaluable)
└─ replays/                respuestas grabadas para seguir si se agota la cuota
```

## Normas del curso

- **Datos sintéticos, siempre.** No pegues en ningún modelo datos personales reales ni información de empresas.
- **Tu clave es tuya.** No la compartas, no la escribas en el código y nunca subas el fichero `.env` a GitHub.
- **Cuota gratuita:** unas 10 llamadas por minuto y unas 500 al día por modelo. El paquete `mucdia` espera y
  reintenta solo. Si se agota, sigue en el portátil de otra persona de tu equipo (cada uno con su clave) o usa las
  respuestas grabadas: `mucdia.usar_modo("replay")`.
- **El reto de la sesión 3 es un CTF de honor:** se ataca solo a nuestro agente de prácticas y solo conversando con
  él. Nada de contenido dañino ni de intentar saltarse los filtros de seguridad de Google (lo prohíben sus términos).
- **No es evaluable.** Venid a probar, romper y preguntar.

## Para seguir aprendiendo

- [docs/chuleta.md](docs/chuleta.md): los comandos y fragmentos de código que más vas a usar.
- [docs/agent_canvas.md](docs/agent_canvas.md): plantilla para diseñar un agente y calcular su ROI antes de construirlo.
- [reto_opcional/](reto_opcional/README.md): lleva el agente de tu equipo un paso más allá.

## Encuesta de la sesión 3

Enlace a la encuesta de valoración: *se publicará el 2 de diciembre*.

---

Profesor: **Gerard Salvador López** · [linkedin.com/in/gerardsl](https://www.linkedin.com/in/gerardsl)

MUCDIA S.A. es una empresa inventada: cualquier parecido con una empresa real es casualidad. Las marcas
citadas (GitHub, Google, Microsoft…) pertenecen a sus titulares.
