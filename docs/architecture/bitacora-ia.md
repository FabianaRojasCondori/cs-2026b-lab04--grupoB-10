# Bitácora de uso de IA — EcoRecicla AQP

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|
| 1 | 10-04 | ChatGPT | Comparar 3 estilos arquitectónicos para EcoRecicla con plazo de 1 mes y 3 devs | Recomendó Monolito Modular con 8 módulos independientes (`usuarios`, `recicladores`, `solicitudes`, `rutas`, `puntos`, `pesajes`, `reportes`, `auditoria`).| **Verificación:** Crear 8 módulos para 3 devs en 1 mes introduce sobreingeniería organizativa que pone en riesgo el plazo (R-01, R-02). Se simplificó y consolidó el dominio en 4 módulos esenciales para el MVP | **Corregida** |
| 2 | 10-04 | Deepseek | Comparar 3 estilos arquitectónicos para EcoRecicla con plazo de 1 mes y 3 devs | Recomendó Monolito Modular implementado como *Django Apps*, asegurando que el framework mantiene límites limpios y facilita la Ley 29733.| **Verificación:** En Django estándar, las *apps* comparten fácilmente el ORM y modelos sin aislamiento estricto, arriesgando fugas de dependencias y datos sensibles. Se decidió reforzar los límites con esquemas lógicos separados en PostgreSQL e interfaces de servicio explícitas. | **Corregida** |
| **3** | 10-04 | ChatGPT | Crítica adversarial ("abogado del diablo") contra la recomendación del Monolito Modular. | Cuestionó el supuesto de que el monolito sea "simple", alertó sobre el D.S. 016-2024-JUS (nuevo reglamento de Ley 29733) y el riesgo del VPS como punto único de falla (SPOF). | **Verificación:** El análisis es acertado. Cumplir la ley exige medidas de *Privacy by Design* y no solo un framework. Se aceptó la recomendación de modelar backups externos automatizados y parametrizar estados de recicladores. Se incluyeron estos riesgos en la sección de consecuencias del ADR-001. | **Aceptada** |
| **4** | 10-04 | DeepSeek | Crítica adversarial enfocada en fallos de producción y costos ocultos del Monolito Modular. | Advirtió que 3 devs bajo presión romperán los límites importando modelos entre apps, y que tareas geoespaciales pesadas pueden agotar la CPU/RAM del VPS económico. | **Verificación:** Crítica técnica muy precisa. Se adoptaron las tácticas propuestas: uso de *fitness functions* (`import-linter` en CI) para impedir imports cruzados de modelos, y un patrón *bulkhead* ligero aislando el cálculo de rutas y reportes mediante colas Redis/Celery. | **Aceptada** |
| 5 | 10-04 | ChatGPT / Deepseek | Generar código Mermaid de la arquitectura modular de EcoRecicla AQP | ChatGPT propuso un diagrama básico con dependencias directas entre módulos (S -.-> RT). DeepSeek modeló una arquitectura hexagonal limpia con puertos/interfaces internos (SPorts, RPorts), servicios externos y esquemas lógicos PostgreSQL. | **Verificación:** El código de ChatGPT permitía acoplamiento directo entre módulos, vulnerando el atributo QA-01. Se seleccionó la propuesta de DeepSeek por reflejar fielmente el aislamiento modular con puertos y adaptadores. | **Corregida** |

## Anexo: Prompts completos

### Prompt 1 — Generación de alternativas de estilo arquitectónico (ChatGPT)
> "Actúa como un Arquitecto de Software Senior con experiencia en plataformas municipales y de logística urbana. 
Contexto: Sistema 'EcoRecicla AQP' para la recolección municipal de residuos reciclables en Arequipa. Permite solicitudes vecinales, rutas optimizadas para recicladores formalizados, acreditación de puntos ecológicos y reportes de pesaje. 
Restricciones: 3 desarrolladores con experiencia en Python/Django, presupuesto de hosting bajo (un único VPS económico), MVP en producción en 1 mes, cumplimiento de la Ley N° 29419 (marco de recicladores) y Ley N° 29733 (protección de datos).
Tarea: propón 3 alternativas de estilo arquitectónico. Para cada una indica fortalezas, debilidades, riesgos y qué atributos de calidad favorece o penaliza.
Formato: tabla comparativa en Markdown y, al final, tu recomendación justificada.
No inventes APIs ni capacidades de servicios; si no estás seguro, indícalo."

### Prompt 2 — Comparación arquitectónica con énfasis normativo y operativo (DeepSeek)
> "Como Arquitecto de Software Senior, analiza las restricciones de EcoRecicla AQP (3 desarrolladores Python/Django, presupuesto para un único VPS económico, MVP en 1 mes, cumplimiento de Ley N° 29419 y Ley N° 29733). Presenta tres alternativas de estilo arquitectónico viables, evaluadas según su idoneidad para este contexto en formato de tabla comparativa y recomendación justificada."

### Prompt 3 — Crítica adversarial / Abogado del diablo (ChatGPT)
> "Ahora actúa como 'abogado del diablo'. Critica duramente la alternativa que recomendaste: ¿qué supuestos no se cumplen con nuestras restricciones?, ¿qué podría fallar en producción?, ¿qué costo oculto tiene? Enumera los 5 riesgos más graves y, para cada uno, una táctica arquitectónica de mitigación."

### Prompt 4 — Crítica adversarial sobre fallos en producción y costos ocultos (DeepSeek)
> "Actúa como abogado del diablo y destruye la recomendación de Monolito Modular con Django Apps para EcoRecicla AQP. Detalla qué supuestos no se cumplen, qué fallará en producción bajo carga real en el VPS, cuáles son los costos ocultos no presupuestados y los 5 riesgos más graves con sus tácticas de mitigación."

### Prompt 5 — Generación del diagrama conceptual en Mermaid (ChatGPT / Deepseek)
> "Genera el código de un diagrama Mermaid (`flowchart TB`) para el Monolito Modular de EcoRecicla AQP. Debe incluir 3 actores (Vecino, Reciclador, Administrador Municipal), una capa de presentación API REST, 4 módulos de dominio desacoplados (Solicitudes, Rutas, Puntos, Reportes), una capa de infraestructura y persistencia en PostgreSQL con esquemas separados. Además, incluye la conexión con servicios externos para cálculo de rutas y notificaciones."
