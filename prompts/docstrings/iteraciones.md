# Registro de iteraciones (completar con evidencia real)

## Estado inicial

No se ha realizado aún el experimento de generación. Las plantillas v2 y v3 se
entregan como candidatos de mejora; sus hipótesis no son resultados observados.

| Versión | Cambio propuesto | Hipótesis / aserciones | Evidencia real |
|---|---|---|---|
| v1 | Petición simple sin formato | Línea base | PENDIENTE |
| v2 | Rol, contexto, tarea, restricciones, JSON y datos delimitados | Mejorar A1/A2/A3 | PENDIENTE |
| v3 | Verificación de firma, convenciones de tipos/defaults, defensas y ejemplo | Mejorar A2-A6 | PENDIENTE |

v2 usa Persona y Template. v3 agrega Cognitive Verifier y un ejemplo de contrato
(one-shot, de la familia de aprendizaje por ejemplos). No se afirma que un único
ejemplo constituya varios ejemplos few-shot. v3 contiene los siete elementos:
rol, contexto, tarea, restricciones, ejemplo, formato y datos.

## Después de evaluar cada versión

Registrar: caso afectado, aserción, fragmento exacto del fallo, cambio propuesto,
hipótesis, tasa antes/después y si hay regresiones. Agregar enlaces relativos a los
reportes y capturas. No inventar tasas ni cambiar respuestas para satisfacer checks.

### v1 → v2

PENDIENTE: completar después de evaluar v1 y antes de capturar v2.

### v2 → v3

PENDIENTE: completar después de evaluar v2 y antes de capturar v3.

### Selección final

PENDIENTE: justificar la versión elegida. Si es <85 %, explicar fallo e hipótesis.

### Revisión del evaluador

La prueba `test_self_en_prosa_no_es_parametro_inventado` protege contra un falso
positivo de buscar globalmente la palabra self: aparecer en una explicación no lo
convierte en parámetro público. A3 analiza la sección Args. Esto es una prueba
preventiva; no se presenta como un fallo observado en una respuesta real.

Durante la comprobación técnica se corrigieron dos incompatibilidades reales con
promptfoo 0.118: las etiquetas pueden incluir ruta y plantilla, y el motor recorta
los extremos de variables/plantillas. El proveedor reconoce la etiqueta y compara
el mismo prompt normalizado que se entrega al asistente. Ninguna respuesta se altera.
