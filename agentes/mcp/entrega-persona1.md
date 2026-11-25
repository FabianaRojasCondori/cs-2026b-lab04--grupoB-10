# Entrega técnica — Andrés / Persona 1

Base examinada: `main`, commit `d1ca0c8d38c1843503a6d23a6449edc7fd216d96`.
Repositorio: FabianaRojasCondori/cs-2026b-lab04--grupoB-10.
Fecha de preparación: 2026-11-25. Alcance: E1/E2/E3 + preguntas 1/2/3.

## Archivos principales

| Entrega | Ubicación |
| --- | --- |
| E1, contratos y justificación | `diseno/catalogo-mcp.md` |
| E2, servidor stdio | `servidor_mcp/ecorecicla_mcp.py` |
| Adaptadores del dominio real | `servidor_mcp/servicio_demo.py` |
| Datos ficticios | `datos/demo.json` |
| Cliente de exploración | `cliente/explorar.py` |
| E3, 37 casos automatizados | `pruebas/test_servidor_mcp.py` |
| Evidencias reales de consola | `pruebas/evidencias/` |
| Procedimiento y estado de capturas | `pruebas/inspector.md` |

## Ejecución desde la raíz del repositorio

```bash
python -m pip install -r requirements-lab07.txt -r agentes/mcp/requirements.txt
python -m pytest -q agentes/mcp/pruebas
python -m pytest -q tests agentes/pruebas_agente agentes/mcp/pruebas
python agentes/mcp/cliente/explorar.py
python -m radon cc -s agentes/mcp/servidor_mcp
```

Verificado con Python 3.12, mcp 2.3.0, pytest 9.2.0, radon 6.0.1,
jsonschema 4.23.0, Node 24.22.3 e Inspector 2.16.0. Se recomienda Python 3.12.
Resultado en Linux: 37 pruebas MCP y 158 en la ejecución conjunta, todas aprobadas.
En Windows puede omitirse una prueba de enlaces simbólicos si faltan permisos.
Radon: complejidad máxima B. El explorador negoció el protocolo `2026-07-28`.
La llamada de fecha inválida del explorador muestra un error deliberado y esperado.

**E3 completado en la PC de Andrés:** se ejecutaron las pruebas,
con 37 pruebas MCP aprobadas y 158 pruebas aprobadas en la ejecución
conjunta. Se agregaron las tres capturas reales de MCP Inspector
y sus comentarios en `pruebas/inspector.md`.

## Contrato para Persona 2

- Ruta del servidor: `agentes/mcp/servidor_mcp/ecorecicla_mcp.py`.
- SDK: `from mcp import Client, StdioServerParameters`; transporte stdio.
- Tres herramientas con los argumentos y salidas de `diseno/catalogo-mcp.md`.
- Única escritura: `registrar_solicitud`; aplicar aprobación humana en el host
  y en la política del agente. No basta confiar en las anotaciones.
- Consulta propuesta para implementar en E4: «Consulta los puntos de vecino-7
  y la ruta de Cayma del 2026-11-25; si corresponde, pide mi aprobación para
  registrar una solicitud demo de 10 litros de PLASTICO en Calle Demo Z 900».
- Los registros persisten entre sesiones y son visibles en rutas. Las consultas
  por sí solas no crean el directorio. Usar datos ficticios y no cambiar a números
  telefónicos reales. Repetir una creación genera un UUID nuevo.
- El cliente de P1 explora directamente y no escribe una traza de E4. Persona 2
  incorpora `espia.py`, el adaptador y `traza_mcp.py` de los recursos docentes.
- Los recursos docentes son AgroConecta: reemplazar rutas/URIs, no copiar sus
  resultados como si fueran evidencia de EcoRecicla.

## Coordinación con Persona 3

No se modifica el README raíz, ADR-011, auditor, configuración de host ni tag:
son entregas de P2/P3. Las respuestas 1–3 están separadas para consolidarlas.
P3 crea `v1.1-mcp` cuando estén integradas todas las entregas, no al subir P1.

Notas de la asistencia para la bitácora grupal: se inspeccionaron los PDF y el
ZIP docente; se leyeron los módulos reales del repositorio; se implementó la
adaptación al dominio; se comprobó persistencia entre instancias y colisiones de
UUID; se verificó el catálogo y los errores por Inspector CLI. Se descartó dar
por completadas las capturas porque la interfaz gráfica no fue accesible en este
entorno. Esto describe trabajo de una sesión asistida, no cinco conversaciones
independientes ni consultas reales en un host con LLM.
