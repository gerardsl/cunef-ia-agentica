"""Un modelo SIMULADO con respuestas de guion: sirve para probar el bucle de tu agente sin gastar cuota.

Es la técnica habitual para hacer tests de software con modelos de lenguaje (un *mock*): el código de tu agente
no sabe que habla con un guion, y tú puedes comprobar que hace exactamente lo que debe.

    guion = [
        {"herramientas": [("ventas_por_categoria", {"desde": "2026-07-01", "hasta": "2026-09-30"})]},
        {"texto": "Electrónica fue la categoría que más vendió."},
    ]
    falso = mucdia.ClienteSimulado(guion)
    falso.chat.completions.create(model="x", messages=[...], tools=[...])   # misma interfaz que cliente_openai()
"""

import json
from types import SimpleNamespace

from openai.types.chat import ChatCompletion


def _tokens(objeto) -> int:
    """Estimación sencilla (≈4 caracteres por token) para que la telemetría simulada sea verosímil."""
    return max(1, len(json.dumps(objeto, ensure_ascii=False, default=str)) // 4)


def _a_dict(m):
    if isinstance(m, dict):
        return m
    return m.model_dump(exclude_none=True) if hasattr(m, "model_dump") else dict(m)


class ClienteSimulado:
    def __init__(self, guion: list[dict]):
        self.guion = guion
        self.peticiones: list[dict] = []          # lo que tu código le ha enviado en cada llamada
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, model: str, messages: list, tools: list | None = None, **kwargs) -> ChatCompletion:
        mensajes = [_a_dict(m) for m in messages]
        self.peticiones.append({"model": model, "messages": mensajes, "tools": tools or [], **kwargs})
        paso = self.guion[min(len(self.peticiones), len(self.guion)) - 1]
        n = len(self.peticiones)
        if "herramientas" in paso:
            llamadas = [{"id": f"sim_{n}_{i}", "type": "function",
                         "function": {"name": nombre, "arguments": json.dumps(args, ensure_ascii=False)}}
                        for i, (nombre, args) in enumerate(paso["herramientas"], start=1)]
            mensaje = {"role": "assistant", "content": None, "tool_calls": llamadas}
            fin = "tool_calls"
        else:
            mensaje = {"role": "assistant", "content": paso["texto"]}
            fin = "stop"
        return ChatCompletion.model_validate({
            "id": f"simulado-{n}", "object": "chat.completion", "created": 0, "model": "simulado",
            "choices": [{"index": 0, "message": mensaje, "finish_reason": fin}],
            "usage": {"prompt_tokens": _tokens(mensajes) + _tokens(tools or []), "completion_tokens": _tokens(mensaje),
                      "total_tokens": _tokens(mensajes) + _tokens(tools or []) + _tokens(mensaje)},
        })

    def mensajes_de_herramienta(self, peticion: int) -> list[dict]:
        """Los resultados de herramientas (role='tool') que tu código envió en la petición n (empezando en 1)."""
        return [m for m in self.peticiones[peticion - 1]["messages"] if m.get("role") == "tool"]
