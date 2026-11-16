# No determinismo: v3

Modelo declarado: ChatGPT (modelo no mostrado)

| Caso | Textos distintos / 3 | JSON distintos / JSON válidos | Aprobados / 3 | Campos con variaciones |
|---|---:|---|---:|---|
| D1 | 2 | 2 / 3 | 3 | retorno, docstring |
| D4 | 3 | 3 / 3 | 3 | parametros, docstring |
| D8 | 2 | 2 / 3 | 3 | retorno, docstring |

## Análisis automático en cinco líneas (revisar antes de entregar)

1. Se compararon tres respuestas nuevas en cada uno de D1, D4 y D8 con v3 y el mismo modelo declarado.
2. 3 de los tres casos presentaron diferencias textuales; la tabla distingue texto y JSON normalizado.
3. Los campos listados indican dónde cambió el JSON; el significado y el idioma se revisan manualmente.
4. Aprobaron 9/9 respuestas; una muestra de nueve respuestas no demuestra estabilidad general.
5. Las grabaciones fijan una salida para regresión reproducible; repetirlas en promptfoo no mide no determinismo.

Las sesiones y el modelo fueron declarados por el operador; no se verifican mediante una API.
