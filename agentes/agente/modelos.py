"""El 'cerebro' del agente es intercambiable (patrón Strategy del Lab 07).

Protocolo: el modelo recibe el historial y devuelve un JSON con
  {"pensamiento": "...", "accion": "<herramienta>", "args": {...}}   o
  {"pensamiento": "...", "final": "<respuesta para el usuario>"}
"""
import json, os, re


class ModeloGrabado:
    """Reproduce decisiones grabadas de un asistente de IA (trayectoria JSON).
    Las herramientas se ejecutan de verdad; solo las decisiones vienen de la grabación."""
    def __init__(self, archivo):
        self._decisiones = json.load(open(archivo, encoding="utf-8"))
        self._i = 0

    def decidir(self, historial: list) -> dict:
        d = self._decisiones[self._i]
        self._i += 1
        return d


class ModeloAnthropic:
    """Proveedor real (opcional). Requiere ANTHROPIC_API_KEY y el paquete anthropic."""
    def __init__(self, modelo="claude-sonnet-4-5", sistema=""):
        import anthropic
        self._cliente, self._modelo, self._sistema = anthropic.Anthropic(), modelo, sistema

    def decidir(self, historial: list) -> dict:
        r = self._cliente.messages.create(model=self._modelo, max_tokens=1024, system=self._sistema,
                                          messages=historial, temperature=0)
        return json.loads(r.content[0].text)


class ModeloInteractivo:
    """Sin clave de API: el estudiante copia el contexto a su asistente de IA (Claude.ai, ChatGPT,
    Gemini, Copilot Chat), pega aquí la respuesta JSON y la decisión se graba para reproducirla.

    Adaptación EcoRecicla: si lo pegado NO es JSON válido (texto libre, bloque ```json, etc.) la
    decisión se graba tal cual como texto y se entrega al agente para que sea el CONTRATO quien la
    rechace (así se cuenta cuántas veces ocurrió, como pide E2.3). Una línea vacía se vuelve a pedir."""
    def __init__(self, grabar_en):
        self._archivo, self._decisiones = grabar_en, []

    @staticmethod
    def _interpretar(texto: str):
        limpio = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip(), flags=re.S)
        try:
            return json.loads(limpio)
        except json.JSONDecodeError:
            return texto.strip()          # el contrato lo rechazará: "la decisión debe ser un objeto JSON"

    def decidir(self, historial: list) -> dict:
        print("\n===== COPIE ESTO EN SU ASISTENTE DE IA =====")
        print(historial[0]["content"] if len(historial) == 1 else historial[-1]["content"])
        print("===== PEGUE LA RESPUESTA JSON (una línea) =====")
        texto = ""
        while not texto.strip():
            texto = input("> ")
        d = self._interpretar(texto)
        self._decisiones.append(d)
        with open(self._archivo, "w", encoding="utf-8") as f:
            json.dump(self._decisiones, f, ensure_ascii=False, indent=1)
        return d
