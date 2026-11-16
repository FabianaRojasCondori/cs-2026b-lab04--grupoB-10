"""Adaptador promptfoo: solo reproduce capturas existentes y verificadas."""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import leer_captura, prompt as renderizar, VERSIONES


def call_api(prompt, options, context):
    try:
        # promptfoo 0.118 puede expandir label a "v3: /ruta/v3.txt: contenido".
        label = context["prompt"]["label"]
        match = re.match(r"^(v[123])(?:$|:)", label)
        if not match:
            raise ValueError("Etiqueta de versión inesperada")
        etiqueta = match.group(1)
        caso = context["vars"]["id"]
        if prompt != renderizar(etiqueta, caso):
            raise ValueError("El prompt evaluado difiere del prompt de captura")
        texto, _ = leer_captura(etiqueta, caso)
        return {"output": texto}
    except (OSError, ValueError, KeyError) as exc:
        return {"error": f"Captura no disponible o inválida: {exc}"}
