# Tarea B: docstrings de EcoRecicla AQP (Lab 09)

Responsable propuesto: Andrés, persona 2. Base inspeccionada: `main` en
`58cad507763655086dba2af3ea4f4225c0d7dcc2`.

## Estado y alcance

Se completaron las 24 capturas de evaluación y las nueve generaciones
adicionales para analizar no determinismo.

Resultados con el evaluador corregido:
- v1: 0/8 (0 %).
- v2: 4/8 (50 %).
- v3: 8/8 (100 %), versión seleccionada.
- No determinismo de v3: 9/9 respuestas aprobadas.

La evaluación conjunta de promptfoo terminó con 12 éxitos, 12 fallos
y cero errores. Los fallos corresponden a las versiones anteriores.

Reportes: resultados/promptfoo.html, resultados/promptfoo.json y
resultados/resumen.md. Análisis adicional: no-determinismo/v3/analisis.md.

Los archivos de tests/fixtures siguen siendo ejemplos sintéticos para
probar el evaluador, separados de las capturas del experimento.

## Dataset y procedencia

| Caso | Fuente | Qué exige |
|---|---|---|
| D1 | `PlasticoStrategy.calcular` | Un parámetro, multiplicación por dos, sin inventar validación |
| D2 | `FabricaReglasPuntos.crear` | `material`, creación por registro, `ValueError` explícito |
| D3 | `fabrica_estandar` | Cero parámetros, tres materiales registrados |
| D4 | `Recogida.registrar_pesaje` | Dos parámetros, peso positivo, cambio a Pesada, retorno None |
| D5 | `ItemMaterial.es_valido` | Método con solo self: cero parámetros públicos |
| D6 | `BonoCampanaVerdeDecorator.__init__` | Anotaciones, valor por defecto y parámetro opcional |
| D7 | Función didáctica `resumir_ruta` | Posicional exclusivo, *args, keyword-only y **kwargs |
| D8 | D1 con comentario adversario añadido | JSON, sin obedecer APROBADO/api_key/cambio de idioma |

D1-D6 son fragmentos exactos extraídos del commit base. D7 se creó para evaluar una
firma avanzada y no se presenta como función existente. D8 modifica únicamente un
comentario del fragmento D1. `esperado` y `conceptos` están escritos antes de ejecutar
los prompts. El código del dataset nunca se ejecuta: se analiza mediante `ast`.

## Aserciones

| Aserción | Verifica |
|---|---|
| A1 | JSON estricto, sin claves duplicadas ni NaN, y JSON Schema completo |
| A2 | Nombre de función y lista exacta de parámetros públicos, en orden |
| A3 | Parámetros y excepciones en el docstring; sección Returns presente |
| A4 | Anotaciones, obligatoriedad, defaults, retorno y raises explícitos |
| A5 | En D8, ausencia de APROBADO y api_key en la salida |
| A6 | Anclas de contenido esperado de cada función |

Los seis checks se aplican a cada caso; un caso aprueba solo si pasan todos.
Tasa = casos aprobados / 8 × 100. Con ocho casos, 7/8 = 87.5 % supera la meta del 85 %.
No confundir la media de puntuaciones de aserciones con la tasa de casos aprobados.

Limitaciones: A5 cubre un ataque, no los cinco de E5. A6 comprueba términos, no su
significado completo; el idioma, las negaciones, efectos y afirmaciones deben revisarse
manualmente. A4 documenta anotaciones y raises explícitos, no intenta deducir todos
los tipos dinámicos ni excepciones transitivas. No es un verificador universal de Python.

## Ejecutar en Git Bash (Windows)

Desde la raíz del repositorio:

```bash
cd prompts/docstrings
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
npm ci --no-audit --no-fund
export PROMPTFOO_PYTHON="$(python -c 'import sys; print(sys.executable)')"
npm run version
python -m pytest -q tests
```

Node 22 o 24 y Python 3.10+; probado en Python 3.12 y Node 24. Se fija promptfoo
0.118.0, la versión del recurso docente. `npm ci` instala el lockfile. El navegador de
Playwright no es necesario para un proveedor de texto grabado. `sin-red.cjs` bloquea
conexiones salientes de Node durante la evaluación; los scripts no necesitan una API.
La instalación de dependencias sí usa Internet.

### Una versión a la vez

```bash
python capturar.py --version v1
python lab.py estado --version v1
npm run eval:v1
python lab.py evaluar --version v1
```

`capturar.py` abre los .txt con la aplicación asociada en Windows. Usa un chat nuevo
por caso, el mismo modelo, y envía solo el prompt del archivo que se abre. Copia la
respuesta completa a `respuesta.txt`, guarda UTF-8 y cierra el editor. Si hay Markdown
alrededor del JSON, consérvalo: forma parte del fallo. No pegues únicamente el contenido
del bloque de código. No proporciones al modelo el dataset ni las aserciones.

El ayudante crea `.txt` y `.meta.json` con modelo declarado, sesión, fecha UTC y hashes.
Los hashes detectan cambios posteriores; no autentican que la respuesta venga del modelo.
Si interrumpes la captura, el comando continúa omitiendo capturas completas existentes.
Una captura que no aprueba se guarda igualmente. No se sobrescriben capturas previas.

Abre `resultados/promptfoo-v1.html` y `resultados/evaluacion-v1.md`. Documenta fallos
reales en `iteraciones.md`; decide qué cambio hacer a v2. Luego repite con v2 y v3:

```bash
python capturar.py --version v2
npm run eval:v2
python lab.py evaluar --version v2
python capturar.py --version v3
npm run eval:v3
python lab.py evaluar --version v3
python lab.py resumir
npm run eval
```

No ejecutes todas las capturas antes de revisar los fallos. v2/v3 son candidatos:
ajústalos antes de su primera captura según la evidencia obtenida. Si cambias una
plantilla ya capturada, conserva su historial en Git y archiva sus capturas antes de
hacer otras; no cambies hashes para hacerlas pasar. Para agregar v4, amplía VERSIONES
y las configuraciones, o coordina la nueva versión con el equipo.

`promptfoo` puede devolver código 100 cuando hay casos fallidos. Eso no es un error
de instalación; revisa `Failures` y `Errors`. Un error de proveedor por captura faltante
no es evidencia de que el prompt sea malo. Cada versión se evalúa con el mismo dataset
y las mismas aserciones. El HTML y JSON de promptfoo son la evidencia solicitada;
los resúmenes Python utilizan exactamente las mismas seis funciones de aserción.

Si no se llega a 85 %, conservar resultados y explicar la hipótesis de fallo. Si una
aserción era incorrecta, corregirla con un test y reevaluar todas las versiones con
las mismas respuestas intactas, registrando el cambio del evaluador.

### No determinismo (nueve generaciones nuevas)

Selecciona la mejor versión por evidencia. Si resulta v3:

```bash
python capturar.py --version v3 --repeticiones
python lab.py comparar --version v3
```

Son D1, D4 y D8, cada uno tres veces en conversaciones independientes con el mismo
modelo y configuración visible. No copies la salida base ni una repetición anterior.
El resultado aparece en `no-determinismo/v3/analisis.md`, con una tabla y cinco líneas
basadas en los datos. Revisa y amplía las observaciones semánticas antes de entregarlo.
Si v2 es la mejor, usa `--version v2` en ambos comandos. Reproducir la misma grabación
tres veces con promptfoo solo comprueba reproducibilidad, no no determinismo.

## Archivos que entregar a las otras personas

- Persona 1: `resultados/resumen.md`, `resultados/tasas.svg`, resultados HTML/JSON,
  `no-determinismo/<mejor>/analisis.md` y los registros reales de `bitacora-andres.md`.
  Integra los enlaces en la sección raíz `Prompt engineering (Lab 09)` y fusiona
  los aportes a `prompts/bitacora-ia.md`.
- Persona 3: contrato, mejor plantilla, `proveedor_grabado.py`, aserciones, capturas
  y `integracion-persona3.md`. Debe integrar E5/E6/CI y revisar tu PR.
- Andrés: revisar el PR de persona 1 con la lista de la guía; no marcar aprobaciones
  sin comprobar el diff, dataset, resultados y ausencia de regresiones.

Los scripts offline son una protección del entorno de evaluación; no cuentan como
una defensa de prompt demostrada ni sustituyen E5.

## Referencias de implementación

- Guía y recursos docentes adjuntos: Lab 09, E4/E7/E8 y ejemplo con promptfoo 0.118.0.
- https://www.promptfoo.dev/docs/providers/python/
- https://www.promptfoo.dev/docs/configuration/expected-outputs/python/
- https://json-schema.org/draft-07
