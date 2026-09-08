# -*- coding: utf-8 -*-
"""
Generador de datos sinteticos reutilizable para las pruebas.

Por que datos SINTETICOS (no un archivo de laboratorio real): al
generarlos nosotros mismos a partir de un circuito conocido (con
parametros que YA sabemos cuales son), podemos verificar que el
algoritmo de ajuste efectivamente recupera esos mismos parametros
dentro de una tolerancia razonable -- algo que no se puede comprobar
con datos reales, porque ahi no conocemos los parametros "verdaderos"
de antemano.
"""

import numpy as np
from impedance.models.circuits import CustomCircuit


def generar_datos_randles_cpe(
    n_puntos=60,
    ruido_relativo=0.01,
    semilla=42,
    parametros=(20.0, 500.0, 1e-5, 0.85),
):
    """
    Genera datos sinteticos de un circuito Randles con CPE
    (R0-p(R1,CPE1)), con ruido gaussiano proporcional a la magnitud de
    cada punto (como en un instrumento real).

    Devuelve (frecuencias, Z, parametros_verdaderos).
    """
    rng = np.random.default_rng(semilla)
    frecuencias = np.logspace(4, -2, n_puntos)

    circuito = CustomCircuit(circuit="R0-p(R1,CPE1)", initial_guess=list(parametros))
    circuito.parameters_ = list(parametros)
    Z = circuito.predict(frecuencias)

    ruido = ruido_relativo * np.abs(Z) * (
        rng.standard_normal(len(Z)) + 1j * rng.standard_normal(len(Z))
    )
    Z_ruidoso = Z + ruido

    # Mismo filtro que usa infrastructure.data_loader en datos reales:
    # se descartan puntos que crucen al semiplano inductivo por ruido.
    frecuencias = frecuencias[np.imag(Z_ruidoso) < 0]
    Z_ruidoso = Z_ruidoso[np.imag(Z_ruidoso) < 0]

    return frecuencias, Z_ruidoso, dict(zip(["Rs", "Rct", "Q", "n"], parametros))
