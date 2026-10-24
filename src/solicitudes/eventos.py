"""Observer para notificaciones y métricas tras cambios en el sistema."""
from abc import ABC, abstractmethod


class Suscriptor(ABC):
    @abstractmethod
    def actualizar(self, evento: str, datos: dict):
        pass


class PublicadorEventos:
    def __init__(self):
        self._suscriptores = {}

    def suscribir(self, evento: str, suscriptor: Suscriptor):
        self._suscriptores.setdefault(evento, []).append(suscriptor)

    def publicar(self, evento: str, datos: dict):
        for suscriptor in self._suscriptores.get(evento, []):
            suscriptor.actualizar(evento, datos)


class NotificadorWhatsApp(Suscriptor):
    def __init__(self, adaptador):
        self.adaptador = adaptador

    def actualizar(self, evento: str, datos: dict):
        if evento == "solicitud_registrada":
            self.adaptador.notificar_solicitud(datos["celular"], datos["id"])


class ActualizadorEstadisticas(Suscriptor):
    def __init__(self):
        self.eventos_procesados = []

    def actualizar(self, evento: str, datos: dict):
        self.eventos_procesados.append((evento, datos))