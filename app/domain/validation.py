# -*- coding: utf-8 -*-
"""
Filtro de sentido fisico: revisa que los parametros que arrojo el
ajuste numerico tengan sentido como cantidades fisicas reales (una
resistencia no puede ser negativa, etc.), no solo que el numero haya
convergido matematicamente.

impedance.py ya evita valores negativos y n>1 con sus limites por
defecto durante el ajuste; aqui se agregan chequeos MAS especificos
(por ejemplo, dos "tiempos caracteristicos" casi iguales en el
circuito de dos constantes de tiempo), explicando el motivo de cada
uno para que el usuario entienda por que se descarto un circuito.
"""

from app.domain.circuits import CIRCUITOS


def es_fisicamente_valido(nombre_circuito, circuit):
    """
    Devuelve (True, "OK") si el circuito ajustado tiene sentido fisico,
    o (False, motivo) si no.
    """
    nombres_parametros = CIRCUITOS[nombre_circuito].parametros
    valores = dict(zip(nombres_parametros, circuit.parameters_))

    for nombre, valor in valores.items():
        # Ninguna resistencia (Rs, Rct, R1, R2) puede ser negativa o
        # cero: una resistencia negativa no existe fisicamente.
        if nombre.startswith("R") and valor <= 0:
            return False, f"{nombre}={valor:.3g} es negativo o cero (no tiene sentido fisico)"

        # El exponente "n" del CPE debe estar entre 0 y 1 por
        # definicion matematica del elemento.
        if nombre.startswith("n") and not (0 < valor <= 1):
            return False, f"{nombre}={valor:.3g} fuera del rango valido (0, 1]"

        # Q (el CPE) y los parametros de Warburg deben ser positivos.
        if nombre.startswith("Q") and valor <= 0:
            return False, f"{nombre}={valor:.3g} es negativo o cero"
        if nombre in ("Wo_mag", "Wo_tau") and valor <= 0:
            return False, f"{nombre}={valor:.3g} es negativo o cero"

    # Si alguna resistencia queda muchisimo mas grande que las demas
    # (varios ordenes de magnitud), suele ser senal de que el ajuste
    # "se disparo" a una solucion sin sentido.
    resistencias = [v for k, v in valores.items() if k.startswith("R")]
    if len(resistencias) > 1 and max(resistencias) / min(resistencias) > 1e6:
        return False, "las resistencias difieren en mas de 6 ordenes de magnitud"

    # Chequeo especial para dos_constantes_tiempo: si los dos "tiempos
    # caracteristicos" quedan casi iguales, el circuito no representa
    # dos procesos REALMENTE distintos -- es una solucion degenerada,
    # probablemente imitando la forma de otro circuito (confirmado con
    # pruebas de robustez: pasa justo donde se confunde con
    # randles_warburg). tau = (R*Q)^(1/n) es la formula estandar del
    # tiempo de relajacion de un elemento R-CPE en paralelo.
    if nombre_circuito == "dos_constantes_tiempo":
        tau1 = (valores["R1"] * valores["Q1"]) ** (1 / valores["n1"])
        tau2 = (valores["R2"] * valores["Q2"]) ** (1 / valores["n2"])
        razon = max(tau1, tau2) / max(min(tau1, tau2), 1e-30)
        umbral_separacion = 3  # los tiempos deben diferir al menos 3x
        if razon < umbral_separacion:
            return False, (
                f"los dos tiempos caracteristicos son casi iguales "
                f"(razon={razon:.2f}x, minimo esperado={umbral_separacion}x) "
                f"-- probablemente no son dos procesos reales distintos"
            )

    return True, "OK"
