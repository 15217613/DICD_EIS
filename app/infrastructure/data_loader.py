# -*- coding: utf-8 -*-
"""
Carga de datasets de EIS: toma un archivo CSV (via file_repository) y
lo interpreta con el significado especifico de EIS -- primera columna
es frecuencia, segunda y tercera son la parte real e imaginaria de la
impedancia -- y recorta el ruido tipico que cruza el eje cerca de la
frecuencia mas alta.
"""

import numpy as np

from app.infrastructure import file_repository


def _recortar_ruido_inductivo_inicial(frecuencias, Z):
    """
    Antes se usaba preprocessing.ignoreBelowX() de impedance.py, que
    borra TODO punto con Im(Z) >= 0 sin importar en que parte de la
    curva aparezca. Eso funcionaba bien mientras la biblioteca solo
    tenia circuitos tipo Randles (donde CUALQUIER punto inductivo solo
    puede ser ruido cerca del cruce, tipicamente a la frecuencia mas
    alta, por efectos parasitos del cableado). Pero al agregar
    "bucle_inductivo" (para corrosion con intermediarios adsorbidos),
    ese filtro agresivo borraria justamente los puntos de BAJA
    frecuencia que le dan sentido fisico al circuito -- descartando la
    evidencia antes de que el analisis la vea.

    Esta version es mas selectiva: solo recorta un tramo INICIAL de
    puntos con Im(Z) >= 0 (asumiendo los datos ordenados de mayor a
    menor frecuencia, la convencion estandar de EIS) -- el tipico
    "cruce por ruido" cerca de la frecuencia mas alta -- y conserva
    TODO lo demas, incluyendo un bucle inductivo genuino que aparezca
    mas adelante, a frecuencias bajas.

    LIMITE CONOCIDO: si el ruido inductivo aparece de forma aislada en
    medio de la curva (no al principio), esta version ya NO lo
    recorta -- a diferencia de la version anterior, que lo hacia sin
    importar donde apareciera. Se acepta este riesgo porque, en la
    practica, ese patron (ruido disperso en medio de una curva por lo
    demas limpia) es mucho menos comun que el cruce inicial o el
    bucle genuino al final, y priorizar uno sobre el otro era
    inevitable con un solo filtro compartido por todos los circuitos.
    """
    orden = np.argsort(frecuencias)[::-1]
    frecuencias_ordenadas = frecuencias[orden]
    Z_ordenado = Z[orden]

    i = 0
    while i < len(Z_ordenado) and np.imag(Z_ordenado[i]) >= 0:
        i += 1

    return frecuencias_ordenadas[i:], Z_ordenado[i:]


def cargar_datos(ruta):
    """
    Lee un archivo de datos EIS con tres columnas (frecuencia, Z_real,
    Z_imag) y sin encabezado de texto.

    Devuelve: frecuencias (array), Z (array de numeros complejos)
    """
    datos = file_repository.leer_csv_crudo(ruta)
    frecuencias = datos[:, 0]
    Z = datos[:, 1] + 1j * datos[:, 2]
    frecuencias, Z = _recortar_ruido_inductivo_inicial(frecuencias, Z)
    return frecuencias, Z