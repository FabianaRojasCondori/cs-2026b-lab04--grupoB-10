"""Adaptadores locales del Lab 11; las reglas de negocio permanecen en src/."""
import json
from decimal import Decimal
from pathlib import Path

from src.puntos.cuenta import CuentaPuntos
from src.puntos.reglas import fabrica_estandar
from src.rutas.planificador import planificar_ruta
from src.solicitudes.modelos import ItemMaterial, Solicitud, Vecino
from src.solicitudes.servicio import ServicioSolicitudes

BASE = Path(__file__).resolve().parents[1]
MATERIALES = ("PLASTICO", "VIDRIO", "PAPEL")


def cargar_demo():
    return json.loads((BASE / "datos/demo.json").read_text(encoding="utf-8"))


class NotificadorDemo:
    """Implementa el puerto del dominio sin enviar mensajes ni usar red."""

    def notificar_solicitud(self, celular, solicitud_id):
        pass


class RepositorioCreacion:
    """Guarda únicamente solicitudes nuevas; open(x) impide sobrescribir."""

    def __init__(self, carpeta, fecha, distrito):
        self.carpeta = Path(carpeta)
        self.fecha = fecha
        self.distrito = distrito

    def guardar(self, solicitud):
        solicitud.distrito = self.distrito
        fila = {
            "id": str(solicitud.id), "vecino_id": solicitud.vecino.id,
            "fecha": self.fecha, "distrito": self.distrito,
            "direccion": solicitud.direccion,
            "material": solicitud.items[0].tipo_material,
            "volumen_litros": str(solicitud.items[0].volumen_estimado_litros),
            "estado": solicitud.estado,
        }
        self.carpeta.mkdir(parents=True, exist_ok=True)
        # El nombre depende del UUID del dominio, nunca de una ruta del usuario.
        with (self.carpeta / f"{solicitud.id}.json").open("x", encoding="utf-8") as f:
            json.dump(fila, f, ensure_ascii=False, indent=2)
            f.write("\n")


class ServicioDemo:
    """Datos ficticios persistentes para demostrar MCP, sin acceso a producción."""

    def __init__(self, carpeta):
        self.carpeta = Path(carpeta)
        self.datos = cargar_demo()

    @property
    def distritos(self):
        return self.datos["distritos"]

    def vecino(self, vecino_id):
        for fila in self.datos["vecinos"]:
            if fila["id"] == vecino_id:
                return Vecino(vecino_id, fila["nombre"], "CELULAR_SIMULADO")
        validos = ", ".join(v["id"] for v in self.datos["vecinos"])
        raise ValueError(f"Vecino desconocido. Use uno de: {validos}")

    def puntos(self, vecino_id):
        self.vecino(vecino_id)
        cuenta = CuentaPuntos(vecino_id)
        fila = next(v for v in self.datos["vecinos"] if v["id"] == vecino_id)
        for solicitud_id, puntos in fila["movimientos"]:
            cuenta.acreditar(solicitud_id, puntos)
        return {"vecino_id": vecino_id, "saldo": cuenta.saldo,
                "movimientos": [{"solicitud_id": s, "puntos": p}
                                for s, p in cuenta.movimientos]}

    def _solicitud(self, fila):
        items = [ItemMaterial(fila["material"], Decimal(str(fila["volumen_litros"])))]
        ServicioSolicitudes.validar_datos(fila["direccion"], items)
        solicitud = Solicitud(self.vecino(fila["vecino_id"]), fila["direccion"], items,
                              distrito=fila["distrito"])
        solicitud.id = fila["id"]
        if fila["estado"] == "Asignada":
            solicitud.asignar_reciclador("reciclador-demo")
        elif fila["estado"] == "Cancelada":
            solicitud.cancelar()
        elif fila["estado"] != "Pendiente":
            raise ValueError("Estado no admitido en el conjunto de demostración")
        return solicitud

    def rutas(self, fecha, distrito):
        filas = list(self.datos["rutas"])
        if self.carpeta.exists():
            for archivo in sorted(self.carpeta.glob("*.json")):
                if archivo.is_symlink():
                    raise ValueError("No se admiten enlaces simbólicos en los datos demo")
                filas.append(json.loads(archivo.read_text(encoding="utf-8")))
        solicitudes = [self._solicitud(f) for f in filas if f["fecha"] == fecha]
        ruta = planificar_ruta(solicitudes, distrito)
        return {"fecha": fecha, "distrito": distrito, "total": len(ruta),
                "truncado": len(ruta) > 20,
                "paradas": [{"solicitud_id": str(s.id), "direccion": s.direccion,
                             "estado": s.estado, "vecino_id": s.vecino.id}
                            for s in ruta[:20]]}

    def registrar(self, vecino_id, fecha, distrito, direccion, material, volumen_litros):
        fabrica_estandar().crear(material)  # Valida con la fábrica real del dominio.
        vecino = self.vecino(vecino_id)
        repositorio = RepositorioCreacion(self.carpeta, fecha, distrito)
        servicio = ServicioSolicitudes(repositorio, NotificadorDemo())
        solicitud = servicio.solicitar_recojo(
            vecino, direccion, [ItemMaterial(material, Decimal(str(volumen_litros)))])
        return {"solicitud_id": str(solicitud.id), "estado": solicitud.estado,
                "fecha": fecha, "distrito": distrito, "demo": True}

    def tabla_puntos(self):
        fabrica = fabrica_estandar()
        return {"unidad": "puntos/litro", "alcance": "tarifas estándar didácticas, sin bonos",
                "tarifas": {m: int(fabrica.crear(m).calcular(Decimal(1))) for m in MATERIALES}}
