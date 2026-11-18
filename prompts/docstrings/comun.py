"""Carga, trazabilidad y lectura de capturas sin corregir sus respuestas."""
import hashlib
import json
import re
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent
VERSIONES = ("v1", "v2", "v3")
CASOS_ND = ("D1", "D4", "D8")


def sha(datos):
    return hashlib.sha256(datos).hexdigest()


def casos():
    return {c["vars"]["id"]: c["vars"] for c in
            yaml.safe_load((RAIZ / "casos.yaml").read_text(encoding="utf-8"))}


def prompt(version, caso):
    if version not in VERSIONES:
        raise ValueError(f"Versión desconocida: {version}")
    datos = casos()[caso]
    # promptfoo 0.118 recorta los extremos de plantillas y variables de texto.
    plantilla = (RAIZ / f"{version}.txt").read_text(encoding="utf-8").strip()
    return re.sub(r"\{\{(funcion|codigo)\}\}", lambda m: datos[m.group(1)].strip(), plantilla)


def ruta(version, caso, repeticion=None):
    if version not in VERSIONES or caso not in casos():
        raise ValueError("Versión o caso no permitido")
    if repeticion is None:
        return RAIZ / "grabaciones" / version / f"{caso}.txt"
    if repeticion not in (1, 2, 3) or caso not in CASOS_ND:
        raise ValueError("No determinismo: D1, D4, D8 y repeticiones 1, 2, 3")
    return RAIZ / "no-determinismo" / version / f"r{repeticion}" / f"{caso}.txt"


def leer_captura(version, caso, repeticion=None):
    archivo = ruta(version, caso, repeticion)
    meta = json.loads(archivo.with_suffix(".meta.json").read_text(encoding="utf-8"))
    datos = archivo.read_bytes()
    if not datos.strip():
        raise ValueError(f"Captura vacía: {archivo}")
    if meta["respuesta_sha256"] != sha(datos):
        raise ValueError(f"Respuesta modificada desde su captura: {archivo}")
    if meta["prompt_sha256"] != sha(prompt(version, caso).encode("utf-8")):
        raise ValueError(f"Cambió el prompt o código: repetir captura de {version}/{caso}")
    if meta["version"] != version or meta["caso"] != caso or meta["repeticion"] != repeticion:
        raise ValueError(f"Identidad de captura incompatible: {archivo}")
    return datos.decode("utf-8-sig"), meta
