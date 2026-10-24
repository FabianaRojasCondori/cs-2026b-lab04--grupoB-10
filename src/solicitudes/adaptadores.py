"""Adapter normaliza únicamente los SDK de encolado, sin calcular puntos."""
from abc import ABC, abstractmethod


class NotificadorWhatsapp(ABC):
    @abstractmethod
    def notificar_solicitud(self, celular, solicitud_id):
        pass


class WhatsappAdapter(NotificadorWhatsapp):
    def __init__(self, sdk):
        self.sdk = sdk

    def notificar_solicitud(self, celular, solicitud_id):
        resultado = self.sdk.programar(celular, f"Solicitud {solicitud_id} registrada")
        if not resultado["encolado"]:
            raise ValueError("Encolado rechazado")


class MensajeriaAdapter(NotificadorWhatsapp):
    def __init__(self, cliente):
        self.cliente = cliente

    def notificar_solicitud(self, celular, solicitud_id):
        codigo, _ = self.cliente.queue(f"Solicitud {solicitud_id} registrada", celular)
        if codigo != 202:
            raise ValueError("Encolado rechazado")
