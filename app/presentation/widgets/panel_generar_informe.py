# -*- coding: utf-8 -*-
"""
Pagina "Generar Informe": un lugar dedicado, al final del flujo, para
exportar el reporte en PDF.

Nota de diseno: el boton "Exportar reporte PDF..." YA existia en
panel_archivo.py (columna izquierda, siempre visible antes de este
cambio). Se decidio DEJARLO ahi tambien (en vez de quitarlo) y agregar
este boton nuevo aqui -- pequena duplicacion a proposito, siguiendo la
misma idea que ya se usa en otras partes del proyecto: mejor un boton
de mas que arriesgar romper las pruebas que ya verifican
panel_archivo.boton_exportar. Los dos botones llaman exactamente al
mismo lugar en main_window.py.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class PanelGenerarInforme(QWidget):
    # Se emite cuando el usuario da clic en el boton de esta pagina.
    exportar_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.addStretch()

        texto = QLabel(
            "<h3>Generar informe</h3>"
            "<p>Cuando termines de explorar tus datos, modelar el "
            "circuito y evaluar los residuos, puedes generar un reporte "
            "en PDF con el resumen completo del analisis: validacion de "
            "Kramers-Kronig, comparacion de circuitos, parametros del "
            "mejor ajuste y las graficas de Nyquist y Bode.</p>"
            "<p style='color:#888; font-size:11px;'>El boton se habilita "
            "cuando ya corriste un analisis completo.</p>"
        )
        texto.setWordWrap(True)
        layout.addWidget(texto)

        self.boton_exportar = QPushButton("📄  Exportar reporte PDF...")
        self.boton_exportar.setEnabled(False)
        self.boton_exportar.setMinimumHeight(40)
        self.boton_exportar.clicked.connect(lambda: self.exportar_solicitado.emit())
        layout.addWidget(self.boton_exportar)

        layout.addStretch()

    def habilitar(self, habilitado):
        self.boton_exportar.setEnabled(habilitado)