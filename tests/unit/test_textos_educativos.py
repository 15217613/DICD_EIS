# -*- coding: utf-8 -*-
"""
Prueba de consistencia para EJEMPLOS_SISTEMAS (donde se ve cada
circuito en materiales/dispositivos reales). No prueba contenido
cientifico (eso no se puede verificar con pytest), solo que la
biblioteca este bien formada: que a NINGUN circuito de CIRCUITOS le
falte su texto, y viceversa -- el mismo tipo de chequeo que ya existe
para FORMULAS_HTML en test_circuits.py.
"""

from app.domain.circuits import CIRCUITOS
from app.presentation.textos_educativos import EJEMPLOS_SISTEMAS, ejemplos_sistemas


def test_todos_los_circuitos_tienen_ejemplo_de_sistema_real():
    for nombre in CIRCUITOS:
        assert nombre in EJEMPLOS_SISTEMAS, (
            f"falta el texto de 'donde se usa en la practica' para {nombre}"
        )
        assert len(EJEMPLOS_SISTEMAS[nombre]) > 20, (
            f"el texto de ejemplos para {nombre} parece demasiado corto"
        )


def test_ejemplos_sistemas_devuelve_cadena_vacia_si_no_existe():
    # Si en el futuro se agrega un circuito nuevo y todavia no se
    # redacta su ejemplo, la funcion no debe tronar -- debe devolver
    # una cadena vacia para que el llamador decida que hacer con eso.
    assert ejemplos_sistemas("circuito_que_no_existe") == ""