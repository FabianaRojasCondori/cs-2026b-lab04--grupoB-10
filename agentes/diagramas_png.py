"""Renderiza un diagrama PlantUML (.puml) o Mermaid (.mmd) a PNG usando el servicio público kroki.io.

No requiere Java ni Node: solo conexión a Internet.
  python diagramas_png.py diseno/estados.puml            -> diseno/estados.png
  python diagramas_png.py trazas/issue1_agente_unico.mmd -> trazas/issue1_agente_unico.png
"""
import pathlib, sys, urllib.request


def renderizar(origen: str) -> pathlib.Path:
    src = pathlib.Path(origen)
    tipo = {".puml": "plantuml", ".mmd": "mermaid", ".dot": "graphviz"}[src.suffix]
    req = urllib.request.Request(f"https://kroki.io/{tipo}/png", data=src.read_text(encoding="utf-8").encode("utf-8"),
                                 headers={"Content-Type": "text/plain", "User-Agent": "Mozilla/5.0 (lab10-ecorecicla)"})
    png = urllib.request.urlopen(req, timeout=60).read()
    destino = src.with_suffix(".png")
    destino.write_bytes(png)
    return destino


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for ruta in sys.argv[1:]:
        print(f"OK: {renderizar(ruta)}")
