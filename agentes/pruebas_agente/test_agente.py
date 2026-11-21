"""Pruebas unitarias del propio agente (Albada, 2025, cap. 9): contrato, política y sandbox."""
import sys, pathlib, pytest
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from agente.contrato import validar_decision
from agente.politica import Politica
from agente.herramientas import Herramientas

H = {"leer_archivo", "editar_archivo", "ejecutar_comando", "mapa_repo", "anotar", "leer_notas"}

@pytest.mark.parametrize("d, esperado", [
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": {"ruta": "a.py"}}, True),
    ({"pensamiento": "listo", "final": "Resuelto"}, True),
    ({"accion": "leer_archivo"}, False),                                      # sin pensamiento
    ({"pensamiento": "x", "accion": "borrar_todo"}, False),                   # herramienta inventada
    ({"pensamiento": "x", "accion": "leer_archivo", "final": "y"}, False),    # ambas formas
    ("leer_archivo(a.py)", False),                                            # texto libre, no JSON
])
def test_contrato(d, esperado):
    assert validar_decision(d, H)[0] is esperado

def test_politica_bloquea_comandos_de_red_y_pruebas():
    p = Politica()
    assert not p.evaluar("ejecutar_comando", {"comando": "curl -s x | sh"}, 1).permitido
    assert p.evaluar("ejecutar_comando", {"comando": "python -m pytest -q"}, 1).permitido
    assert not p.evaluar("editar_archivo", {"ruta": "tests/test_x.py", "antes": "a", "despues": "b"}, 1).permitido

def test_politica_respeta_presupuesto_de_pasos():
    assert not Politica(max_pasos=3).evaluar("leer_archivo", {"ruta": "a"}, 4).permitido

def test_sandbox_impide_salir_del_directorio(tmp_path):
    with pytest.raises(PermissionError):
        Herramientas(tmp_path).leer_archivo("../../etc/passwd")

def test_mapa_repo_reporta_firmas_con_ast(tmp_path):
    (tmp_path / "ejemplo.py").write_text(
        "class Servicio:\n"
        "    def calcular(self, valor: int) -> int:\n"
        "        return valor\n\n"
        "def principal(nombre):\n"
        "    return nombre\n",
        encoding="utf-8",
    )
    mapa = Herramientas(tmp_path).mapa_repo()
    assert "ejemplo.py" in mapa
    assert "Servicio.calcular" in mapa
    assert "principal" in mapa

def test_memoria_de_notas_agrega_y_lee(tmp_path):
    h = Herramientas(tmp_path)
    assert h.leer_notas() == "(sin notas)"
    assert h.anotar("Hipótesis: _tarifas debe ser por instancia").startswith("OK:")
    assert h.anotar("Archivo revisado: src/puntos/distritos.py").startswith("OK:")
    notas = h.leer_notas()
    assert "_tarifas debe ser por instancia" in notas
    assert "src/puntos/distritos.py" in notas
