# -*- coding: utf-8 -*-
"""
Carga de datasets de EIS: toma un archivo CSV (via file_repository) y
lo interpreta con el significado especifico de EIS -- primera columna
es frecuencia, segunda y tercera son la parte real e imaginaria de la
impedancia -- y aplica el preprocesamiento de impedance.py para
descartar puntos con ruido que cruzan el eje.
"""

from impedance import preprocessing

from app.infrastructure import file_repository


def cargar_datos(ruta):
    """
    Lee un archivo de datos EIS con tres columnas (frecuencia, Z_real,
    Z_imag) y sin encabezado de texto.

    Devuelve: frecuencias (array), Z (array de numeros complejos)
    """
    datos = file_repository.leer_csv_crudo(ruta)
    frecuencias = datos[:, 0]
    Z = datos[:, 1] + 1j * datos[:, 2]
    frecuencias, Z = preprocessing.ignoreBelowX(frecuencias, Z)
    return frecuencias, Z
