# -*- coding: utf-8 -*-
"""
Pruebas para el circuito bucle_inductivo (corrosion con intermediario
adsorbido) -- el circuito con topologia mas distinta de la biblioteca
(tres ramas en paralelo, con un elemento inductivo genuino en una de
ellas, no solo capacitivo).
"""

import numpy as np
import pytest
from impedance.models.circuits import CustomCircuit

from app.domain import impedance, validation


def test_ajustar_bucle_inductivo_recupera_parametros_conocidos(
    datos_bucle_inductivo,
):
    frecuencias, Z, parametros_verdaderos = datos_bucle_inductivo
    circuito = impedance.ajustar_circuito("bucle_inductivo", frecuencias, Z)

    nombres = ["Rs", "Rct", "Q", "n", "R3", "L1"]
    for nombre, valor_ajustado, valor_verdadero in zip(
        nombres, circuito.parameters_, parametros_verdaderos.values()
    ):
        error_relativo = abs(valor_ajustado - valor_verdadero) / abs(valor_verdadero)
        assert error_relativo < 0.05, (
            f"{nombre}: ajustado={valor_ajustado:.4g}, "
            f"verdadero={valor_verdadero:.4g}, error={error_relativo*100:.1f}%"
        )


def test_bucle_inductivo_pasa_el_filtro_de_sentido_fisico(datos_bucle_inductivo):
    frecuencias, Z, _ = datos_bucle_inductivo
    circuito = impedance.ajustar_circuito("bucle_inductivo", frecuencias, Z)
    valido, motivo = validation.es_fisicamente_valido("bucle_inductivo", circuito)
    assert valido, motivo


def test_bucle_inductivo_robustez_con_varias_semillas():
    """
    Prueba de robustez (10 semillas independientes, 1% de ruido) --
    misma metodologia que ya se uso para randles_warburg_semiinfinito.
    Con weight_by_modulus=True ya activo en todo el motor, se espera
    una tasa de exito alta.
    """
    parametros_verdaderos = [20.0, 500.0, 1e-5, 0.85, 100.0, 5.0]
    frecuencias = np.logspace(4, -2, 60)
    generador = CustomCircuit(
        circuit="R0-p(R1,CPE1,R3-L1)", initial_guess=parametros_verdaderos
    )
    generador.parameters_ = parametros_verdaderos
    Z = generador.predict(frecuencias)

    exitos = 0
    for semilla in range(10):
        rng = np.random.default_rng(semilla)
        ruido = 0.01 * np.abs(Z) * (
            rng.standard_normal(len(Z)) + 1j * rng.standard_normal(len(Z))
        )
        Z_ruidoso = Z + ruido
        try:
            circuito = impedance.ajustar_circuito(
                "bucle_inductivo", frecuencias, Z_ruidoso
            )
            Z_ajuste = circuito.predict(frecuencias)
            error_pct = impedance.calcular_error_relativo_porcentual(
                Z_ajuste, Z_ruidoso
            )
            if error_pct < 10:
                exitos += 1
        except Exception:
            pass

    assert exitos >= 9, f"solo {exitos}/10 corridas exitosas -- revisar robustez"


def test_bucle_inductivo_no_se_confunde_con_semicirculo_puro(datos_randles_cpe):
    """
    Chequeo de honestidad cientifica: si los datos NO tienen bucle
    inductivo (son un randles_cpe normal), el circuito bucle_inductivo
    todavia deberia poder ajustarse (R3-L1 simplemente termina siendo
    un aporte insignificante), pero NO deberia ganarle a randles_cpe
    en AIC, porque tiene 2 parametros de mas sin necesidad real.
    """
    frecuencias, Z, _ = datos_randles_cpe
    circuito_simple = impedance.ajustar_circuito("randles_cpe", frecuencias, Z)
    aic_simple, _ = impedance.calcular_aic_bic(circuito_simple, frecuencias, Z)

    circuito_bucle = impedance.ajustar_circuito("bucle_inductivo", frecuencias, Z)
    aic_bucle, _ = impedance.calcular_aic_bic(circuito_bucle, frecuencias, Z)

    assert aic_simple < aic_bucle, (
        "randles_cpe deberia tener menor AIC que bucle_inductivo cuando "
        "los datos no tienen bucle inductivo real -- si esto falla, el "
        "criterio AIC no esta penalizando bien los parametros de mas"
    )