# -*- coding: utf-8 -*-
"""
Prueba central para el circuito randles_warburg_semiinfinito, en el
mismo espiritu que test_ajustar_circuito_recupera_parametros_conocidos
de test_impedance.py: generar datos con parametros CONOCIDOS y
confirmar que el ajuste los recupera dentro de una tolerancia
razonable.

Se usa una tolerancia del 10% (no 5%, como randles_cpe) a proposito:
las pruebas de robustez (ver domain/impedance.py::ajustar_circuito)
mostraron que este circuito, incluso en su zona 'facil' de parametros,
tiene un poco mas de variabilidad que randles_cpe -- 10% sigue siendo
una tolerancia razonable para confirmar que el ajuste funciona, sin
que la prueba falle por variaciones normales de una corrida a otra.
"""

from app.domain import impedance


def test_ajustar_randles_warburg_semiinfinito_recupera_parametros_conocidos(
    datos_randles_warburg_semiinfinito,
):
    frecuencias, Z, parametros_verdaderos = datos_randles_warburg_semiinfinito
    circuito = impedance.ajustar_circuito(
        "randles_warburg_semiinfinito", frecuencias, Z
    )

    nombres = ["Rs", "Rct", "Wo_mag", "Wo_tau", "Q", "n"]
    for nombre, valor_ajustado, valor_verdadero in zip(
        nombres, circuito.parameters_, parametros_verdaderos.values()
    ):
        error_relativo = abs(valor_ajustado - valor_verdadero) / abs(valor_verdadero)
        assert error_relativo < 0.10, (
            f"{nombre}: ajustado={valor_ajustado:.4g}, "
            f"verdadero={valor_verdadero:.4g}, error={error_relativo*100:.1f}%"
        )


def test_randles_warburg_semiinfinito_pasa_el_filtro_de_sentido_fisico(
    datos_randles_warburg_semiinfinito,
):
    """Con parametros realistas, el ajuste no solo debe recuperar los
    valores -- tambien debe pasar el filtro de sentido fisico (todas
    las resistencias positivas, n entre 0 y 1, etc.)."""
    from app.domain import validation

    frecuencias, Z, _ = datos_randles_warburg_semiinfinito
    circuito = impedance.ajustar_circuito(
        "randles_warburg_semiinfinito", frecuencias, Z
    )
    valido, motivo = validation.es_fisicamente_valido(
        "randles_warburg_semiinfinito", circuito
    )
    assert valido, motivo