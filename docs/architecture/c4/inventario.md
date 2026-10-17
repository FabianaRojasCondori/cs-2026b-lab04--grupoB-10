# Inventario C4 - EcoRecicla AQP

Responsable: Andres Raul Ore Soto  
Grupo: B-10  
Laboratorio: 06

## 1. Fuentes de trazabilidad

Las rutas siguientes son relativas a la raíz del repositorio:

- docs/architecture/drivers.md
- docs/architecture/adr/001-estilo-arquitectonico.md
- docs/architecture/adr/002-base-datos.md
- docs/architecture/adr/003-motor-puntos.md
- docs/architecture/diagramas/despliegue.py
- docs/design/paquetes.puml
- docs/design/secuencia-solicitar-recojo.puml
- docs/design/clases.puml
- README.md

Nota: aunque su nombre es 003-motor-puntos.md, el ADR-003
documenta la adopción de una PWA con Service Workers e IndexedDB.

## 2. Elementos del modelo

| Elemento | Tipo C4 | Responsabilidad | Origen |
|---|---|---|---|
| Vecino | Persona | Solicita recojos y consulta sus puntos. | drivers.md: RF-01 y RF-03. |
| Reciclador formalizado | Persona | Consulta rutas y registra recojos y pesajes. | drivers.md: RF-02 y RF-03. |
| Administrador municipal | Persona | Supervisa recicladores y consulta reportes. | drivers.md: RF-04 y RF-05. |
| EcoRecicla AQP | Sistema de software | Gestiona solicitudes, rutas, puntos y reportes de reciclaje. | README.md y ADR-001. |
| Servicio de mapas y rutas | Sistema externo | Proporciona mapas e itinerarios mediante una API externa. | despliegue.py y README.md. |
| WhatsApp Business API | Sistema externo | Entrega notificaciones a los usuarios. | despliegue.py y secuencia-solicitar-recojo.puml. |
| Aplicación web progresiva | Contenedor | Presenta las funciones según el rol y permite registro local y sincronización. | ADR-003, drivers.md y despliegue.py. |
| API EcoRecicla | Contenedor | Implementa el monolito modular y expone sus servicios. | ADR-001 y README.md. |
| Base de datos | Contenedor | Almacena información en PostgreSQL con esquemas separados por módulo. | ADR-002. |
| Worker de notificaciones | Contenedor | Ejecuta notificaciones y reintentos en segundo plano. | Mensaje asíncrono del Lab 05; detalle de implementación del Lab 06. |
| Cola y caché | Contenedor | Mantiene tareas pendientes y datos temporales en Redis. | despliegue.py. |
| solicitudes | Componente de la API | Valida y registra solicitudes, administra su ciclo de vida y solicita notificaciones. | paquetes.puml y secuencia-solicitar-recojo.puml. |
| rutas | Componente de la API | Consulta solicitudes y organiza paradas e itinerarios. | paquetes.puml. |
| puntos | Componente de la API | Procesa SolicitudPesada y registra beneficios ecológicos. | paquetes.puml. |
| reportes | Componente de la API | Genera consolidados mediante los contratos de solicitudes y puntos. | paquetes.puml. |
| compartido | Componente de la API | Proporciona tipos base, constantes y utilidades comunes. | paquetes.puml. |

## 3. Dependencias entre componentes

Se conservan las dependencias de docs/design/paquetes.puml:

- solicitudes -> compartido
- rutas -> compartido
- puntos -> compartido
- reportes -> compartido
- rutas -> solicitudes
- puntos -> solicitudes
- reportes -> solicitudes
- reportes -> puntos

Las flechas representan dependencias de código o contratos.

En particular, puntos depende del contrato SolicitudPesada definido
por solicitudes. La dirección de esta dependencia no representa
necesariamente la dirección temporal de entrega del evento.

Solicitudes no depende de rutas, puntos ni reportes.
Compartido no depende de los módulos de dominio.
No existen dependencias cíclicas.

## 4. Decisiones de modelado

- Se conserva el monolito modular de Django.
- Django REST Framework está documentado en el README del Lab 04.
- Se representa una PWA con funciones según el rol, siguiendo la
  decisión de mantener una sola base de código frontend del ADR-003.
- Se utilizan Service Workers e IndexedDB, establecidos en el ADR-003.
- No se fija React ni una versión de PostgreSQL porque los ADR
  existentes no los especifican.
- Celery concreta el procesamiento asíncrono descrito en el Lab 05
  y propuesto en la división del Lab 06. Esta precisión se incorpora
  al ADR-001 para su revisión en el PR.
- Worker y Redis son contenedores distintos: el primero ejecuta
  tareas y el segundo mantiene la cola y la caché.
- Cada módulo accede únicamente a su esquema de PostgreSQL.
  Las consultas entre módulos utilizan contratos de aplicación.
- Los adaptadores y la validación permanecen dentro del módulo
  correspondiente; no se inventan nuevos módulos de dominio.
- Nginx y las herramientas de monitoreo del despliegue previo
  se documentarán al desarrollar la vista de despliegue.
- Los mapas y WhatsApp son sistemas externos, no contenedores propios.

## 5. Continuidad con los siguientes entregables

El flujo de la vista dinámica será "Solicitar recojo de reciclables",
tomado de docs/design/secuencia-solicitar-recojo.puml.

Debe conservar el orden:
validar datos, guardar la solicitud y solicitar la notificación
asíncrona. Si los datos son inválidos, no se guarda ni se notifica.

El nivel de código se consulta en docs/design/clases.puml;
no se genera un nuevo diagrama de clases para este laboratorio.