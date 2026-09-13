# -*- coding: utf-8 -*-
"""
Pruebas del servicio de exportacion a PDF. Se probaron dos niveles:
- que el PDF se genere correctamente con un analisis real (integracion
  con analysis_service, igual que lo usa la ventana).
- que no truene con casos limite (sin circuitos validos, sin imagen).

No se valida el contenido EXACTO del texto dentro del PDF (eso
requeriria una libreria adicional solo para leerlo de vuelta); en vez
de eso se confirma que el archivo se genera, tiene un tamano razonable,
y que la cabecera es la de un PDF valido -- suficiente para detectar si
algo se rompe.
"""

import os

import numpy as np
import pytest

from app.application import eis_service, analysis_service, export_service
from app.domain.models import ResultadoAnalisis

RUTA_EJEMPLO = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "examples", "datos_prueba.csv"
)


def _es_pdf_valido(ruta):
    with open(ruta, "rb") as f:
        return f.read(5) == b"%PDF-"


def test_exportar_reporte_con_analisis_real(tmp_path):
    frecuencias, Z = eis_service.cargar_archivo(RUTA_EJEMPLO)
    resultado = analysis_service.ejecutar_analisis(frecuencias, Z)

    ruta_salida = str(tmp_path / "reporte.pdf")
    ruta_generada = export_service.exportar_reporte_pdf(
        resultado, ruta_salida, nombre_archivo_datos="datos_prueba.csv"
    )

    assert ruta_generada == ruta_salida
    assert os.path.exists(ruta_salida)
    assert os.path.getsize(ruta_salida) > 1000
    assert _es_pdf_valido(ruta_salida)


def test_exportar_reporte_con_imagen_y_nombres_bonitos(tmp_path):
    """Igual que el anterior, pero con los dos extras que agrega la
    ventana real: una imagen de la grafica y los diccionarios de
    nombres amigables."""
    frecuencias, Z = eis_service.cargar_archivo(RUTA_EJEMPLO)
    resultado = analysis_service.ejecutar_analisis(frecuencias, Z)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ruta_imagen = str(tmp_path / "grafica.png")
    fig, ax = plt.subplots()
    ax.plot(Z.real, -Z.imag, "o")
    fig.savefig(ruta_imagen)
    plt.close(fig)

    ruta_salida = str(tmp_path / "reporte_completo.pdf")
    export_service.exportar_reporte_pdf(
        resultado, ruta_salida,
        nombre_archivo_datos="datos_prueba.csv",
        ruta_imagen_grafica=ruta_imagen,
        nombres_bonitos={"randles_cpe": "Randles con CPE (nombre bonito)"},
        nombres_parametros_bonitos={"Rs": "Resistencia de la solucion"},
    )

    assert _es_pdf_valido(ruta_salida)
    # El PDF con imagen deberia pesar mas que uno sin imagen.
    assert os.path.getsize(ruta_salida) > 5000


def test_exportar_reporte_sin_circuitos_validos_no_truena(tmp_path):
    """Caso limite: si ningun circuito paso el filtro fisico, el
    reporte debe seguir generandose (con un aviso), no lanzar una
    excepcion."""
    resultado_vacio = ResultadoAnalisis(
        frecuencias=np.array([1.0, 2.0]),
        Z=np.array([1 + 1j, 2 + 2j]),
        kk_valido=False,
        kk_mensaje="mensaje de prueba",
        n_semicirculos=1,
    )
    ruta_salida = str(tmp_path / "reporte_vacio.pdf")
    export_service.exportar_reporte_pdf(
        resultado_vacio, ruta_salida, nombre_archivo_datos="vacio.csv"
    )
    assert _es_pdf_valido(ruta_salida)

def test_exportar_reporte_con_grafica_de_bode(tmp_path):
    """Confirma que la seccion de Bode se agrega quando se provee su
    imagen -- comparando el tamano del PDF con y sin ella (misma idea
    que ya se usa para confirmar que la imagen de Nyquist se incluye)."""
    frecuencias, Z = eis_service.cargar_archivo(RUTA_EJEMPLO)
    resultado = analysis_service.ejecutar_analisis(frecuencias, Z)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    ruta_imagen_bode = str(tmp_path / "bode.png")
    magnitud = np.abs(Z)
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.loglog(frecuencias, magnitud, "o")
    ax2.semilogx(frecuencias, np.angle(Z, deg=True), "o")
    fig.savefig(ruta_imagen_bode)
    plt.close(fig)

    ruta_sin_bode = str(tmp_path / "reporte_sin_bode.pdf")
    export_service.exportar_reporte_pdf(
        resultado, ruta_sin_bode, nombre_archivo_datos="datos_prueba.csv"
    )

    ruta_con_bode = str(tmp_path / "reporte_con_bode.pdf")
    export_service.exportar_reporte_pdf(
        resultado, ruta_con_bode,
        nombre_archivo_datos="datos_prueba.csv",
        ruta_imagen_bode=ruta_imagen_bode,
    )

    assert _es_pdf_valido(ruta_con_bode)
    assert os.path.getsize(ruta_con_bode) > os.path.getsize(ruta_sin_bode)