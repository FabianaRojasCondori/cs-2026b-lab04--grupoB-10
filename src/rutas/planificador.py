"""Planificacion de la ruta diaria de un reciclador (HU-03).

La ruta se arma con las solicitudes de un distrito y se ordena por direccion
(orden didactico de visita). No depende del modulo de solicitudes: solo usa los
atributos `distrito`, `estado` y `direccion` de cada solicitud.
"""


def planificar_ruta(solicitudes, distrito: str) -> list:
    """Devuelve, en orden de visita, las solicitudes que el reciclador debe atender."""
    del_distrito = [s for s in solicitudes if s.distrito == distrito]
    return sorted(del_distrito, key=lambda s: s.direccion)
