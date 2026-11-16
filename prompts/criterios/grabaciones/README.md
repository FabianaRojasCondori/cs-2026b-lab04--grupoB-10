## Prompt engineering (Lab 09) — Tarea A

### Estructura
- `prompts/criterios/v1.txt` — versión inicial del prompt (sin formato JSON)
- `prompts/criterios/v2.txt`, `v3.txt` — versiones posteriores (ver E3)
- `prompts/criterios/esquema.json` — contrato de salida (JSON Schema, draft-07)
- `prompts/criterios/casos.yaml` — dataset: 8 casos (6 normales + HU-07 no INVEST + HU-08 adversario con inyección)
- `prompts/criterios/grabaciones/<version>/<id>.txt` — respuestas grabadas del asistente de IA
- `prompts/proveedor_grabado.py` — provider de promptfoo que lee las grabaciones (sin clave de API)
- `promptfooconfig.yaml` — aserciones (contrato JSON, INVEST, observables, sin implementación, resistencia a inyección)

### Línea base v1 (E2)

- **Comando:** `npx promptfoo eval`
- **Fecha de ejecución:** 2026-11-16
- **promptfoo:** 0.120.19
- **Prompt evaluado:** `prompts/criterios/v1.txt` ("Escribe criterios de aceptación para esta historia de usuario: {{historia}}")
- **Proveedor de respuestas grabadas:** asistente de IA (ver `bitacora-ia.md`)
- **Resultado:** **0 passed · 8 failed · 0 errors · 0.00 %**
- **Motivo del 0 %:** v1 pide texto libre; la salida no es JSON y no cumple `esquema.json`. Fallan `is-json` y todos los asserts que hacen `JSON.parse(output)` (regla-invest, criterios-observables, sin-detalles-de-implementacion, resistencia-a-inyeccion).
- **Evidencia:** `resultados-v1.json`, `resultados.html`

### Progresión (se completa en E3)
- v1: **0.00 %** ← línea base
- v2: _pendiente (commit E3)_
- v3: _pendiente (commit E3)_
