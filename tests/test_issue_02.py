"""ISSUE-02: la ruta del reciclador incluye solicitudes canceladas."""
from decimal import Decimal
from src.solicitudes.modelos import Vecino, ItemMaterial, Solicitud
from src.rutas.planificador import planificar_ruta


def nueva(direccion, distrito="Cayma"):
    vecino = Vecino("v-1", "Vecino ficticio", "CELULAR_SIMULADO")
    return Solicitud(vecino, direccion, [ItemMaterial("PLASTICO", Decimal("10"))], distrito=distrito)


def test_issue_02_ruta_excluye_solicitudes_canceladas():
    activa = nueva("Av. Ejercito 100")
    cancelada = nueva("Calle Mercaderes 200")
    cancelada.cancelar()
    ruta = planificar_ruta([activa, cancelada], distrito="Cayma")
    assert [s.id for s in ruta] == [activa.id]


def test_ruta_solo_del_distrito_pedido():
    cayma = nueva("Av. Ejercito 100", "Cayma")
    yanahuara = nueva("Av. Lima 300", "Yanahuara")
    assert [s.id for s in planificar_ruta([cayma, yanahuara], "Cayma")] == [cayma.id]
