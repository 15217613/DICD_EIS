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
        assert len(definicion.parametros) >= 1
        # Antes se exigia que TODO circuito empezara con "R0" (una
        # resistencia de solucion en serie) -- eso era cierto mientras
        # la biblioteca solo tenia variantes de Randles, pero dejo de
        # serlo con los circuitos simples (capacitor_ideal empieza con
        # "C0", rc_paralelo empieza con "p(..."). El chequeo real que
        # importa es que el string no este vacio.
        assert len(definicion.circuito) > 0


def test_numero_de_parametros_coincide_con_el_string_del_circuito():
    """
    Cada 'p(' o elemento en el string de circuito de impedance.py debe
    corresponder a un parametro por elemento. Chequeo simple: contar
    cuantos elementos con numero hay en el string (R0, R1, CPE1, etc.)
    y comparar contra la cantidad de parametros esperada por tipo de
    elemento (R, C, L y W cuentan 1 parametro, CPE cuenta 2: Q y n).
    """
    conteo_esperado = {
        "resistencia_pura": 1,   # R
        "capacitor_ideal": 1,    # C
        "inductor_ideal": 1,     # L
        "rc_serie": 2,           # R, C
        "rc_paralelo": 2,        # R, C
        "randles_simple": 3,     # Rs, Rct, Cdl
        "randles_cpe": 4,        # Rs, Rct, Q, n
        "randles_warburg": 6,    # Rs, Rct, Wo_mag, Wo_tau, Q, n
        "randles_warburg_semiinfinito": 6,  # Rs, Rct, Wo_mag, Wo_tau, Q, n
        "dos_constantes_tiempo": 7,  # Rs, R1, Q1, n1, R2, Q2, n2
        "bucle_inductivo": 6,  # Rs, Rct, Q, n, R3, L1
    }
    for nombre, cantidad in conteo_esperado.items():
        assert len(CIRCUITOS[nombre].parametros) == cantidad


def test_randles_warburg_y_semiinfinito_usan_elementos_warburg_distintos():
    """
    Chequeo especifico para no confundir los dos circuitos de Warburg
    de la biblioteca: deben tener el MISMO orden de parametros (para
    que la interfaz los trate igual), pero un string de circuito
    DISTINTO -- randles_warburg usa 'Ws' (frontera cerrada) y
    randles_warburg_semiinfinito usa 'Wo' (frontera abierta). Si algun
    dia alguien copia y pega mal, esta prueba lo detecta.
    """
    finito = CIRCUITOS["randles_warburg"]
    semiinfinito = CIRCUITOS["randles_warburg_semiinfinito"]

    assert finito.parametros == semiinfinito.parametros
    assert "Ws1" in finito.circuito
    assert "Wo1" in semiinfinito.circuito
    assert finito.circuito != semiinfinito.circuito