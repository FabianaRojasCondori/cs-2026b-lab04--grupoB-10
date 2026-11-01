"""Fitness functions automatizadas de arquitectura (Lab 08).

Verifican que la arquitectura no se degrade respecto a:
- QA-01: Rendimiento (p95 <= 2000 ms) — evidencia de Andrés (iteracion-1.md).
- QA-02: Disponibilidad (0 solicitudes perdidas ante caída externa) — evidencia
  de Fabiana (iteracion-2.md).
"""
from fitness.rendimiento import evaluar_qa01, SEMILLAS, UMBRAL_P95_MS
from fitness.disponibilidad import simular


def test_ff03_qa01_rendimiento_campana_12_distritos():
    """QA-01 (H,M): el p95 a 16 req/s debe ser <= 2000 ms en las 5 semillas."""
    for s in SEMILLAS:
        p95 = evaluar_qa01(semilla=s)
        assert p95 <= UMBRAL_P95_MS, (
            f"QA-01 incumplido: p95={p95:.1f}ms > {UMBRAL_P95_MS}ms "
            f"en semilla={s}"
        )


def test_ff04_qa02_cero_solicitudes_perdidas():
    """QA-02 (H,H): Circuit Breaker + Outbox conserva las 1800 solicitudes."""
    resultado = simular(
        estrategia="breaker",
        total_solicitudes=1800,
        caida_minutos=20,
        semilla=7,
    )
    assert resultado["perdidos"] == 0, (
        f"QA-02 incumplido: se perdieron {resultado['perdidos']} solicitudes."
    )
    assert resultado["completados"] == 1800, (
        f"QA-02: solo {resultado['completados']}/1800 solicitudes conservadas."
    )


def test_ff05_qa02_breaker_protege_al_proveedor():
    """QA-02: el breaker llama <= 1/5 del proveedor caído que los reintentos."""
    breaker = simular(estrategia="breaker", semilla=7)
    reintentos = simular(estrategia="reintentos", semilla=7)

    assert breaker["perdidos"] < reintentos["perdidos"], (
        f"El breaker debería perder menos que los reintentos: "
        f"breaker={breaker['perdidos']}, reintentos={reintentos['perdidos']}"
    )
    assert breaker["llamadas_en_caida"] < (reintentos["llamadas_en_caida"] / 5), (
        f"Efecto tormenta esperado: breaker={breaker['llamadas_en_caida']}, "
        f"reintentos={reintentos['llamadas_en_caida']}"
    )
