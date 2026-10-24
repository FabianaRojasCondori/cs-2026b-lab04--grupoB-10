"""Modelo del flujo de solicitudes. E3 sustituirá los condicionales por State."""
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
        self.id = uuid4()
        self.vecino = vecino
        self.direccion = direccion
        self.items = list(items)
        self.estado = "Pendiente"
        self.reciclador_id = None
        self.peso_kg = None
        self.puntos = None

    def asignar_reciclador(self, reciclador_id):
        if self.estado != "Pendiente":
            raise ValueError("Transición no permitida")
        if not reciclador_id:
            raise ValueError("Reciclador inválido")
        self.reciclador_id = reciclador_id
        self.estado = "Asignada"

    def registrar_recojo(self):
        if self.estado != "Asignada":
            raise ValueError("Transición no permitida")
        self.estado = "Recogida"

    def registrar_pesaje(self, peso_kg):
        if self.estado != "Recogida":
            raise ValueError("Transición no permitida")
        if peso_kg <= 0:
            raise ValueError("El peso debe ser positivo")
        self.peso_kg = peso_kg
        self.estado = "Pesada"

    def registrar_acreditacion(self, puntos):
        if self.estado != "Pesada":
            raise ValueError("Transición no permitida")
        if puntos <= 0:
            raise ValueError("Los puntos deben ser positivos")
        self.puntos = puntos
        self.estado = "PuntosAcreditados"
