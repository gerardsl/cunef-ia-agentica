"""Comprobaciones automáticas, pistas y soluciones de respaldo de los labs.

    mucdia.lab.comprobar_esquema(esquema)          # ✅ o ❌ con lo que falla
    mucdia.lab.comprobar_bucle(ejecutar_agente)    # prueba tu bucle con un modelo simulado (sin gastar cuota)
    mucdia.lab.pista("bucle")                      # una pista
    mucdia.lab.solucion("bucle")                   # la solución (si te has atascado: cópiala y sigue)
"""

import inspect
import json
import typing

from . import negocio
from .simulado import ClienteSimulado

PISTAS = {
    "esquema": [
        "Recorre `inspect.signature(funcion).parameters`: cada parámetro tiene `.annotation` y `.default`.",
        "Un parámetro es obligatorio si no tiene valor por defecto: `p.default is inspect.Parameter.empty`.",
        "La descripción de la herramienta es el docstring: `inspect.getdoc(funcion)`.",
        'Cada propiedad es un diccionario: `{"type": TIPOS[tipo], "description": descripcion}`.',
    ],
    "bucle": [
        "Pensar: `respuesta = cliente.chat.completions.create(model=MODELO, messages=mensajes, tools=HERRAMIENTAS)`.",
        "Medir: `respuesta.usage.prompt_tokens` (entrada) y `respuesta.usage.completion_tokens` (salida).",
        "¿Ha terminado?: `if not mensaje.tool_calls: return mensaje.content, traza`.",
        "Actuar: `resultado = FUNCIONES[nombre](**argumentos)` dentro de un `try`; en el `except`, "
        'devuelve el error como texto: `resultado = f"ERROR al ejecutar {nombre}: {error}"`.',
    ],
    "codigo": [
        "El modelo solo sabe lo que le cuenta el docstring: dile qué hay disponible (`consultar(sql)`, `pd`, `np`), "
        "que imprima el resultado con `print()` y que la salida se recorta.",
        "En las instrucciones del agente: que compruebe el resultado antes de responder y que explique qué ha calculado.",
        "Pregunta algo que las herramientas fijas no saben hacer: retención de clientes, correlaciones, días de la semana…",
    ],
}

SOLUCIONES = {
    "esquema": '''\
def esquema(funcion):
    """Convierte una función de Python en la descripción JSON que ve el modelo."""
    propiedades, obligatorios = {}, []
    for nombre, p in inspect.signature(funcion).parameters.items():
        tipo, descripcion = p.annotation, ""
        if typing.get_origin(tipo) is typing.Annotated:          # Annotated[str, "descripción"]
            tipo, descripcion = typing.get_args(tipo)[0], typing.get_args(tipo)[1]
        if type(None) in typing.get_args(tipo):                  # str | None  →  str (opcional)
            tipo = next(t for t in typing.get_args(tipo) if t is not type(None))
        propiedades[nombre] = {"type": TIPOS[tipo], "description": descripcion}
        if p.default is inspect.Parameter.empty:
            obligatorios.append(nombre)
    return {"type": "function", "function": {
        "name": funcion.__name__,
        "description": inspect.getdoc(funcion),
        "parameters": {"type": "object", "properties": propiedades, "required": obligatorios},
    }}''',
    "bucle": '''\
def ejecutar_agente(pregunta, max_pasos=6, cliente=CLIENTE, verbose=True):
    """Devuelve (respuesta_final, traza): la traza tiene una fila por cada llamada al modelo."""
    mensajes = [{"role": "system", "content": SISTEMA}, {"role": "user", "content": pregunta}]
    traza = []
    for paso in range(1, max_pasos + 1):
        # 1) PENSAR: el modelo ve la conversación y las herramientas
        t0 = time.perf_counter()
        respuesta = cliente.chat.completions.create(model=MODELO, messages=mensajes, tools=HERRAMIENTAS)
        mensaje = respuesta.choices[0].message

        # 2) MEDIR: tokens de esta llamada y herramientas que pide
        traza.append({"paso": paso,
                      "tokens_entrada": respuesta.usage.prompt_tokens,
                      "tokens_salida": respuesta.usage.completion_tokens,
                      "ms": round((time.perf_counter() - t0) * 1000),
                      "herramientas": [ll.function.name for ll in (mensaje.tool_calls or [])]})

        # 3) ¿HA TERMINADO? Si no pide herramientas, su texto es la respuesta final
        if not mensaje.tool_calls:
            return mensaje.content, traza

        # 4) Guardamos su mensaje tal cual (incluye la firma de razonamiento de Gemini 3)
        mensajes.append(mensaje)

        # 5) ACTUAR y OBSERVAR: ejecutamos cada herramienta y le devolvemos el resultado
        for llamada in mensaje.tool_calls:
            nombre = llamada.function.name
            argumentos = json.loads(llamada.function.arguments or "{}")
            if verbose:
                print(f"🔧 Paso {paso}: {nombre}({argumentos})")
            try:
                resultado = FUNCIONES[nombre](**argumentos)
            except Exception as error:  # el modelo también aprende de los errores
                resultado = f"ERROR al ejecutar {nombre}: {error}"
            mensajes.append({"role": "tool", "tool_call_id": llamada.id, "content": str(resultado)})
    return "⚠️ He alcanzado el máximo de pasos sin una respuesta final.", traza''',
    "codigo": '''\
@tool
def ejecutar_python(codigo: Annotated[str, "Código Python que calcula la respuesta y la imprime con print()"]) -> str:
    """Ejecuta código Python de análisis de datos sobre la base de datos de MUCDIA y devuelve lo que imprime.
    Disponibles: pandas como pd, numpy como np y consultar(sql), que ejecuta SQL de solo lectura (SQLite) y
    devuelve un DataFrame. Usa la vista v_ventas_lineas con estado = 'completada' para las ventas.
    Imprime solo el resultado final (la salida se recorta a 3.000 caracteres). Límite: 20 segundos."""
    return mucdia.ejecutar_codigo(codigo, segundos=20, max_caracteres=3000)''',
}


def pista(clave: str) -> None:
    """Muestra las pistas de un ejercicio: 'esquema', 'bucle' o 'codigo'."""
    for i, texto in enumerate(PISTAS.get(clave, ["No hay pistas con ese nombre."]), start=1):
        print(f"💡 {i}. {texto}")


def solucion(clave: str) -> None:
    """Imprime la solución de un ejercicio para que puedas copiarla y seguir."""
    print(SOLUCIONES.get(clave, "No hay solución con ese nombre."))


def _fallo(mensaje: str, clave: str) -> bool:
    print(f"❌ {mensaje}\n   Pista: mucdia.lab.pista({clave!r})  ·  Atascado: mucdia.lab.solucion({clave!r})")
    return False


# ------------------------------------------------------------------------------------------- lab 1a · esquema
def comprobar_esquema(esquema) -> bool:
    try:
        e = esquema(negocio.top_productos)
    except Exception as error:  # noqa: BLE001
        return _fallo(f"esquema(top_productos) lanza un error: {type(error).__name__}: {error}", "esquema")
    try:
        f = e["function"]
        props, req = f["parameters"]["properties"], f["parameters"]["required"]
    except (KeyError, TypeError):
        return _fallo("La estructura no es la esperada: {'type': 'function', 'function': {'name', 'description', "
                      "'parameters': {'type': 'object', 'properties', 'required'}}}", "esquema")
    if f.get("name") != "top_productos":
        return _fallo(f"El nombre debería ser 'top_productos' y es {f.get('name')!r}.", "esquema")
    if not isinstance(f.get("description"), str) or "productos" not in f["description"]:
        return _fallo("La descripción de la herramienta debería ser su docstring.", "esquema")
    esperados = {"desde": "string", "hasta": "string", "n": "integer", "categoria": "string"}
    for nombre, tipo in esperados.items():
        p = props.get(nombre)
        if not isinstance(p, dict) or p.get("type") != tipo:
            return _fallo(f"El parámetro '{nombre}' debería ser {{'type': '{tipo}', ...}} y es {p!r}.", "esquema")
        if not p.get("description"):
            return _fallo(f"Al parámetro '{nombre}' le falta la descripción (sale de Annotated[...]).", "esquema")
    if sorted(req) != ["desde", "hasta"]:
        return _fallo(f"Solo 'desde' y 'hasta' son obligatorios (no tienen valor por defecto); tienes {req}.", "esquema")
    print("✅ ¡Correcto! Así es como un framework convierte tus funciones en herramientas. Lo que verá el modelo:")
    print(json.dumps(e, ensure_ascii=False, indent=2))
    return True


# ------------------------------------------------------------------------------------------- lab 1a · bucle
def comprobar_bucle(ejecutar_agente) -> bool:
    if "cliente" not in inspect.signature(ejecutar_agente).parameters:
        return _fallo("ejecutar_agente debe aceptar el parámetro cliente= (para poder probarlo con un modelo simulado).",
                      "bucle")
    t3 = {"desde": "2026-07-01", "hasta": "2026-09-30"}
    falso = ClienteSimulado([
        {"herramientas": [("ventas_por_categoria", t3),
                          ("top_productos", {**t3, "orden": "desc"}),       # parámetro que no existe → TypeError
                          ("herramienta_inventada", {})]},                  # herramienta que no existe → KeyError
        {"texto": "Respuesta final de prueba"},
    ])
    try:
        resultado = ejecutar_agente("¿Qué categoría vendió más en el T3 de 2026?", cliente=falso, verbose=False)
    except Exception as error:  # noqa: BLE001
        return _fallo(f"El bucle se ha roto con {type(error).__name__}: {error}. Si una herramienta falla (o no existe), "
                      "captura la excepción y devuélvesela al modelo como observación.", "bucle")
    if not (isinstance(resultado, tuple) and len(resultado) == 2):
        return _fallo("ejecutar_agente debe devolver dos cosas: (respuesta_final, traza).", "bucle")
    texto, traza = resultado
    if len(falso.peticiones) == 0:
        return _fallo("No has llamado al modelo (paso PENSAR).", "bucle")
    if not falso.peticiones[0]["tools"]:
        return _fallo("Llamas al modelo sin herramientas: pásale tools=HERRAMIENTAS.", "bucle")
    if len(falso.peticiones) == 1:
        return _fallo("Solo has llamado una vez al modelo: tras ejecutar las herramientas hay que volver a llamarlo "
                      "(el bucle debe continuar).", "bucle")
    resultados = falso.mensajes_de_herramienta(2)
    ids = {m.get("tool_call_id") for m in resultados}
    if ids != {"sim_1_1", "sim_1_2", "sim_1_3"}:
        return _fallo(f"Esperaba 3 resultados de herramienta (role='tool') con su tool_call_id; he recibido {len(resultados)}.",
                      "bucle")
    por_id = {m["tool_call_id"]: str(m.get("content")) for m in resultados}
    if "Electrónica" not in por_id["sim_1_1"]:
        return _fallo("El resultado de ventas_por_categoria no contiene los datos: ¿ejecutas la función con **argumentos?",
                      "bucle")
    if "ERROR" not in por_id["sim_1_2"].upper() or "ERROR" not in por_id["sim_1_3"].upper():
        return _fallo("Cuando una herramienta falla, devuelve al modelo un texto que empiece por 'ERROR…'.", "bucle")
    if not any(m.get("role") == "assistant" and m.get("tool_calls") for m in falso.peticiones[1]["messages"]):
        return _fallo("Falta el mensaje del modelo con sus tool_calls antes de los resultados (mensajes.append(mensaje)).",
                      "bucle")
    if texto != "Respuesta final de prueba":
        return _fallo(f"Cuando el modelo no pide herramientas, devuelve su texto. Has devuelto {texto!r}.", "bucle")
    if not (isinstance(traza, list) and len(traza) == 2):
        return _fallo("La traza debe tener una fila por llamada al modelo (aquí, 2).", "bucle")
    if not all(isinstance(f, dict) and int(f.get("tokens_entrada") or 0) > 0 and "tokens_salida" in f for f in traza):
        return _fallo("Cada fila de la traza debe incluir tokens_entrada y tokens_salida (de respuesta.usage).", "bucle")
    infinito = ClienteSimulado([{"herramientas": [("ventas_por_categoria", t3)]}])
    try:
        texto2, _ = ejecutar_agente("pregunta que nunca termina", max_pasos=3, cliente=infinito, verbose=False)
    except Exception as error:  # noqa: BLE001
        return _fallo(f"Con un modelo que nunca termina, el bucle falla: {error}", "bucle")
    if len(infinito.peticiones) != 3:
        return _fallo(f"Con max_pasos=3 deberías llamar 3 veces al modelo y has llamado {len(infinito.peticiones)}.",
                      "bucle")
    print("✅ ¡Tu bucle funciona! Ejecuta herramientas (también varias a la vez), sobrevive a los errores, se detiene "
          "cuando debe y mide cada paso. Todo probado sin gastar cuota, con un modelo simulado.")
    return True
