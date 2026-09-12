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
    nombres = ["Rs", "Rct", "Q", "n", "Rad", "Lad"]
    return frecuencias, Z_ruidoso, dict(zip(nombres, parametros))


def generar_datos_randles_cpe_warburg(
    n_puntos=60,
    ruido_relativo=0.01,
    semilla=1,
    parametros=(20.0, 500.0, 50.0, 1e-5, 0.85),
):
    """Randles + CPE + Warburg semi-infinito clasico (un solo
    parametro Aw). Devuelve (frecuencias, Z, parametros_verdaderos)."""
    rng = np.random.default_rng(semilla)
    frecuencias = np.logspace(4, -2, n_puntos)
    circuito = CustomCircuit(circuit="R0-p(R1-W1,CPE1)", initial_guess=list(parametros))
    circuito.parameters_ = list(parametros)
    Z = circuito.predict(frecuencias)
    ruido = ruido_relativo * np.abs(Z) * (
        rng.standard_normal(len(Z)) + 1j * rng.standard_normal(len(Z))
    )
    Z_ruidoso = Z + ruido
    frecuencias = frecuencias[np.imag(Z_ruidoso) < 0]
    Z_ruidoso = Z_ruidoso[np.imag(Z_ruidoso) < 0]
    nombres = ["Rs", "Rct", "Aw", "Q", "n"]
    return frecuencias, Z_ruidoso, dict(zip(nombres, parametros))


def generar_datos_dos_tiempos_ideal(
    circuito_string,
    nombres_parametros,
    n_puntos=60,
    ruido_relativo=0.01,
    semilla=2,
    # OJO con estos valores por defecto: las frecuencias
    # caracteristicas (1/(2*pi*R*C)) de AMBOS procesos deben caer
    # DENTRO del rango medido (0.01 a 10000 Hz) y estar razonablemente
    # separadas para poder distinguirse -- confirmado con pruebas: si
    # el primer proceso tiene una frecuencia caracteristica por ENCIMA
    # del rango medido, su pico nunca se alcanza a ver y la deteccion
    # de dos picos se vuelve imposible (no es un bug del ajuste, es
    # una limitacion real de que datos se pueden medir).
    parametros=(20.0, 5000.0, 3e-8, 500.0, 3e-5),
):
    """
    Generador generico para los circuitos de dos constantes de tiempo
    con capacitor IDEAL (pelicula_transferencia_carga,
    dos_constantes_tiempo_rc): Rs + p(R1,C1) + p(R2,C2).
    """
    rng = np.random.default_rng(semilla)
    frecuencias = np.logspace(4, -2, n_puntos)
    circuito = CustomCircuit(circuit=circuito_string, initial_guess=list(parametros))
    circuito.parameters_ = list(parametros)
    Z = circuito.predict(frecuencias)
    ruido = ruido_relativo * np.abs(Z) * (
        rng.standard_normal(len(Z)) + 1j * rng.standard_normal(len(Z))
    )
    Z_ruidoso = Z + ruido
    frecuencias = frecuencias[np.imag(Z_ruidoso) < 0]
    Z_ruidoso = Z_ruidoso[np.imag(Z_ruidoso) < 0]
    return frecuencias, Z_ruidoso, dict(zip(nombres_parametros, parametros))


def generar_datos_pelicula_transf_difusion(
    n_puntos=60,
    ruido_relativo=0.01,
    semilla=4,
    # Mismo cuidado que en generar_datos_dos_tiempos_ideal, mas Aw
    # elegido lo bastante grande para ser detectable frente al resto
    # de las resistencias (confirmado con pruebas: un Aw muy chico
    # comparado con Rpo/Rct se pierde en el 1% de ruido).
    parametros=(20.0, 5000.0, 3e-8, 500.0, 30.0, 3e-5),
):
    """Pelicula + transferencia de carga + difusion: Rs + p(R1,C1) +
    p(R2-W1,C2). Devuelve (frecuencias, Z, parametros_verdaderos)."""
    rng = np.random.default_rng(semilla)
    frecuencias = np.logspace(4, -2, n_puntos)
    circuito = CustomCircuit(
        circuit="R0-p(R1,C1)-p(R2-W1,C2)", initial_guess=list(parametros)
    )
    circuito.parameters_ = list(parametros)
    Z = circuito.predict(frecuencias)
    ruido = ruido_relativo * np.abs(Z) * (
        rng.standard_normal(len(Z)) + 1j * rng.standard_normal(len(Z))
    )
    Z_ruidoso = Z + ruido
    frecuencias = frecuencias[np.imag(Z_ruidoso) < 0]
    Z_ruidoso = Z_ruidoso[np.imag(Z_ruidoso) < 0]
    nombres = ["Rs", "Rpo", "Ccoat", "Rct", "Aw", "Cdl"]
    return frecuencias, Z_ruidoso, dict(zip(nombres, parametros))


def generar_datos_dos_tiempos_cpe(
    circuito_string,
    nombres_parametros,
    n_puntos=60,
    ruido_relativo=0.01,
    semilla=2,
    # Mismo cuidado con las frecuencias caracteristicas que en
    # generar_datos_dos_tiempos_ideal -- deben caer dentro del rango
    # medido para que los dos picos sean detectables.
    parametros=(20.0, 5000.0, 1e-6, 0.8, 500.0, 1e-4, 0.8),
):
    """
    Generador generico para los circuitos de dos constantes de tiempo
    CON CPE (dos_constantes_tiempo, pelicula_cpe_transferencia):
    Rs + p(R1,CPE1) + p(R2,CPE2).
    """
    rng = np.random.default_rng(semilla)
    frecuencias = np.logspace(4, -2, n_puntos)
    circuito = CustomCircuit(circuit=circuito_string, initial_guess=list(parametros))
    circuito.parameters_ = list(parametros)
    Z = circuito.predict(frecuencias)
    ruido = ruido_relativo * np.abs(Z) * (
        rng.standard_normal(len(Z)) + 1j * rng.standard_normal(len(Z))
    )
    Z_ruidoso = Z + ruido
    frecuencias = frecuencias[np.imag(Z_ruidoso) < 0]
    Z_ruidoso = Z_ruidoso[np.imag(Z_ruidoso) < 0]
    return frecuencias, Z_ruidoso, dict(zip(nombres_parametros, parametros))


def generar_datos_tres_constantes_tiempo(
    n_puntos=80,
    ruido_relativo=0.01,
    semilla=1,
    # OJO con estos valores por defecto: las TRES resistencias son del
    # MISMO orden de magnitud (500 ohms cada una) a proposito --
    # confirmado con pruebas: si son muy distintas entre si (por
    # ejemplo 8000/1000/200), el semicirculo mas grande "se traga"
    # visualmente a los demas y nunca se distinguen como bultos
    # separados, sin importar que tan bien separadas esten sus
    # frecuencias caracteristicas. Las frecuencias caracteristicas
    # SI estan bien separadas (~100x entre si) via Q muy distintos.
    parametros=(20.0, 500.0, 2.839611882897283e-07, 0.9,
                500.0, 2.328220136351889e-05, 0.85,
                500.0, 0.0012044508909108554, 0.8),
):
    """Tres constantes de tiempo: Rs + p(R1,CPE1) + p(R2,CPE2) +
    p(R3,CPE3). Devuelve (frecuencias, Z, parametros_verdaderos)."""
    rng = np.random.default_rng(semilla)
    frecuencias = np.logspace(4, -3, n_puntos)
    circuito = CustomCircuit(
        circuit="R0-p(R1,CPE1)-p(R2,CPE2)-p(R3,CPE3)",
        initial_guess=list(parametros),
    )
    circuito.parameters_ = list(parametros)
    Z = circuito.predict(frecuencias)
    ruido = ruido_relativo * np.abs(Z) * (
        rng.standard_normal(len(Z)) + 1j * rng.standard_normal(len(Z))
    )
    Z_ruidoso = Z + ruido
    frecuencias = frecuencias[np.imag(Z_ruidoso) < 0]
    Z_ruidoso = Z_ruidoso[np.imag(Z_ruidoso) < 0]
    nombres = ["Rs", "R1", "Q1", "n1", "R2", "Q2", "n2", "R3", "Q3", "n3"]
    return frecuencias, Z_ruidoso, dict(zip(nombres, parametros))