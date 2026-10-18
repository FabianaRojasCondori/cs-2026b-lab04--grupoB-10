# E7: Análisis de Consistencia - EcoRecicla AQP

## Evaluación de Reglas (C1 - C5)
- **C1 (Consistencia de Nombres):** Exitoso. Los nombres de las entidades críticas en el diagrama de clases (`Vecino`, `Solicitud`, `ItemMaterial`) se corresponden con los del código.
- **C2 (Correspondencia de Eventos y Métodos):** Exitoso. Los métodos de transición del ciclo de vida en `Solicitud` coinciden con los estados de la máquina de estados.
- **C3 (Estados Válidos):** Exitoso. Los estados quedan restringidos de forma segura al enumerado `EstadoSolicitud`.
- **C4 (Multiplicidad):** Exitoso. La relación uno a muchos entre `Solicitud` y `ItemMaterial` se respeta mediante una lista en el constructor.
- **C5 (Direccionalidad):** Exitoso. El flujo de control sigue la dirección de las asociaciones sin dependencias inversas inesperadas.

## Identificación y Refutación de Falso Positivo
- **Falso Positivo Detectado:** El software auditor arrojó una alerta de inconsistencia en la regla **C2**, argumentando que el método `registrar_peso()` de la clase `Solicitud` no registraba cambios en la entidad `ItemMaterial`.
- **Refutación:** Se rechaza el error. El pesaje es un evento puramente de transición en el ciclo de vida transaccional de la `Solicitud` (pasa de Recogida a Pesada). El peso total consolidado se evalúa a nivel macro para la asignación de puntos, por lo que alterar individualmente cada material en esa fase sería una redundancia operativa.
