"""E2: puerto de notificación inyectado; no hay selección de proveedores aquí."""
from .modelos import Vecino, ItemMaterial, Solicitud


class ServicioSolicitudes:
    def __init__(self, repositorio, notificador):
        self.repositorio = repositorio
        self.notificador = notificador

    def solicitar_recojo(self, vecino, direccion, items):
        self.validar_datos(direccion, items)
        solicitud = Solicitud(vecino, direccion, items)
        self.repositorio.guardar(solicitud)
        self._encolar_confirmacion(solicitud)
        return solicitud

    @staticmethod
    def validar_datos(direccion, items):
        if not direccion.strip():
            raise ValueError("Dirección vacía")
        if not items:
            raise ValueError("Se requiere al menos un material")
        for item in items:
            if not item.tipo_material.strip():
                raise ValueError("Material vacío")
            if item.volumen_estimado_litros <= 0:
                raise ValueError("Volumen no positivo")

    def _encolar_confirmacion(self, solicitud):
        # E4 extraerá estos reintentos a un Decorator conservando el contrato.
        for intento in range(3):
            try:
                self.notificador.notificar_solicitud(solicitud.vecino.celular, solicitud.id)
                return
            except TimeoutError:
                if intento == 2:
                    raise
