"""E3: decisiones inválidas propias (vistas en E2 o imaginadas) que el contrato debe rechazar.

Complementan test_agente.py (del mini framework). Cada caso simula un fallo real del asistente:
la 'trampa del JSON frágil' (Koenigstein, 2026, cap. 5)."""
import sys, pathlib, pytest
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from agente.contrato import validar_decision
from agente.herramientas import Herramientas
from agente.politica import Politica

H = {"listar_archivos", "leer_archivo", "buscar", "ejecutar_pruebas", "editar_archivo", "ver_cambios", "ejecutar_comando"}

CASOS_INVALIDOS = [
    # visto en E2: el asistente respondió en prosa en vez de JSON
    ("Voy a hacer que acreditar() sea idempotente comprobando la solicitud.", "la decisión debe ser un objeto JSON"),
    # campo de más: el asistente agrega 'confianza' o 'explicacion' fuera del protocolo
    ({"pensamiento": "edito", "accion": "editar_archivo", "args": {"ruta": "src/puntos/cuenta.py", "antes": "a", "despues": "b"}, "confianza": 0.9}, "campos no permitidos"),
    # args como texto en lugar de objeto JSON
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": "src/puntos/cuenta.py"}, "'args' debe ser un objeto JSON"),
    # acción vacía
    ({"pensamiento": "pienso", "accion": "", "args": {}}, "herramienta desconocida"),
    # pensamiento vacío (solo espacios)
    ({"pensamiento": "   ", "accion": "ejecutar_pruebas", "args": {}}, "falta 'pensamiento'"),
    # 'final' que no es texto (lista)
    ({"pensamiento": "termino", "final": ["resuelto"]}, "'final' debe ser texto"),
    # ni acción ni final
    ({"pensamiento": "no sé qué hacer"}, "debe incluir 'accion' o 'final'"),
    # herramienta con mayúsculas / nombre parecido (el catálogo es exacto)
    ({"pensamiento": "leo", "accion": "Leer_Archivo", "args": {"ruta": "x"}}, "herramienta desconocida"),
    # una lista de decisiones en vez de una sola
    ([{"pensamiento": "a", "final": "b"}], "la decisión debe ser un objeto JSON"),
    # None (la respuesta llegó vacía)
    (None, "la decisión debe ser un objeto JSON"),
]


@pytest.mark.parametrize("d, motivo", CASOS_INVALIDOS)
def test_contrato_rechaza_decisiones_invalidas_propias(d, motivo):
    ok, detalle = validar_decision(d, H)
    assert ok is False
    assert motivo in detalle


@pytest.mark.parametrize("d", [
    {"pensamiento": "reproduzco", "accion": "ejecutar_pruebas", "args": {"ruta": "tests/test_issue_01.py"}},
    {"pensamiento": "sin args explícitos", "accion": "ver_cambios"},
    {"pensamiento": "listo", "final": "Corregí el issue #01; pruebas en verde."},
])
def test_contrato_acepta_decisiones_validas_del_protocolo(d):
    assert validar_decision(d, H) == (True, "")


def test_politica_protege_issues_y_tests_en_ecorecicla():
    p = Politica(rutas_protegidas=("tests/", "issues/"))
    assert not p.evaluar("editar_archivo", {"ruta": "issues/ISSUE-01.md", "antes": "a", "despues": "b"}, 1).permitido
    assert not p.evaluar("editar_archivo", {"ruta": "tests/test_issue_01.py", "antes": "a", "despues": "b"}, 1).permitido
    assert p.evaluar("editar_archivo", {"ruta": "src/puntos/cuenta.py", "antes": "a", "despues": "b"}, 1).permitido


def test_politica_permite_lint_imports_y_bloquea_pip_install():
    p = Politica()
    assert p.evaluar("ejecutar_comando", {"comando": "lint-imports"}, 1).permitido
    assert p.evaluar("ejecutar_comando", {"comando": "radon cc -s src/puntos"}, 1).permitido
    assert not p.evaluar("ejecutar_comando", {"comando": "pip install requests"}, 1).permitido
    assert not p.evaluar("ejecutar_comando", {"comando": "rm -rf src"}, 1).permitido


def test_politica_revisor_solo_lectura_no_puede_editar():
    revisor = Politica(herramientas_permitidas={"ver_cambios", "leer_archivo", "buscar", "ejecutar_pruebas"}, max_pasos=8)
    assert not revisor.evaluar("editar_archivo", {"ruta": "src/puntos/cuenta.py", "antes": "a", "despues": "b"}, 1).permitido
    assert not revisor.evaluar("ejecutar_comando", {"comando": "python -m pytest -q"}, 1).permitido
    assert revisor.evaluar("ver_cambios", {}, 1).permitido


def test_aprobar_edicion_humana_rechaza_con_n():
    # aprobar_edicion es un atributo de la política (humano en el circuito, E6): se asigna tras construirla
    rechaza, acepta = Politica(), Politica()
    rechaza.aprobar_edicion = lambda args: False      # el humano respondió "n"
    acepta.aprobar_edicion = lambda args: True        # el humano respondió "s"
    edicion = {"ruta": "src/puntos/cuenta.py", "antes": "a", "despues": "b"}
    assert not rechaza.evaluar("editar_archivo", edicion, 1).permitido
    assert "revisor humano" in rechaza.evaluar("editar_archivo", edicion, 1).motivo
    assert acepta.evaluar("editar_archivo", edicion, 1).permitido


def test_editar_archivo_exige_fragmento_unico(tmp_path):
    (tmp_path / "m.py").write_text("x = 1\nx = 1\n", encoding="utf-8")
    h = Herramientas(tmp_path)
    assert h.editar_archivo("m.py", "x = 1", "x = 2").startswith("ERROR")
    assert h.editar_archivo("m.py", "x = 1\nx = 1", "x = 2") == "OK: m.py modificado"


def test_ejecutar_pruebas_no_acepta_rutas_fuera_del_sandbox(tmp_path):
    with pytest.raises(PermissionError):
        Herramientas(tmp_path).ejecutar_pruebas("../../tests")
