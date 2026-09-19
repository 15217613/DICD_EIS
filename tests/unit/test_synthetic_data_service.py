# -*- coding: utf-8 -*-
"""
Pruebas del generador didactico de datos sinteticos: la funcion de
dominio que agrega ruido (domain/impedance.py::simular_impedancia_con_ruido)
y el servicio de aplicacion que arma el rango de frecuencias y orquesta
todo (application/synthetic_data_service.py).
"""

import numpy as np
import pytest

from app.domain import impedance
from app.application import synthetic_data_service as sds


def test_generar_frecuencias_espaciado_logaritmico_descendente():
    frecuencias = sds.generar_frecuencias(100000, 0.01, puntos_por_decada=10)
    assert frecuencias[0] == pytest.approx(100000)
    assert frecuencias[-1] == pytest.approx(0.01)
    # 7 decadas (1e5 a 1e-2) x 10 puntos/decada + 1 = 71 puntos
    assert len(frecuencias) == 71
    assert np.all(np.diff(frecuencias) < 0)  # descendente, como un barrido real


def test_generar_frecuencias_acepta_orden_ascendente_tambien():
    frecuencias = sds.generar_frecuencias(0.01, 1000, puntos_por_decada=5)
    assert frecuencias[0] == pytest.approx(0.01)
    assert frecuencias[-1] == pytest.approx(1000)


def test_generar_frecuencias_rechaza_valores_no_positivos():
    with pytest.raises(sds.ErrorGeneracionSintetica):
        sds.generar_frecuencias(-100, 0.01)
    with pytest.raises(sds.ErrorGeneracionSintetica):
        sds.generar_frecuencias(100, 0)


def test_generar_frecuencias_rechaza_inicio_igual_a_final():
    with pytest.raises(sds.ErrorGeneracionSintetica):
        sds.generar_frecuencias(100, 100)


def test_simular_impedancia_sin_ruido_devuelve_la_misma_curva_dos_veces():
    frecuencias = np.logspace(4, -2, 30)
    Z_teorico, Z_sin_ruido = impedance.simular_impedancia_con_ruido(
        "randles_cpe", [20.0, 500.0, 1e-5, 0.85], frecuencias, ruido_relativo=0.0
    )
    assert np.allclose(Z_teorico, Z_sin_ruido)


def test_simular_impedancia_con_ruido_se_aleja_de_la_curva_teorica():
    frecuencias = np.logspace(4, -2, 30)
    valores = [20.0, 500.0, 1e-5, 0.85]
    Z_teorico, Z_con_ruido = impedance.simular_impedancia_con_ruido(
        "randles_cpe", valores, frecuencias, ruido_relativo=0.05, semilla=1
    )
    # Con 5% de ruido, la curva ruidosa NO debe ser identica a la
    # teorica, pero tampoco debe estar disparatadamente lejos.
    diferencia_relativa = np.abs(Z_con_ruido - Z_teorico) / np.abs(Z_teorico)
    assert np.mean(diferencia_relativa) > 0
    assert np.mean(diferencia_relativa) < 0.3


def test_simular_impedancia_misma_semilla_da_el_mismo_ruido():
    frecuencias = np.logspace(4, -2, 30)
    valores = [20.0, 500.0, 1e-5, 0.85]
    _, Z1 = impedance.simular_impedancia_con_ruido(
        "randles_cpe", valores, frecuencias, ruido_relativo=0.02, semilla=7
    )
    _, Z2 = impedance.simular_impedancia_con_ruido(
        "randles_cpe", valores, frecuencias, ruido_relativo=0.02, semilla=7
    )
    assert np.allclose(Z1, Z2)


def test_generar_datos_sinteticos_extremo_a_extremo_recupera_el_circuito():
    """
    Prueba central de esta funcionalidad: si le pido al generador
    'randles_cpe' con valores conocidos y 1% de ruido (el nivel
    realista usado en todo el proyecto), el analisis automatico
    deberia recuperar ESE mismo circuito como el mejor -- es la misma
    logica de test_impedance.py::test_ajustar_circuito_recupera_parametros_conocidos,
    pero pasando por el generador didactico completo en vez de la
    funcion de dominio directamente.
    """
    from app.application import analysis_service

    valores_verdaderos = [20.0, 500.0, 1e-5, 0.85]
    frecuencias, _Z_teorico, Z_con_ruido = sds.generar_datos_sinteticos(
        "randles_cpe", valores_verdaderos, f_inicial=100000, f_final=0.01,
        puntos_por_decada=10, ruido_relativo=0.01, semilla=42,
    )
    resultado = analysis_service.ejecutar_analisis(frecuencias, Z_con_ruido)
    assert len(resultado.mejores) > 0
    assert resultado.mejores[0].nombre == "randles_cpe"


def test_generar_datos_sinteticos_valores_invalidos_da_error_amigable():
    with pytest.raises(sds.ErrorGeneracionSintetica):
        # n=5 esta fuera de rango fisico, pero eso no es lo que se
        # prueba aqui -- lo que se prueba es que un valor que rompe la
        # FORMULA (como una R negativa en un elemento que no la
        # admite) se traduce en un mensaje amigable, no en una
        # excepcion cruda de impedance.py.
        sds.generar_datos_sinteticos(
            "capacitor_ideal", ["no es un numero"], f_inicial=1000, f_final=0.1,
        )