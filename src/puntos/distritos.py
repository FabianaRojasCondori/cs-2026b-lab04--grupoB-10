"""Tarifas de puntos por distrito piloto (ADR-008: multitenencia por distrito).

Cada distrito puede sobrescribir la regla de un material (por ejemplo, una
campana local que duplica el plastico) sin tocar las reglas estandar de
`src/puntos/reglas.py`. Lo que no se sobrescribe cae en la fabrica estandar.
"""
from src.puntos.reglas import fabrica_estandar


class ReglasDistrito:
    """Reglas de puntos vigentes en un distrito."""

    _tarifas = {}  # material -> callable que crea la ReglaPuntos local

    def __init__(self, distrito: str, fabrica=None):
        self.distrito = distrito
        self._fabrica = fabrica or fabrica_estandar()

    def configurar(self, material: str, creador) -> None:
        """Sobrescribe la regla de `material` solo para este distrito."""
        self._tarifas[material] = creador

    def regla(self, material: str):
        """Regla local si existe; si no, la regla estandar del material."""
        creador = self._tarifas.get(material)
        return creador() if creador else self._fabrica.crear(material)

    def calcular(self, material: str, volumen_litros):
        """Puntos que otorga `volumen_litros` de `material` en este distrito."""
        return self.regla(material).calcular(volumen_litros)
