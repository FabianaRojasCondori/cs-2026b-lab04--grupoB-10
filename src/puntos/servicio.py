"""Orquesta cálculo y confirmación sin conocer materiales ni tarifas concretas."""
from decimal import Decimal


class ServicioPuntos:
    def __init__(self, fabrica):
        self.fabrica = fabrica

    def calcular_y_acreditar(self, solicitud):
        # El estado validará la transición; no hay efectos antes de esa validación.
        total = sum((self.fabrica.crear(item.tipo_material).calcular(item.volumen_estimado_litros)
                     for item in solicitud.items), Decimal(0))
        puntos = int(total)
        solicitud.registrar_acreditacion(puntos)
        return puntos
