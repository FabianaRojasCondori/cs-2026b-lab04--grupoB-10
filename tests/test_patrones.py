"""Pruebas de extensión e integración de patrones, no de nombres de clases."""
from decimal import Decimal
import pytest
from src.solicitudes.servicio import Vecino, ItemMaterial, ServicioSolicitudes
from src.solicitudes.externos import RepositorioMemoria, WhatsAppSDK, MensajeriaCliente
from src.solicitudes.adaptadores import WhatsappAdapter, MensajeriaAdapter
from src.puntos.reglas import ReglaPuntos, fabrica_estandar
from src.puntos.servicio import ServicioPuntos


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
