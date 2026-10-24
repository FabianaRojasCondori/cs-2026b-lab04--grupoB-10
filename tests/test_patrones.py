"""Pruebas de extensión e integración de patrones, no de nombres de clases."""
from decimal import Decimal
import pytest
from src.solicitudes.servicio import Vecino, ItemMaterial, ServicioSolicitudes
from src.solicitudes.externos import RepositorioMemoria, WhatsAppSDK, MensajeriaCliente
from src.solicitudes.adaptadores import WhatsappAdapter, MensajeriaAdapter
from src.puntos.reglas import ReglaPuntos, fabrica_estandar, BonoCampanaVerdeDecorator
from src.puntos.servicio import ServicioPuntos

# --- E4: Importaciones de Observer ---
from src.solicitudes.eventos import (
    PublicadorEventos,
    NotificadorWhatsApp,
    ActualizadorEstadisticas,
)

def solicitud(material="PLASTICO"):
    servicio = ServicioSolicitudes(RepositorioMemoria(), WhatsappAdapter(WhatsAppSDK()))
    return servicio.solicitar_recojo(Vecino("v", "Demo", "SIM"), "A", [ItemMaterial(material, Decimal("10"))])


def test_open_closed_nuevo_material_sin_modificar_servicio():
    class MetalStrategy(ReglaPuntos):
        def calcular(self, volumen_litros):
            return volumen_litros * 3
    fabrica = fabrica_estandar()
    fabrica.registrar("METAL", MetalStrategy)
    servicio = ServicioPuntos(fabrica)
    s = solicitud("METAL")
    s.asignar_reciclador("r")
    s.registrar_recojo()
    s.registrar_pesaje(Decimal("2"))
    assert servicio.calcular_y_acreditar(s) == 30
    assert (s.estado, s.puntos) == ("PuntosAcreditados", 30)


@pytest.mark.parametrize("sdk_cls,adapter_cls", [(WhatsAppSDK, WhatsappAdapter), (MensajeriaCliente, MensajeriaAdapter)])
def test_adapter_normaliza_dos_interfaces(sdk_cls, adapter_cls):
    sdk = sdk_cls()
    adapter_cls(sdk).notificar_solicitud("SIM", "solicitud-demo")
    assert sdk.pendientes == [("SIM", "Solicitud solicitud-demo registrada")]


def test_factory_rechaza_material_desconocido():
    with pytest.raises(ValueError, match="Material no soportado"):
        fabrica_estandar().crear("DESCONOCIDO")


def test_fabricas_no_comparten_registro_global():
    primera, segunda = fabrica_estandar(), fabrica_estandar()
    primera.registrar("METAL", lambda: primera.crear("PAPEL"))
    assert primera.crear("METAL").calcular(Decimal("3")) == 3
    with pytest.raises(ValueError):
        segunda.crear("METAL")



OPERACIONES = [
    ("asignar_reciclador", ("r",)),
    ("registrar_recojo", ()),
    ("registrar_pesaje", (Decimal("2"),)),
    ("registrar_acreditacion", (20,)),
]
TRANSICIONES_PROHIBIDAS = [
    (pasos, nombre, argumentos)
    for pasos in range(5)
    for indice, (nombre, argumentos) in enumerate(OPERACIONES)
    if indice != pasos
]


@pytest.mark.parametrize("pasos,operacion,argumentos", TRANSICIONES_PROHIBIDAS)
def test_state_impide_todas_las_transiciones_prohibidas(pasos, operacion, argumentos):
    s = solicitud()
    for nombre, args in OPERACIONES[:pasos]:
        getattr(s, nombre)(*args)
    antes = (s.estado, s.reciclador_id, s.peso_kg, s.puntos)
    with pytest.raises(ValueError, match="Transición no permitida"):
        getattr(s, operacion)(*argumentos)
    assert (s.estado, s.reciclador_id, s.peso_kg, s.puntos) == antes

# Entregable E4: Observer y Decorator
def test_observer_publica_a_multiples_suscriptores_sin_acoplar_servicio():
    """
    Observer: demuestra que al emitir 'solicitud_registrada', el PublicadorEventos
    notifica a WhatsApp y al colector de estadísticas de forma desacoplada.
    """
    publicador = PublicadorEventos()
    sdk = WhatsAppSDK()
    adaptador_whatsapp = WhatsappAdapter(sdk)

    notificador = NotificadorWhatsApp(adaptador_whatsapp)
    estadisticas = ActualizadorEstadisticas()

    publicador.suscribir("solicitud_registrada", notificador)
    publicador.suscribir("solicitud_registrada", estadisticas)

    payload = {"celular": "959123456", "id": "solicitud-abc-123"}
    publicador.publicar("solicitud_registrada", payload)

    assert sdk.pendientes == [("959123456", "Solicitud solicitud-abc-123 registrada")]
    assert len(estadisticas.eventos_procesados) == 1
    assert estadisticas.eventos_procesados[0] == ("solicitud_registrada", payload)


def test_decorator_bono_campana_verde_duplica_puntos_en_la_fabrica():
    """
    Decorator: demuestra que BonoCampanaVerdeDecorator envuelve una ReglaPuntos
    base y multiplica los puntos calculados sin alterar la clase original.
    """
    fabrica = fabrica_estandar()

    regla_plastico_base = fabrica.crear("PLASTICO")
    assert regla_plastico_base.calcular(Decimal("10")) == Decimal("20")

    regla_con_bono = BonoCampanaVerdeDecorator(regla_plastico_base, multiplicador=2)
    assert regla_con_bono.calcular(Decimal("10")) == Decimal("40")

    fabrica.registrar(
        "PLASTICO_PROMO",
        lambda: BonoCampanaVerdeDecorator(fabrica.crear("PLASTICO"), multiplicador=2),
    )

    regla_desde_fabrica = fabrica.crear("PLASTICO_PROMO")
    assert regla_desde_fabrica.calcular(Decimal("5")) == Decimal("20")