# -*- coding: utf-8 -*-
"""
Hilo en segundo plano para correr el analisis sin congelar la ventana.

Por que vive en infrastructure/ y no en application/: QThread es un
detalle de COMO se ejecuta el analisis en esta interfaz en particular
(Qt), no parte de la logica de negocio. Si manana esta misma app se
expusiera por otro medio (una API web, un script de linea de
comandos), no haria falta este archivo -- se seguiria usando
application/analysis_service.py directamente. Por eso HiloAnalisis solo
"envuelve" una llamada a application.analysis_service en un QThread, y
traduce su callback(mensaje, porcentaje) en senales de Qt.
"""

import traceback
from PySide6.QtCore import QThread, Signal

from app.application import analysis_service


class HiloAnalisis(QThread):
    """
    Ejecuta application.analysis_service.ejecutar_analisis() en
    segundo plano.

    Senales que emite:
    - progreso(str, int): mensaje amigable + porcentaje (0-100)
    - terminado(object): un app.domain.models.ResultadoAnalisis, cuando
      el analisis termina exitosamente
    - fallo(str): mensaje de error amigable, si algo salio mal
    """
    progreso = Signal(str, int)
    terminado = Signal(object)
    fallo = Signal(str)

    def __init__(self, frecuencias, Z, n_mostrar=3, parent=None):
        super().__init__(parent)
        self.frecuencias = frecuencias
        self.Z = Z
        self.n_mostrar = n_mostrar

    def run(self):
        try:
            resultado = analysis_service.ejecutar_analisis(
                self.frecuencias,
                self.Z,
                callback=self._reportar_progreso,
                n_mostrar=self.n_mostrar,
            )
            self.terminado.emit(resultado)
        except Exception as e:
            detalle = traceback.format_exc()
            print(detalle)  # queda en la consola para depuracion tecnica
            self.fallo.emit(
                "Ocurrio un problema al analizar los datos.\n\n"
                f"Detalle: {e}"
            )

    def _reportar_progreso(self, mensaje, porcentaje):
        self.progreso.emit(mensaje, porcentaje)
