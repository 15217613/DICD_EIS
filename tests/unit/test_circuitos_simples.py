# -*- coding: utf-8 -*-
"""
Pruebas para los circuitos simples (resistencia_pura, capacitor_ideal,
inductor_ideal, rc_serie, rc_paralelo): al ser combinaciones directas
de 1-2 elementos con formulas cerradas, se espera una recuperacion de
parametros MUY precisa (menos del 3% de error con 1% de ruido) -- a
diferencia de circuitos con CPE o Warburg, aqui no hay ambiguedad
posible entre parametros.
"""

import numpy as np
import pytest
from impedance.models.circuits import CustomCircuit

from app.domain import impedance, validation


def _generar_datos(string_circuito, valores, semilla=1, ruido_relativo=0.01):
    frecuencias = np.logspace(4, -2, 50)
    circuito = CustomCircuit(circuit=string_circuito, initial_guess=list(valores))
    circuito.parameters_ = list(valores)
    Z = circuito.predict(frecuencias)

    rng = np.random.default_rng(semilla)
    ruido = ruido_relativo * np.abs(Z) * (
        rng.standard_normal(len(Z)) + 1j * rng.standard_normal(len(Z))
    )
    Z_ruidoso = Z + ruido
    mask = np.imag(Z_ruidoso) < 0
    return frecuencias[mask], Z_ruidoso[mask]


CASOS = [
    ("resistencia_pura", "R0", [120.0]),
    ("capacitor_ideal", "C0", [2e-6]),
    ("rc_serie", "R0-C0", [80.0, 3e-6]),
    ("rc_paralelo", "p(R0,C0)", [400.0, 5e-6]),
]


@pytest.mark.parametrize("nombre_circuito,string_circuito,valores_verdaderos", CASOS)
def test_ajustar_circuitos_simples_recupera_parametros_conocidos(
    nombre_circuito, string_circuito, valores_verdaderos
):
    frecuencias, Z = _generar_datos(string_circuito, valores_verdaderos)
    circuito_ajustado = impedance.ajustar_circuito(nombre_circuito, frecuencias, Z)

    for v_ajustado, v_verdadero in zip(circuito_ajustado.parameters_, valores_verdaderos):
        error_relativo = abs(v_ajustado - v_verdadero) / abs(v_verdadero)
        assert error_relativo < 0.03, (
            f"{nombre_circuito}: ajustado={v_ajustado:.4g}, "
            f"verdadero={v_verdadero:.4g}, error={error_relativo*100:.1f}%"
        )


def test_inductor_ideal_recupera_parametro_conocido():
    # Caso aparte porque el inductor puro da Z.imag > 0 (arriba del
    # eje en la convencion -Z.imag) -- el filtro de
    # infrastructure/data_loader.py descarta esos puntos por disenio
    # (ver docstring de data_loader.py), asi que aqui se prueba
    # directamente con domain/impedance.py, sin ese filtro.
    frecuencias = np.logspace(4, -2, 50)
    L_verdadero = 5e-4
    circuito = CustomCircuit(circuit="L0", initial_guess=[L_verdadero])
    circuito.parameters_ = [L_verdadero]
    Z = circuito.predict(frecuencias)

    rng = np.random.default_rng(1)
    ruido = 0.01 * np.abs(Z) * (
        rng.standard_normal(len(Z)) + 1j * rng.standard_normal(len(Z))
    )
    Z_ruidoso = Z + ruido

    circuito_ajustado = impedance.ajustar_circuito("inductor_ideal", frecuencias, Z_ruidoso)
    error_relativo = abs(circuito_ajustado.parameters_[0] - L_verdadero) / L_verdadero
    assert error_relativo < 0.03


@pytest.mark.parametrize("nombre_circuito,string_circuito,valores_verdaderos", CASOS)
def test_circuitos_simples_pasan_el_filtro_de_sentido_fisico(
    nombre_circuito, string_circuito, valores_verdaderos
):
    frecuencias, Z = _generar_datos(string_circuito, valores_verdaderos)
    circuito_ajustado = impedance.ajustar_circuito(nombre_circuito, frecuencias, Z)
    valido, motivo = validation.es_fisicamente_valido(nombre_circuito, circuito_ajustado)
    assert valido, motivo


def test_resistencia_negativa_en_circuito_simple_se_rechaza():
    """El chequeo generico de R<=0 ya existia -- se confirma que
    tambien aplica cuando el parametro se llama simplemente 'R' (no
    'Rct' ni 'Rs')."""
    import types
    circuito_falso = types.SimpleNamespace(parameters_=[-50.0])
    valido, motivo = validation.es_fisicamente_valido("resistencia_pura", circuito_falso)
    assert valido is False
    assert "negativo" in motivo


def test_capacitor_negativo_se_rechaza():
    """Chequeo NUEVO agregado en esta sesion: antes de esto, un
    parametro que empezara con 'C' nunca se validaba como positivo."""
    import types
    circuito_falso = types.SimpleNamespace(parameters_=[-1e-6])
    valido, motivo = validation.es_fisicamente_valido("capacitor_ideal", circuito_falso)
    assert valido is False
    assert "negativo" in motivo