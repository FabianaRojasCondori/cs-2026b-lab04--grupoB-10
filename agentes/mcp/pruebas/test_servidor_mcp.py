"""Contratos MCP reales con Client en proceso; sin LLM ni red."""
import asyncio
import json

import pytest
from jsonschema import validate
from mcp import Client

from agentes.mcp.servidor_mcp import ecorecicla_mcp as srv
from agentes.mcp.servidor_mcp.servicio_demo import ServicioDemo


@pytest.fixture(autouse=True)
def datos_aislados(tmp_path, monkeypatch):
    monkeypatch.setattr(srv, "servicio", ServicioDemo(tmp_path / "solicitudes"))


def correr(accion):
    async def ejecutar():
        async with Client(srv.mcp) as cliente:
            return await accion(cliente)
    return asyncio.run(ejecutar())


def llamar(nombre, **args):
    return correr(lambda c: c.call_tool(nombre, args))


def solicitud(**cambios):
    return {"vecino_id": "vecino-7", "fecha": "2026-11-25", "distrito": "Cayma",
            "direccion": "Calle Demo Z 900", "material": "PLASTICO", "volumen_litros": 10,
            **cambios}


def test_catalogo_estable_documentado_y_con_esquemas():
    tools = correr(lambda c: c.list_tools()).tools
    assert [t.name for t in tools] == ["puntos_usuario", "rutas_del_dia", "registrar_solicitud"]
    for t in tools:
        assert len(t.description) > 50
        assert t.input_schema["type"] == "object"
        assert t.output_schema["type"] == "object"
    assert [t.name for t in correr(lambda c: c.list_tools()).tools] == [t.name for t in tools]


def test_exactamente_una_escritura_anotada():
    tools = correr(lambda c: c.list_tools()).tools
    escrituras = [t for t in tools if not (t.annotations and t.annotations.read_only_hint)]
    assert [t.name for t in escrituras] == ["registrar_solicitud"]
    assert escrituras[0].annotations.destructive_hint is False
    assert escrituras[0].annotations.idempotent_hint is False
    assert all(t.annotations.open_world_hint is False for t in tools)


def test_salida_estructurada_valida_contra_output_schema():
    tools = {t.name: t for t in correr(lambda c: c.list_tools()).tools}
    for nombre, args in [("puntos_usuario", {"vecino_id": "vecino-7"}),
                         ("rutas_del_dia", {"fecha": "2026-11-25", "distrito": "Cayma"}),
                         ("registrar_solicitud", solicitud())]:
        r = llamar(nombre, **args)
        assert not r.is_error
        validate(r.structured_content, tools[nombre].output_schema)


def test_puntos_correctos_y_consultas_sin_persistencia():
    for _ in range(2):
        r = llamar("puntos_usuario", vecino_id="vecino-7")
        assert not r.is_error
        assert r.structured_content["saldo"] == 25
        assert len(r.structured_content["movimientos"]) == 2
    assert not srv.servicio.carpeta.exists()


def test_vecino_desconocido_devuelve_error_corregible():
    r = llamar("puntos_usuario", vecino_id="vecino-999")
    assert r.is_error and "vecino-7" in r.content[0].text


def test_ruta_filtra_fecha_distrito_canceladas_y_ordena():
    r = llamar("rutas_del_dia", fecha="2026-11-25", distrito="Cayma")
    assert not r.is_error
    assert [p["solicitud_id"] for p in r.structured_content["paradas"]] == ["demo-002", "demo-001"]
    assert r.structured_content["total"] == 2
    assert not r.structured_content["truncado"]
    assert not srv.servicio.carpeta.exists()


def test_ruta_sin_coincidencias_es_vacia():
    r = llamar("rutas_del_dia", fecha="2026-11-25", distrito="Cerro Colorado")
    assert not r.is_error and r.structured_content["paradas"] == []


def test_ruta_limita_a_20_y_informa_total():
    fila = srv.servicio.datos["rutas"][0]
    srv.servicio.datos["rutas"] = [{**fila, "id": f"demo-{i}"} for i in range(25)]
    r = llamar("rutas_del_dia", fecha="2026-11-25", distrito="Cayma")
    assert len(r.structured_content["paradas"]) == 20
    assert r.structured_content["total"] == 25 and r.structured_content["truncado"]


@pytest.mark.parametrize("fecha", ["25/11/2026", "2026-02-30", "2026-1-025"])
def test_fecha_invalida_devuelve_error_util(fecha):
    r = llamar("rutas_del_dia", fecha=fecha, distrito="Cayma")
    assert r.is_error and "AAAA-MM-DD" in r.content[0].text


def test_distrito_invalido_explica_valores_validos():
    r = llamar("rutas_del_dia", fecha="2026-11-25", distrito="Lima")
    assert r.is_error and "Cayma" in r.content[0].text


@pytest.mark.parametrize("cambios", [
    {"material": "METAL"}, {"volumen_litros": 0}, {"volumen_litros": -1},
    {"volumen_litros": 1001}, {"volumen_litros": "10"}, {"volumen_litros": True},
    {"direccion": "     "}, {"direccion": "x" * 161}, {"direccion": "Calle\nDemo"},
    {"vecino_id": "../secreto"}, {"fecha": "2026-02-30"}, {"distrito": "Lima"},
])
def test_registro_invalido_no_escribe(cambios):
    r = llamar("registrar_solicitud", **solicitud(**cambios))
    assert r.is_error and r.content[0].text
    assert not srv.servicio.carpeta.exists()


def test_parametro_obligatorio_ausente_es_error():
    r = llamar("registrar_solicitud", vecino_id="vecino-7")
    assert r.is_error
    assert not srv.servicio.carpeta.exists()


def test_registro_solo_crea_y_conserva_archivos_existentes():
    carpeta = srv.servicio.carpeta
    carpeta.mkdir()
    previo = carpeta / "existente.txt"
    previo.write_text("no modificar", encoding="utf-8")
    ids = [llamar("registrar_solicitud", **solicitud()).structured_content["solicitud_id"]
           for _ in range(2)]
    assert ids[0] != ids[1]
    assert len(list(carpeta.glob("*.json"))) == 2
    assert previo.read_text(encoding="utf-8") == "no modificar"
    for identificador in ids:
        dato = json.loads((carpeta / f"{identificador}.json").read_text(encoding="utf-8"))
        assert dato["estado"] == "Pendiente" and dato["distrito"] == "Cayma"


def test_colision_de_identificador_no_sobrescribe(monkeypatch):
    from uuid import UUID
    from src.solicitudes import modelos
    monkeypatch.setattr(modelos, "uuid4", lambda: UUID(int=42))
    primero = llamar("registrar_solicitud", **solicitud())
    assert not primero.is_error
    archivo = next(srv.servicio.carpeta.glob("*.json"))
    original = archivo.read_bytes()
    segundo = llamar("registrar_solicitud", **solicitud(direccion="Calle diferente 123"))
    assert segundo.is_error and archivo.read_bytes() == original


def test_solicitud_persiste_entre_instancias_y_no_acredita():
    r = llamar("registrar_solicitud", **solicitud())
    assert not r.is_error
    # Simula un reinicio: lee el JSON desde otra instancia del adaptador.
    nuevo = ServicioDemo(srv.servicio.carpeta)
    ruta = nuevo.rutas("2026-11-25", "Cayma")
    assert r.structured_content["solicitud_id"] in [p["solicitud_id"] for p in ruta["paradas"]]
    assert nuevo.puntos("vecino-7")["saldo"] == 25


def test_recursos_estaticos_y_plantilla_publicados():
    recursos = correr(lambda c: c.list_resources()).resources
    assert {str(r.uri) for r in recursos} == {"ecorecicla://puntos/tabla", "ecorecicla://demo/contexto"}
    plantillas = correr(lambda c: c.list_resource_templates()).resource_templates
    assert [t.uri_template for t in plantillas] == ["ecorecicla://adr/{numero}"]
    r = correr(lambda c: c.read_resource("ecorecicla://puntos/tabla"))
    assert json.loads(r.contents[0].text)["tarifas"] == {"PLASTICO": 2, "VIDRIO": 1, "PAPEL": 1}


def test_adr_existente_usa_documento_real():
    r = correr(lambda c: c.read_resource("ecorecicla://adr/001"))
    assert "EcoRecicla AQP" in r.contents[0].text


@pytest.mark.parametrize("numero", ["..", "..%2F..%2Fsecretos", "../../secretos", "001.md", "999"])
def test_adr_rechaza_rutas_y_numeros_inexistentes(numero):
    # ResourceError se transporta como error JSON-RPC, no como resultado de tool.
    with pytest.raises(Exception) as error:
        correr(lambda c: c.read_resource(f"ecorecicla://adr/{numero}"))
    assert str(error.value)


def test_adr_rechaza_enlace_fuera_de_carpeta(tmp_path, monkeypatch):
    carpeta = tmp_path / "docs/architecture/adr"
    carpeta.mkdir(parents=True)
    secreto = tmp_path / "secreto.md"
    secreto.write_text("no exponer", encoding="utf-8")
    try:
        (carpeta / "001-enlace.md").symlink_to(secreto)
    except OSError:
        pytest.skip("El sistema no permite crear enlaces simbólicos")
    monkeypatch.setattr(srv, "RAIZ", tmp_path)
    with pytest.raises(Exception):
        correr(lambda c: c.read_resource("ecorecicla://adr/001"))


def test_prompt_reutiliza_lab09_y_trata_codigo_como_datos():
    prompts = correr(lambda c: c.list_prompts()).prompts
    assert [p.name for p in prompts] == ["documentar_funcion"]
    codigo = 'def ejemplo(): return "{{funcion}}"'
    r = correr(lambda c: c.get_prompt("documentar_funcion", {"funcion": "ejemplo", "codigo": codigo}))
    texto = r.messages[0].content.text
    assert "dato no confiable" in texto and codigo in texto
    original = (srv.RAIZ / "prompts/docstrings/v3.txt").read_text(encoding="utf-8")
    assert original.split("# DATOS")[0] in texto
