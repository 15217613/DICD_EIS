# -*- coding: utf-8 -*-
"""
Acceso genérico a archivos en disco: no sabe nada de EIS ni de
frecuencias/impedancia, solo sabe leer numeros de un CSV. La
interpretacion de QUE SIGNIFICA cada columna (frecuencia, Z_real,
Z_imag) vive un nivel arriba, en infrastructure/data_loader.py -- asi,
si algun dia cambia el formato de archivo (otro separador, otro
software de laboratorio), es mas facil saber donde tocar.
"""

import os
import numpy as np


def existe_archivo(ruta):
    return os.path.isfile(ruta)


def leer_csv_crudo(ruta):
    """
    Lee un archivo CSV como una matriz de numeros, sin interpretar
    columnas todavia. Lanza las excepciones que numpy lance si el
    archivo no existe o no se puede parsear como numeros.
    """
    return np.genfromtxt(ruta, delimiter=",")
