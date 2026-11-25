"""Exploración real por stdio, sin LLM, red ni escrituras de negocio."""
import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

BASE = Path(__file__).resolve().parents[1]


async def main():
    servidor = StdioServerParameters(command=sys.executable,
                                    args=[str(BASE / "servidor_mcp/ecorecicla_mcp.py")])
    async with Client(servidor) as cliente:
        print(f"Servidor: {cliente.server_info.name} | protocolo: {cliente.protocol_version}")
        print("HERRAMIENTAS")
        for tool in (await cliente.list_tools()).tools:
            modo = "LECTURA" if tool.annotations.read_only_hint else "ESCRITURA"
            print(f"- {tool.name} [{modo}]")
        print("RECURSOS")
        for recurso in (await cliente.list_resources()).resources:
            print(f"- {recurso.uri}")
        for recurso in (await cliente.list_resource_templates()).resource_templates:
            print(f"- {recurso.uri_template} (plantilla)")
        print("PROMPTS")
        for prompt in (await cliente.list_prompts()).prompts:
            print(f"- {prompt.name}")
        for nombre, args in [
            ("puntos_usuario", {"vecino_id": "vecino-7"}),
            ("rutas_del_dia", {"fecha": "2026-11-25", "distrito": "Cayma"}),
            ("rutas_del_dia", {"fecha": "2026-02-30", "distrito": "Cayma"}),
        ]:
            r = await cliente.call_tool(nombre, args)
            print(nombre, "is_error=", r.is_error,
                  json.dumps(r.structured_content, ensure_ascii=False)
                  if r.structured_content is not None else r.content[0].text)
        r = await cliente.read_resource("ecorecicla://adr/001")
        print("ADR:", r.contents[0].text.splitlines()[0])
        p = await cliente.get_prompt("documentar_funcion", {
            "funcion": "duplicar", "codigo": "def duplicar(x: int) -> int: return x * 2"})
        print("PROMPT:", p.messages[0].content.text.splitlines()[0])


if __name__ == "__main__":
    asyncio.run(main())
