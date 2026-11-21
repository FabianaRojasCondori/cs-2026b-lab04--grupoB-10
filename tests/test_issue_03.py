"""ISSUE-03: la regla de puntos configurada en un distrito afecta a otro."""
from decimal import Decimal
from src.puntos.reglas import PlasticoStrategy, BonoCampanaVerdeDecorator
from src.puntos.distritos import ReglasDistrito


def test_issue_03_regla_de_un_distrito_no_afecta_a_otro():
    cayma = ReglasDistrito("Cayma")
    yanahuara = ReglasDistrito("Yanahuara")
    cayma.configurar("PLASTICO", lambda: BonoCampanaVerdeDecorator(PlasticoStrategy(), 3))
    assert cayma.calcular("PLASTICO", Decimal("10")) == 60
    assert yanahuara.calcular("PLASTICO", Decimal("10")) == 20


def test_sin_configuracion_usa_la_regla_estandar():
    assert ReglasDistrito("Cerro Colorado").calcular("VIDRIO", Decimal("4")) == 4
