# -*- coding: utf-8 -*-
"""
Fixtures compartidos de pytest. Un "fixture" es una funcion que
prepara algo que varias pruebas necesitan (aqui, datos sinteticos de
EIS) para no repetir la misma preparacion en cada archivo de prueba.
"""

import os

# Las pruebas que abren una ventana de PySide6 necesitan un backend de
# Qt que no requiera una pantalla real -- este entorno de pruebas (y
# cualquier servidor de integracion continua) no tiene una. "offscreen"
# le pide a Qt que renderice en memoria en vez de abrir una ventana de
# verdad. Se define ANTES de que cualquier prueba importe PySide6.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tests.fixtures.synthetic_data import (
    generar_datos_randles_cpe,
    generar_datos_randles_warburg_semiinfinito,
    generar_datos_bucle_inductivo,
    generar_datos_randles_cpe_warburg,
    generar_datos_dos_tiempos_ideal,
    generar_datos_pelicula_transf_difusion,
    generar_datos_dos_tiempos_cpe,
    generar_datos_tres_constantes_tiempo,
)


@pytest.fixture
def datos_randles_cpe():
    """Datos sinteticos de un circuito Randles+CPE conocido, con 1% de
    ruido -- el mismo dataset usado durante todo el desarrollo de este
    proyecto para probar la interfaz manualmente."""
    frecuencias, Z, parametros_verdaderos = generar_datos_randles_cpe()
    return frecuencias, Z, parametros_verdaderos


@pytest.fixture
def datos_randles_warburg_semiinfinito():
    """Datos sinteticos de un circuito Randles con Warburg
    semi-infinito, con parametros elegidos deliberadamente en la zona
    'facil' (Wo_mag menor que Rct) -- ver la nota de robustez en
    synthetic_data.py y en domain/impedance.py."""
    frecuencias, Z, parametros_verdaderos = generar_datos_randles_warburg_semiinfinito()
    return frecuencias, Z, parametros_verdaderos


@pytest.fixture
def datos_bucle_inductivo():
    """Datos sinteticos de un circuito con bucle inductivo (corrosion
    con intermediario adsorbido). A diferencia de otros fixtures, aqui
    los puntos con Im(Z) >= 0 NO se filtran -- son el bucle mismo."""
    frecuencias, Z, parametros_verdaderos = generar_datos_bucle_inductivo()
    return frecuencias, Z, parametros_verdaderos


@pytest.fixture
def datos_randles_cpe_warburg():
    """Datos sinteticos de Randles+CPE+Warburg semi-infinito clasico
    (un solo parametro Aw)."""
    frecuencias, Z, parametros_verdaderos = generar_datos_randles_cpe_warburg()
    return frecuencias, Z, parametros_verdaderos


@pytest.fixture
def datos_pelicula_transferencia_carga():
    """Datos sinteticos de pelicula_transferencia_carga (capacitor
    ideal, dos tiempos): Rs + p(Rpo,Ccoat) + p(Rct,Cdl)."""
    frecuencias, Z, parametros_verdaderos = generar_datos_dos_tiempos_ideal(
        "R0-p(R1,C1)-p(R2,C2)", ["Rs", "Rpo", "Ccoat", "Rct", "Cdl"]
    )
    return frecuencias, Z, parametros_verdaderos


@pytest.fixture
def datos_dos_constantes_tiempo_rc():
    """Datos sinteticos de dos_constantes_tiempo_rc (identico en
    topologia a pelicula_transferencia_carga, nombres genericos)."""
    frecuencias, Z, parametros_verdaderos = generar_datos_dos_tiempos_ideal(
        "R0-p(R1,C1)-p(R2,C2)", ["Rs", "R1", "C1", "R2", "C2"]
    )
    return frecuencias, Z, parametros_verdaderos


@pytest.fixture
def datos_pelicula_transf_difusion():
    """Datos sinteticos de pelicula_transf_difusion (capa + 
    transferencia de carga + difusion)."""
    frecuencias, Z, parametros_verdaderos = generar_datos_pelicula_transf_difusion()
    return frecuencias, Z, parametros_verdaderos


@pytest.fixture
def datos_dos_constantes_tiempo():
    """Datos sinteticos de dos_constantes_tiempo (CPE) -- llena un
    vacio real: este circuito nunca tuvo una prueba de recuperacion
    con datos sinteticos, solo pruebas de validacion con objetos
    falsos."""
    frecuencias, Z, parametros_verdaderos = generar_datos_dos_tiempos_cpe(
        "R0-p(R1,CPE1)-p(R2,CPE2)", ["Rs", "R1", "Q1", "n1", "R2", "Q2", "n2"]
    )
    return frecuencias, Z, parametros_verdaderos


@pytest.fixture
def datos_pelicula_cpe_transferencia():
    """Datos sinteticos de pelicula_cpe_transferencia (identico en
    topologia a dos_constantes_tiempo, nombres de recubrimientos)."""
    frecuencias, Z, parametros_verdaderos = generar_datos_dos_tiempos_cpe(
        "R0-p(R1,CPE1)-p(R2,CPE2)",
        ["Rs", "Rpo", "Qcoat", "ncoat", "Rct", "Qdl", "ndl"],
    )
    return frecuencias, Z, parametros_verdaderos


@pytest.fixture
def datos_tres_constantes_tiempo_ruido_bajo():
    """Tres constantes de tiempo con ruido MUY bajo (0.01%) -- confirma
    que el algoritmo funciona correctamente en condiciones casi
    ideales. NO representa una medicion real (ver
    datos_tres_constantes_tiempo_ruido_realista para eso)."""
    frecuencias, Z, parametros_verdaderos = generar_datos_tres_constantes_tiempo(
        ruido_relativo=0.0001
    )
    return frecuencias, Z, parametros_verdaderos


@pytest.fixture
def datos_tres_constantes_tiempo_ruido_realista():
    """Tres constantes de tiempo con 1% de ruido -- el nivel usado en
    el resto de las pruebas del proyecto. Documenta (no oculta) que
    este circuito es fragil a este nivel de ruido."""
    frecuencias, Z, parametros_verdaderos = generar_datos_tres_constantes_tiempo(
        ruido_relativo=0.01
    )
    return frecuencias, Z, parametros_verdaderos