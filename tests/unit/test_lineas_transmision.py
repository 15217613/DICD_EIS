# -*- coding: utf-8 -*-
"""
Pruebas para los dos circuitos de linea de transmision (tlm_rc, con el
elemento T de impedance.py; linea_transmision_electroquimica, con el
elemento TLMQ). A diferencia del resto de la biblioteca, estos NO son
combinaciones de R/C/CPE discretos -- representan un electrodo poroso
con estructura continua, usando los elementos ya construidos en
impedance.py en vez de armar una escalera de R y C a mano.
"""

import types

from app.domain import impedance, validation


# ---------------------------------------------------------------------------
# tlm_rc (modelo de Paasch: A, B, a, b)
# ---------------------------------------------------------------------------
def test_ajustar_tlm_rc_recupera_parametros_conocidos(datos_tlm_rc):
    frecuencias, Z, parametros_verdaderos = datos_tlm_rc
    circuito = impedance.ajustar_circuito("tlm_rc", frecuencias, Z)

    for nombre, v_ajustado, v_verdadero in zip(
        ["Rs", "A", "B", "a", "b"], circuito.parameters_,
        parametros_verdaderos.values(),
    ):
        error = abs(v_ajustado - v_verdadero) / abs(v_verdadero)
        assert error < 0.15, f"{nombre}: error={error*100:.1f}%"


def test_tlm_rc_pasa_el_filtro_de_sentido_fisico(datos_tlm_rc):
    frecuencias, Z, _ = datos_tlm_rc
    circuito = impedance.ajustar_circuito("tlm_rc", frecuencias, Z)
    valido, motivo = validation.es_fisicamente_valido("tlm_rc", circuito)
    assert valido, motivo


def test_tlm_rc_con_parametro_a_negativo_se_rechaza():
    circuito_falso = types.SimpleNamespace(
        parameters_=[20.0, 500.0, 500.0, -1.0, 0.05]
    )
    valido, motivo = validation.es_fisicamente_valido("tlm_rc", circuito_falso)
    assert valido is False
    assert "negativo" in motivo


# ---------------------------------------------------------------------------
# linea_transmision_electroquimica (modelo de Landesfeind: Rion, Qs, gamma)
# ---------------------------------------------------------------------------
def test_ajustar_linea_transmision_electroquimica_recupera_parametros_conocidos(
    datos_linea_transmision_electroquimica,
):
    frecuencias, Z, parametros_verdaderos = datos_linea_transmision_electroquimica
    circuito = impedance.ajustar_circuito(
        "linea_transmision_electroquimica", frecuencias, Z
    )

    for nombre, v_ajustado, v_verdadero in zip(
        ["Rs", "Rion", "Qs", "gamma"], circuito.parameters_,
        parametros_verdaderos.values(),
    ):
        error = abs(v_ajustado - v_verdadero) / abs(v_verdadero)
        assert error < 0.10, f"{nombre}: error={error*100:.1f}%"


def test_linea_transmision_electroquimica_pasa_el_filtro_de_sentido_fisico(
    datos_linea_transmision_electroquimica,
):
    frecuencias, Z, _ = datos_linea_transmision_electroquimica
    circuito = impedance.ajustar_circuito(
        "linea_transmision_electroquimica", frecuencias, Z
    )
    valido, motivo = validation.es_fisicamente_valido(
        "linea_transmision_electroquimica", circuito
    )
    assert valido, motivo


def test_linea_transmision_electroquimica_con_gamma_fuera_de_rango_se_rechaza():
    circuito_falso = types.SimpleNamespace(parameters_=[20.0, 2000.0, 1e-4, 1.5])
    valido, motivo = validation.es_fisicamente_valido(
        "linea_transmision_electroquimica", circuito_falso
    )
    assert valido is False
    assert "rango valido" in motivo


def test_linea_transmision_electroquimica_con_rion_negativo_se_rechaza():
    circuito_falso = types.SimpleNamespace(parameters_=[20.0, -100.0, 1e-4, 0.9])
    valido, motivo = validation.es_fisicamente_valido(
        "linea_transmision_electroquimica", circuito_falso
    )
    assert valido is False
    assert "negativo" in motivo