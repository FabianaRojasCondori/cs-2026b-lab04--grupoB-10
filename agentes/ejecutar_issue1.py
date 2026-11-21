"""E2: un solo agente ReAct resuelve ISSUE-01 con ModeloInteractivo (sin clave de API).

Uso (desde la carpeta agentes/, con el entorno virtual activo):
  python ejecutar_issue1.py                       # modo interactivo: copiar/pegar con su asistente de IA
  python ejecutar_issue1.py --grabado ARCHIVO.json  # reproduce una trayectoria ya grabada
  python ejecutar_issue1.py --issue 3             # el mismo agente único sobre otro issue (E4/E5)

Produce:
  trayectorias/issueN_agente_unico.json   decisiones del asistente (se graban al vuelo)
  trazas/issueN_agente_unico.jsonl        eventos de la máquina de estados
  trazas/issueN_agente_unico.resumen.json pasos, bloqueos, rechazos del contrato y contexto final
"""
import argparse, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agente.nucleo import Agente
from agente.herramientas import Herramientas
from agente.modelos import ModeloGrabado, ModeloInteractivo
from agente.politica import Politica
from sandbox import preparar_sandbox, RAIZ

PROTOCOLO = """Eres un agente de código que trabaja sobre una copia del repositorio EcoRecicla AQP \
(Python 3, monolito modular: src/puntos, src/solicitudes, src/rutas; pruebas con pytest).

Tu objetivo: resolver issues/{issue}.md. Lee el issue, reproduce el fallo con las pruebas, localiza la causa, \
corrige el CÓDIGO (nunca las pruebas ni el issue) y verifica que las pruebas pasen.
IMPORTANTE: en este repositorio hay 3 issues abiertos (ISSUE-01, 02 y 03) y cada uno tiene su prueba en rojo \
en tests/test_issue_0N.py. SOLO debes resolver {issue}; las otras dos pruebas seguirán en rojo y están fuera de tu alcance. \
Puedes usar ejecutar_pruebas con args {{"ruta": "tests/test_issue_0N.py"}} para correr solo la prueba de tu issue.

REGLAS DEL PROTOCOLO (obligatorias):
- Responde SIEMPRE con UN SOLO objeto JSON en UNA sola línea, sin texto antes ni después, sin bloques ```.
- Para usar una herramienta: {{"pensamiento": "<por qué>", "accion": "<herramienta>", "args": {{...}}}}
- Para terminar:            {{"pensamiento": "<por qué>", "final": "<resumen del cambio y resultado de las pruebas>"}}
- Solo puedes usar estas herramientas (nombre exacto): {catalogo}
- Dentro de los strings JSON escapa los saltos de línea como \\n y las comillas como \\".
- Tras cada acción recibirás "Observación: ..."; decide el siguiente paso a partir de ella.
- Haz un solo cambio mínimo y correcto. Máximo {max_pasos} pasos."""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--issue", type=int, default=1, help="número de issue (1, 2 o 3); por defecto 1")
    ap.add_argument("--grabado", metavar="JSON", help="reproducir una trayectoria grabada en vez del modo interactivo")
    ap.add_argument("--max-pasos", type=int, default=12)
    ap.add_argument("--sufijo", default="agente_unico", help="sufijo de los archivos de salida")
    a = ap.parse_args()

    issue = f"ISSUE-0{a.issue}"
    nombre = f"issue{a.issue}_{a.sufijo}"
    (RAIZ / "trayectorias").mkdir(exist_ok=True)
    (RAIZ / "trazas").mkdir(exist_ok=True)
    trabajo = preparar_sandbox()
    h = Herramientas(trabajo, original="../..")             # ver_cambios compara con el repositorio real

    modelo = ModeloGrabado(a.grabado) if a.grabado else ModeloInteractivo(RAIZ / "trayectorias" / f"{nombre}.json")
    politica = Politica(max_pasos=a.max_pasos, rutas_protegidas=("tests/", "issues/"))
    objetivo = PROTOCOLO.format(issue=issue, catalogo=json.dumps(h.catalogo(), ensure_ascii=False), max_pasos=a.max_pasos)
    agente = Agente("agente_unico", modelo, h, politica, objetivo, str(RAIZ / "trazas" / f"{nombre}.jsonl"))

    print(f"Sandbox listo en {trabajo}. Issue objetivo: {issue}. Modo: {'grabado' if a.grabado else 'INTERACTIVO'}\n")
    final = agente.ejecutar()

    contexto = len(json.dumps(agente.historial, ensure_ascii=False))
    acciones = [e for e in agente.eventos if e["tipo"] == "accion"]
    resumen = {
        "issue": issue, "agente": "agente_unico", "modo": "grabado" if a.grabado else "interactivo",
        "pasos": len(acciones),
        "permitidas": sum(1 for e in acciones if not e["bloqueada"]),
        "bloqueadas_por_politica": sum(1 for e in acciones if e["bloqueada"] and e["estado"] != "CONTRATO_INVALIDO"),
        "rechazadas_por_contrato": sum(1 for e in acciones if e["estado"] == "CONTRATO_INVALIDO"),
        "herramientas": sorted({e["accion"] for e in acciones if not e["bloqueada"]}),
        "estado_final": agente.eventos[-1]["estado"],
        "contexto_final_caracteres": contexto, "contexto_final_tokens_aprox": contexto // 4,
        "pruebas_sandbox": h.ejecutar_pruebas().splitlines()[-1],
    }
    (RAIZ / "trazas" / f"{nombre}.resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n================ RESULTADO ================")
    print(f"FINAL DEL AGENTE: {final}")
    print(json.dumps(resumen, ensure_ascii=False, indent=1))
    print(f"\nTraza: trazas/{nombre}.jsonl   Trayectoria: trayectorias/{nombre}.json")
    print(f"Diagrama: python agente/traza.py trazas/{nombre}.jsonl && python diagramas_png.py trazas/{nombre}.mmd")
    print("Diff para revisión humana (el agente NO fusiona):")
    print(h.ver_cambios())


if __name__ == "__main__":
    main()
