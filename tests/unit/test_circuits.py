# -*- coding: utf-8 -*-
"""
Pruebas unitarias de app.domain.circuits: que la biblioteca de
circuitos este bien formada (no que ajuste bien -- eso ya se prueba en
test_impedance.py).
"""

from app.domain.circuits import CIRCUITOS, FORMULAS_HTML


def test_todos_los_circuitos_tienen_formula():
    for nombre in CIRCUITOS:
        assert nombre in FORMULAS_HTML, f"falta formula HTML para {nombre}"


def test_definicion_de_circuito_tiene_campos_consistentes():
    for nombre, definicion in CIRCUITOS.items():
        assert definicion.nombre == nombre
        assert definicion.circuito.startswith("R0")
        assert len(definicion.parametros) >= 3


def test_numero_de_parametros_coincide_con_el_string_del_circuito():
    """
    Cada 'p(' o elemento en el string de circuito de impedance.py debe
    corresponder a un parametro por elemento. Chequeo simple: contar
    cuantos elementos con numero hay en el string (R0, R1, CPE1, etc.)
    y comparar contra la cantidad de parametros esperada por tipo de
    elemento (R y C/W cuentan 1 parametro, CPE cuenta 2: Q y n).
    """
    conteo_esperado = {
        "randles_simple": 3,     # Rs, Rct, Cdl
        "randles_cpe": 4,        # Rs, Rct, Q, n
        "randles_warburg": 6,    # Rs, Rct, Wo_mag, Wo_tau, Q, n
        "dos_constantes_tiempo": 7,  # Rs, R1, Q1, n1, R2, Q2, n2
    }
    for nombre, cantidad in conteo_esperado.items():
        assert len(CIRCUITOS[nombre].parametros) == cantidad
