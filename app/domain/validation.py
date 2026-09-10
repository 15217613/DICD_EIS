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
        if nombre.startswith("R") and valor <= 0:
            return False, f"{nombre}={valor:.3g} es negativo o cero (no tiene sentido fisico)"

        if nombre.startswith("n") and not (0 < valor <= 1):
            return False, f"{nombre}={valor:.3g} fuera del rango valido (0, 1]"

        if nombre.startswith("Q") and valor <= 0:
            return False, f"{nombre}={valor:.3g} es negativo o cero"
        if nombre in ("Wo_mag", "Wo_tau") and valor <= 0:
            return False, f"{nombre}={valor:.3g} es negativo o cero"

        # Capacitancias (C, Cdl) e inductancias (L) tampoco tienen
        # sentido si son negativas o cero -- este chequeo antes solo
        # cubria R, Q y n; se agrega ahora que C y L pasan a ser
        # parametros de primera clase (circuitos simples), pero de
        # paso tambien corrige un vacio que ya existia: Cdl (en
        # randles_simple) nunca se habia validado como positivo.
        if nombre.startswith("C") and valor <= 0:
            return False, f"{nombre}={valor:.3g} es negativo o cero"
        if nombre.startswith("L") and valor <= 0:
            return False, f"{nombre}={valor:.3g} es negativo o cero"

    resistencias = [v for k, v in valores.items() if k.startswith("R")]
    if len(resistencias) > 1 and max(resistencias) / min(resistencias) > 1e6:
        return False, "las resistencias difieren en mas de 6 ordenes de magnitud"

    if nombre_circuito == "dos_constantes_tiempo":
        tau1 = (valores["R1"] * valores["Q1"]) ** (1 / valores["n1"])
        tau2 = (valores["R2"] * valores["Q2"]) ** (1 / valores["n2"])
        razon = max(tau1, tau2) / max(min(tau1, tau2), 1e-30)
        umbral_separacion = 3
        if razon < umbral_separacion:
            return False, (
                f"los dos tiempos caracteristicos son casi iguales "
                f"(razon={razon:.2f}x, minimo esperado={umbral_separacion}x) "
                f"-- probablemente no son dos procesos reales distintos"
            )

    return True, "OK"