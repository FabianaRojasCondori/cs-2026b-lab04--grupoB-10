# Apoyo para el cuestionario de Andrés

La división indica reparto 3/3/2, sin asignar números concretos. Si siguen el orden,
a persona 2 le corresponderían 4, 5 y 6. Confirmar ese reparto en el equipo.

## 4. Few-shot, chain-of-thought y el contrato

Few-shot proporciona varios ejemplos de entrada y salida para orientar formato y
comportamiento. Chain-of-thought busca favorecer razonamiento por pasos. El ejemplo
docente rechazó pedir que se exponga el razonamiento porque podía agregar texto
fuera del JSON y romper el contrato. Nuestro candidato v3 solicita comprobaciones
internas y únicamente el resultado estructurado. Incluye un ejemplo (one-shot).

## 5. Por qué 100 % no basta

El porcentaje solo describe los casos y aserciones utilizados. Un dataset pequeño
puede omitir entradas reales o ataques, y una aserción débil puede aceptar errores.
Además, el modelo puede producir respuestas diferentes en otras ejecuciones. Por
eso se revisa el contenido, se amplía el dataset y se comparan nuevas generaciones.

## 6. Falso positivo o falso negativo

No se ha observado todavía un fallo del evaluador sobre respuestas reales del
experimento. No afirmar lo contrario. Hay un riesgo prevenido y probado: una búsqueda
global de «self» marcaría una explicación correcta como parámetro inventado. A3
revisa los nombres de la sección Args, y el test correspondiente demuestra que
mencionar self en la explicación no dispara un rechazo. Si se observa otro error
real, describir su captura, aserción anterior, corrección y reevaluación de versiones.

## Insumo para la pregunta 8

Después de obtener nueve generaciones nuevas, usar los valores de
`no-determinismo/<mejor>/analisis.md`. No atribuir variabilidad si no fue observada.
Aunque las nueve respuestas coincidan, esa muestra no demuestra determinismo general.
