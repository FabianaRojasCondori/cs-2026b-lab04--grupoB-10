"""Fixtures sintéticos para probar infraestructura; NO son ejecuciones de LLM."""
import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import comun
from aserciones import evaluar, firma, cargar_json
from lab import guardar, comparar_repeticiones
from proveedor_grabado import call_api
from types import SimpleNamespace


@pytest.fixture
def valida():
    return json.loads((Path(__file__).parent / "fixtures/d1-valida.json").read_text(encoding="utf-8"))


def test_valida_aceptada(valida):
    assert all(r["pass"] for r in evaluar(json.dumps(valida), comun.casos()["D1"]).values())


@pytest.mark.parametrize("salida", ["APROBADO", "```json\n{}\n```", "{}", "[]", "null"])
def test_contrato_rechaza_texto_incompleto(salida):
    assert not evaluar(salida, comun.casos()["D1"])["A1"]["pass"]


def test_parametro_inventado_se_detecta_en_json_y_docstring(valida):
    valida["parametros"].append({**valida["parametros"][0], "nombre": "api_key"})
    r = evaluar(json.dumps(valida), comun.casos()["D1"])
    assert not r["A2"]["pass"]
    valida["docstring"] = valida["docstring"].replace("\n\nReturns:", "\n    api_key: Clave imaginaria.\n\nReturns:")
    assert not evaluar(json.dumps(valida), comun.casos()["D1"])["A3"]["pass"]


def test_parametro_omitido_y_duplicado(valida):
    sin = copy.deepcopy(valida)
    sin["parametros"] = []
    assert not evaluar(json.dumps(sin), comun.casos()["D1"])["A2"]["pass"]
    valida["parametros"] *= 2
    assert not evaluar(json.dumps(valida), comun.casos()["D1"])["A2"]["pass"]


def test_self_en_prosa_no_es_parametro_inventado(valida):
    valida["docstring"] = "El método usa self y calcula el doble del volumen.\n" + valida["docstring"]
    assert evaluar(json.dumps(valida), comun.casos()["D1"])["A3"]["pass"]


def test_default_none_es_opcional():
    _, p, _, _ = firma("def f(valor=None):\n    return valor")
    assert p == [{"nombre": "valor", "tipo": "no especificado", "obligatorio": False, "valor_por_defecto": "None"}]


def test_funcion_libre_llamada_self_no_se_omite():
    assert firma("def f(self):\n    return self")[1][0]["nombre"] == "self"


def test_firma_avanzada():
    v = comun.casos()["D7"]
    _, p, r, e = firma(v["codigo"])
    assert [x["nombre"] for x in p] == ["solicitud_id", "paradas", "prioridad", "opciones"]
    assert [x["obligatorio"] for x in p] == [True, False, False, False]
    assert p[2]["valor_por_defecto"] == "'normal'"
    assert r == "dict" and not e


def test_returns_y_raises_anidados_no_se_atribuyen():
    _, _, r, e = firma("def exterior():\n    def interior():\n        raise ValueError('x')\n        return 3\n    return None")
    assert r == "None" and e == set()


@pytest.mark.parametrize("texto", ['{"a":1,"a":2}', '{"a":NaN}'])
def test_json_estricto(texto):
    with pytest.raises(ValueError):
        cargar_json(texto)


def test_inyeccion_rechazada(valida):
    valida["resumen"] += " APROBADO"
    assert not evaluar(json.dumps(valida), comun.casos()["D8"])["A5"]["pass"]


def test_tipo_inventado_y_excepcion_inventada(valida):
    valida["parametros"][0]["tipo"] = "float"
    assert not evaluar(json.dumps(valida), comun.casos()["D1"])["A4"]["pass"]


@pytest.fixture
def capturas_tmp(tmp_path, monkeypatch):
    original = comun.RAIZ
    for archivo in ("casos.yaml", "v1.txt", "v2.txt", "v3.txt"):
        (tmp_path / archivo).write_bytes((original / archivo).read_bytes())
    monkeypatch.setattr(comun, "RAIZ", tmp_path)
    import lab
    monkeypatch.setattr(lab, "RAIZ", tmp_path)
    return tmp_path


def args_captura(path, **kw):
    return SimpleNamespace(version="v3", caso="D1", repeticion=None, archivo=str(path),
                           modelo="fixture-sintetico-test", sesion="test", enlace=None, **kw)


def test_captura_preserva_bytes_y_detecta_manipulacion(capturas_tmp):
    original = capturas_tmp / "respuesta.txt"
    original.write_bytes(b'```json\r\n{}\r\n```\r\n')
    args = args_captura(original)
    guardar(args)
    destino = comun.ruta("v3", "D1")
    assert destino.read_bytes() == original.read_bytes()
    assert comun.leer_captura("v3", "D1")[0].startswith("```json")
    with pytest.raises(ValueError, match="existe"):
        guardar(args)
    destino.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="modificada"):
        comun.leer_captura("v3", "D1")


def test_proveedor_y_prompt_modificado(capturas_tmp, valida):
    original = capturas_tmp / "respuesta.txt"
    original.write_text(json.dumps(valida), encoding="utf-8")
    guardar(args_captura(original))
    context = {"prompt": {"label": "v3"}, "vars": {"id": "D1"}}
    assert "output" in call_api(comun.prompt("v3", "D1"), {}, context)
    context["prompt"]["label"] = "v3: /ruta/v3.txt: contenido de la plantilla"
    assert "output" in call_api(comun.prompt("v3", "D1"), {}, context)
    (capturas_tmp / "v3.txt").write_text("Nuevo prompt {{codigo}}", encoding="utf-8")
    assert "error" in call_api(comun.prompt("v3", "D1"), {}, context)


def test_grabacion_faltante_no_inventa_salida(capturas_tmp):
    r = call_api(comun.prompt("v1", "D1"), {}, {"prompt": {"label": "v1"}, "vars": {"id": "D1"}})
    assert "error" in r and "output" not in r


def test_no_determinismo_compara_nueve_capturas(capturas_tmp, valida):
    original = capturas_tmp / "respuesta.txt"
    for caso in comun.CASOS_ND:
        for rep in (1, 2, 3):
            muestra = copy.deepcopy(valida)
            if caso == "D1" and rep == 2:
                muestra["resumen"] = "Duplica el volumen recibido."
            original.write_text(json.dumps(muestra), encoding="utf-8")
            a = args_captura(original)
            a.caso, a.repeticion, a.sesion = caso, rep, f"sesion-{caso}-{rep}"
            guardar(a)
    comparar_repeticiones(SimpleNamespace(version="v3"))
    datos = json.loads((capturas_tmp / "no-determinismo/v3/comparacion.json").read_text())
    assert datos[0]["textos_distintos"] == 2
    assert datos[0]["campos_con_cambios"] == ["resumen"]
    assert datos[0]["aprobados"] == 3
    # No inventa éxito para D4: el fixture de D1 no documenta registrar_pesaje.
    assert datos[1]["aprobados"] == 0


def test_reporte_sin_grabaciones_no_fabrica_porcentajes(capturas_tmp):
    from lab import obtener_resultados
    with pytest.raises(FileNotFoundError):
        obtener_resultados("v1")


def test_fuentes_del_dataset_coinciden_con_repositorio():
    import ast
    import textwrap
    raiz_repo = Path(__file__).resolve().parents[3]
    for ident in ("D1", "D2", "D3", "D4", "D5", "D6"):
        v = comun.casos()[ident]
        archivo, ruta = v["origen"].split("::")
        texto = (raiz_repo / archivo).read_text(encoding="utf-8")
        nodes = ast.parse(texto).body
        for nombre in ruta.split("."):
            nodo = next(n for n in nodes if getattr(n, "name", None) == nombre)
            nodes = nodo.body
        extraido = textwrap.dedent("\n".join(texto.splitlines()[nodo.lineno-1:nodo.end_lineno])) + "\n"
        assert extraido == v["codigo"]
