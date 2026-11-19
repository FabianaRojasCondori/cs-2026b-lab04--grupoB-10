# Bitácora de IA - Tarea A: criterios de aceptación

## Rol y alcance

Se utilizó IA para ayudar a diseñar y verificar los prompts de EcoRecicla AQP
para la generación de criterios de aceptación en Gherkin.

La revisión final fue humana: se comprobaron los identificadores, el esquema,
el cumplimiento de INVEST, la observabilidad de los escenarios y la resistencia
a instrucciones adversarias.

## Interacciones realizadas

| Interacción | Resultado |
|---|---|
| Crear la grabación inicial de los ocho casos | Se generaron respuestas base para las versiones v1, v2 y v3. |
| Mejorar la salida de v2 | Se agregó estructura JSON explícita y reglas básicas para el contrato de salida. |
| Mejorar la salida de v3 | Se agregó rol, contexto, tarea INVEST, restricciones, few-shot y delimitación de la historia como dato. |
| Validar las grabaciones | Se comprobó el JSON, el esquema, las pistas, el tipo de escenarios y la resistencia a la inyección en HU-08. |

## Anatomía aplicada

- **Rol:** se indicó al asistente que actuaría como analista QA.
- **Contexto:** se describió EcoRecicla AQP y sus actores principales.
- **Tarea:** se pidió evaluar INVEST y generar escenarios Gherkin.
- **Restricciones:** se prohibió inventar reglas y describir implementación.
- **Ejemplos:** v3 incluye un ejemplo de salida verificable.
- **Formato:** la respuesta debe ser exclusivamente un objeto JSON válido.
- **Datos delimitados:** v3 encierra la historia entre `<historia>` y `</historia>`.

Los elementos agregados permitieron mejorar el contrato estructurado y reducir
las respuestas ambiguas o fuera de formato.

## Decisiones y verificaciones

- HU-07 se clasificó como `invest_ok: false` y no contiene escenarios.
- HU-08 conserva el identificador HU-08 y no obedece las instrucciones insertadas.
- Las historias cumplidas contienen al menos un escenario de éxito y uno de
  error o borde.
- Las grabaciones v2 y v3 cumplen el esquema definido en `esquema.json`.
- Las grabaciones se conservaron sin corregir respuestas humanas posteriores.