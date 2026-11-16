"""Proveedor de Promptfoo que reproduce respuestas guardadas para cada caso."""

import pathlib
import re


BASE = pathlib.Path(__file__).parent / "criterios" / "grabaciones"


def call_api(prompt, options, context):
    etiqueta = context["prompt"]["label"]
    coincidencia = re.search(r"(v[\w.]+)\.txt", etiqueta)
    if coincidencia is None:
        return {"error": f"No se pudo determinar la version desde el prompt: {etiqueta}"}

    version = coincidencia.group(1)
    caso = context["vars"]["id"]
    archivo = BASE / version / f"{caso}.txt"
    if not archivo.exists():
        return {"error": f"Sin grabacion para {version}/{caso}: {archivo}"}

    return {"output": archivo.read_text(encoding="utf-8").strip()}
