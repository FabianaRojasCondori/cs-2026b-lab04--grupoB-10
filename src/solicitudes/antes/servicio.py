"""E1: línea base ejecutable según la HU-01 y los estados del Lab 05.

Se conserva sin refactorizar para comparar comportamiento y métricas.
Las tarifas por litro son datos didácticos, no reglas municipales oficiales.
"""
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


class ServicioSolicitudes:
    def __init__(self, repositorio, sdk, proveedor="whatsapp"):
        self.repositorio = repositorio
        self.sdk = sdk
        self.proveedor = proveedor

    def solicitar_recojo(self, vecino, direccion, items):
        if not direccion.strip():
            raise ValueError("Dirección vacía")
        if not items:
            raise ValueError("Se requiere al menos un material")
        for item in items:
            if not item.tipo_material.strip():
                raise ValueError("Material vacío")
            elif item.volumen_estimado_litros <= 0:
                raise ValueError("Volumen no positivo")
        if self.proveedor not in ("whatsapp", "alternativo"):
            raise ValueError("Proveedor no soportado")
        solicitud = Solicitud(vecino, direccion, items)
        self.repositorio.guardar(solicitud)
        mensaje = f"Solicitud {solicitud.id} registrada"
        for intento in range(3):
            try:
                if self.proveedor == "whatsapp":
                    resultado = self.sdk.programar(vecino.celular, mensaje)
                    if not resultado["encolado"]:
                        raise ValueError("Encolado rechazado")
                elif self.proveedor == "alternativo":
                    codigo, _ = self.sdk.queue(mensaje, vecino.celular)
                    if codigo != 202:
                        raise ValueError("Encolado rechazado")
                break
            except TimeoutError:
                if intento == 2:
                    raise
        return solicitud


class ServicioPuntos:
    def calcular_y_acreditar(self, solicitud):
        if solicitud.estado != "Pesada":
            raise ValueError("Transición no permitida")
        total = Decimal(0)
        for item in solicitud.items:
            if item.tipo_material == "PLASTICO":
                total += item.volumen_estimado_litros * 2
            elif item.tipo_material == "VIDRIO":
                total += item.volumen_estimado_litros
            elif item.tipo_material == "PAPEL":
                total += item.volumen_estimado_litros
            else:
                raise ValueError("Material no soportado")
        puntos = int(total)
        solicitud.registrar_acreditacion(puntos)
        return puntos
