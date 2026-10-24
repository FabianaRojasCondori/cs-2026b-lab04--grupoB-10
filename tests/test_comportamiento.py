"""Mismo contrato observable en todas las implementaciones incluidas."""
import importlib
from decimal import Decimal
import pytest
from src.solicitudes.externos import RepositorioMemoria, WhatsAppSDK, MensajeriaCliente

VERSIONES = ["antes", "despues"]


@pytest.fixture(params=VERSIONES)
def caso(request):
    modulo = "src.solicitudes.antes.servicio" if request.param == "antes" else "src.solicitudes.servicio"
    m = importlib.import_module(modulo)
    def construir(fallas=0, proveedor="whatsapp", repo=None, sdk=None):
        repo = repo if repo is not None else RepositorioMemoria()
        sdk = sdk if sdk is not None else (WhatsAppSDK(fallas) if proveedor == "whatsapp" else MensajeriaCliente(fallas))
        if request.param == "antes":
            servicio = m.ServicioSolicitudes(repo, sdk, proveedor)
            puntos = m.ServicioPuntos()
        else:
            from src.solicitudes.adaptadores import WhatsappAdapter, MensajeriaAdapter
            from src.puntos.reglas import fabrica_estandar
            from src.puntos.servicio import ServicioPuntos
            adapter = WhatsappAdapter(sdk) if proveedor == "whatsapp" else MensajeriaAdapter(sdk)
            servicio = m.ServicioSolicitudes(repo, adapter)
            puntos = ServicioPuntos(fabrica_estandar())
        return m, servicio, puntos, repo, sdk
    return construir


def crear(caso, material="PLASTICO", volumen="10", **kwargs):
    m, servicio, puntos, repo, sdk = caso(**kwargs)
    vecino = m.Vecino("vecino-demo", "Vecino ficticio", "CELULAR_SIMULADO")
    solicitud = servicio.solicitar_recojo(vecino, "Dirección de prueba", [m.ItemMaterial(material, Decimal(volumen))])
    return solicitud, puntos, repo, sdk


def pesar(solicitud):
    solicitud.asignar_reciclador("reciclador-demo")
    solicitud.registrar_recojo()
    solicitud.registrar_pesaje(Decimal("2.5"))


def test_registro_valido_guarda_y_encola(caso):
    s, _, repo, sdk = crear(caso)
    assert s.estado == "Pendiente"
    assert repo.solicitudes == [s]
    assert sdk.pendientes == [("CELULAR_SIMULADO", f"Solicitud {s.id} registrada")]


def test_segundo_sdk_conserva_resultado(caso):
    s, _, repo, sdk = crear(caso, proveedor="alternativo")
    assert repo.solicitudes == [s]
    assert sdk.pendientes == [("CELULAR_SIMULADO", f"Solicitud {s.id} registrada")]


@pytest.mark.parametrize("direccion,material,volumen", [(" ", "PAPEL", "1"), ("A", " ", "1"), ("A", "PAPEL", "0"), ("A", "PAPEL", "-1")])
def test_datos_invalidos_no_guardan_ni_notifican(caso, direccion, material, volumen):
    m, servicio, _, repo, sdk = caso()
    with pytest.raises(ValueError):
        servicio.solicitar_recojo(m.Vecino("v", "Demo", "SIM"), direccion, [m.ItemMaterial(material, Decimal(volumen))])
    assert repo.solicitudes == []
    assert sdk.pendientes == []


def test_sin_items_no_guarda_ni_notifica(caso):
    m, servicio, _, repo, sdk = caso()
    with pytest.raises(ValueError):
        servicio.solicitar_recojo(m.Vecino("v", "Demo", "SIM"), "A", [])
    assert repo.solicitudes == []
    assert sdk.pendientes == []


def test_fallo_persistencia_no_notifica(caso):
    repo, sdk = RepositorioMemoria(falla=True), WhatsAppSDK()
    with pytest.raises(OSError):
        crear(caso, repo=repo, sdk=sdk)
    assert repo.solicitudes == []
    assert sdk.pendientes == []


@pytest.mark.parametrize("proveedor", ["whatsapp", "alternativo"])
def test_dos_timeouts_reintenta_sin_duplicar(caso, proveedor):
    s, _, repo, sdk = crear(caso, fallas=2, proveedor=proveedor)
    assert sdk.llamadas == 3
    assert len(sdk.pendientes) == 1
    assert repo.solicitudes == [s]


def test_tres_timeouts_conservan_registro_sin_encolado(caso):
    repo, sdk = RepositorioMemoria(), WhatsAppSDK(fallas=3)
    with pytest.raises(TimeoutError):
        crear(caso, repo=repo, sdk=sdk)
    assert sdk.llamadas == 3
    assert len(repo.solicitudes) == 1
    assert repo.solicitudes[0].estado == "Pendiente"
    assert sdk.pendientes == []


def test_ciclo_completo_y_puntos(caso):
    s, puntos, _, _ = crear(caso)
    s.asignar_reciclador("reciclador-demo")
    assert s.estado == "Asignada"
    s.registrar_recojo()
    assert s.estado == "Recogida"
    s.registrar_pesaje(Decimal("2.5"))
    assert s.estado == "Pesada"
    assert puntos.calcular_y_acreditar(s) == 20
    assert (s.estado, s.puntos, s.peso_kg) == ("PuntosAcreditados", 20, Decimal("2.5"))


@pytest.mark.parametrize("material,esperado", [("PLASTICO", 20), ("VIDRIO", 10), ("PAPEL", 10)])
def test_reglas_por_material(caso, material, esperado):
    s, puntos, _, _ = crear(caso, material=material)
    pesar(s)
    assert puntos.calcular_y_acreditar(s) == esperado


def test_material_no_soportado_no_acredita(caso):
    s, puntos, _, _ = crear(caso, material="METAL")
    pesar(s)
    with pytest.raises(ValueError, match="Material no soportado"):
        puntos.calcular_y_acreditar(s)
    assert (s.estado, s.puntos) == ("Pesada", None)


def test_no_se_acredita_dos_veces(caso):
    s, puntos, _, _ = crear(caso)
    pesar(s)
    puntos.calcular_y_acreditar(s)
    with pytest.raises(ValueError):
        puntos.calcular_y_acreditar(s)
    assert s.puntos == 20


@pytest.mark.parametrize("peso", ["0", "-1"])
def test_peso_invalido_no_cambia_estado(caso, peso):
    s, _, _, _ = crear(caso)
    s.asignar_reciclador("reciclador-demo")
    s.registrar_recojo()
    with pytest.raises(ValueError):
        s.registrar_pesaje(Decimal(peso))
    assert (s.estado, s.peso_kg) == ("Recogida", None)


def test_acreditacion_cero_no_cambia_estado(caso):
    s, _, _, _ = crear(caso)
    pesar(s)
    with pytest.raises(ValueError):
        s.registrar_acreditacion(0)
    assert (s.estado, s.puntos) == ("Pesada", None)


def test_no_se_puede_saltar_a_recogida(caso):
    s, _, _, _ = crear(caso)
    with pytest.raises(ValueError):
        s.registrar_recojo()
    assert s.estado == "Pendiente"


def test_reciclador_vacio_no_cambia_estado(caso):
    s, _, _, _ = crear(caso)
    with pytest.raises(ValueError):
        s.asignar_reciclador("")
    assert (s.estado, s.reciclador_id) == ("Pendiente", None)


def test_redondeo_final_sin_acreditar_cero(caso):
    s, puntos, _, _ = crear(caso, material="PAPEL", volumen="0.5")
    pesar(s)
    with pytest.raises(ValueError):
        puntos.calcular_y_acreditar(s)
    assert (s.estado, s.puntos) == ("Pesada", None)
