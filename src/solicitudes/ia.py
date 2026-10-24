"""E5: Componente de IA aislado tras Strategy, Decorator y Chain of Responsibility."""
from abc import ABC, abstractmethod


class ProveedorLLM(ABC):
    """Strategy / Puerto para el modelo de lenguaje."""
    @abstractmethod
    def clasificar_residuo(self, descripcion: str) -> str:
        pass


class AdaptadorClienteLLM(ProveedorLLM):
    """Adapter para el cliente simulado."""
    def __init__(self, cliente_sdk):
        self.cliente_sdk = cliente_sdk

    def clasificar_residuo(self, descripcion: str) -> str:
        resultado = self.cliente_sdk.generate(descripcion)
        return resultado.get("response", "").strip()


class ConCacheLLM(ProveedorLLM):
    """Decorator: evita consultar al LLM ante descripciones idénticas."""
    def __init__(self, proveedor: ProveedorLLM):
        self._proveedor = proveedor
        self._cache = {}

    def clasificar_residuo(self, descripcion: str) -> str:
        clave = descripcion.strip().lower()
        if clave not in self._cache:
            self._cache[clave] = self._proveedor.clasificar_residuo(descripcion)
        return self._cache[clave]


class Guardrail(ABC):
    """Manejador de la Chain of Responsibility para validar la salida de la IA."""
    def __init__(self, siguiente=None):
        self._siguiente = siguiente

    def validar(self, clasificacion: str) -> str:
        procesado = self._aplicar(clasificacion)
        if self._siguiente:
            return self._siguiente.validar(procesado)
        return procesado

    @abstractmethod
    def _aplicar(self, clasificacion: str) -> str:
        pass


class SinResiduosPeligrosos(Guardrail):
    """Bloquea materiales no aptos para recolección domiciliaria."""
    PELIGROSOS = ["BATERIA", "PILA", "QUIMICO", "MEDICAMENTO", "EXPLOSIVO"]

    def _aplicar(self, clasificacion: str) -> str:
        for item in self.PELIGROSOS:
            if item in clasificacion.upper():
                raise ValueError(f"Guardrail: material no reciclable o peligroso '{item}' detectado")
        return clasificacion


class CategoriaPermitida(Guardrail):
    """Garantiza que la clasificación pertenezca a categorías municipales válidas."""
    VALIDAS = {"PLASTICO", "VIDRIO", "PAPEL", "CARTON", "METAL"}

    def _aplicar(self, clasificacion: str) -> str:
        categoria = clasificacion.upper().strip()
        if categoria not in self.VALIDAS:
            raise ValueError(f"Guardrail: categoría '{categoria}' no admitida en EcoRecicla AQP")
        return categoria


class ClasificadorResiduosIA:
    """Servicio cliente que combina la estrategia de IA y la cadena de guardrails."""
    def __init__(self, proveedor: ProveedorLLM, guardrail: Guardrail):
        self.proveedor = proveedor
        self.guardrail = guardrail

    def clasificar(self, texto_usuario: str) -> str:
        salida_bruta = self.proveedor.clasificar_residuo(texto_usuario)
        return self.guardrail.validar(salida_bruta)