# Aporte de Andrés a la bitácora de IA — Lab 09

Responsable: Andrés, persona 2.
Asistente utilizado: ChatGPT; modelo específico no mostrado.

| N.º | Interacción | Hallazgo o propuesta | Decisión y evidencia |
|---|---|---|---|
| 1 | Solicité preparar la Tarea B a partir de la guía y el repositorio. | Se propusieron contrato, ocho casos, seis aserciones, prompts v1-v3 y herramientas de captura. | Se incorporó la estructura mediante el patch y se conservaron las respuestas reales por versión. |
| 2 | Compartí la evaluación de v1 y su respuesta D1. | V1 produjo texto y Markdown en lugar del JSON requerido; obtuvo 0/8. | Se incorporó en v2 un formato JSON explícito. Evidencia: resultados/evaluacion-v1.md y grabaciones/v1/D1.txt. |
| 3 | Compartí los fallos de v2 y las respuestas D4 y D7. | A3 rechazaba un párrafo explicativo posterior a Raises y los nombres *paradas y **opciones. | Se rechazó mantener esa validación original por sus falsos positivos. Se corrigió el evaluador, se añadieron dos pruebas y se reevaluaron las mismas capturas. Evidencia: tests/test_correccion_a3.py. |
| 4 | Revisé con el asistente los incumplimientos restantes de v2. | Faltaban instrucciones explícitas sobre anotaciones y representación textual de valores predeterminados. | Se precisó v3 antes de capturarla. V2 obtuvo 4/8 con A3 corregida y v3 obtuvo 8/8. Evidencia: resultados/resumen.md. |
| 5 | Compartí los errores de instalación y ejecución de promptfoo en Windows. | Hubo incompatibilidad entre Node 24 y el módulo nativo instalado, y un problema al localizar Python mediante una ruta con espacios. | Se utilizó Node 22 portátil y PROMPTFOO_PYTHON=python. La evaluación conjunta terminó con 12 éxitos, 12 fallos y cero errores. Evidencia: resultados/promptfoo.json. |

## No determinismo

Se obtuvieron nueve respuestas nuevas de v3: tres por cada caso D1, D4 y D8.
Los tres casos presentaron variaciones textuales y aprobaron las nueve respuestas.
La comparación detectó cambios en retorno/docstring para D1 y D8, y en
parametros/docstring para D4. Estos cambios de campos no demuestran por sí solos
un cambio de significado.

Evidencia: no-determinismo/v3/analisis.md.

## Alcance

Las grabaciones se conservaron sin corregir sus respuestas.
Las tasas describen el dataset y las aserciones utilizados; no garantizan
corrección universal. La revisión del significado y del idioma es humana.

Este aporte debe consolidarse con los de las otras personas en la bitácora
general del Lab 09.