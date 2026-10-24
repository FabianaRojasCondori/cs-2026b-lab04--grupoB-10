"""Strategy + Factory por registro. Tarifas didácticas en puntos/litro."""
from abc import ABC, abstractmethod


class ReglaPuntos(ABC):
    @abstractmethod
    def calcular(self, volumen_litros):
        pass


class PlasticoStrategy(ReglaPuntos):
    def calcular(self, volumen_litros):
        return volumen_litros * 2


class VidrioStrategy(ReglaPuntos):
    def calcular(self, volumen_litros):
        return volumen_litros


class PapelStrategy(ReglaPuntos):
    def calcular(self, volumen_litros):
        return volumen_litros


class FabricaReglasPuntos:
    def __init__(self):
        self._creadores = {}

    def registrar(self, material, creador):
        self._creadores[material] = creador

    def crear(self, material):
        try:
            creador = self._creadores[material]
        except KeyError:
            raise ValueError("Material no soportado") from None
        return creador()


def fabrica_estandar():
    fabrica = FabricaReglasPuntos()
    fabrica.registrar("PLASTICO", PlasticoStrategy)
    fabrica.registrar("VIDRIO", VidrioStrategy)
    fabrica.registrar("PAPEL", PapelStrategy)
    return fabrica
