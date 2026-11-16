"""Ayudante local de captura/evaluación. No invoca ningún modelo ni necesita API."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from aserciones import cargar_json, evaluar
from comun import RAIZ, VERSIONES, CASOS_ND, casos, prompt, ruta, sha, leer_captura


def guardar_json(archivo, objeto):
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(json.dumps(objeto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def preparar(args):
    for caso in casos():
        archivo = RAIZ / "entradas" / args.version / f"{caso}.txt"
        archivo.parent.mkdir(parents=True, exist_ok=True)
        archivo.write_text(prompt(args.version, caso), encoding="utf-8", newline="\n")
        print(archivo.relative_to(RAIZ))
    print("Copie cada entrada en una conversación nueva. Guarde la respuesta completa sin corregirla.")


def guardar(args):
    destino = ruta(args.version, args.caso, args.repeticion)
    metadata = destino.with_suffix(".meta.json")
    if destino.exists() or metadata.exists():
        raise ValueError("Ya existe esta captura. Se conserva para no reemplazar evidencia.")
    datos = Path(args.archivo).read_bytes()
    texto = datos.decode("utf-8-sig")
    if not texto.strip():
        raise ValueError("La respuesta está vacía")
    meta = {
        "version": args.version, "caso": args.caso, "repeticion": args.repeticion,
        "fecha_captura_utc": datetime.now(timezone.utc).isoformat(),
        "modelo_declarado": args.modelo, "sesion_declarada": args.sesion,
        "enlace_conversacion": args.enlace,
        "prompt_sha256": sha(prompt(args.version, args.caso).encode("utf-8")),
        "respuesta_sha256": sha(datos),
        "nota": "Copia manual declarada por el operador; los hashes no certifican su origen.",
    }
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("xb") as stream:
        stream.write(datos)
    guardar_json(metadata, meta)
    print(f"Guardada sin editar: {destino.relative_to(RAIZ)}")
    resultado = evaluar(texto, casos()[args.caso])
    for nombre, r in resultado.items():
        print(f"{nombre}: {'OK' if r['pass'] else 'FALLA'} - {r['reason']}")
    print("Una respuesta fallida es evidencia válida de un fallo: no la corrija.")


def obtener_resultados(version):
    filas = []
    for caso, v in casos().items():
        salida, meta = leer_captura(version, caso)
        checks = evaluar(salida, v)
        filas.append({"caso": caso, "aprobado": all(c["pass"] for c in checks.values()),
                      "aserciones": checks, "respuesta_sha256": meta["respuesta_sha256"]})
    exitos = sum(f["aprobado"] for f in filas)
    return {"version": version, "total": len(filas), "exitos": exitos,
            "tasa": exitos / len(filas) * 100, "casos": filas,
            "origen": "Evaluación local de capturas; comparte las seis aserciones con promptfoo",
            "evaluador_sha256": sha((RAIZ / "aserciones.py").read_bytes()),
            "dataset_sha256": sha((RAIZ / "casos.yaml").read_bytes()),
            "esquema_sha256": sha((RAIZ / "esquema.json").read_bytes())}


def evaluar_version(args):
    r = obtener_resultados(args.version)
    guardar_json(RAIZ / "resultados" / f"resumen-{args.version}.json", r)
    lineas = [f"# Evaluación {args.version}", "", r["origen"], "",
              f"**{r['exitos']}/{r['total']} casos aprobados ({r['tasa']:.2f} %).**", "",
              "| Caso | Aprobado | Aserciones fallidas |", "|---|---|---|"]
    for f in r["casos"]:
        fallos = ", ".join(k for k, v in f["aserciones"].items() if not v["pass"]) or "Ninguna"
        lineas.append(f"| {f['caso']} | {f['aprobado']} | {fallos} |")
    lineas += ["", "Revisar manualmente idioma, sentido, condiciones y efectos laterales.",
               "Un caso aprueba solo si pasan las seis aserciones; el denominador es 8."]
    (RAIZ / "resultados" / f"evaluacion-{args.version}.md").write_text("\n".join(lineas)+"\n", encoding="utf-8")
    print("\n".join(lineas))


def comparar_versiones(args):
    resultados = [obtener_resultados(v) for v in VERSIONES]
    lineas = ["# Resultados Tarea B", "", "| Versión | Casos aprobados | Tasa |", "|---|---:|---:|"]
    for r in resultados:
        lineas.append(f"| {r['version']} | {r['exitos']}/{r['total']} | {r['tasa']:.2f} % |")
    lineas += ["", "## Regresiones"]
    for anterior, actual in zip(resultados, resultados[1:]):
        regresiones = [a["caso"] for a, b in zip(anterior["casos"], actual["casos"])
                       if a["aprobado"] and not b["aprobado"]]
        lineas.append(f"- {anterior['version']} → {actual['version']}: {', '.join(regresiones) or 'ninguna'}.")
    lineas += ["", "La mejor versión se selecciona tras revisar estas tasas, los fallos y el contenido.",
               "Meta: al menos 85 % (con 8 casos, 7/8 = 87.5 %). Si no se alcanza, documentar la hipótesis.",
               "", "![Tasas calculadas](tasas.svg)"]
    destino = RAIZ / "resultados"
    destino.mkdir(exist_ok=True)
    (destino / "resumen.md").write_text("\n".join(lineas)+"\n", encoding="utf-8")
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="700" height="260" viewBox="0 0 700 260">',
           '<rect width="700" height="260" fill="white"/>',
           '<g font-family="sans-serif" fill="#18304a"><text x="30" y="34" font-size="20">Tarea B: casos aprobados (%)</text>']
    for i, r in enumerate(resultados):
        y = 75 + 55*i
        svg += [f'<text x="30" y="{y+20}">{r["version"]}</text>',
                f'<rect x="85" y="{y}" width="500" height="28" fill="#edf2f7"/>',
                f'<rect x="85" y="{y}" width="{r["tasa"]*5:.2f}" height="28" fill="#167d8d"/>',
                f'<text x="600" y="{y+20}">{r["tasa"]:.1f}%</text>']
    svg += ['<text x="85" y="244">0</text><text x="555" y="244">100 %</text></g></svg>']
    (destino / "tasas.svg").write_text("\n".join(svg), encoding="utf-8")
    print("Generados resultados/resumen.md y resultados/tasas.svg con datos de capturas.")


def comparar_repeticiones(args):
    filas = []
    sesiones = []
    modelos = set()
    for caso in CASOS_ND:
        capturas = [leer_captura(args.version, caso, r) for r in (1, 2, 3)]
        sesiones.extend(m["sesion_declarada"] for _, m in capturas)
        modelos.update(m["modelo_declarado"] for _, m in capturas)
        normalizados, objetos = [], []
        for texto, _ in capturas:
            try:
                o = cargar_json(texto)
                objetos.append(o if isinstance(o, dict) else None)
                normalizados.append(json.dumps(o, ensure_ascii=False, sort_keys=True))
            except (ValueError, TypeError):
                objetos.append(None)
        validos = sum(all(c["pass"] for c in evaluar(t, casos()[caso]).values()) for t, _ in capturas)
        cambios = [campo for campo in ("resumen", "parametros", "retorno", "excepciones", "docstring")
                   if all(isinstance(o, dict) for o in objetos) and len({
                       json.dumps(o.get(campo), ensure_ascii=False, sort_keys=True) for o in objetos}) > 1]
        filas.append({"caso": caso, "textos_distintos": len({m["respuesta_sha256"] for _, m in capturas}),
                      "json_distintos": len(set(normalizados)), "json_validos": len(normalizados),
                      "aprobados": validos, "campos_con_cambios": cambios})
    if len(set(sesiones)) != 9:
        raise ValueError("Declare nueve conversaciones independientes (sesion diferente para cada captura).")
    if len(modelos) != 1:
        raise ValueError("Use el mismo modelo declarado en las nueve ejecuciones.")
    lineas = [f"# No determinismo: {args.version}", "", f"Modelo declarado: {next(iter(modelos))}", "",
              "| Caso | Textos distintos / 3 | JSON distintos / JSON válidos | Aprobados / 3 | Campos con variaciones |",
              "|---|---:|---|---:|---|"]
    for f in filas:
        lineas.append(f"| {f['caso']} | {f['textos_distintos']} | {f['json_distintos']} / {f['json_validos']} | {f['aprobados']} | {', '.join(f['campos_con_cambios']) or 'ninguno detectable'} |")
    cambios = sum(f["textos_distintos"] > 1 for f in filas)
    total = sum(f["aprobados"] for f in filas)
    lineas += ["", "## Análisis automático en cinco líneas (revisar antes de entregar)", "",
               f"1. Se compararon tres respuestas nuevas en cada uno de D1, D4 y D8 con {args.version} y el mismo modelo declarado.",
               f"2. {cambios} de los tres casos presentaron diferencias textuales; la tabla distingue texto y JSON normalizado.",
               "3. Los campos listados indican dónde cambió el JSON; el significado y el idioma se revisan manualmente.",
               f"4. Aprobaron {total}/9 respuestas; una muestra de nueve respuestas no demuestra estabilidad general.",
               "5. Las grabaciones fijan una salida para regresión reproducible; repetirlas en promptfoo no mide no determinismo.",
               "", "Las sesiones y el modelo fueron declarados por el operador; no se verifican mediante una API."]
    destino = RAIZ / "no-determinismo" / args.version
    (destino / "analisis.md").write_text("\n".join(lineas)+"\n", encoding="utf-8")
    guardar_json(destino / "comparacion.json", filas)
    print(f"Generado no-determinismo/{args.version}/analisis.md")


def estado(args):
    faltan = []
    versiones = [args.version] if args.version else VERSIONES
    for version in versiones:
        for caso in casos():
            try:
                leer_captura(version, caso)
                print(f"OK {version}/{caso}")
            except (OSError, ValueError, KeyError) as exc:
                faltan.append(f"{version}/{caso}: {exc}")
    if faltan:
        print(f"PENDIENTES O INVÁLIDAS: {len(faltan)} capturas")
        for f in faltan:
            print(f)
        return 1
    print("Capturas completas y hashes consistentes. Esto no implica que aprueben las aserciones.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="comando", required=True)
    for nombre, funcion in [("preparar", preparar), ("evaluar", evaluar_version), ("comparar", comparar_repeticiones)]:
        p = sub.add_parser(nombre)
        p.add_argument("--version", choices=VERSIONES, required=True)
        p.set_defaults(func=funcion)
    p = sub.add_parser("guardar")
    p.add_argument("--version", choices=VERSIONES, required=True)
    p.add_argument("--caso", choices=tuple(casos()), required=True)
    p.add_argument("--archivo", required=True)
    p.add_argument("--modelo", required=True)
    p.add_argument("--sesion", required=True)
    p.add_argument("--enlace", default=None)
    p.add_argument("--repeticion", type=int, choices=(1, 2, 3))
    p.set_defaults(func=guardar)
    p = sub.add_parser("resumir")
    p.set_defaults(func=comparar_versiones)
    p = sub.add_parser("estado")
    p.add_argument("--version", choices=VERSIONES)
    p.set_defaults(func=estado)
    args = parser.parse_args()
    try:
        return args.func(args) or 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
