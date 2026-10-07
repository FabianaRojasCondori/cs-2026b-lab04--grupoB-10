\# HU-01: Solicitar recojo de reciclables



\## Historia de usuario



Como vecino, quiero solicitar el recojo de mis materiales reciclables,

indicando la dirección, el tipo de material y su volumen estimado,

para que se programe su recolección y pueda consultar el estado

de mi solicitud.



\## Trazabilidad



\- Caso: EcoRecicla AQP.

\- Requisito principal: RF-01 de docs/architecture/drivers.md.

\- Arquitectura: monolito modular según ADR-001.

\- Módulo principal: solicitudes.

\- Persistencia: mediante un repositorio, con implementación en PostgreSQL.

\- Servicio externo: WhatsApp, accedido mediante el puerto NotificadorWhatsapp.



\## Criterios de aceptación



\### CA-01: Solicitud válida



Dado un vecino autenticado que ingresa una dirección no vacía y

al menos un material con tipo no vacío y volumen estimado mayor que cero,

cuando confirma la solicitud de recojo,

entonces el sistema guarda una solicitud en estado Pendiente,

devuelve su identificador y solicita una notificación asíncrona

de confirmación por WhatsApp.



\### CA-02: Solicitud sin materiales



Dado un vecino autenticado que no ha agregado materiales,

cuando intenta confirmar la solicitud de recojo,

entonces el sistema informa el error, no guarda una solicitud

y no solicita una notificación por WhatsApp.



\### CA-03: Datos inválidos



Dado un vecino autenticado que ingresa una dirección vacía,

un tipo de material vacío o un volumen estimado menor o igual que cero,

cuando intenta confirmar la solicitud de recojo,

entonces el sistema informa el error, no guarda una solicitud

y no solicita una notificación por WhatsApp.



\## Reglas de negocio del diseño



\- Cada solicitud pertenece a exactamente un vecino.

\- Un vecino puede tener cero o muchas solicitudes.

\- Cada solicitud válida contiene uno o más ItemMaterial.

\- Cada ItemMaterial pertenece a una sola solicitud.

\- El volumen estimado se expresa en litros.

\- Una solicitud se crea en estado Pendiente.

\- El error de validación no es un estado de Solicitud:

&#x20; en ese escenario no se crea la entidad.

\- La respuesta de éxito se entrega después de guardar la solicitud.

\- La entrega del WhatsApp se realiza en segundo plano;

&#x20; la confirmación de la solicitud no espera la respuesta del proveedor.



\## Contrato del ciclo de vida para E3



Los nombres de los estados y operaciones deben conservarse

en los diagramas y en el código:



| Estado de origen | Operación de Solicitud | Estado de destino | Condición |

|---|---|---|---|

| Inicial | Solicitud(vecino, direccion, items) | Pendiente | Datos válidos y uno o más materiales |

| Pendiente | asignar\_reciclador(reciclador\_id) | Asignada | Identificador de reciclador válido |

| Asignada | registrar\_recojo() | Recogida | Recojo confirmado |

| Recogida | registrar\_pesaje(peso\_kg) | Pesada | Peso mayor que cero |

| Pesada | registrar\_acreditacion(puntos) | PuntosAcreditados | Acreditación confirmada y puntos mayores que cero |



El módulo Puntos calcula y acredita los puntos.

Solicitud.registrar\_acreditacion() registra la confirmación recibida;

no implementa las reglas de cálculo del módulo Puntos.



\## Alcance de la secuencia E2



La secuencia cubre el registro de la solicitud y los errores de

validación de CA-02 y CA-03. Las operaciones posteriores del ciclo

de vida se incluyen en clases para mantener consistencia con E3.



La autenticación ocurre antes del flujo representado.

El formulario proporciona los ItemMaterial como datos de entrada;

su edición en pantalla queda fuera de esta secuencia.



\## Decisiones propuestas para revisión del equipo



\- Se usa el litro como unidad del volumen estimado.

\- La notificación confirma al vecino el registro de su solicitud.

\- La validación exige dirección y tipo de material no vacíos,

&#x20; al menos un material y volúmenes positivos.



Estas decisiones detallan RF-01 y deben ser revisadas por el equipo.

