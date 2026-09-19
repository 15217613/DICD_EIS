# -*- coding: utf-8 -*-
"""
Panel de analisis: el boton "Analizar" (el que corre Kramers-Kronig,
ajusta TODOS los circuitos de la biblioteca y calcula AIC/BIC/pesos de
Akaike), junto con su barra de progreso y su registro de avance.

DONDE VIVIA ANTES Y POR QUE SE MOVIO: este boton vivia en
panel_archivo.py (pantalla "Importar Datos"). Con el menu lateral,
"Explorar Espectros" y "Modelar Circuito" ya son pasos SEPARADOS del
flujo -- pero el boton de Analizar se habia quedado en el paso 1,
donde no encajaba: obligaba al estudiante a decidir si correr todo el
ajuste estadistico (que tarda y usa CPU) antes incluso de poder mirar
la curva de Nyquist con calma. Ahora que carga de datos y ejecucion
del analisis son decisiones separadas, tiene mas sentido que el boton
este en el paso donde esa decision realmente se usa: "Modelar
Circuito", justo al lado del selector de circuitos y del simulador de
parametros.

Es un widget AUTOSUFICIENTE de presentacion (mismo patron que
panel_archivo.py y panel_generar_informe.py): no sabe COMO se hace un
analisis, solo avisa con una senal que el usuario lo pidio, y expone
metodos publicos (habilitar_analizar, reiniciar_progreso,
actualizar_progreso) para que quien SI sabe hacer el analisis
(main_window.py, usando infrastructure.workers.HiloAnalisis) le
reporte el avance.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QLabel, QPushButton, QProgressBar, QTextEdit,
)


class PanelAnalisis(QGroupBox):
    # Se emite cuando el usuario da clic en "Analizar". No lleva datos:
    # main_window.py ya sabe cuales son los datos actuales.
    analizar_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__(
            "Analisis estadistico (Kramers-Kronig + AIC/BIC/Akaike)", parent
        )
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)

        self.boton_analizar = QPushButton("Analizar")
        # Deshabilitado hasta que haya datos cargados -- se habilita
        # desde main_window.py cuando llegan datos (de un archivo real
        # o del generador sintetico).
        self.boton_analizar.setEnabled(False)
        self.boton_analizar.setMinimumHeight(36)
        self.boton_analizar.clicked.connect(lambda: self.analizar_solicitado.emit())

        self.barra_progreso = QProgressBar()
        self.barra_progreso.setRange(0, 100)
        self.barra_progreso.setValue(0)

        self.label_estado = QLabel("")
        self.label_estado.setWordWrap(True)
        self.label_estado.setStyleSheet("color: #555;")

        self.registro = QTextEdit()
        self.registro.setReadOnly(True)
        # Alto acotado a proposito: en esta pantalla ya conviven la
        # grafica, el selector de circuito y la tabla de resultados --
        # el registro es informacion secundaria, no debe competir por
        # espacio con esas piezas principales.
        self.registro.setMaximumHeight(90)

        layout.addWidget(self.boton_analizar)
        layout.addWidget(self.barra_progreso)
        layout.addWidget(self.label_estado)
        layout.addWidget(QLabel("Registro de avance:"))
        layout.addWidget(self.registro)

    # ------------------------------------------------------------------
    # API publica: main_window.py llama a estos metodos para reflejar
    # en pantalla el estado del analisis.
    # ------------------------------------------------------------------
    def habilitar_analizar(self, habilitado):
        self.boton_analizar.setEnabled(habilitado)

    def reiniciar_progreso(self):
        self.registro.clear()
        self.barra_progreso.setValue(0)
        self.label_estado.setText("")

    def actualizar_progreso(self, mensaje, porcentaje):
        self.barra_progreso.setValue(porcentaje)
        self.label_estado.setText(mensaje)
        self.registro.append(f"[{porcentaje:3d}%] {mensaje}")