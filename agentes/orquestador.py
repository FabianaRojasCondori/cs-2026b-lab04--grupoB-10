"""Sistema multiagente con coordinación por gestor (Albada, 2025, cap. 8):
Planificador -> [Ejecutor (actor) <-> Revisor (crítico)] -> Humano.
Cada agente tiene su propia política (mínimo privilegio).

Adaptación EcoRecicla (preparada por la Persona 1 para E5/E6 de la Persona 2):
  python orquestador.py --issue 2 --interactivo   # graba las decisiones de cada agente en trayectorias/issue2_*.json
  python orquestador.py --issue 2                 # reproduce las trayectorias grabadas (ModeloGrabado)
La Persona 2 activa aquí `aprobar_edicion` en la política del ejecutor (E6)."""
import argparse, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agente.nucleo import Agente
from agente.herramientas import Herramientas
from agente.modelos import ModeloGrabado, ModeloInteractivo
from agente.politica import Politica, aprobar_edicion_consola
from sandbox import preparar_sandbox, RAIZ

ap = argparse.ArgumentParser()
ap.add_argument("--issue", type=int, default=2)
ap.add_argument("--interactivo", action="store_true", help="grabar decisiones con el asistente de IA")
ap.add_argument("--rondas", type=int, default=2)
args = ap.parse_args()

ISSUE = f"ISSUE-0{args.issue}"
MAX_RONDAS = args.rondas                                            # presupuesto del bucle actor-crítico
(RAIZ / "trazas").mkdir(exist_ok=True); (RAIZ / "trayectorias").mkdir(exist_ok=True)
h = Herramientas(preparar_sandbox(), original="../..")            # cada ejecución parte del estado original


def modelo(nombre, ronda):                                          # issue2_ejecutor.json, issue2_ejecutor_r2.json, ...
    archivo = RAIZ / "trayectorias" / f"issue{args.issue}_{nombre}{'' if ronda == 1 else f'_r{ronda}'}.json"
    return ModeloInteractivo(archivo) if args.interactivo else ModeloGrabado(archivo)


def traza(nombre, ronda):
    return str(RAIZ / "trazas" / f"{nombre}{'' if ronda == 1 else f'_r{ronda}'}.jsonl")


PROTOCOLO = ("Responde SIEMPRE con un solo JSON en una línea: "
             '{"pensamiento": "...", "accion": "<herramienta>", "args": {...}} o {"pensamiento": "...", "final": "..."}. ')

planificador = Agente("planificador", modelo("planificador", 1), h,
                      Politica(herramientas_permitidas=set(), max_pasos=2),
                      f"{PROTOCOLO}Planifica en 3 a 5 pasos cómo resolver issues/{ISSUE}.md en el repositorio de EcoRecicla AQP "
                      f"(src/puntos, src/solicitudes, src/rutas; pruebas con pytest). No tienes herramientas: responde con 'final'.",
                      traza("planificador", 1))
plan = planificador.ejecutar()
print(f"PLANIFICADOR:\n{plan}\n")
agentes, retro = [planificador], ""

for ronda in range(1, MAX_RONDAS + 1):
    politica_ejecutor = Politica(max_pasos=12, rutas_protegidas=("tests/", "issues/"))
    politica_ejecutor.aprobar_edicion = aprobar_edicion_consola
    ejecutor = Agente("ejecutor", modelo("ejecutor", ronda), h,
                      politica_ejecutor,
                      f"{PROTOCOLO}Resuelve issues/{ISSUE}.md siguiendo este plan:\n{plan}\n{retro}"
                      f"No modifiques tests/ ni issues/. Herramientas: {json.dumps(h.catalogo(), ensure_ascii=False)}",
                      traza("ejecutor", ronda))
    resumen = ejecutor.ejecutar()
    revisor = Agente("revisor", modelo("revisor", ronda), h,
                     Politica(herramientas_permitidas={"ver_cambios", "leer_archivo", "buscar", "ejecutar_pruebas"}, max_pasos=8),
                     f"{PROTOCOLO}Revisa el cambio del ejecutor (usa ver_cambios y ejecutar_pruebas). "
                     f"Tu 'final' debe empezar con APROBADO o CAMBIOS SOLICITADOS.\nResumen del ejecutor:\n{resumen}",
                     traza("revisor", ronda))
    veredicto = revisor.ejecutar()
    agentes += [ejecutor, revisor]
    print(f"--- RONDA {ronda}\nEJECUTOR: {resumen}\nREVISOR: {veredicto}\n")
    if not veredicto.startswith("CAMBIOS SOLICITADOS"):            # el crítico acepta: se pasa al humano
        break
    retro = f"El revisor solicitó cambios:\n{veredicto}\n"         # el crítico rechaza: nueva ronda

print(f"Rondas actor-crítico: {ronda} de {MAX_RONDAS}. Decisión final: HUMANO (aprobar o rechazar el PR).")
for a in agentes:
    n = len(json.dumps(a.historial, ensure_ascii=False))
    print(f"[{a.nombre}] contexto final: {n} caracteres (~{n // 4} tokens)")
