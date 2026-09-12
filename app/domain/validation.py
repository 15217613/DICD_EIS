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

# Mapea cada circuito con "dos procesos parecidos en serie" a los
# nombres de parametro que definen el TIEMPO CARACTERISTICO de cada
# proceso (ver el chequeo de ambiguedad mas abajo). Cada entrada es
# (R_proceso1, C_o_Q_proceso1, n_proceso1_o_None,
#  R_proceso2, C_o_Q_proceso2, n_proceso2_o_None) -- "None" para los
# circuitos con capacitor IDEAL, donde no existe un exponente n (se
# asume n=1 implicitamente).
_ESQUEMA_DOS_TIEMPOS = {
    "pelicula_cpe_transferencia": ("Rpo", "Qcoat", "ncoat", "Rct", "Qdl", "ndl"),
    "pelicula_transferencia_carga": ("Rpo", "Ccoat", None, "Rct", "Cdl", None),
    "dos_constantes_tiempo_rc": ("R1", "C1", None, "R2", "C2", None),
    "pelicula_transf_difusion": ("Rpo", "Ccoat", None, "Rct", "Cdl", None),
}


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

    elif nombre_circuito in _ESQUEMA_DOS_TIEMPOS:
        # Generalizacion del chequeo anterior a los circuitos nuevos
        # que comparten la MISMA ambiguedad de fondo (dos ramas R-C o
        # R-CPE en serie, con tiempos de relajacion que se pueden
        # confundir entre si): pelicula_cpe_transferencia (mismo
        # calculo que dos_constantes_tiempo, solo con otros nombres de
        # parametro), y las variantes con capacitor IDEAL
        # (pelicula_transferencia_carga, dos_constantes_tiempo_rc,
        # pelicula_transf_difusion), donde tau = R*C directamente
        # (equivalente a asumir exponente n=1).
        nombre_R1, nombre_C1, nombre_n1, nombre_R2, nombre_C2, nombre_n2 = (
            _ESQUEMA_DOS_TIEMPOS[nombre_circuito]
        )
        exponente1 = valores[nombre_n1] if nombre_n1 else 1.0
        exponente2 = valores[nombre_n2] if nombre_n2 else 1.0
        tau1 = (valores[nombre_R1] * valores[nombre_C1]) ** (1 / exponente1)
        tau2 = (valores[nombre_R2] * valores[nombre_C2]) ** (1 / exponente2)
        razon = max(tau1, tau2) / max(min(tau1, tau2), 1e-30)
        umbral_separacion = 3
        if razon < umbral_separacion:
            return False, (
                f"los dos tiempos caracteristicos son casi iguales "
                f"(razon={razon:.2f}x, minimo esperado={umbral_separacion}x) "
                f"-- probablemente no son dos procesos reales distintos "
                f"(por ejemplo, la capa y la transferencia de carga no se "
                f"alcanzan a distinguir con estos datos)"
            )

    elif nombre_circuito == "tres_constantes_tiempo":
        # Extension a TRES procesos: se revisan las tres parejas
        # posibles (1-2, 2-3, 1-3). Si CUALQUIER pareja tiene tiempos
        # casi iguales, se rechaza -- con tres procesos hay mas
        # oportunidades de que dos de ellos terminen colapsando en
        # uno solo (justo el tipo de resultado degenerado que las
        # pruebas de robustez mostraron que es comun en este circuito
        # con ruido realista).
        tau1 = (valores["R1"] * valores["Q1"]) ** (1 / valores["n1"])
        tau2 = (valores["R2"] * valores["Q2"]) ** (1 / valores["n2"])
        tau3 = (valores["R3"] * valores["Q3"]) ** (1 / valores["n3"])
        umbral_separacion = 3
        parejas = [("1-2", tau1, tau2), ("2-3", tau2, tau3), ("1-3", tau1, tau3)]
        for etiqueta, ta, tb in parejas:
            razon = max(ta, tb) / max(min(ta, tb), 1e-30)
            if razon < umbral_separacion:
                return False, (
                    f"los tiempos caracteristicos de los procesos {etiqueta} "
                    f"son casi iguales (razon={razon:.2f}x, minimo "
                    f"esperado={umbral_separacion}x) -- probablemente no son "
                    f"procesos reales distintos"
                )

    return True, "OK"