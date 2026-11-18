import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from aserciones import secciones, entradas_doc


def test_parrafo_exterior_no_es_excepcion():
    doc = (
        "Registra el peso.\n\n"
        "Raises:\n"
        "    ValueError: Si el peso no es positivo.\n\n"
        "La actualización cambia el estado.\n"
        "solicitud._cambiar_estado(Pesada())."
    )
    assert entradas_doc(secciones(doc)["Raises"]) == ["ValueError"]


def test_variadicos_con_asteriscos():
    doc = (
        "Resume la ruta.\n\n"
        "Args:\n"
        "    solicitud_id: Identificador.\n"
        "    *paradas: Paradas adicionales.\n"
        "    prioridad: Prioridad.\n"
        "    **opciones: Opciones adicionales.\n\n"
        "Returns:\n"
        "    dict: Argumentos agrupados."
    )
    assert entradas_doc(secciones(doc)["Args"]) == [
        "solicitud_id", "paradas", "prioridad", "opciones"
    ]
