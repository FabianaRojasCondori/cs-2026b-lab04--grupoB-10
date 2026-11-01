"""EcoRecicla AQP: Simulación Monte Carlo de disponibilidad y resiliencia (QA-02).
Midiendo el impacto de Circuit Breaker y Transactional Outbox ante caídas externas.
"""
import random

def simular(estrategia="breaker", total_solicitudes=1800, p_falla_transitoria=0.08, caida_minutos=20, semilla=7):
    """Simula una jornada de 10 horas inyectando caídas del SDK de mensajería (WhatsApp/SMS)."""
    rng = random.Random(semilla)
    duracion_jornada = 600  # 10 horas en minutos
    inicio_caida = 180       # Minuto 180 (caída de 20 minutos)
    fin_caida = inicio_caida + caida_minutos
    
    solicitudes_perdidas = 0
    llamadas_en_caida = 0
    completadas = 0
    
    # Parámetros del Circuit Breaker
    circuito_abierto = False
    fallas_consecutivas = 0
    umbral_fallas = 3
    tiempo_recuperacion = 2.0  # minutos para reintentar (estado semiabierto)
    ultimo_fallo = -100.0

    for i in range(total_solicitudes):
        minuto_actual = (i / total_solicitudes) * duracion_jornada
        proveedor_caido = (inicio_caida <= minuto_actual <= fin_caida)
        
        # Transición de ABIERTO a SEMIABIERTO
        if circuito_abierto and (minuto_actual - ultimo_fallo >= tiempo_recuperacion):
            circuito_abierto = False

        if estrategia == "sin_tacticas":
            if proveedor_caido:
                llamadas_en_caida += 1
                solicitudes_perdidas += 1
            else:
                if rng.random() < p_falla_transitoria:
                    solicitudes_perdidas += 1
                else:
                    completadas += 1

        elif estrategia == "reintentos":
            # Realiza hasta 3 reintentos inmediatos
            exito = False
            for _ in range(3):
                if proveedor_caido:
                    llamadas_en_caida += 1
                else:
                    if rng.random() >= p_falla_transitoria:
                        exito = True
                        break
            if exito:
                completadas += 1
            else:
                solicitudes_perdidas += 1

        elif estrategia == "breaker":
            # Circuit Breaker + Tabla Outbox en PostgreSQL
            if circuito_abierto:
                # Falla rápida: no satura al proveedor y persiste en outbox
                completadas += 1
            else:
                if proveedor_caido:
                    llamadas_en_caida += 1
                    fallas_consecutivas += 1
                    if fallas_consecutivas >= umbral_fallas:
                        circuito_abierto = True
                        ultimo_fallo = minuto_actual
                    completadas += 1  # Guardado en outbox (0 pérdidas)
                else:
                    if rng.random() < p_falla_transitoria:
                        fallas_consecutivas += 1
                        completadas += 1  # Guardado en outbox
                    else:
                        fallas_consecutivas = 0
                        completadas += 1

    return {
        "estrategia": estrategia,
        "total": total_solicitudes,
        "perdidos": solicitudes_perdidas,
        "completados": completadas,
        "llamadas_en_caida": llamadas_en_caida
    }

if __name__ == "__main__":
    for est in ["sin_tacticas", "reintentos", "breaker"]:
        res = simular(est)
        print(f"Estrategia: {est:<13} | Perdidos: {res['perdidos']:<4} | Llamadas en caída: {res['llamadas_en_caida']:<4}")