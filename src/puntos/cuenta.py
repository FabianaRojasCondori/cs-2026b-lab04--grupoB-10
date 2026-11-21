"""Cuenta de puntos canjeables de un vecino (HU-05: acreditar puntos por recojo).

La acreditacion llega como evento `puntos_acreditados` desde la cola outbox
(ADR-007). La cola garantiza entrega *al menos una vez*, por lo que un mismo
evento puede llegar repetido tras un reintento.
"""


class CuentaPuntos:
    """Saldo de puntos de un vecino y el historial de movimientos que lo explican."""

    def __init__(self, vecino_id: str):
        self.vecino_id = vecino_id
        self.saldo = 0
        self.movimientos = []  # lista de (solicitud_id, puntos)

    def acreditar(self, solicitud_id: str, puntos: int) -> int:
        """Suma `puntos` al saldo por la solicitud indicada y devuelve el nuevo saldo."""
        if puntos <= 0:
            raise ValueError("Los puntos deben ser positivos")
        self.saldo += puntos
        self.movimientos.append((solicitud_id, puntos))
        return self.saldo

    def movimientos_de(self, solicitud_id: str) -> list:
        """Movimientos registrados para una solicitud."""
        return [m for m in self.movimientos if m[0] == solicitud_id]
