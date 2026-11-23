"""Conexión al servidor MCP «mi-carrera» (sesión 2): desde Microsoft Agent Framework y «a mano» (JSON-RPC)."""

import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

from agent_framework import MCPStdioTool

from . import config

RUTA_SERVIDOR = config.RAIZ / "sesion2" / "servidor_mcp_carrera.py"


def _entorno() -> dict:
    """Entorno del proceso del servidor. El cliente stdio de MCP solo hereda unas pocas variables (PATH, HOME…):
    nunca tu clave. Le pasamos además el modo del modelo (al reproducir respuestas grabadas, el servidor usa el perfil
    de ejemplo y la fecha de la clase, para que todo coincida con la grabación) y, si las has fijado, CANDIDATURA_*."""
    from mcp.client.stdio import get_default_environment

    from . import replay

    entorno = {**get_default_environment(), "PYTHONIOENCODING": "utf-8", "MODO_LLM": config.modo()}
    if replay.debe_reproducir():
        entorno["MODO_LLM"] = "replay"
    for variable in ("CANDIDATURA_PERFIL", "CANDIDATURA_FECHA"):
        if os.getenv(variable):
            entorno[variable] = os.environ[variable]
    return entorno


def _log_servidor():
    config.DIR_USO.mkdir(parents=True, exist_ok=True)
    return open(config.DIR_USO / "mcp_servidor.log", "a", encoding="utf-8")  # noqa: SIM115


class MCPLocal(MCPStdioTool):
    """MCPStdioTool que guarda el stderr del servidor en un fichero.

    En Jupyter (sobre todo en Windows) sys.stderr no es un fichero real y el cliente stdio de MCP falla al lanzar
    el subproceso. El comportamiento es idéntico al de MCPStdioTool.
    """

    def get_mcp_client(self):
        from mcp.client.stdio import StdioServerParameters, stdio_client

        argumentos = {"command": self.command, "args": self.args, "env": self.env}
        if self.encoding:
            argumentos["encoding"] = self.encoding
        if getattr(self, "_client_kwargs", None):
            argumentos.update(self._client_kwargs)
        return stdio_client(server=StdioServerParameters(**argumentos), errlog=_log_servidor())


def servidor_mcp(herramientas: list[str] | None = None, **kwargs) -> MCPLocal:
    """Servidor MCP «mi-carrera» (tu CV y tus competencias), listo para dárselo a un agente como herramienta.

    Equivale a: MCPStdioTool(name="mi_carrera", command="python", args=["sesion2/servidor_mcp_carrera.py"])
    herramientas: lista opcional para limitar las herramientas expuestas, p. ej. ["leer_cv", "buscar_competencias"].
    """
    return MCPLocal(name="mi_carrera", command=sys.executable, args=[str(RUTA_SERVIDOR)], load_prompts=False,
                    allowed_tools=herramientas, env=_entorno(), **kwargs)


class ClienteMCPCrudo:
    """Habla con el servidor MCP «a mano»: mensajes JSON-RPC 2.0, uno por línea, por la entrada y la salida estándar
    del proceso del servidor. Es lo que hacen por dentro todos los clientes MCP (Agent Framework, Copilot, Claude…).

        mcp = mucdia.ClienteMCPCrudo()
        mcp.peticion("initialize", {...})        # → lo que enviamos · ← lo que responde el servidor
        mcp.notificacion("notifications/initialized")
        mcp.peticion("tools/list")
        mcp.cerrar()
    """

    def __init__(self, ancho: int = 700, segundos: int = 60, servidor: str | Path = RUTA_SERVIDOR):
        self.ancho, self.segundos, self._id = ancho, segundos, 0
        self.proceso = subprocess.Popen([sys.executable, str(servidor)], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=_log_servidor(), env=_entorno(),
                                        text=True, encoding="utf-8", bufsize=1)
        self._lineas: queue.Queue = queue.Queue()
        threading.Thread(target=self._leer, daemon=True).start()

    def _leer(self):
        for linea in self.proceso.stdout:
            self._lineas.put(linea)
        self._lineas.put(None)

    def _mostrar(self, flecha: str, mensaje: dict):
        texto = json.dumps(mensaje, ensure_ascii=False)
        print(f"{flecha} {texto[:self.ancho]}{' …' if len(texto) > self.ancho else ''}\n", flush=True)

    def _enviar(self, mensaje: dict):
        self._mostrar("→", mensaje)
        self.proceso.stdin.write(json.dumps(mensaje, ensure_ascii=False) + "\n")
        self.proceso.stdin.flush()

    def notificacion(self, metodo: str, params: dict | None = None) -> None:
        """Mensaje sin id: el servidor no responde."""
        self._enviar({"jsonrpc": "2.0", "method": metodo, **({"params": params} if params is not None else {})})

    def peticion(self, metodo: str, params: dict | None = None) -> dict:
        """Mensaje con id: espera la respuesta con ese mismo id y la devuelve."""
        self._id += 1
        self._enviar({"jsonrpc": "2.0", "id": self._id, "method": metodo,
                      **({"params": params} if params is not None else {})})
        while True:
            try:
                linea = self._lineas.get(timeout=self.segundos)
            except queue.Empty:
                raise TimeoutError(f"El servidor no ha respondido en {self.segundos} s") from None
            if linea is None:
                raise RuntimeError(f"El servidor se ha cerrado: mira {config.DIR_USO / 'mcp_servidor.log'}")
            respuesta = json.loads(linea)
            self._mostrar("←", respuesta)
            if respuesta.get("id") == self._id:
                return respuesta

    def cerrar(self) -> None:
        if self.proceso.poll() is None:
            self.proceso.stdin.close()
            try:
                self.proceso.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proceso.kill()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.cerrar()

    def __del__(self):
        try:
            self.cerrar()
        except Exception:  # noqa: BLE001
            pass

