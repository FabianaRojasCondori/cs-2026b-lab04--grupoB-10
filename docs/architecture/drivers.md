# Drivers arquitectónicos — EcoRecicla AQP

## 1. Requisitos funcionales clave

| ID | Requisito | Actor | Prioridad |
|---|---|---|---|
| RF-01 | Solicitar recojo de residuos reciclables indicando tipo de material y volumen estimado. | Vecino | Alta |
| RF-02 | Visualizar y actualizar la hoja de ruta óptima del día asignada por el municipio. | Reciclador | Alta |
| RF-03 | Registrar la entrega y acreditar puntos canjeables en la cuenta del vecino. | Reciclador / Vecino | Alta |
| RF-04 | Consultar el reporte mensual consolidado de toneladas de material reciclado por sector. | Municipalidad | Media |
| RF-05 | Validar la identidad, padrón y estado formalizado de las asociaciones de recicladores. | Municipalidad | Alta |

## 2. Atributos de calidad (ordenados por prioridad)

1. **Modificabilidad (Crítico):** Permitir incorporar nuevos distritos o cambiar esquemas de cálculo de puntos sin alterar la lógica de otros módulos.
2. **Capacidad de interacción (Usabilidad móvil):** La interfaz para el reciclador debe operar con fluidez y mínimo consumo de datos en dispositivos de gama baja bajo conectividad intermitente (3G).
3. **Fiabilidad / Integridad:** Garantizar cero pérdidas de registros de solicitudes y transacciones de puntos ante eventuales caídas transitorias de conectividad.
4. **Rendimiento:** Tiempos de respuesta ágiles en la consulta de rutas y confirmación de entregas en horarios pico de recojo matutino.

## 3. Restricciones

| ID | Tipo | Restricción |
|---|---|---|
| R-01 | Plazo | MVP desplegado y validado en producción en 1 mes. |
| R-02 | Equipo | 3 desarrolladores con experiencia en Python, Django y PostgreSQL; sin personal dedicado a DevOps. |
| R-03 | Presupuesto | Presupuesto reducido; alojamiento en un único servidor virtual en la nube (VPS económico). |
| R-04 | Normativa | Cumplimiento del marco de formalización de recicladores (Ley N° 29419) y Ley de Protección de Datos Personales (Ley N° 29733). |

## 4. Escenarios de atributos de calidad

| ID | Atributo | Fuente | Estímulo | Entorno | Artefacto | Respuesta | Medida |
|---|---|---|---|---|---|---|---|
| QA-01 | Modificabilidad (Crítico) | Administrador municipal | Solicita incorporar un nuevo distrito piloto o modificar el algoritmo de cálculo de puntos ecológicos | Mantenimiento / Evolución en operación normal | Módulo de Puntos / Configuración | Se agrega un nuevo adaptador de reglas sin modificar ni recompilar los módulos de usuarios ni reportes | Tiempo de implementación y despliegue ≤ 2 días-persona |
| QA-02 | Capacidad de interacción | Reciclador formalizado | Registra una entrega de material reciclable desde la calle | Celular de gama baja con cobertura móvil inestable (3G) | PWA / Cliente Móvil | La interfaz carga localmente, almacena la transacción en caché y sincroniza en segundo plano al recuperar red | Flujo completado en ≤ 3 toques y sincronización automática en ≤ 5 s tras reconexión |
| QA-03 | Rendimiento | 150 recicladores concurrentes | Solicitan la descarga y visualización de su hoja de ruta al iniciar la jornada (7:00 - 8:00 a. m.) | Hora pico de sincronización de rutas | API REST / Módulo de Rutas | El sistema procesa y entrega el itinerario optimizado con coordenadas georreferenciadas | p95 del tiempo de respuesta ≤ 2.0 segundos |
