workspace "EcoRecicla AQP" "Lab 06 - Grupo B-10 - Modelo C4" {
    !identifiers hierarchical
    !impliedRelationships false

    model {
        vecino = person "Vecino" "Solicita recojos y consulta sus puntos."
        reciclador = person "Reciclador formalizado" "Consulta rutas y registra recojos y pesajes."
        admin = person "Administrador municipal" "Supervisa recicladores y consulta reportes."

        eco = softwareSystem "EcoRecicla AQP" "Gestiona solicitudes, rutas, puntos y reportes de reciclaje." {
            pwa = container "Aplicacion web progresiva" "Interfaz por rol para vecinos, recicladores y administracion; permite registro local y sincronizacion al recuperar conexion." "JavaScript / Service Worker / IndexedDB" "Web Browser"

            api = container "API EcoRecicla" "Monolito modular con servicios de aplicacion y adaptadores." "Python / Django REST Framework"

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
        // RELACIONES_E3
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
        // VISTA_E3

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