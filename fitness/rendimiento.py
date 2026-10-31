"""EcoRecicla AQP: modelo M/G/c de QA-01 del Lab 08.
Adaptado del recurso docente de AgroConecta. Tiempos hipotéticos, no mediciones.
Ejecutar desde la raíz: python fitness/rendimiento.py
"""
import csv
import heapq
import math
from pathlib import Path
import random
import statistics

UMBRAL_P95_MS = 2000
SEMILLAS = (7, 17, 27, 37, 47)


def simular(lam, workers, servicio, segundos=120, semilla=7):
    """Poisson, cola FIFO sin límite, workers idénticos; respuesta en ms."""
    if lam <= 0 or workers < 1 or segundos <= 0:
        raise ValueError("La tasa, workers y duración deben ser positivos")
    llegadas_rng = random.Random(semilla)
    servicio_rng = random.Random(semilla + 10000)
    libres = [0.0] * workers
    respuestas = []
    t = 0.0
    while True:
        t += llegadas_rng.expovariate(lam)
        if t >= segundos:
            break
        libre = heapq.heappop(libres)
        duracion = servicio(servicio_rng)
        if duracion < 0:
            raise ValueError("Tiempo de servicio negativo")
        fin = max(t, libre) + duracion
        heapq.heappush(libres, fin)
        respuestas.append((fin - t) * 1000)
    if not respuestas:
        raise ValueError("No se generaron llegadas; aumenta duración o tasa")
    respuestas.sort()
    def percentil(q):
        return respuestas[math.ceil(q * len(respuestas)) - 1]
    return {"n": len(respuestas), "p50": percentil(.50),
            "p95": percentil(.95), "media": statistics.mean(respuestas)}


def servicio_mixto(indice=False, cache=False, acierto=.85):
    """70% consultas; 30% registros. Caché solo para consultas autorizadas.
    Se consumen los mismos sorteos en cada alternativa para compararlas.
    """
    if not 0 <= acierto <= 1:
        raise ValueError("Acierto fuera de [0, 1]")
    def servicio(rng):
        lectura = rng.random() < .70
        hit = rng.random() < acierto
        z = rng.gauss(0, 1)
        if lectura and cache and hit:
            return math.exp(-4.6 + .3 * z)
        if lectura and indice:
            return math.exp(-2.30 + .40 * z)
        return math.exp(-1.35 + .45 * z)
    return servicio


CONFIGURACIONES = {
    "Sin tacticas": (4, servicio_mixto()),
    "Indice": (4, servicio_mixto(indice=True)),
    "Cache 85%": (4, servicio_mixto(cache=True)),
    "Indice + cache 85%": (4, servicio_mixto(indice=True, cache=True)),
    "8 workers ideales": (8, servicio_mixto()),
}


def evaluar_qa01(semilla=7):
    """Contrato para E5: float p95 en ms, táctica elegida, 16 req/s totales."""
    return simular(16, 4, servicio_mixto(indice=True, cache=True),
                   semilla=semilla)["p95"]


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    salida = Path(__file__).resolve().parents[1] / "docs/architecture/add/evidencia"
    salida.mkdir(parents=True, exist_ok=True)
    filas = []
    resumen = []
    for distritos, tasa in ((3, 4), (6, 8), (12, 16)):
        for nombre, (workers, servicio) in CONFIGURACIONES.items():
            resultados = []
            for semilla in SEMILLAS:
                r = simular(tasa, workers, servicio, semilla=semilla)
                filas.append(dict(distritos=distritos, tasa_total=tasa,
                                  alternativa=nombre, workers=workers,
                                  semilla=semilla, **r))
                resultados.append(r["p95"])
            resumen.append((distritos, tasa, nombre,
                            statistics.median(resultados), max(resultados)))
    with (salida / "rendimiento.csv").open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)
    tabla = ["| Distritos | req/s totales | Alternativa | Mediana p95 (ms) | Máximo p95 (ms) | Todas cumplen |",
             "|---|---|---|---|---|---|"]
    for d, tasa, nombre, mediana, maximo in resumen:
        tabla.append(f"| {d} | {tasa} | {nombre} | {mediana:.1f} | {maximo:.1f} | {'Sí' if maximo <= UMBRAL_P95_MS else 'No'} |")
    texto = "\n".join(tabla) + "\n"
    (salida / "resultados.md").write_text(texto, encoding="utf-8")
    print(texto)
    fig, ax = plt.subplots(figsize=(10, 5.5), layout="constrained")
    for nombre in CONFIGURACIONES:
        valores = [(t, m) for _, t, n, _, m in resumen if n == nombre]
        ax.plot([v[0] for v in valores], [v[1] for v in valores], marker="o", label=nombre)
    ax.axhline(UMBRAL_P95_MS, color="red", linestyle="--", label="QA-01: 2000 ms")
    ax.set(yscale="log", xlabel="Llegadas totales (req/s)", ylabel="Máximo p95 de 5 semillas (ms)",
           title="EcoRecicla AQP: crecimiento de 3 a 12 distritos", xticks=[4, 8, 16])
    ax.grid(alpha=.2)
    ax.legend()
    fig.savefig(salida / "rendimiento.png", dpi=160)
    plt.close(fig)
    sensibilidad = []
    for acierto in (0, .1, .25, .5, .85, 1):
        for indice in (False, True):
            valores = [simular(16, 4, servicio_mixto(indice, True, acierto), semilla=s)["p95"] for s in SEMILLAS]
            sensibilidad.append((acierto, indice, max(valores)))
    lineas = ["| Acierto en lecturas | Índice | Máximo p95 (ms) |", "|---|---|---|"]
    lineas += [f"| {a:.0%} | {i} | {p:.1f} |" for a, i, p in sensibilidad]
    (salida / "sensibilidad.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    fig, ax = plt.subplots(figsize=(9, 5), layout="constrained")
    for indice in (False, True):
        valores = [(a * 100, p) for a, i, p in sensibilidad if i == indice]
        ax.plot([a for a, _ in valores], [p for _, p in valores], marker="o",
                label="Índice + caché" if indice else "Solo caché")
    ax.axhline(2000, color="red", linestyle="--", label="QA-01: 2000 ms")
    ax.set(yscale="log", xlabel="Aciertos en consultas (%)", ylabel="Máximo p95 de 5 semillas (ms)",
           title="Sensibilidad: 12 distritos, 16 req/s, 4 workers")
    ax.grid(alpha=.2)
    ax.legend()
    fig.savefig(salida / "sensibilidad.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
