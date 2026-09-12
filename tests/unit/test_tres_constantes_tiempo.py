# -*- coding: utf-8 -*-
"""
Pruebas para tres_constantes_tiempo -- el circuito mas complejo (y
mas fragil) de la biblioteca. A diferencia de los demas archivos de
prueba, aqui la "prueba de robustez" no espera un alto porcentaje de
exito: documenta EXPLICITAMENTE que, con el nivel de ruido usado en
el resto del proyecto (1%), este circuito NO es confiable -- ver
domain/impedance.py::estimar_valores_iniciales_multiples_tres_tc para
el analisis completo de por que.
"""

import types

import numpy as np

from app.domain import impedance, validation


def test_estimacion_de_candidatos_incluye_uno_cercano_a_la_verdad_con_ruido_bajo(
    datos_tres_constantes_tiempo_ruido_bajo,
):
    """
    Prueba POSITIVA, pero mas honesta que "ajustar_circuito devuelve
    el resultado correcto": confirma que, entre los candidatos que
    genera estimar_valores_iniciales_multiples_tres_tc, ALGUNO logra
    recuperar los parametros con precision cuando el ruido es casi
    nulo -- es decir, que la deteccion de doble valle SI encuentra el
    punto de partida correcto.

    Por que no se prueba directamente "ajustar_circuito da el
    resultado correcto": se confirmo durante el desarrollo que, incluso
    con ruido casi nulo, el paso de "elegir el candidato con menor
    error residual ponderado" puede escoger un candidato DISTINTO al
    correcto -- con 10 parametros correlacionados, existen soluciones
    casi-degeneradas que ajustan la curva casi tan bien como la
    solucion verdadera, asi que el residual mas bajo no siempre
    corresponde a los parametros correctos. Es una capa adicional de
    fragilidad de este circuito, mas alla de la sensibilidad al ruido
    ya documentada.
    """
    frecuencias, Z, parametros_verdaderos = datos_tres_constantes_tiempo_ruido_bajo
    candidatos = impedance.estimar_valores_iniciales_multiples_tres_tc(frecuencias, Z)

    from impedance.models.circuits import CustomCircuit

    mejor_error_encontrado = np.inf
    for guess in candidatos:
        try:
            circuito = CustomCircuit(
                circuit="R0-p(R1,CPE1)-p(R2,CPE2)-p(R3,CPE3)", initial_guess=guess
            )
            circuito.fit(frecuencias, Z, maxfev=300, weight_by_modulus=True)
        except Exception:
            continue
        error_max = max(
            abs(a - v) / abs(v)
            for a, v in zip(circuito.parameters_, parametros_verdaderos.values())
        )
        mejor_error_encontrado = min(mejor_error_encontrado, error_max)

    assert mejor_error_encontrado < 0.05, (
        f"ni un solo candidato logro recuperar los parametros con precision "
        f"(mejor error encontrado: {mejor_error_encontrado*100:.1f}%) -- esto "
        f"si indicaria un problema real en la deteccion de valles"
    )


def test_tres_constantes_tiempo_documenta_su_fragilidad_con_ruido_realista(
    datos_tres_constantes_tiempo_ruido_realista,
):
    """
    Prueba INFORMATIVA, no una prueba de exito: con 1% de ruido (el
    nivel realista usado en el resto del proyecto), NO se espera una
    recuperacion precisa de parametros -- eso ya se confirmo
    exhaustivamente durante el desarrollo (ver el hallazgo documentado
    en domain/impedance.py). Esta prueba solo confirma que el circuito
    sigue AJUSTANDO SIN TRONAR (no lanza una excepcion) bajo ruido
    realista, y dejar constancia en el codigo de que el error tipico
    es grande -- si algun cambio futuro lo hace fallar con una
    excepcion en vez de simplemente dar un mal ajuste, esta prueba lo
    detecta.
    """
    frecuencias, Z, parametros_verdaderos = datos_tres_constantes_tiempo_ruido_realista
    circuito = impedance.ajustar_circuito("tres_constantes_tiempo", frecuencias, Z)
    assert circuito is not None
    assert len(circuito.parameters_) == 10
    assert np.all(np.isfinite(circuito.parameters_))


def test_tres_constantes_tiempo_con_tau_iguales_se_rechaza():
    """Si dos de los tres procesos colapsan a un tiempo caracteristico
    casi igual (el tipo de resultado degenerado que el ruido realista
    puede producir), el filtro de sentido fisico debe rechazarlo."""
    # tau1 = (100*1e-4)^(1/0.8), tau2 = igual, tau3 bien separado
    circuito_falso = types.SimpleNamespace(
        parameters_=[10.0, 100.0, 1e-4, 0.8, 100.0, 1e-4, 0.8, 500.0, 1e-8, 0.8]
    )
    valido, motivo = validation.es_fisicamente_valido(
        "tres_constantes_tiempo", circuito_falso
    )
    assert valido is False
    assert "1-2" in motivo


def test_tres_constantes_tiempo_con_tau_bien_separados_pasa():
    circuito_falso = types.SimpleNamespace(
        parameters_=[
            10.0, 8000.0, 1.7747574268108018e-08, 0.9,
            1000.0, 1.1641100681759444e-05, 0.85,
            200.0, 0.0030111272272771382, 0.8,
        ]
    )
    valido, motivo = validation.es_fisicamente_valido(
        "tres_constantes_tiempo", circuito_falso
    )
    assert valido is True, motivo


def test_tres_constantes_tiempo_advertencia_aparece_en_la_descripcion():
    """
    Chequeo de que la advertencia visible realmente este en el texto
    que se muestra en la interfaz -- no basta con que exista en un
    comentario de codigo que el usuario final nunca ve.
    """
    from app.presentation import textos_educativos as te

    descripcion = te.DESCRIPCION_CIRCUITOS["tres_constantes_tiempo"]
    assert "ADVERTENCIA" in descripcion
    assert "ruido" in descripcion.lower()