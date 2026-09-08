# -*- coding: utf-8 -*-
"""
Pruebas unitarias de app.domain.impedance: los calculos puros de EIS,
sin ninguna interfaz de por medio. Cada prueba aisla UNA funcion.
"""

import numpy as np

from app.domain import impedance


def test_validar_kramers_kronig_acepta_datos_limpios(datos_randles_cpe):
    frecuencias, Z, _ = datos_randles_cpe
    valido, mensaje = impedance.validar_kramers_kronig(frecuencias, Z)
    assert bool(valido)
    assert "lin-KK" in mensaje


def test_detectar_semicirculos_encuentra_uno_en_randles_simple(datos_randles_cpe):
    frecuencias, Z, _ = datos_randles_cpe
    n = impedance.detectar_semicirculos(frecuencias, Z)
    assert n == 1


def test_ajustar_circuito_recupera_parametros_conocidos(datos_randles_cpe):
    """
    Prueba central del proyecto: si generamos datos con parametros
    CONOCIDOS y le agregamos ruido realista, el ajuste deberia
    recuperar esos mismos parametros dentro de una tolerancia razonable
    (5%). Esto es lo que da confianza en que el algoritmo realmente
    funciona, mas alla de que "no truene".
    """
    frecuencias, Z, parametros_verdaderos = datos_randles_cpe
    circuito = impedance.ajustar_circuito("randles_cpe", frecuencias, Z)

    nombres = ["Rs", "Rct", "Q", "n"]
    for nombre, valor_ajustado, valor_verdadero in zip(
        nombres, circuito.parameters_, parametros_verdaderos.values()
    ):
        error_relativo = abs(valor_ajustado - valor_verdadero) / abs(valor_verdadero)
        assert error_relativo < 0.05, (
            f"{nombre}: ajustado={valor_ajustado:.4g}, "
            f"verdadero={valor_verdadero:.4g}, error={error_relativo*100:.1f}%"
        )


def test_calcular_aic_bic_devuelve_numeros_finitos(datos_randles_cpe):
    frecuencias, Z, _ = datos_randles_cpe
    circuito = impedance.ajustar_circuito("randles_cpe", frecuencias, Z)
    aic, bic = impedance.calcular_aic_bic(circuito, frecuencias, Z)
    assert np.isfinite(aic)
    assert np.isfinite(bic)


def test_calcular_pesos_akaike_suman_uno():
    pesos = impedance.calcular_pesos_akaike([100.0, 105.0, 130.0])
    assert abs(sum(pesos) - 1.0) < 1e-9
    # El AIC mas bajo debe tener el peso mas alto
    assert pesos[0] > pesos[1] > pesos[2]


def test_calcular_pesos_akaike_con_aic_identicos_reparte_parejo():
    pesos = impedance.calcular_pesos_akaike([50.0, 50.0])
    assert abs(pesos[0] - 0.5) < 1e-9
    assert abs(pesos[1] - 0.5) < 1e-9


def test_calcular_impedancia_con_parametros_reproduce_datos_verdaderos(datos_randles_cpe):
    """
    Si le damos a la simulacion manual los parametros VERDADEROS que
    generaron los datos sinteticos, la curva resultante debe parecerse
    mucho a los datos (el unico error deberia venir del ruido que se
    agrego al generarlos, no de la formula).
    """
    frecuencias, Z, parametros_verdaderos = datos_randles_cpe
    valores = list(parametros_verdaderos.values())
    Z_manual = impedance.calcular_impedancia_con_parametros(
        "randles_cpe", frecuencias, valores
    )
    error_relativo_maximo = np.max(np.abs(Z_manual - Z) / np.abs(Z))
    assert error_relativo_maximo < 0.05


def test_calcular_impedancia_con_parametros_cambia_si_cambian_los_valores(datos_randles_cpe):
    """No debe devolver siempre lo mismo -- si cambio un parametro, la
    curva debe cambiar de verdad (si no, el 'simulador' no serviria de
    nada)."""
    frecuencias, Z, parametros_verdaderos = datos_randles_cpe
    valores = list(parametros_verdaderos.values())

    Z_original = impedance.calcular_impedancia_con_parametros(
        "randles_cpe", frecuencias, valores
    )
    valores_modificados = list(valores)
    valores_modificados[1] *= 2  # Rct al doble
    Z_modificado = impedance.calcular_impedancia_con_parametros(
        "randles_cpe", frecuencias, valores_modificados
    )
    assert np.max(np.abs(Z_modificado - Z_original)) > 1.0


def test_calcular_impedancia_con_parametros_no_falla_sin_ajustar_antes():
    """La simulacion manual debe funcionar aunque el circuito NUNCA se
    haya ajustado (use_initial=True no deberia exigir un fit previo)."""
    frecuencias = np.logspace(4, -2, 30)
    Z = impedance.calcular_impedancia_con_parametros(
        "randles_simple", frecuencias, [10.0, 200.0, 1e-6]
    )
    assert len(Z) == len(frecuencias)
    assert np.all(np.isfinite(Z.real))
    assert np.all(np.isfinite(Z.imag))


def test_error_relativo_porcentual_es_cero_para_datos_identicos():
    Z = np.array([10 + 5j, 20 - 3j, 5 + 1j])
    error = impedance.calcular_error_relativo_porcentual(Z, Z)
    assert error == 0.0


def test_error_relativo_porcentual_detecta_diferencia_conocida():
    # Si el modelo esta exactamente 10% mas alto que los datos en
    # magnitud, el error relativo promedio debe ser 10%.
    Z_datos = np.array([100 + 0j, 200 + 0j, 50 + 0j])
    Z_modelo = Z_datos * 1.10
    error = impedance.calcular_error_relativo_porcentual(Z_modelo, Z_datos)
    assert abs(error - 10.0) < 1e-6


def test_error_relativo_porcentual_es_menor_para_el_ajuste_real(datos_randles_cpe):
    """
    El circuito realmente ajustado deberia tener MENOS error relativo
    que una simulacion manual con parametros deliberadamente
    incorrectos -- si esto no fuera cierto, el indicador de error no
    serviria para nada.
    """
    frecuencias, Z, parametros_verdaderos = datos_randles_cpe
    circuito_ajustado = impedance.ajustar_circuito("randles_cpe", frecuencias, Z)
    Z_ajuste = circuito_ajustado.predict(frecuencias)
    error_ajuste = impedance.calcular_error_relativo_porcentual(Z_ajuste, Z)

    valores_incorrectos = list(parametros_verdaderos.values())
    valores_incorrectos[1] *= 3  # Rct muy exagerado
    Z_manual = impedance.calcular_impedancia_con_parametros(
        "randles_cpe", frecuencias, valores_incorrectos
    )
    error_manual = impedance.calcular_error_relativo_porcentual(Z_manual, Z)

    assert error_ajuste < error_manual
