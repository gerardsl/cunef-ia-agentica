"""Conexión al servidor MCP de MUCDIA desde Microsoft Agent Framework."""

import sys

from agent_framework import MCPStdioTool

from . import config

RUTA_SERVIDOR = config.RAIZ / "sesion2" / "servidor_mcp_mucdia.py"


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
        config.DIR_USO.mkdir(parents=True, exist_ok=True)
        log = open(config.DIR_USO / "mcp_servidor.log", "a", encoding="utf-8")  # noqa: SIM115
        return stdio_client(server=StdioServerParameters(**argumentos), errlog=log)


def servidor_mcp(herramientas: list[str] | None = None, **kwargs) -> MCPLocal:
    """Servidor MCP de MUCDIA (solo lectura), listo para dárselo a un agente como herramienta.

    Equivale a: MCPStdioTool(name="mucdia", command="python", args=["sesion2/servidor_mcp_mucdia.py"])
    herramientas: lista opcional para limitar las herramientas expuestas, p. ej. ["describir_datos", "consultar_sql"].
    """
    return MCPLocal(name="mucdia", command=sys.executable, args=[str(RUTA_SERVIDOR)], load_prompts=False,
                    allowed_tools=herramientas, **kwargs)
