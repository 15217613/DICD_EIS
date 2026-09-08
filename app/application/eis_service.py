# -*- coding: utf-8 -*-
"""
Servicio de aplicacion para cargar archivos de datos EIS.

Este es el punto de entrada que usa la interfaz (presentation) para
pedir "cargame este archivo", sin tener que saber COMO se lee un CSV
ni que libreria se usa por debajo -- ese detalle vive en
infrastructure/data_loader.py. Aqui se orquesta la operacion y se
traduce cualquier error tecnico a un mensaje pensado para mostrarsele
directamente al usuario.
"""

from app.infrastructure import data_loader


class ErrorCargaArchivo(Exception):
    """Se lanza cuando un archivo no se pudo leer como datos de EIS.
    El mensaje ya viene redactado para mostrarse tal cual al usuario."""
    pass


def cargar_archivo(ruta):
    """
    Devuelve (frecuencias, Z) si el archivo se pudo leer, o lanza
    ErrorCargaArchivo con un mensaje amigable si no.
    """
    try:
        return data_loader.cargar_datos(ruta)
    except Exception as e:
        raise ErrorCargaArchivo(
            "No se pudo leer este archivo como datos de EIS.\n\n"
            f"Detalle: {e}\n\n"
            "Revisa que sea un CSV con tres columnas (frecuencia, "
            "Z_real, Z_imag) y sin encabezado de texto."
        ) from e
