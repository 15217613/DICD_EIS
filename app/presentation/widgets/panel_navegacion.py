# -*- coding: utf-8 -*-
"""
Menu lateral de navegacion: la lista numerada de pasos del flujo de
analisis (Importar datos, Validar K-K, Explorar espectros, etc.).

Es un widget PURAMENTE de presentacion: no sabe nada de EIS ni decide
que pantalla mostrar -- solo dibuja la lista y avisa, con una senal,
que paso eligio el usuario. Quien de verdad cambia de pantalla (la
ventana principal) escucha esa senal y mueve un QStackedWidget. Es la
misma idea que ya se usa en panel_archivo.py: un widget "tonto" que
solo avisa intenciones del usuario, sin decidir nada por su cuenta.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QFrame,
)

# Cada paso: (icono, texto). El icono es un simple emoji -- se eligio
# esto en vez de un set de iconos "de verdad" (como QIcon.fromTheme o
# archivos .svg) para no agregar una dependencia ni archivos de
# recursos solo por un detalle visual. Contra: se ve un poco menos
# "profesional" que un icono vectorial disenado a proposito.
PASOS = [
    ("📥", "Importar Datos"),
    ("✅", "Validar (K-K)"),
    ("📈", "Explorar Espectros"),
    ("🔧", "Modelar Circuito"),
    ("📉", "Evaluar Residuos"),
    ("🎓", "Interpretar y Pedagogia"),
    ("📄", "Generar Informe"),
]


class PanelNavegacion(QWidget):
    # Se emite con el INDICE del paso elegido (0 a 6) cuando el
    # usuario da clic en un renglon de la lista.
    paso_elegido = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(230)
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        titulo = QLabel("🧭  Flujo de Analisis")
        titulo.setStyleSheet(
            "font-weight: bold; font-size: 13px; padding: 10px; "
            "background-color: #eaf1fb; border-bottom: 1px solid #d0d7e2;"
        )
        layout.addWidget(titulo)

        self.lista = QListWidget()
        self.lista.setFrameShape(QFrame.NoFrame)
        self.lista.setStyleSheet(
            """
            QListWidget { border: none; outline: none; font-size: 12px; }
            QListWidget::item { padding: 10px 12px; }
            QListWidget::item:selected {
                background-color: #dbe9fb;
                color: #1a5bb8;
                font-weight: bold;
                border-left: 3px solid #1a5bb8;
            }
            """
        )
        for i, (icono, texto) in enumerate(PASOS):
            item = QListWidgetItem(f"{i + 1}   {icono}  {texto}")
            self.lista.addItem(item)
        self.lista.currentRowChanged.connect(self.paso_elegido.emit)
        layout.addWidget(self.lista, stretch=1)

        # Pie informativo -- decorativo, no controla nada del ajuste
        # real: solo recuerda que algoritmo usa la libreria por debajo
        # (Levenberg-Marquardt, ya fijo en domain/impedance.py). Si
        # algun dia se vuelve configurable de verdad, este es un buen
        # lugar para mostrarlo con datos reales en vez de fijos.
        pie = QLabel(
            "<b>Algoritmo:</b> Levenberg-Marquardt<br>"
            "<b>Iteraciones max:</b> 300"
        )
        pie.setStyleSheet(
            "padding: 10px; font-size: 10px; color: #555; "
            "background-color: #f4f6f9; border-top: 1px solid #d0d7e2;"
        )
        pie.setWordWrap(True)
        layout.addWidget(pie)

    # ------------------------------------------------------------------
    def seleccionar_paso(self, indice):
        """Resalta un paso SIN disparar la senal (para cuando la
        ventana principal cambia de pantalla por otro motivo -- ej. al
        terminar un analisis salta sola a "Validar K-K" -- y solo se
        quiere reflejar el cambio en el menu, no procesarlo otra vez
        como si el usuario hubiera dado clic)."""
        self.lista.blockSignals(True)
        self.lista.setCurrentRow(indice)
        self.lista.blockSignals(False)