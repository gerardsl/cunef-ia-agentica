# Política de uso responsable de la inteligencia artificial

**Fecha:** 2026-09-30
**Versión:** 1.0
**Estado:** Vigente
**Responsable:** Comité de IA (Dirección de Sistemas, DPO, Dirección Jurídica y Dirección de Operaciones)

## Objetivo

Establecer cómo Almansa diseña, despliega y supervisa sistemas de IA, incluidos los agentes que usan herramientas, de forma segura, transparente y conforme al Reglamento (UE) 2024/1689 de Inteligencia Artificial (AI Act) y al RGPD.

## Inventario y clasificación de riesgo

Todo sistema de IA debe darse de alta en el inventario del Comité de IA antes de usarse con datos reales. Para cada sistema se documenta: finalidad, proveedor del modelo, datos que trata, herramientas a las que tiene acceso, nivel de autonomía y clasificación de riesgo según el AI Act.

Almansa **no utilizará** sistemas de IA para decisiones de selección de personal ni para evaluar la solvencia de clientes (casos de alto riesgo del Anexo III del AI Act) sin una evaluación específica aprobada por el Comité.

## Transparencia

Los clientes deben saber siempre que están interactuando con un sistema de IA (artículo 50 del AI Act). El asistente de atención al cliente se presenta como "asistente virtual de Almansa" y ofrece en todo momento la opción de hablar con una persona.

## Supervisión humana y límites de autonomía

Requieren aprobación humana explícita antes de ejecutarse:
- descuentos superiores al 10 % o compensaciones superiores a 10 €;
- reembolsos superiores a 100 €;
- cualquier envío de información fuera de Almansa;
- cambios en datos de clientes.

## Seguridad

- **Mínimo privilegio:** cada agente tiene solo las herramientas que necesita.
- El contenido externo (reseñas, correos de clientes, páginas web) se trata como **no confiable**: nunca se ejecutan instrucciones que aparezcan dentro de él.
- Antes de su puesta en producción, todo agente debe superar un ejercicio de **red teaming** (ataques de inyección de instrucciones, fuga de datos y abuso de herramientas) y una batería de evaluación de calidad.
- Las acciones de los agentes quedan registradas (trazas) durante al menos 6 meses.

## Incidentes

Cualquier comportamiento anómalo de un sistema de IA (respuestas dañinas, acciones no autorizadas, fugas de datos) se comunica al Comité de IA y, si afecta a datos personales, al DPO en un máximo de 24 horas.

## Alfabetización en IA

El personal que usa o supervisa sistemas de IA recibe formación sobre sus capacidades, límites y riesgos, en línea con el artículo 4 del AI Act.
