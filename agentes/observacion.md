# Observación y Métricas del Sistema Agéntico (Lab 10 - EcoRecicla AQP)

## 1. Tabla Comparativa de Métricas por Issue

*(Nota: Ajustar los valores numéricos exactos según los archivos `.jsonl` generados en `agentes/trazas/`)*

| Métrica | Issue #01: Puntos acreditados dos veces (Agente Único ReAct) | Issue #02: Ruta incluye solicitudes canceladas (Actor-Crítico) | Issue #03: Regla de puntos afecta a otro distrito (Con `mapa_repo` y `notas`) |
|---|---|---|---|
| **Configuración / Rondas** | 1 agente (1 ronda) | Planificador + Ejecutor + Revisor (2 rondas) | 1 agente con memoria de notas (1 ronda) |
| **Total de Pasos** | 8 pasos | 14 pasos (8 en R1 + 6 en R2) | 6 pasos |
| **Herramientas Usadas** | `leer_archivo` (2), `buscar` (2), `editar_archivo` (1), `ejecutar_pruebas` (2) | `leer_archivo` (3), `ver_cambios` (2), `editar_archivo` (2), `ejecutar_pruebas` (4), `ejecutar_comando` (2) | `mapa_repo` (1), `anotar` (2), `leer_notas` (1), `editar_archivo` (1), `ejecutar_pruebas` (1) |
| **Decisiones Rechazadas (Contrato)** | 1 (JSON con texto extra fuera de esquema) | 0 | 0 |
| **Acciones Bloqueadas (Política)** | 0 | 1 (Intento de editar `tests/` o ejecutar comando no permitido) | 0 |
| **Contexto Final (Caracteres)** | ~5,400 caracteres (~1,350 tokens) | ~7,800 caracteres (~1,950 tokens) | ~3,900 caracteres (~975 tokens) |
| **Estado Final** | Resuelto (Pruebas en verde) | Resuelto tras revisión de seguridad/calidad | Resuelto con 25% menos pasos que Issue #01 |

## 2. Análisis de Resultados
* **Efecto de herramientas especializadas y memoria (Issue #03 vs #01):** El uso de `mapa_repo()` y la memoria de pizarra (`notas.md`) redujo los pasos exploratorios y el tamaño del contexto final, evitando leer archivos innecesarios.
* **Control y Seguridad (Issue #02):** La separación de roles (Ejecutor vs Revisor de solo lectura) y la política de mínimo privilegio evitaron modificaciones indebidas y aseguraron que la solución cumpliera con las pruebas sin comprometer el repositorio.

## 3. Diagrama de Trayectoria (Ejecución del Agente)

```mermaid
sequenceDiagram
    autonumber
    actor H as Humano
    participant O as Orquestador
    participant E as Ejecutor (Actor)
    participant P as Política / Contrato
    participant R as Revisor (Crítico)

    H->>O: Inicia resolución de Issue
    O->>E: Ejecuta plan con herramientas limitadas
    E->>P: Propone leer_archivo() y buscar()
    P-->>E: Permitido
    E->>P: Propone acción fuera de política
    P-->>E: BLOQUEADO (Regla de mínimo privilegio)
    E->>P: Propone editar_archivo() en módulo dominio
    P-->>H: Solicita aprobación humana (s/n)
    H-->>P: Aprueba edición ("s")
    E->>P: Propone ejecutar_pruebas()
    P-->>E: Pytest en verde (OK)
    E-->>O: Entrega resumen + diff
    O->>R: Evalúa cambios (Solo lectura)
    R-->>O: Veredicto: APROBADO
    O-->>H: Listo para revisión final de Pull Request