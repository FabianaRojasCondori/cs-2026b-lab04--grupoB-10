"""Sandbox del agente: una copia parcial del repositorio EcoRecicla en agentes/trabajo/.

Regla de oro: el agente NUNCA toca el repositorio real. Trabaja sobre esta copia y un humano
decide qué cambios pasan a src/ (ver README de agentes/).

Solo se copian las carpetas relevantes para los issues (ingeniería de contexto, lienzo decisión 4):
src/, issues/, pytest.ini y las pruebas que no dependen de prompts/ ni fitness/.
"""
import pathlib, shutil

RAIZ = pathlib.Path(__file__).resolve().parent          # .../agentes
REPO = RAIZ.parent                                       # raíz del repositorio
TRABAJO = RAIZ / "trabajo"
PRUEBAS = ("test_issue_01.py", "test_issue_02.py", "test_issue_03.py",
           "test_patrones.py", "test_comportamiento.py")
IGNORAR = shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc")


def preparar_sandbox() -> pathlib.Path:
    """Recrea agentes/trabajo/ desde el repositorio real y devuelve su ruta."""
    shutil.rmtree(TRABAJO, ignore_errors=True)
    TRABAJO.mkdir()
    shutil.copytree(REPO / "src", TRABAJO / "src", ignore=IGNORAR)
    shutil.copytree(REPO / "issues", TRABAJO / "issues", ignore=IGNORAR)
    (TRABAJO / "tests").mkdir()
    for nombre in PRUEBAS:
        shutil.copy(REPO / "tests" / nombre, TRABAJO / "tests" / nombre)
    shutil.copy(REPO / "pytest.ini", TRABAJO / "pytest.ini")
    return TRABAJO
