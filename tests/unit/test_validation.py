# -*- coding: utf-8 -*-
"""
Pruebas unitarias de app.domain.validation: el filtro de sentido
fisico. Aqui se prueban los casos limite (parametros invalidos) usando
objetos de circuito "falsos" -- no hace falta ajustar nada de verdad,
solo verificar que la funcion clasifique bien cada caso.
"""

import types

from app.domain import validation


def _circuito_falso(parameters_):
    """Crea un objeto minimo que se comporta como un CustomCircuit ya
    ajustado, solo con el atributo que es_fisicamente_valido necesita."""
    return types.SimpleNamespace(parameters_=parameters_)


def test_randles_cpe_valido_pasa():
    circuito = _circuito_falso([20.0, 500.0, 1e-5, 0.85])
    valido, motivo = validation.es_fisicamente_valido("randles_cpe", circuito)
    assert valido is True
    assert motivo == "OK"


def test_resistencia_negativa_se_rechaza():
    circuito = _circuito_falso([20.0, -500.0, 1e-5, 0.85])
    valido, motivo = validation.es_fisicamente_valido("randles_cpe", circuito)
    assert valido is False
    assert "negativo" in motivo


def test_exponente_cpe_fuera_de_rango_se_rechaza():
    circuito = _circuito_falso([20.0, 500.0, 1e-5, 1.5])
    valido, motivo = validation.es_fisicamente_valido("randles_cpe", circuito)
    assert valido is False
    assert "rango valido" in motivo


def test_dos_constantes_tiempo_con_tau_iguales_se_rechaza():
    """
    Caso conocido y documentado del proyecto: si los dos "tiempos
    caracteristicos" del circuito de dos constantes de tiempo quedan
    casi iguales, no representan procesos realmente distintos -- es una
    solucion degenerada.
    """
    # R*Q*(jw)^n con R1=R2, Q1=Q2, n1=n2 da tau1 == tau2 exactamente.
    circuito = _circuito_falso([10.0, 100.0, 1e-4, 0.8, 100.0, 1e-4, 0.8])
    valido, motivo = validation.es_fisicamente_valido(
        "dos_constantes_tiempo", circuito
    )
    assert valido is False
    assert "tiempos caracteristicos" in motivo


def test_dos_constantes_tiempo_con_tau_bien_separados_pasa():
    # Un proceso 1000x mas lento que el otro: claramente distintos.
    circuito = _circuito_falso([10.0, 100.0, 1e-6, 0.8, 200.0, 1e-2, 0.8])
    valido, motivo = validation.es_fisicamente_valido(
        "dos_constantes_tiempo", circuito
    )
    assert valido is True
