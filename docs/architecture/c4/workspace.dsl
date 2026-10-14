workspace "EcoRecicla AQP" "Lab 06 - Grupo B-10 - Modelo C4" {
    !identifiers hierarchical
    !impliedRelationships false

    model {
        vecino = person "Vecino" "Solicita recojos y consulta sus puntos."
        reciclador = person "Reciclador formalizado" "Consulta rutas y registra recojos y pesajes."
        admin = person "Administrador municipal" "Supervisa recicladores y consulta reportes."

        eco = softwareSystem "EcoRecicla AQP" "Gestiona solicitudes, rutas, puntos y reportes de reciclaje."

        mapas = softwareSystem "Servicio de mapas y rutas" "Proporciona mapas e itinerarios mediante una API externa." "Externo"
        whatsapp = softwareSystem "WhatsApp Business API" "Entrega avisos a los usuarios." "Externo"

        vecino -> eco "Solicita recojos y consulta puntos"
        reciclador -> eco "Consulta rutas y registra entregas"
        admin -> eco "Supervisa recicladores y consulta reportes"
        eco -> mapas "Consulta mapas e itinerarios" "HTTPS/JSON"
        eco -> whatsapp "Envia notificaciones" "HTTPS/JSON"

        // RELACIONES_E2
        // RELACIONES_E3
    }

    views {
        systemContext eco "Contexto" "Nivel 1: EcoRecicla AQP y su entorno." {
            include *
            autoLayout lr
        }

        // VISTA_E2
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