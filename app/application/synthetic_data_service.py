# -*- coding: utf-8 -*-
"""
Servicio de aplicacion para el "Generador Didactico" de datos
sinteticos: orquesta la creacion de un arreglo de frecuencias con el
mismo muestreo logaritmico que usa un potenciostato real, y llama al
dominio para evaluar la formula del circuito elegido y agregarle
ruido.

Igual que eis_service.py (que carga un archivo REAL), este servicio es
el punto de entrada que usa la interfaz -- no sabe nada de Qt, solo
recibe numeros simples (nombre de circuito, valores, rango de
frecuencias, nivel de ruido) y devuelve arreglos listos para entrar a
la MISMA tuberia de analisis que un archivo cargado de verdad.
"""

import numpy as np

from app.domain import impedance as domain_impedance


class ErrorGeneracionSintetica(Exception):
    """Se lanza cuando los parametros elegidos no permiten generar un
    conjunto de datos valido (ej. rango de frecuencias vacio, o la
    formula del circuito falla con los valores dados). El mensaje ya
    viene redactado para mostrarse tal cual al usuario."""
    pass


def generar_frecuencias(f_inicial, f_final, puntos_por_decada=10):
    """
    Genera un arreglo de frecuencias espaciadas logaritmicamente entre
    f_inicial y f_final (en Hz, cualquier orden), con
    puntos_por_decada puntos por cada decada -- la misma forma de
    muestrear un barrido de frecuencias que usa un potenciostato real
    (Gamry, BioLogic, Autolab), donde el espaciado es logaritmico, no
    lineal.
    """
    if f_inicial <= 0 or f_final <= 0:
        raise ErrorGeneracionSintetica(
            "Las frecuencias inicial y final deben ser mayores que cero."
        )
    if f_inicial == f_final:
        raise ErrorGeneracionSintetica(
            "La frecuencia inicial y la final no pueden ser iguales."
        )
    if puntos_por_decada < 1:
        raise ErrorGeneracionSintetica(
            "Debe haber al menos 1 punto por decada."
        )

    n_decadas = abs(np.log10(f_inicial) - np.log10(f_final))
    n_puntos = max(int(round(n_decadas * puntos_por_decada)) + 1, 2)
    return np.logspace(np.log10(f_inicial), np.log10(f_final), n_puntos)


def generar_datos_sinteticos(
    nombre_circuito, valores, f_inicial, f_final,
    puntos_por_decada=10, ruido_relativo=0.01, semilla=None,
):
    """
    Devuelve (frecuencias, Z_teorico, Z_con_ruido).

    Z_teorico es la curva "limpia" (la respuesta correcta, sin ruido)
    -- util para la vista previa antes de comprometerse con el
    ruido. Z_con_ruido es lo que se manda a la tuberia de analisis,
    como si fuera un archivo real recien cargado.
    """
    frecuencias = generar_frecuencias(f_inicial, f_final, puntos_por_decada)
    try:
        Z_teorico, Z_con_ruido = domain_impedance.simular_impedancia_con_ruido(
            nombre_circuito, valores, frecuencias, ruido_relativo, semilla
        )
    except Exception as e:
        raise ErrorGeneracionSintetica(
            "No se pudo evaluar la formula de este circuito con esos "
            f"valores.\n\nDetalle: {e}"
        ) from e

    return frecuencias, Z_teorico, Z_con_ruido