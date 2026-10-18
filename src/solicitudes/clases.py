from enum import Enum
from typing import List, Optional

class EstadoSolicitud(Enum):
    PENDIENTE = "Pendiente"
    ASIGNADA = "Asignada"
    RECOGIDA = "Recogida"
    PESADA = "Pesada"
    PUNTOS_ACREDITADOS = "PuntosAcreditados"

class NotificadorFolder:
    """Puerto / Interfaz para notificaciones (ej. WhatsApp)"""
    def enviar_notificacion(self, numero: str, mensaje: str) -> bool:
        pass

class ItemMaterial:
    def __init__(self, tipo_material: str, peso_estimado: float):
        self.tipo_material: str = tipo_material
        self.peso_estimado: float = peso_estimado

class Vecino:
    def __init__(self, id_vecino: int, nombre: str, direccion: str, celular: str):
        self.id_vecino: int = id_vecino
        self.nombre: str = nombre
        self.direccion: str = direccion
        self.celular: str = celular

class Solicitud:
    def __init__(self, id_solicitud: int, vecino: Vecino):
        self.id_solicitud: int = id_solicitud
        self.vecino: Vecino = vecino
        self.items: List[ItemMaterial] = []
        self.estado: EstadoSolicitud = EstadoSolicitud.PENDIENTE

    def agregar_item(self, item: ItemMaterial) -> None:
        self.items.append(item)

    def asignar_reciclador(self, id_reciclador: int) -> None:
        if self.estado == EstadoSolicitud.PENDIENTE:
            self.estado = EstadoSolicitud.ASIGNADA

    def registrar_recojo(self) -> None:
        if self.estado == EstadoSolicitud.ASIGNADA:
            self.estado = EstadoSolicitud.RECOGIDA

    def registrar_peso(self) -> None:
        if self.estado == EstadoSolicitud.RECOGIDA:
            self.estado = EstadoSolicitud.PESADA

    def acreditar_puntos(self) -> None:
        if self.estado == EstadoSolicitud.PESADA:
            self.estado = EstadoSolicitud.PUNTOS_ACREDITADOS

class ServicioSolicitudes:
    def __init__(self, notificador: NotificadorFolder):
        self.notificador: NotificadorFolder = notificador
        self.solicitudes_activas: List[Solicitud] = []

    def crear_nueva_solicitud(self, vecino: Vecino) -> Solicitud:
        nueva = Solicitud(len(self.solicitudes_activas) + 1, vecino)
        self.solicitudes_activas.append(nueva)
        return nueva
