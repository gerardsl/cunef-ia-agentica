"""Utilidades para ver por dentro qué ha hecho un agente (llamadas a herramientas y resultados)."""

import json


def _corto(valor, n: int) -> str:
    texto = valor if isinstance(valor, str) else json.dumps(valor, ensure_ascii=False, default=str)
    texto = " ".join(str(texto).split())
    return texto if len(texto) <= n else texto[: n - 1] + "…"


def _codigo(argumentos) -> str | None:
    """Si la herramienta recibe código (un agente que programa), lo devuelve para mostrarlo con sus saltos de línea."""
    if isinstance(argumentos, str):
        try:
            argumentos = json.loads(argumentos)
        except json.JSONDecodeError:
            return None
    if isinstance(argumentos, dict) and isinstance(argumentos.get("codigo"), str):
        return argumentos["codigo"]
    return None


def mostrar_traza(respuesta, n: int = 220) -> None:
    """Imprime los pasos de una respuesta de Agent Framework: herramientas llamadas, resultados y texto."""
    paso = 0
    for m in getattr(respuesta, "messages", []) or []:
        for c in m.contents or []:
            if c.type == "function_call":
                paso += 1
                if (codigo := _codigo(c.arguments)) is not None:
                    recorte = codigo if len(codigo) <= n else codigo[: n - 1] + "…"
                    print(f"🔧 Paso {paso} · {m.author_name or 'agente'} ejecuta {c.name}:")
                    print("\n".join("     │ " + linea for linea in recorte.strip().splitlines()))
                else:
                    print(f"🔧 Paso {paso} · {m.author_name or 'agente'} llama a {c.name}({_corto(c.arguments, n)})")
            elif c.type == "function_result":
                print(f"   ↳ resultado: {_corto(c.result if c.exception is None else c.exception, n)}")
            elif c.type == "function_approval_request":
                print(f"✋ Pide aprobación para {c.function_call.name}({_corto(c.function_call.arguments, n)})")
            elif c.type == "text" and (c.text or "").strip() and m.role == "assistant":
                print(f"💬 {m.author_name or 'agente'}: {_corto(c.text, n)}")
    if paso == 0:
        print("(el agente respondió sin usar herramientas)")
