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