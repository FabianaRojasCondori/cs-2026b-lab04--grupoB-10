# Registro de iteraciones (completar con evidencia real)

## Estado inicial

Se completó la evaluación de v1 sobre los ocho casos del dataset.
La tasa base fue 0/8 casos aprobados (0.00 %). Las versiones v2 y v3
siguen pendientes de evaluación; sus mejoras todavía son hipótesis.

| Versión | Cambio propuesto | Hipótesis / aserciones | Evidencia real |
|---|---|---|---|
| v1 | Petición simple sin formato | Línea base | 0/8 (0.00 %). Véase resultados/evaluacion-v1.md |
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

La evaluación de v1 obtuvo 0/8 casos aprobados (0.00 %).
El reporte muestra A1–A6 rechazadas en los ocho casos.

En D1 se comprobó un incumplimiento del formato: la respuesta comienza
con "### Documentación" e incluye una función dentro de un bloque
Markdown de Python. El contrato requiere un objeto JSON, por lo que
esa respuesta no puede consumirse directamente.

Las seis aserciones comparten una validación inicial del JSON y del
esquema. Por ello, los rechazos de A2–A6 no se interpretan como seis
defectos independientes ni como evidencia de que la inyección tuvo éxito.

Para v2 se incorpora una instrucción explícita de devolver únicamente
JSON, sin Markdown ni texto adicional, y se especifican los campos
esperados. Se agregan rol, contexto y restricciones para documentar
los parámetros reales sin inventarlos.

Hipótesis: estas instrucciones permitirán cumplir el contrato y
evaluar después los parámetros, docstring y demás requisitos.
La mejora deberá comprobarse con ocho respuestas nuevas de v2.

Evidencia:
- [Reporte de v1](resultados/evaluacion-v1.md)
- [Respuesta original D1](grabaciones/v1/D1.txt)

Tasa antes: 0.00 %.
Tasa después y regresiones: pendientes de evaluar v2.

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
