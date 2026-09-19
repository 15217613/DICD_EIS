# -*- coding: utf-8 -*-
"""
Panel izquierdo de "Importar Datos": cargar un archivo y exportar el
reporte.

CAMBIO EN ESTA VERSION: el boton "Analizar" (y su barra de progreso y
registro de avance) se movieron a su propio widget,
presentation/widgets/panel_analisis.py, que ahora vive en la pantalla
"Modelar Circuito" -- ver el docstring de ese archivo para el porque
completo. Este widget se queda enfocado en UNA sola cosa: conseguir
los datos (elegir el archivo) y, al final del flujo, exportar el
reporte. Es la misma idea de "widget chico y enfocado" que ya se usa
en el resto del proyecto.

Este es un widget AUTOSUFICIENTE de presentacion: no sabe nada de como
se lee un archivo ni de como se ejecuta un analisis -- solo abre el
dialogo de "elegir archivo" y avisa, con SENALES, que el usuario quiere
cargar tal ruta. Quien de verdad hace esas cosas (la ventana principal,
usando la capa de aplicacion) se entera por las senales, y le devuelve
el resultado a este panel llamando a sus metodos publicos
(mostrar_archivo_cargado, habilitar_exportar).

Esta es la misma idea de "separacion de capas" aplicada DENTRO de la
presentacion: este widget no importa nada de app.application ni
app.domain, para poder probarlo o reutilizarlo sin arrastrar toda la
logica de negocio.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QLabel, QPushButton, QFileDialog,
)


class PanelArchivo(QGroupBox):
    # Se emite con la ruta elegida cuando el usuario selecciona un
    # archivo en el dialogo (no antes -- si cancela el dialogo, no se
    # emite nada).
    archivo_elegido = Signal(str)
    # Se emite cuando el usuario da clic en "Exportar reporte PDF".
    exportar_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__("Archivo de datos", parent)
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)

        self.label_archivo = QLabel("Ningun archivo seleccionado.")
        self.label_archivo.setWordWrap(True)

        boton_cargar = QPushButton("Cargar archivo CSV...")
        boton_cargar.clicked.connect(self._elegir_archivo)

        self.boton_exportar = QPushButton("Exportar reporte PDF...")
        self.boton_exportar.setEnabled(False)
        self.boton_exportar.clicked.connect(lambda: self.exportar_solicitado.emit())

        layout.addWidget(boton_cargar)
        layout.addWidget(self.label_archivo)
        layout.addSpacing(10)
        layout.addWidget(self.boton_exportar)
        layout.addStretch()

    def _elegir_archivo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona un archivo CSV de datos EIS",
            "",
            "Archivos CSV (*.csv);;Todos los archivos (*)",
        )
        if ruta:
            self.archivo_elegido.emit(ruta)

    # ------------------------------------------------------------------
    # API publica: quien escuche las senales de arriba llama a estos
    # metodos para reflejar en pantalla que paso.
    # ------------------------------------------------------------------
    def mostrar_archivo_cargado(self, nombre_archivo, ruta, n_puntos):
        self.label_archivo.setText(f"Archivo: {nombre_archivo} ({n_puntos} puntos)")
        self.label_archivo.setToolTip(ruta)
        self.boton_exportar.setEnabled(False)  # un archivo nuevo aun no tiene analisis

    def habilitar_exportar(self, habilitado):
        self.boton_exportar.setEnabled(habilitado)