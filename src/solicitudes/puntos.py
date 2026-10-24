"""Ruta de consulta pedida en guia7.pdf; implementación canónica en src/puntos.

Este puente evita duplicar clases. ServicioSolicitudes no importa este archivo:
las reglas permanecen en el módulo Puntos, conforme al Lab 05.
"""
from src.puntos.reglas import (
    ReglaPuntos, PlasticoStrategy, VidrioStrategy, PapelStrategy,
    FabricaReglasPuntos, fabrica_estandar,
)

__all__ = [
    "ReglaPuntos", "PlasticoStrategy", "VidrioStrategy", "PapelStrategy",
    "FabricaReglasPuntos", "fabrica_estandar",
]
