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


def generar_datos_randles_warburg_semiinfinito(
    n_puntos=60,
    ruido_relativo=0.01,
    semilla=7,
    # OJO con estos parametros "por defecto": se eligieron a proposito
    # con Wo_mag (150) MENOR que Rct (500) -- confirmado con pruebas
    # de robustez, el ajuste de este circuito se vuelve muy fragil
    # cuando Wo_mag es comparable o mayor que Rct (ver la nota en
    # domain/impedance.py::ajustar_circuito). Si cambias estos valores
    # para otra prueba, evita esa combinacion o el ajuste puede fallar
    # a converger sin que sea un bug del codigo.
    parametros=(20.0, 500.0, 150.0, 8.0, 1e-5, 0.85),
):
    """
    Genera datos sinteticos de un circuito Randles con Warburg
    semi-infinito (R0-p(R1-Wo1,CPE1)).

    Devuelve (frecuencias, Z, parametros_verdaderos).
    """
    rng = np.random.default_rng(semilla)
    frecuencias = np.logspace(4, -2, n_puntos)

    circuito = CustomCircuit(
        circuit="R0-p(R1-Wo1,CPE1)", initial_guess=list(parametros)
    )
    circuito.parameters_ = list(parametros)
    Z = circuito.predict(frecuencias)

    ruido = ruido_relativo * np.abs(Z) * (
        rng.standard_normal(len(Z)) + 1j * rng.standard_normal(len(Z))
    )
    Z_ruidoso = Z + ruido

    frecuencias = frecuencias[np.imag(Z_ruidoso) < 0]
    Z_ruidoso = Z_ruidoso[np.imag(Z_ruidoso) < 0]

    nombres = ["Rs", "Rct", "Wo_mag", "Wo_tau", "Q", "n"]
    return frecuencias, Z_ruidoso, dict(zip(nombres, parametros))


def generar_datos_bucle_inductivo(
    n_puntos=60,
    ruido_relativo=0.01,
    semilla=3,
    parametros=(20.0, 500.0, 1e-5, 0.85, 100.0, 5.0),
):
    """
    Genera datos sinteticos de un circuito con bucle inductivo
    (R0-p(R1,CPE1,R3-L1)) -- el modelo clasico de corrosion con un
    intermediario adsorbido.

    Devuelve (frecuencias, Z, parametros_verdaderos).
    """
    rng = np.random.default_rng(semilla)
    frecuencias = np.logspace(4, -2, n_puntos)

    circuito = CustomCircuit(
        circuit="R0-p(R1,CPE1,R3-L1)", initial_guess=list(parametros)
    )
    circuito.parameters_ = list(parametros)
    Z = circuito.predict(frecuencias)

    ruido = ruido_relativo * np.abs(Z) * (
        rng.standard_normal(len(Z)) + 1j * rng.standard_normal(len(Z))
    )
    Z_ruidoso = Z + ruido

    # OJO: a diferencia de los demas generadores de este archivo, AQUI
    # NO se descartan los puntos con Im(Z) >= 0 -- esos puntos son
    # justamente el bucle inductivo que le da sentido al circuito. El
    # filtro real (infrastructure/data_loader.py) tampoco los
    # descartaria: solo recorta un tramo INICIAL de puntos inductivos
    # (ruido cerca de la frecuencia mas alta), y aqui no hay ninguno.
    nombres = ["Rs", "Rct", "Q", "n", "R3", "L1"]
    return frecuencias, Z_ruidoso, dict(zip(nombres, parametros))