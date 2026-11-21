"""Observabilidad: convierte las trazas JSONL en un diagrama de secuencia (Mermaid) y en métricas.

Uso (desde la carpeta agentes/):
  python agente/traza.py                                   # trazas del orquestador (planificador/ejecutor/revisor)
  python agente/traza.py trazas/issue1_agente_unico.jsonl  # una o varias trazas sueltas (agente único, etc.)

Salida: <misma ruta>.mmd junto a la primera traza (o trazas/trayectoria.mmd) y las métricas en JSON.
"""
import json, collections, pathlib, sys

ORDEN = ["planificador", "ejecutor", "revisor", "ejecutor_r2", "revisor_r2", "ejecutor_r3", "revisor_r3"]
ALIAS = {"planificador": "PL", "ejecutor": "EJ", "revisor": "RV"}


def _leer(f: pathlib.Path, ronda: int):
    return [dict(json.loads(l), ronda=ronda) for l in open(f, encoding="utf-8") if l.strip()]


def cargar(carpeta="trazas"):
    eventos = []
    for n in ORDEN:
        f = pathlib.Path(carpeta) / f"{n}.jsonl"
        if f.exists():
            eventos += _leer(f, int(n.split("_r")[1]) if "_r" in n else 1)
    return eventos


def cargar_archivos(rutas):
    eventos = []
    for i, r in enumerate(rutas, 1):
        eventos += _leer(pathlib.Path(r), i)
    return eventos


def resumir(e) -> str:
    obs, acc, args = e["observacion"], e["accion"], e["args"]
    if acc == "leer_archivo": return f"contenido de {args['ruta'].split('/')[-1]}"
    if acc == "buscar": return "sin resultados" if "sin resultados" in obs else f"{len(obs.splitlines())} coincidencia(s)"
    if acc == "ver_cambios": return f"diff de {len(obs.splitlines())} líneas"
    if acc == "listar_archivos": return f"{len(obs.splitlines())} archivo(s)"
    if acc == "ejecutar_comando" and args.get("comando", "").startswith("radon"): return "complejidad"
    if acc == "editar_archivo" and obs.startswith("OK"): return "OK, archivo modificado"
    return (obs.strip().splitlines() or [""])[-1].replace(";", ",").replace("#", "N.")[:40]


def _alias(nombre: str) -> str:
    return ALIAS.get(nombre, "".join(w[0] for w in nombre.split("_"))[:3].upper() or "AG")


def a_mermaid(eventos) -> str:
    agentes = []
    for e in eventos:
        if e["agente"] not in agentes:
            agentes.append(e["agente"])
    multi = set(agentes) & set(ALIAS)
    hay_contrato = any(e["tipo"] == "accion" and e["estado"] == "CONTRATO_INVALIDO" for e in eventos)
    l = ["sequenceDiagram", "    autonumber", "    actor U as Humano"]
    if multi:
        l += ["    participant PL as Planificador", "    participant EJ as Ejecutor (actor)", "    participant RV as Revisor (crítico)"]
    else:
        l += [f"    participant {_alias(a)} as {a.replace('_', ' ').title()}" for a in agentes]
    if hay_contrato:
        l.append("    participant C as Contrato")
    l += ["    participant P as Política", "    participant H as Herramientas"]
    ronda_actual = 1
    for e in eventos:
        a = _alias(e["agente"])
        if e["ronda"] != ronda_actual and multi:
            ronda_actual = e["ronda"]
            l.append(f"    Note over EJ,RV: Ronda {ronda_actual} del bucle actor-crítico")
        if e["tipo"] == "objetivo":
            if multi:
                origen = "U" if a == "PL" else ("PL" if a == "EJ" and e["ronda"] == 1 else ("RV" if a == "EJ" else "EJ"))
                l.append(f"    {origen}->>{a}: " + ("objetivo" if a == "PL" else "plan" if origen == "PL" else "cambios solicitados" if origen == "RV" else "resumen + diff"))
            else:
                l.append(f"    U->>{a}: objetivo (issue)")
        elif e["tipo"] == "accion":
            if e["estado"] == "CONTRATO_INVALIDO":
                l += [f"    {a}-xC: decisión inválida", f"    C--x{a}: ERROR DE CONTRATO"]
            elif e["bloqueada"]:
                l += [f"    {a}-xP: {e['accion']}", f"    P--x{a}: {'LÍMITE' if e['estado'] == 'LIMITE_ALCANZADO' else 'BLOQUEADO'}"]
            else:
                l += [f"    {a}->>H: {e['accion']}", f"    H-->>{a}: {resumir(e)}"]
        elif e["tipo"] == "final":
            if not multi or (a == "RV" and not e["texto"].startswith("CAMBIOS")):
                l.append(f"    {a}-->>U: {e['texto'].split('.')[0][:60].replace('#', 'N.').replace(';', ',')}")
    return "\n".join(l)


def metricas(eventos) -> dict:
    m = collections.defaultdict(collections.Counter)
    for e in eventos:
        if e["tipo"] == "accion":
            ag = e["agente"]
            m[ag]["pasos"] += 1
            if e["estado"] == "CONTRATO_INVALIDO":
                m[ag]["rechazadas_por_contrato"] += 1
            elif e["bloqueada"]:
                m[ag]["bloqueadas_por_politica"] += 1
                m[ag][e["accion"]] += 1
            else:
                m[ag]["permitidas"] += 1
                m[ag][e["accion"]] += 1
        elif e["tipo"] == "final":
            m[e["agente"]]["finalizo"] = 1
    return {k: dict(v) for k, v in m.items()}


if __name__ == "__main__":
    rutas = sys.argv[1:]
    if rutas:
        ev = cargar_archivos(rutas)
        destino = pathlib.Path(rutas[0]).with_suffix(".mmd")
    else:
        ev = cargar()
        destino = pathlib.Path("trazas/trayectoria.mmd")
    destino.write_text(a_mermaid(ev), encoding="utf-8")
    print(f"Diagrama Mermaid escrito en {destino}")
    print(json.dumps(metricas(ev), ensure_ascii=False, indent=1))
