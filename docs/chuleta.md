# Chuleta

## El paquete `mucdia`

```python
import mucdia
from mucdia import negocio

mucdia.comprobar()                      # entorno, datos, clave y una llamada de prueba
cliente = mucdia.cliente()              # cliente de chat para Microsoft Agent Framework (con límite y reintentos)
oa = mucdia.cliente_openai()            # cliente estilo OpenAI: oa.chat.completions.create(...)
mucdia.uso()                            # llamadas, tokens y lo que costaría en el plan de pago

mucdia.usar_modelo("gemini-3.1-flash-lite")   # otro modelo (cuota propia); después vuelve a crear el cliente
mucdia.usar_modo("replay")              # auto (por defecto) | live | replay | record

df = mucdia.consultar("SELECT * FROM tiendas")            # SQL → DataFrame de pandas
print(mucdia.esquema())                 # tablas, columnas y notas del diccionario de datos
mucdia.buscar_documentos("devolución", k=4)                # buscador de documentos internos (sin modelo)
mucdia.mostrar_traza(respuesta)         # qué herramientas ha llamado el agente y con qué argumentos
```

**Herramientas de negocio ya hechas** (`negocio.HERRAMIENTAS_ANALISIS` las agrupa):
`ventas_por_categoria`, `ventas_por_tienda`, `ventas_mensuales`, `top_productos`, `roturas_de_stock`, `campanias`,
`tickets_por_categoria`, `valoraciones_producto`, `objetivos_vs_real` y `buscar_en_documentos`.

## Microsoft Agent Framework

**Un agente**

```python
from agent_framework import Agent

agente = Agent(
    client=mucdia.cliente(),
    name="analista",
    instructions="Eres el analista de MUCDIA. Usa las herramientas y no inventes datos. Responde en español.",
    tools=[negocio.ventas_por_tienda, negocio.top_productos],
)
respuesta = await agente.run("¿Qué tienda vendió más en el tercer trimestre de 2026?")
print(respuesta.text)
```

**Una herramienta propia**: el nombre, el *docstring* y las descripciones de los parámetros son lo que lee el modelo.

```python
from typing import Annotated
from agent_framework import tool

@tool
def margen_producto(producto: Annotated[str, "Nombre o parte del nombre del producto"]) -> str:
    """Devuelve el precio, el coste y el margen unitario de un producto."""
    df = mucdia.consultar(
        "SELECT nombre, precio_lista, coste_unitario FROM productos WHERE nombre LIKE ?", (f"%{producto}%",))
    return df.to_csv(index=False)
```

**Memoria de conversación (sesión)**

```python
sesion = agente.create_session()
await agente.run("¿Cuánto vendió Valencia en el primer trimestre de 2026?", session=sesion)
await agente.run("¿Y en el mismo trimestre de 2025?", session=sesion)     # recuerda el contexto
```

**Salida estructurada**

```python
from pydantic import BaseModel

class Resumen(BaseModel):
    tienda: str
    ventas_eur: float
    conclusion: str

r = await agente.run("Resume la tienda que más vendió en 2025", options={"response_format": Resumen})
r.value.ventas_eur
```

**Aprobación humana** para acciones con impacto

```python
@tool(approval_mode="always_require")
def enviar_email(destinatario: str, asunto: str, cuerpo: str) -> str:
    """Envía un email."""
    ...

r = await agente.run("…", session=sesion)
for peticion in r.user_input_requests:                  # el agente se para y pide permiso
    print(peticion.function_call.name, peticion.function_call.parse_arguments())
# from agent_framework import Message
# r = await agente.run(Message("user", [peticion.to_function_approval_response(approved=True)]), session=sesion)
```

**Herramientas por MCP** (sesión 2)

```python
servidor = mucdia.servidor_mcp()                         # lanza sesion2/servidor_mcp_mucdia.py por stdio
analista_sql = Agent(client=mucdia.cliente(), name="analista_sql",
                     instructions="Explora el esquema antes de escribir SQL.", tools=[servidor])
```

**Un equipo secuencial** (sesión 2)

```python
from agent_framework.orchestrations import SequentialBuilder

equipo = SequentialBuilder(participants=[analista, revisor, redactor],
                           ensure_trailing_user_turn=True,      # necesario con Gemini
                           output_from="all").build()
resultado = await equipo.run("Prepara un informe de…")
```

**DevUI** (interfaz web para probar agentes y ver sus trazas)

```bash
python sesion1/app_devui.py        # después: pestaña PUERTOS → 8080 → 🌐
```

## La base de datos en 30 segundos

- **Vistas recomendadas:** `v_ventas_lineas` (cada línea de venta con fecha, tienda, producto y categoría) y
  `v_ventas_mensuales` (ventas completadas agregadas por mes, tienda, canal y categoría).
- **Ventas reales:** filtra `estado = 'completada'`.
- **Trimestres:** `trimestre` tiene el formato `'2026-T3'`.
- Más detalle en [data/README.md](../data/README.md) o con `print(mucdia.esquema())`.

## Gemini: plan gratuito

| | |
|---|---|
| Modelo del curso | `gemini-3.5-flash-lite` (alternativa con cuota propia: `gemini-3.1-flash-lite`) |
| Límites aproximados | ~10 llamadas/minuto · ~500 al día por modelo |
| Reinicio de la cuota | 09:00, hora de Madrid |
| Precio de referencia del plan de pago | 0,30 $ por millón de tokens de entrada · 2,50 $ por millón de salida |
