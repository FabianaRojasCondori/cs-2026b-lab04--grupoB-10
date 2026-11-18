# Contrato de integración para persona 3

## Interfaz existente: diferencia con el ejemplo docente

En el commit base, `src/solicitudes/ia.py::ProveedorLLM` expone
`clasificar_residuo(descripcion: str) -> str`. **No expone `completar(prompt)`.**
No copiar el generador de AgroConecta esperando que ese método exista. Persona 3
puede ampliar el puerto con una operación genérica y adaptar las implementaciones,
o introducir un puerto segregado de generación enlazado al proveedor actual.
Debe documentar la decisión, preservar clasificación/caché/guardrails y ejecutar
las pruebas anteriores. Este paquete no modifica la interfaz de producción.

## Insumos disponibles

- Plantilla: `prompts/docstrings/<version>.txt`; placeholders `funcion`, `codigo`.
- Contrato: `prompts/docstrings/esquema.json`.
- Salida: JSON completo con función, resumen, parámetros, retorno, excepciones y docstring.
- Evaluador: `prompts.docstrings.aserciones.evaluar(texto, variables)` devuelve A1-A6;
  la integración debe rechazar salida inválida antes de presentarla o usarla.
- `proveedor_grabado.py::call_api` es un adaptador de **promptfoo**, no implementa
  automáticamente el puerto `ProveedorLLM` de la aplicación.
- Capturas: `grabaciones/<version>/<caso>.txt` más `.meta.json`.
- Caso D8: solo un ataque; completar los cinco de E5 y el antes/después por separado.

## CI sugerida (insertar en el workflow de persona 3)

Usar Node 22/24 y Python 3.12. Desde `prompts/docstrings`:

```bash
python -m pip install -r requirements.txt
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
npm ci --no-audit --no-fund
export PROMPTFOO_PYTHON="$(python -c 'import sys; print(sys.executable)')"
python -m pytest -q tests
python lab.py estado --version v3
npm run eval:v3
```

Sustituir v3 por la versión efectivamente elegida. El comando falla si falta una
captura: completar la evidencia antes de exigir verde. v1/v2 pueden tener fallos
esperados y se conservan como reportes de comparación; no exigir 100 % a la línea base.
Si la mejor versión tiene 7/8 casos, promptfoo devolverá código de fallo por ese caso.
El workflow debe distinguir errores de infraestructura, regresiones y un umbral
explícito >=85 %, en lugar de usar `|| true` que ocultaría todo.

No se incluye aquí un segundo workflow para evitar competir con el archivo
`.github/workflows/prompts.yml` asignado a persona 3. Los tests de este paquete no
sustituyen las dos pruebas de integración de E6 con el puerto real.
