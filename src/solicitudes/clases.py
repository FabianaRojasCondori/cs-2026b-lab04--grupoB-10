"""Entrada de consulta del Lab 05; las implementaciones ya no se duplican aquí.

Lab 07 completa el esqueleto según las firmas del UML. modelos.py es la entidad
canónica, estados.py implementa State y servicio.py coordina el registro.
Para pyreverse analizar el paquete solicitudes y el paquete puntos completos.
"""
from .modelos import Vecino, ItemMaterial, Solicitud
from .estados import EstadoSolicitud
from .servicio import ServicioSolicitudes
from .adaptadores import NotificadorWhatsapp

__all__ = [
    "Vecino", "ItemMaterial", "Solicitud", "EstadoSolicitud",
    "ServicioSolicitudes", "NotificadorWhatsapp",
]
