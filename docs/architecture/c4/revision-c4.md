# Revisión Oficial de Arquitectura C4 - EcoRecicla AQP

## Evaluación con Lista de Chequeo (Tabla 3)

### 1. Criterios Generales
- [x] **Nivel de Abstracción Adecuado:** Se mantienen claramente diferenciados los niveles de Contexto, Contenedores, Componentes, Código y Despliegue.
- [x] **Consistencia:** Los nombres de los actores (Vecino, Reciclador, Municipalidad) y componentes coinciden en todas las vistas.
- [x] **Legibilidad:** Diagramas estructurados correctamente en sintaxis Mermaid.

### 2. Elementos
- [x] **Nombres descriptivos:** Ningún elemento utiliza nombres genéricos como "Servidor", "Base de Datos" o "Docker". Se especifican nombres funcionales (ej. `API Gateway`, `Base de Datos PostgreSQL`).
- [x] **Tecnologías explícitas:** Cada contenedor indica la tecnología utilizada (ej. React Native, Node.js, PostgreSQL, Python).
- [x] **Actores definidos:** Se definen los tres roles del dominio: Vecino, Reciclador y Municipalidad.

### 3. Relaciones
- [x] **Verbos de acción:** Todas las relaciones describen la interacción (ej. "Solicita recojo", "Consulta ruta optimizada").
- [x] **Protocolos especificados:** Se incluyen los protocolos de comunicación utilizados (ej. HTTPS/REST, WebSockets, JDBC, HTTPS API).

---

## Auditoría y Refutación de Falso Positivo (Prompt IA 2)

Durante la auditoría automatizada con IA se registró la siguiente observación:

- **Observación de la IA:** *"La Tarea de Optimización de Rutas debe integrarse dentro de la API principal para reducir llamadas entre servicios y simplificar el despliegue."*
- **Análisis Técnico y Refutación (Falso Positivo):** 
  - **Refutación:** Esta recomendación es **incorrecta** para la arquitectura de EcoRecicla AQP. El cálculo de rutas óptimas para los recicladores es un proceso intensivo en cómputo (algoritmos sobre grafos / TSP). Mantener la **Tarea de optimización de rutas** como un servicio/contenedor independiente (worker asíncrono) evita bloquear el hilo principal del **API principal** (Node.js/Express) durante horas pico de solicitudes de los vecinos. Se mantiene la separación explícita de este contenedor.