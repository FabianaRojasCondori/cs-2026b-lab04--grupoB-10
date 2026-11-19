# Bitácora de uso de IA — Lab 09

**Responsable:** Persona 3  
**Proyecto:** EcoRecicla AQP  
**Actividad:** Integración del generador de docstrings, validación y pruebas.

| # | Interacción / consulta | Propuesta o resultado de la IA | Verificación y decisión |
|---|---|---|---|
| 1 | Análisis de la interfaz existente del proveedor de IA. | Se identificó la necesidad de integrar la generación de docstrings con el cliente LLM existente. | Se revisó `src/solicitudes/ia.py` y se comprobó que `ProveedorLLM` expone `clasificar_residuo(descripcion)`, no `completar(prompt)`. Se decidió no modificar esa interfaz de clasificación. |
| 2 | Diseño de la integración del generador de docstrings. | Se evaluó separar la generación de documentación de la clasificación de residuos. | Se implementó el puerto `ProveedorGeneracionDocstrings` y el adaptador `AdaptadorClienteGeneracion` en `src/solicitudes/generador_docstrings.py`. |
| 3 | Validación de las respuestas generadas por el modelo. | Se propuso comprobar que la salida cumpla un contrato estructurado antes de utilizarla. | Se implementó la lectura JSON estricta, la validación con JSON Schema y las comprobaciones A1-A6 mediante `prompts/docstrings/aserciones.py`. |
| 4 | Revisión de posibles instrucciones maliciosas dentro del código fuente. | Se evaluó el riesgo de que comentarios del código intenten modificar las instrucciones del generador. | Se incorporó `test_generador_rechaza_instrucciones_maliciosas` en `tests/test_generador_docstrings.py`. La prueba verifica que una respuesta manipulada que agrega `APROBADO` sea rechazada. |
| 5 | Pruebas de integración del generador. | Se planteó verificar tanto las respuestas válidas como las inválidas del proveedor. | Se añadieron pruebas con `ClienteLLMFalso` y con el proveedor grabado. Se comprueba la aceptación de respuestas válidas y el rechazo de respuestas inválidas. |

## Sugerencia de IA rechazada

Durante el análisis de integración se consideró reutilizar directamente el puerto `ProveedorLLM` existente para generar docstrings mediante una operación `completar(prompt)`.

**Motivo del rechazo:** al revisar `src/solicitudes/ia.py`, se comprobó que el contrato original únicamente define `clasificar_residuo(descripcion)`. Por tanto, asumir que existía `completar(prompt)` habría producido una integración incompatible y habría mezclado la clasificación de residuos con la generación de documentación.

**Decisión adoptada:** mantener intacta la interfaz de clasificación e implementar un puerto segregado, `ProveedorGeneracionDocstrings`, con su adaptador correspondiente.

**Evidencias:**
- `src/solicitudes/ia.py`
- `src/solicitudes/generador_docstrings.py`
- `prompts/docstrings/integracion-persona3.md`
- `tests/test_generador_docstrings.py`

## Reflexión

El uso de IA permitió apoyar el diseño de la integración, la validación de respuestas y la elaboración de pruebas. Sin embargo, las propuestas se contrastaron con las interfaces reales del proyecto y se verificaron mediante código y pruebas automatizadas. La decisión de separar el puerto de generación permitió incorporar la nueva funcionalidad sin alterar el contrato existente de clasificación de residuos.

*Nota: esta bitácora reúne una síntesis de las consultas, propuestas y decisiones relacionadas con el uso de IA durante el desarrollo. Algunas interacciones se reconstruyeron a partir del trabajo realizado y de las evidencias técnicas disponibles, por lo que no se presentan como una transcripción literal de cinco conversaciones independientes.*