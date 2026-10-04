from pathlib import Path

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.network import Nginx, Internet
from diagrams.programming.framework import Django
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.monitoring import Grafana
from diagrams.generic.device import Mobile

carpeta_img = Path(__file__).resolve().parent / "img"
carpeta_img.mkdir(parents=True, exist_ok=True)

graph_attr = {
    "fontsize": "18",
    "bgcolor": "white",
    "pad": "0.4",
}

with Diagram(
    "EcoRecicla AQP - Vista de Despliegue",
    filename=str(carpeta_img / "despliegue"),
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    vecino_admin = Users("Vecinos y Municipio\n(Navegador / Web)")
    reciclador = Mobile("Recicladores\n(PWA Celular 3G)")

    with Cluster("Servidor en la Nube (VPS Económico)"):
        proxy = Nginx("Nginx Proxy Inverso\n(HTTPS / SSL)")

        with Cluster("Monolito Modular"):
            app = Django(
                "Django Core\n(Solicitudes, Rutas, Puntos, Reportes)"
            )
            cache = Redis("Redis Cache\n(Sesiones y colas)")

        db = PostgreSQL("PostgreSQL\n(Esquemas lógicos por módulo)")
        mon = Grafana("Monitoreo\n(Métricas básicas)")

    ext_maps = Internet("Servicio Externo:\nOpenStreetMap / Maps API")
    ext_whatsapp = Internet("Servicio Externo:\nWhatsApp Business API")

    vecino_admin >> proxy
    reciclador >> proxy
    proxy >> app
    app >> db
    app >> cache
    app >> Edge(style="dotted") >> mon
    app >> Edge(label="Rutas", style="dashed") >> ext_maps
    app >> Edge(label="Alertas", style="dashed") >> ext_whatsapp
