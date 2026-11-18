"""Asistente interactivo para Windows/Git Bash; la generación se hace en el chat."""
import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from comun import RAIZ, VERSIONES, CASOS_ND, casos, prompt, ruta, leer_captura
from lab import guardar


def abrir(archivo):
    print(f"Archivo: {archivo}")
    if os.name == "nt":
        os.startfile(str(archivo))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--version", choices=VERSIONES, required=True)
    p.add_argument("--repeticiones", action="store_true", help="Nueve capturas nuevas: D1/D4/D8 x 3")
    a = p.parse_args()
    modelo = input("Modelo exacto mostrado en tu asistente (si no se muestra, indícalo): ").strip()
    if not modelo:
        raise SystemExit("Debes identificar el asistente/modelo usado.")
    plan = [(c, r) for r in (1, 2, 3) for c in CASOS_ND] if a.repeticiones else [(c, None) for c in casos()]
    for caso, rep in plan:
        destino = ruta(a.version, caso, rep)
        if destino.exists():
            leer_captura(a.version, caso, rep)
            print(f"Ya capturado: {destino.relative_to(RAIZ)}; se conserva.")
            continue
        entrada = RAIZ / "entradas" / a.version / f"{caso}.txt"
        entrada.parent.mkdir(parents=True, exist_ok=True)
        entrada.write_text(prompt(a.version, caso), encoding="utf-8")
        print(f"\nCASO {a.version}/{caso}, repetición: {rep or 'evaluación base'}")
        print("1. Se abrirá el prompt. Cópialo completo en un chat NUEVO, con el mismo modelo.")
        print("2. Envía solo ese prompt. No incluyas el esquema, casos.yaml ni respuestas previas.")
        abrir(entrada)
        input("Cuando tengas la respuesta del modelo y hayas cerrado el archivo del prompt, pulsa Enter: ")
        respuesta = RAIZ / "respuesta.txt"
        respuesta.write_text("", encoding="utf-8")
        print("3. Pega la respuesta COMPLETA en respuesta.txt, guarda como UTF-8 y cierra el editor.")
        print("Conserva también explicaciones y cercas Markdown si el modelo las incluyó.")
        abrir(respuesta)
        input("Después de guardar y cerrar respuesta.txt, pulsa Enter: ")
        enlace = input("URL del chat para trazabilidad (opcional; Enter para omitir): ").strip() or None
        sesion = f"{a.version}-{caso}-r{rep or 0}-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        guardar(SimpleNamespace(version=a.version, caso=caso, repeticion=rep,
                                archivo=str(respuesta), modelo=modelo, sesion=sesion, enlace=enlace))
    print("\nCapturas terminadas. Ejecuta la evaluación o la comparación correspondiente.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as e:
        raise SystemExit(f"ERROR: {e}")
