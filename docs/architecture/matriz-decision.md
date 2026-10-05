# Matriz de decisión — EcoRecicla AQP

## Alternativas
- **A. Monolito tradicional en capas:** Organización horizontal clásica (presentación, negocio, datos). Es rápido de arrancar y económico de alojar, pero sufre de acoplamiento progresivo, lo que dificulta aislar cambios en las reglas de puntos o distritos sin afectar otros flujos.
- **B. Monolito modular:** Despliegue único que agrupa el código en módulos de dominio autónomos con contratos e interfaces públicas bien delimitadas. Ofrece alta modificabilidad y orden sin la penalización de costos ni complejidad operativa de una red distribuida.
- **C. Microservicios:** Despliegue de servicios totalmente independientes con sus propias bases de datos y comunicación por red/mensajería. Maximiza la escalabilidad y autonomía de despliegue, pero desborda los costos de hosting y el tiempo de entrega de un equipo pequeño.

## 2. Criterios y pesos (deben sumar 100%)
| Criterio | Peso | Justificación (Driver relacionado) |
|---|:---:|---|
| **Tiempo de entrega** | 25% | **R-01:** Plazo perentorio de 1 mes para el MVP en producción con equipo reducido (R-02). |
| **Costo operativo** | 25% | **R-03:** Presupuesto bajo; la infraestructura debe funcionar de manera estable en un único VPS económico. |
| **Modificabilidad** | 20% | **QA-01:** Atributo crítico del caso; incorporar distritos o variar reglas de puntos en ≤ 2 días-persona sin alterar otros módulos. |
| **Simplicidad operativa** | 15% | **R-02:** 3 desarrolladores sin personal dedicado a DevOps ni administración avanzada de clusters. |
| **Escalabilidad** | 15% | **QA-03:** Soporte paulatino de recicladores concurrentes y solicitudes vecinales en distritos piloto. |
| **Total** | **100%** | |

## 3. Matriz (puntaje 1 = muy malo ... 5 = excelente)

| Criterio (peso) | A | B | C|
|---|:---:|:---:|:---:|
| Costo operativo (25%) | 5 | 5 | 2 |
| Tiempo de entrega (25%) | 5 | 4 | 2 |
| Modificabilidad (20%) | 2 | 4 | 5 |
| Simplicidad operativa (15%) | 5 | 4 | 1 |
| Escalabilidad (15%) | 2 | 3 | 5 |
| **Total ponderado** | **3.95** | **4.10** | **2.90** |

Total ponderado = Σ (peso × puntaje). 

- **Monolito en capas:** 0.25 x 5 + 0.25 x 5 + 0.20 x 2 + 0.15 x 5 + 0.15 x 2  = 1.25 + 1.25 + 0.40 + 0.75 + 0.30 = 3.95 
- **Monolito modular:** 0.25 x 5 + 0.25 x 4 + 0.20 x 4 + 0.15 x 4 + 0.15 x 3 = 1.25 + 1.00 + 0.80 + 0.60 + 0.45 = 4.10 
- **Microservicios:** 0.25 x 2 + 0.25 x 2 + 0.20 x 5 + 0.15 x 1 + 0.15 x 5 = 0.50 + 0.50 + 1.00 + 0.15 + 0.75 = 2.90

## 4. Conclusión
Se elige la alternativa **B. Monolito modular (4.10)** porque satisface plenamente la restricción de plazo (R-01) y costo de infraestructura (R-03), ofreciendo a la vez el desacoplamiento indispensable para garantizar la **Modificabilidad (QA-01)**. 

La segunda mejor opción evaluada fue el **Monolito en capas (3.95)**, la cual se descartó formalmente debido a su deficiencia estructural frente a cambios frecuentes en la lógica de puntos y distritos.

Ver [ADR-001](adr/001-estilo-arquitectonico.md).