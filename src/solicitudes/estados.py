"""State: cada estado redefine solo la transición permitida por el Lab 05."""


class EstadoSolicitud:
    nombre = "?"

    def asignar_reciclador(self, solicitud, reciclador_id):
        raise ValueError("Transición no permitida")

    def registrar_recojo(self, solicitud):
        raise ValueError("Transición no permitida")

    def registrar_pesaje(self, solicitud, peso_kg):
        raise ValueError("Transición no permitida")

    def registrar_acreditacion(self, solicitud, puntos):
        raise ValueError("Transición no permitida")


class Pendiente(EstadoSolicitud):
    nombre = "Pendiente"

    def asignar_reciclador(self, solicitud, reciclador_id):
        if not reciclador_id:
            raise ValueError("Reciclador inválido")
        solicitud.reciclador_id = reciclador_id
        solicitud._cambiar_estado(Asignada())


class Asignada(EstadoSolicitud):
    nombre = "Asignada"

    def registrar_recojo(self, solicitud):
        solicitud._cambiar_estado(Recogida())


class Recogida(EstadoSolicitud):
    nombre = "Recogida"

    def registrar_pesaje(self, solicitud, peso_kg):
        if peso_kg <= 0:
            raise ValueError("El peso debe ser positivo")
        solicitud.peso_kg = peso_kg
        solicitud._cambiar_estado(Pesada())


class Pesada(EstadoSolicitud):
    nombre = "Pesada"

    def registrar_acreditacion(self, solicitud, puntos):
        if puntos <= 0:
            raise ValueError("Los puntos deben ser positivos")
        solicitud.puntos = puntos
        solicitud._cambiar_estado(PuntosAcreditados())


class PuntosAcreditados(EstadoSolicitud):
    nombre = "PuntosAcreditados"
