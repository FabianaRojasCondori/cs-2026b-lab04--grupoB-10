## Prompt engineering (Lab 09) — Tarea A

### Estructura
- `prompts/criterios/v1.txt` — versión inicial del prompt (sin formato JSON)
- `prompts/criterios/v2.txt`, `v3.txt` — versiones posteriores (ver E3)
- `prompts/criterios/esquema.json` — contrato de salida (JSON Schema, draft-07)
- `prompts/criterios/casos.yaml` — dataset: 8 casos (6 normales + HU-07 no INVEST + HU-08 adversario con inyección)
- `prompts/criterios/grabaciones/<version>/<id>.txt` — respuestas grabadas de v1 (texto libre)
- `prompts/criterios/grabaciones/<version>/<id>.json` — respuestas grabadas de v2 y v3 (JSON estructurado)
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

### Progresión

| Versión | Casos evaluados | Pass rate | Δ vs anterior |
|---|---|---|---|
| v1 (baseline) | 8 | **0.00 %** (0/8) | - |
| v2 | 8 | **100.00 %** (8/8) | +100 pp |
| v3 (final) | 8 | **100.00 %** (8/8) | 0 pp (sin regresión) |
| **Total** | **24** | **66.67 %** (16/24), 0 errores | - |

**Meta del laboratorio: ≥ 85 % en la versión final.**
La métrica se calcula **por versión** siguiendo la Figura 5 de la guía
(v1=0 %, v2=25 %, v3=87.5 %, v3.1=100 %). **v3 = 100 % supera la meta.**

### Análisis de fallos de v1

Los 5 asserts fallan por una **causa raíz única**: v1 no produce JSON, produce texto libre ("1. Dado que el vecino…"). `is-json` la rechaza, y los cuatro asserts `javascript` que hacen `JSON.parse(output)` también fallan antes de evaluar su lógica.

Cada cambio de v2/v3 ataca un fallo concreto:
- **v2** introduce rol + contexto + formato JSON explícito → pasa A1 (contrato).
- **v3** agrega tarea paso a paso (Cognitive Verifier), preguntas si la historia
  no cumple INVEST (Flipped Interaction), few-shot, y delimita los datos con
  `<historia>…</historia>` para resistir inyecciones.

### Anatomía y patrones aplicados (rúbrica E3)

| Elemento (de 7) | v2 | v3 |
|---|---|---|
| Rol | ✅ | ✅ |
| Contexto | ✅ | ✅ |
| Tarea | ✅ | ✅ |
| Restricciones | ✅ | ✅ (+ no-implementación, no-obedecer inyección) |
| Ejemplos (few-shot) | ❌ | ✅ |
| Formato | ✅ | ✅ |
| Datos delimitados | ❌ (`{{historia}}` suelto) | ✅ (`<historia>…</historia>`) |
| **Total** | **5/7** | **7/7** |

| Patrón (Tabla 2) | v2 | v3 |
|---|---|---|
| Persona | ✅ | ✅ |
| Template | ✅ | ✅ |
| Cognitive Verifier | ❌ | ✅ |
| Flipped Interaction | ❌ | ✅ |
| **Total** | **2** | **4** |

### Correcciones al evaluador (meta-evaluación)

| # | Aserción | Falso positivo detectado | Corrección |
|---|---|---|---|
| 1 | `criterios-observables` | Sensible a acentos: si la respuesta usa "formalización" (con tilde) y el hint es `"formalizacion"` (sin tilde), la aserción la marca FAIL aunque sea correcta. | Documentado. Fix: normalizar NFD + quitar diacríticos antes de comparar. |
| 2 | `criterios-observables` | No verifica nada cuando `invest_ok=false` (siempre devuelve `true` para HU-07 por `pistas: []`). | Documentado. Fix: exigir ≥1 pregunta y 0 escenarios cuando `invest_ok=false`. |
| 3 | `resistencia-a-inyeccion` | Hardcodea `"HU-08"`; un caso adversario futuro no sería verificado. | Documentado como limitación conocida. |

### No regresión

Ningún caso que v1 o v2 aprobaban falla en v3.
v2 y v3 pasan los mismos 8/8 casos (HU-01 a HU-08). Sin regresiones.