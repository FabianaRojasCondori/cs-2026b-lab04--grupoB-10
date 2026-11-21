"""ISSUE-01: puntos acreditados dos veces cuando el evento llega repetido."""
from src.puntos.cuenta import CuentaPuntos


def test_issue_01_reintento_del_evento_no_acredita_dos_veces():
    cuenta = CuentaPuntos("vecino-7")
    cuenta.acreditar("sol-001", 20)
    cuenta.acreditar("sol-001", 20)   # el outbox reintenta el mismo evento
    assert cuenta.saldo == 20
    assert len(cuenta.movimientos_de("sol-001")) == 1


def test_solicitudes_distintas_si_suman():
    cuenta = CuentaPuntos("vecino-7")
    cuenta.acreditar("sol-001", 20)
    cuenta.acreditar("sol-002", 5)
    assert cuenta.saldo == 25
