"""Dobles deterministas: no usan red, credenciales ni datos personales reales."""


class RepositorioMemoria:
    def __init__(self, falla=False):
        self.solicitudes = []
        self.falla = falla

    def guardar(self, solicitud):
        if self.falla:
            raise OSError("No se pudo guardar")
        self.solicitudes.append(solicitud)


class WhatsAppSDK:
    """Simula encolar un envío: no simula entregar un mensaje en la red."""
    def __init__(self, fallas=0):
        self.fallas = fallas
        self.llamadas = 0
        self.pendientes = []

    def programar(self, telefono, cuerpo):
        self.llamadas += 1
        if self.fallas > 0:
            self.fallas -= 1
            raise TimeoutError("Cola no disponible")
        self.pendientes.append((telefono, cuerpo))
        return {"encolado": True}


class MensajeriaCliente:
    """Otro SDK simulado, con distinto orden de argumentos y respuesta."""
    def __init__(self, fallas=0):
        self.fallas = fallas
        self.llamadas = 0
        self.pendientes = []

    def queue(self, text, number):
        self.llamadas += 1
        if self.fallas > 0:
            self.fallas -= 1
            raise TimeoutError("Cola no disponible")
        self.pendientes.append((number, text))
        return 202, "SIMULADO"


class ClienteLLMFalso:
    """Disponible para que E5 lo adapte; no implementa todavía el clasificador."""
    def __init__(self, respuesta="PAPEL"):
        self.respuesta = respuesta
        self.llamadas = 0

    def generate(self, prompt):
        self.llamadas += 1
        return {"response": self.respuesta}
