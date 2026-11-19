
import ast
import json
from abc import ABC, abstractmethod
from pathlib import Path

from jsonschema import Draft7Validator, ValidationError


# Rutas del proyecto
RAIZ = Path(__file__).resolve().parents[2]
CARPETA_PROMPTS = RAIZ / "prompts" / "docstrings"

VERSIONES_PERMITIDAS = {"v1", "v2", "v3"}


class SalidaDocstringsInvalida(Exception):
    """Se produce cuando la respuesta del proveedor no cumple el contrato."""
    pass


class ProveedorGeneracionDocstrings(ABC):
    """Puerto independiente para generar documentación mediante un LLM."""

    @abstractmethod
    def completar(self, prompt: str) -> str:
        pass


class AdaptadorClienteGeneracion(ProveedorGeneracionDocstrings):
    """Adapta el cliente existente a la interfaz de generación de docstrings."""

    def __init__(self, cliente_sdk):
        self.cliente_sdk = cliente_sdk

    def completar(self, prompt: str) -> str:
        resultado = self.cliente_sdk.generate(prompt)

        if not isinstance(resultado, dict):
            raise RuntimeError("Respuesta inesperada del proveedor")

        texto = resultado.get("response")

        if not isinstance(texto, str) or not texto.strip():
            raise RuntimeError("El proveedor devolvió una respuesta vacía")

        return texto.strip()


class GeneradorDocstrings:
    """Genera y valida documentación de funciones Python."""

    def __init__(self, proveedor, version="v3"):
        if version not in VERSIONES_PERMITIDAS:
            raise ValueError("Versión de prompt no permitida")

        self.proveedor = proveedor
        self.version = version

        archivo_prompt = CARPETA_PROMPTS / f"{version}.txt"
        archivo_esquema = CARPETA_PROMPTS / "esquema.json"

        self.plantilla = archivo_prompt.read_text(encoding="utf-8")

        self.esquema = json.loads(
            archivo_esquema.read_text(encoding="utf-8")
        )

        self.validador = Draft7Validator(self.esquema)

    @staticmethod
    def nombre_funcion(codigo):
        """Obtiene el nombre real de la función sin ejecutar el código."""

        arbol = ast.parse(codigo)

        funciones = [
            nodo for nodo in arbol.body
            if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(funciones) != 1:
            raise ValueError(
                "Se esperaba exactamente una función de nivel superior"
            )

        return funciones[0].name

    @staticmethod
    def cargar_json_estricto(texto):
        """Rechaza claves duplicadas y valores no permitidos por JSON."""

        def detectar_duplicados(pares):
            resultado = {}

            for clave, valor in pares:
                if clave in resultado:
                    raise ValueError("El JSON contiene claves duplicadas")

                resultado[clave] = valor

            return resultado

        def rechazar_constante(valor):
            raise ValueError(f"Constante JSON no permitida: {valor}")

        return json.loads(
            texto,
            object_pairs_hook=detectar_duplicados,
            parse_constant=rechazar_constante
        )

    
    def generar(self, funcion, codigo, variables_evaluacion=None):
        """Genera documentación y verifica su estructura y contenido."""

        if not isinstance(funcion, str) or not funcion.strip():
            raise ValueError("La función no puede estar vacía")

        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError("El código no puede estar vacío")

        nombre_real = self.nombre_funcion(codigo)

        if funcion != nombre_real:
            raise ValueError("El nombre indicado no coincide con el código")

        plantilla = self.plantilla.strip()

        prompt = (
            plantilla
            .replace("{{funcion}}", funcion.strip())
            .replace("{{codigo}}", codigo.strip())
        )

        try:
            respuesta = self.proveedor.completar(prompt)
            resultado = self.cargar_json_estricto(respuesta)

            # A1: validar la estructura del JSON.
            self.validador.validate(resultado)

            # A2-A4: comprobar la firma, parámetros, tipos y secciones.
            from prompts.docstrings.aserciones import evaluar

            variables = variables_evaluacion or {
                "funcion": funcion,
                "codigo": codigo,
                "es_metodo": False,
                "tipo_caso": "normal",
            }

            evaluacion = evaluar(respuesta, variables)

            if not all(
                resultado["pass"]
                for resultado in evaluacion.values()
            ):
                fallidas = [
                    nombre
                    for nombre, resultado in evaluacion.items()
                    if not resultado["pass"]
                ]

                raise ValueError(
                    "Fallaron las validaciones: " + ", ".join(fallidas)
                )
            
            return resultado

        except (json.JSONDecodeError, ValidationError, ValueError) as error:
            raise SalidaDocstringsInvalida(
                f"Respuesta rechazada para {nombre_real}: "
                f"{type(error).__name__}: {error}"
            ) from error
