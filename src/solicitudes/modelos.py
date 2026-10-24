"""Entidad canónica: delega cada transición al objeto State."""
from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4


@dataclass(frozen=True)
class Vecino:
    id: str
    nombre: str
    celular: str


@dataclass(frozen=True)
class ItemMaterial:
    tipo_material: str
    volumen_estimado_litros: Decimal

    def es_valido(self):
        return bool(self.tipo_material.strip()) and self.volumen_estimado_litros > 0



class Solicitud:
    def __init__(self, vecino, direccion, items):
        from .estados import Pendiente
        self.id = uuid4()
        self.vecino = vecino
        self.direccion = direccion
        self.items = list(items)
        self._estado = Pendiente()
        self.reciclador_id = None
        self.peso_kg = None
        self.puntos = None

    @property
    def estado(self):
        return self._estado.nombre

    def _cambiar_estado(self, estado):
        self._estado = estado

    def asignar_reciclador(self, reciclador_id):
        self._estado.asignar_reciclador(self, reciclador_id)

    def registrar_recojo(self):
        self._estado.registrar_recojo(self)

    def registrar_pesaje(self, peso_kg):
        self._estado.registrar_pesaje(self, peso_kg)

    def registrar_acreditacion(self, puntos):
        self._estado.registrar_acreditacion(self, puntos)
