workspace "EcoRecicla AQP" "Lab 06 - Grupo B-10 - Modelo C4" {
    !identifiers hierarchical
    !impliedRelationships false

    model {
        vecino = person "Vecino" "Solicita recojos y consulta sus puntos."
        reciclador = person "Reciclador formalizado" "Consulta rutas y registra recojos y pesajes."
        admin = person "Administrador municipal" "Supervisa recicladores y consulta reportes."

        eco = softwareSystem "EcoRecicla AQP" "Gestiona solicitudes, rutas, puntos y reportes de reciclaje." {
            pwa = container "Aplicacion web progresiva" "Interfaz por rol para vecinos, recicladores y administracion; permite registro local y sincronizacion al recuperar conexion." "JavaScript / Service Worker / IndexedDB" "Web Browser"

            api = container "API EcoRecicla" "Monolito modular con servicios de aplicacion y adaptadores." "Python / Django REST Framework" {
                solicitudes = component "solicitudes" "Valida y registra solicitudes, gestiona su ciclo de vida y solicita notificaciones mediante un adaptador." "Django app"

                rutas = component "rutas" "Consulta solicitudes y organiza paradas e itinerarios de recojo." "Django app"

                puntos = component "puntos" "Procesa SolicitudPesada y calcula y registra beneficios ecologicos." "Django app"

                reportes = component "reportes" "Genera consolidados consultando contratos de solicitudes y puntos." "Django app"

                compartido = component "compartido" "Tipos base, constantes, utilidades geograficas, horarios y filtros comunes." "Modulo Python"
            }

            db = container "Base de datos" "Una instancia con esquemas solicitudes, rutas, puntos y reportes; cada modulo accede solo a su esquema." "PostgreSQL" "Database"

            worker = container "Worker de notificaciones" "Ejecuta tareas de notificacion y reintentos en segundo plano." "Python / Celery"

            cola = container "Cola y cache" "Mantiene tareas pendientes y datos temporales de sesiones y cache." "Redis" "Queue"
        }

        mapas = softwareSystem "Servicio de mapas y rutas" "Proporciona mapas e itinerarios mediante una API externa." "Externo"
        whatsapp = softwareSystem "WhatsApp Business API" "Entrega avisos a los usuarios." "Externo"

        vecino -> eco "Solicita recojos y consulta puntos"
        reciclador -> eco "Consulta rutas y registra entregas"
        admin -> eco "Supervisa recicladores y consulta reportes"
        eco -> mapas "Consulta mapas e itinerarios" "HTTPS/JSON"
        eco -> whatsapp "Envia notificaciones" "HTTPS/JSON"

        vecino -> eco.pwa "Registra solicitudes y consulta puntos" "HTTPS"
        reciclador -> eco.pwa "Consulta rutas y registra recojos" "HTTPS"
        admin -> eco.pwa "Supervisa recicladores y consulta reportes" "HTTPS"

        eco.pwa -> eco.api "Invoca los servicios del sistema" "HTTPS/JSON (REST)"
        eco.api -> eco.db "Lee y escribe mediante el esquema de cada modulo" "SQL/TCP"
        eco.api -> eco.cola "Encola notificaciones y accede a cache" "Redis protocol/TCP"
        eco.worker -> eco.cola "Consume tareas pendientes" "Redis protocol/TCP"
        eco.worker -> whatsapp "Envia avisos y reintenta entregas fallidas" "HTTPS/JSON"
        eco.api -> mapas "Consulta mapas e itinerarios" "HTTPS/JSON"
        
        eco.pwa -> eco.api.solicitudes "Registra solicitudes y actualiza recojos" "HTTPS/JSON"
        eco.pwa -> eco.api.rutas "Consulta la hoja de ruta" "HTTPS/JSON"
        eco.pwa -> eco.api.puntos "Consulta puntos y beneficios" "HTTPS/JSON"
        eco.pwa -> eco.api.reportes "Solicita reportes municipales" "HTTPS/JSON"

        eco.api.solicitudes -> eco.api.compartido "Usa tipos base y constantes" "Llamada Python en proceso"
        eco.api.rutas -> eco.api.compartido "Usa utilidades geograficas y horarios" "Llamada Python en proceso"
        eco.api.puntos -> eco.api.compartido "Usa reglas base" "Llamada Python en proceso"
        eco.api.reportes -> eco.api.compartido "Usa filtros de fecha" "Llamada Python en proceso"

        eco.api.rutas -> eco.api.solicitudes "Consulta solicitudes para generar paradas" "Contrato Python en proceso"
        eco.api.puntos -> eco.api.solicitudes "Depende del contrato SolicitudPesada y comunica acreditacion" "Contratos y eventos Python en proceso"
        eco.api.reportes -> eco.api.solicitudes "Consulta toneladas y atenciones" "Contrato Python de solo lectura"
        eco.api.reportes -> eco.api.puntos "Consulta beneficios ecologicos" "Contrato Python de solo lectura"

        eco.api.solicitudes -> eco.db "Lee y escribe el esquema solicitudes" "SQL/TCP"
        eco.api.rutas -> eco.db "Lee y escribe el esquema rutas" "SQL/TCP"
        eco.api.puntos -> eco.db "Lee y escribe el esquema puntos" "SQL/TCP"
        eco.api.reportes -> eco.db "Lee y escribe el esquema reportes" "SQL/TCP"

        eco.api.solicitudes -> eco.cola "Encola la notificacion despues de guardar" "Redis protocol/TCP"
        eco.api.rutas -> mapas "Solicita itinerarios mediante su adaptador" "HTTPS/JSON"

        // --- E5: ENTORNO DE DESPLIEGUE ---
        produccion = deploymentEnvironment "Producción" {
            deploymentNode "Dispositivo del Usuario" "Teléfono móvil inteligente o navegador web de escritorio." "Android / iOS / Chrome / Firefox" {
                containerInstance eco.pwa
            }

            deploymentNode "Servidor VPS en la Nube" "Servidor virtual de bajo costo para el MVP (DigitalOcean / Linode / AWS Lightsail)." "Ubuntu 24.04 LTS, 2 vCPU, 4 GB RAM" {
                deploymentNode "Docker Compose" "Orquestación de servicios locales en el servidor único." "Docker 27" {
                    containerInstance eco.api
                    containerInstance eco.worker
                    containerInstance eco.db
                    containerInstance eco.cola
                }
            }
        }
    
    }

    views {
        systemContext eco "Contexto" "Nivel 1: EcoRecicla AQP y su entorno." {
            include *
            autoLayout lr
        }

        container eco "Contenedores" "Nivel 2: aplicaciones y almacenes de datos de EcoRecicla AQP." {
            include *
            autoLayout lr
        }
        
        component eco.api "Componentes" "Nivel 3: modulos de la API; dependencias del Lab 05." {
            include *
            autoLayout lr
        }

        // --- E4: VISTA DINÁMICA ---
        dynamic eco.api "SolicitarRecojo" "Flujo crítico: Vecino solicita recojo de reciclables (secuencia Lab 05)." {
            eco.pwa -> eco.api.solicitudes "1. POST /solicitudes (dirección, lista de items)"
            eco.api.solicitudes -> eco.api.compartido "2. Valida estructura de items y tipos base"
            eco.api.solicitudes -> eco.db "3. INSERT solicitud en estado Pendiente (SQL)"
            eco.api.solicitudes -> eco.cola "4. Encola tarea de notificación asíncrona"
            eco.worker -> eco.cola "5. Consume tarea de notificación pendiente"
            eco.worker -> whatsapp "6. Envía confirmación por WhatsApp al vecino"
            autoLayout lr
        }

        // --- E5: VISTA DE DESPLIEGUE ---
        deployment eco produccion "Despliegue" "Despliegue de EcoRecicla AQP en el servidor VPS único de producción." {
            include *
            autoLayout lr
        }

        styles {
            element "Person" {
                shape Person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "Externo" {
                background #666666
                color #ffffff
            }
            element "Database" {
                shape Cylinder
            }
            element "Queue" {
                shape Pipe
            }
            element "Web Browser" {
                shape WebBrowser
            }
        }
    }
}