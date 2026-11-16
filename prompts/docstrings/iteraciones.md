# Registro de iteraciones (completar con evidencia real)

## Estado inicial

Se completó la evaluación de v1 sobre los ocho casos del dataset.
La tasa base fue 0/8 casos aprobados (0.00 %). Las versiones v2 y v3
siguen pendientes de evaluación; sus mejoras todavía son hipótesis.

| Versión | Cambio propuesto | Hipótesis / aserciones | Evidencia real |
|---|---|---|---|
| v1 | Petición simple sin formato | Línea base | 0/8 (0.00 %). Véase resultados/evaluacion-v1.md |
| v2 | Rol, contexto, tarea, restricciones, JSON y datos delimitados | Mejorar A1/A2/A3 | 4/8 (50.00 %) con A3 corregida. Véase resultados/evaluacion-v2.md |
| v3 | Verificación de firma, convenciones de tipos/defaults, defensas y ejemplo | Mejorar A2-A6 | 8/8 (100.00 %). Véase resultados/evaluacion-v3.md |

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

V2 obtuvo inicialmente 3/8 casos aprobados (37.50 %). Se identificaron
dos falsos positivos en A3: el evaluador interpretaba el párrafo
posterior a Raises como otra excepción y rechazaba los nombres
*paradas y **opciones en Args.

Se corrigió el evaluador y se añadieron dos pruebas de regresión.
Después se reevaluaron v1 y v2 utilizando las mismas grabaciones,
sin modificarlas. Con A3 corregida, v2 obtuvo 4/8 (50.00 %):
aprobaron D1, D2, D4 y D8.

Persisten los siguientes incumplimientos:
- D3 y D5: se infirieron tipos de retorno, mientras que A4 exige
  "no especificado" cuando la función no tiene anotación de retorno.
- D6: valor_por_defecto contiene el número 2; el esquema exige
  una cadena con la expresión Python: "2".
- D7: valor_por_defecto contiene "normal"; para representar la
  expresión literal de Python debe conservar sus comillas internas.

V3 explicita las convenciones de anotaciones, valores predeterminados,
parámetros variables y formato del docstring. También incorpora
verificación interna de la firma, un ejemplo y restricciones frente
a instrucciones incluidas en el código fuente.

Hipótesis: estas precisiones resolverán los fallos de contrato que
persisten en D3, D5, D6 y D7. Se comprobará con ocho respuestas nuevas.

El aumento de 37.50 % a 50.00 % corresponde a corregir el evaluador;
no constituye una mejora del prompt ni una nueva generación.

Evidencia:
- [Reporte v2](resultados/evaluacion-v2.md)
- [Captura D6](grabaciones/v2/D6.txt)
- [Pruebas de A3](tests/test_correccion_a3.py)

Resultado de v3: 8/8 casos aprobados (100.00 %), frente a 4/8
(50.00 %) de v2 con el evaluador corregido. La mejora fue de
50 puntos porcentuales. D3, D5, D6 y D7 pasaron a aprobar;
D1, D2, D4 y D8 conservaron su aprobación. No se observaron
regresiones en los ocho casos del dataset.

### Selección final

Se selecciona v3 porque obtuvo 8/8 casos aprobados (100.00 %),
superando la meta del 85 % y conservando los casos aprobados por v2.
La comparación utiliza el mismo dataset, esquema y evaluador corregido.

Las instrucciones explícitas sobre anotaciones y representación de
valores predeterminados resolvieron los incumplimientos observados.
D8 también aprobó las aserciones del caso adversario.

Este resultado corresponde a ocho respuestas grabadas y a las
aserciones definidas. No garantiza corrección universal ni resistencia
frente a cualquier ataque. Se mantiene la revisión humana del contenido.

Evidencia:
- [Evaluación v3](resultados/evaluacion-v3.md)
- [Comparación de versiones](resultados/resumen.md)
- [Gráfico de tasas](resultados/tasas.svg)

El análisis de no determinismo se realizará con nueve generaciones
nuevas de v3 sobre D1, D4 y D8.

### Revisión del evaluador

La prueba `test_self_en_prosa_no_es_parametro_inventado` protege contra un falso
positivo de buscar globalmente la palabra self: aparecer en una explicación no lo
convierte en parámetro público. A3 analiza la sección Args. Esto es una prueba
preventiva; no se presenta como un fallo observado en una respuesta real.

Durante la comprobación técnica se corrigieron dos incompatibilidades reales con
promptfoo 0.118: las etiquetas pueden incluir ruta y plantilla, y el motor recorta
los extremos de variables/plantillas. El proveedor reconoce la etiqueta y compara
el mismo prompt normalizado que se entrega al asistente. Ninguna respuesta se altera.
