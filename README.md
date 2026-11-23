# IA agéntica · Sesión 2: agentes conectados

Materiales de la segunda masterclass de **IA agéntica** del Máster Universitario en Ciencia de Datos e IA (MUCDIA) de
**CUNEF Universidad**: **miércoles 25 de noviembre de 2026, de 19:30 a 21:00**.

[![Abrir en GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/gerardsl/cunef-ia-agentica?quickstart=1)

**Tu agente de candidaturas.** El caso eres tú: una oferta real que te interese y tu CV. Construirás un agente que lee
la oferta (respetando las reglas de cada web), adapta tu CV a través de un servidor MCP sin inventar nada, investiga la
empresa con fuentes y te prepara un plan de cuatro semanas y tu pitch… en tu propia webapp. Para probar sin datos
propios hay un CV ficticio de ejemplo. Detalles en [sesion2/README.md](sesion2/README.md).

## Antes de clase (15 minutos)

1. **Cuenta de GitHub** (gratuita). Con ella tienes horas de Codespaces gratis cada mes, de sobra para la sesión.
2. **Clave gratuita de Gemini** en Google AI Studio (hay que ser mayor de 18 años). Sigue
   [docs/setup.md](docs/setup.md): la clave debe ser de un proyecto **sin facturación**, así nunca pagarás nada.
3. **Abre tu Codespace** con el botón de arriba: en la pantalla de creación, pega tu clave en el campo
   `GEMINI_API_KEY` y pulsa **Create new codespace**. La primera vez tarda unos minutos en prepararse. Si tenías un
   Codespace de antes, crea uno nuevo: este repositorio es nuevo.
4. Ten a mano **el enlace de tu oferta** y **tu CV** (PDF, Word o texto). Si la oferta es de LinkedIn, Indeed o
   InfoJobs, también su texto: esas webs no dejan que las lea un programa.

¿Algo falla? Consulta [docs/problemas_frecuentes.md](docs/problemas_frecuentes.md).

## Qué hay en el repositorio

```
├─ sesion2/    tu agente de candidaturas: leer la oferta · tu CV por MCP · investigar la empresa · tu webapp
├─ mucdia/     paquete de apoyo: cliente del modelo, cuota, respuestas grabadas, telemetría, comprobaciones y pistas
├─ docs/       puesta en marcha y problemas frecuentes
└─ replays/    respuestas grabadas para seguir si no tienes clave o se agota la cuota
```

## Normas

- **Tus datos, los mínimos.** Trabajarás con tu propio CV: envía solo lo necesario (sin teléfono, dirección ni DNI).
  La carpeta `sesion2/mi_perfil/` nunca se sube a GitHub. No pegues en ningún modelo datos personales de otras
  personas ni información confidencial de empresas.
- **Tu clave es tuya.** No la compartas, no la escribas en el código y nunca subas el fichero `.env` a GitHub.
- **Tu trabajo se queda en tu Codespace.** Para traer lo nuevo, solo `git pull`; no hace falta hacer *commit*. Si
  quieres guardarlo en tu GitHub, haz un *fork*: tu CV (`sesion2/mi_perfil/`) nunca se sube.
- **Cuota gratuita:** unas 10 llamadas por minuto y unas 500 al día por modelo. El paquete `mucdia` espera y
  reintenta solo. Si se agota, sigue en el portátil de otra persona de tu equipo (cada uno con su clave) o usa las
  respuestas grabadas: `mucdia.usar_modo("replay")`.
- **No es evaluable.** Ven a probar, romper y preguntar.

Las soluciones se publicarán aquí el día después de la clase.
