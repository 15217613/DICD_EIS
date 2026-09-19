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

from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, Property, Signal
from PySide6.QtGui import QTransform, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QFrame, QPushButton,
)

from app.presentation.widgets import iconos

# Cada paso: (icono, texto). El icono es un simple emoji -- se eligio
# esto en vez de un set de iconos "de verdad" (como QIcon.fromTheme o
# archivos .svg) para no agregar una dependencia ni archivos de
# recursos solo por un detalle visual. Contra: se ve un poco menos
# "profesional" que un icono vectorial disenado a proposito.
PASOS = [
    ("importar", "Importar Datos"),
    ("validar", "Validar (K-K)"),
    ("explorar", "Explorar Espectros"),
    ("modelar", "Modelar Circuito"),
    ("residuos", "Evaluar Residuos"),
    ("pedagogia", "Interpretar y Pedagogia"),
    ("informe", "Generar Informe"),
]

class BotonFlechaRotable(QPushButton):
    """Boton cuyo icono se puede girar suavemente -- se usa para la
    flecha de colapsar/expandir el menu. Se guarda el dibujo ORIGINAL
    sin rotar, y en cada paso de la animacion se rota ESE original (no
    el ya rotado de antes) -- si rotaramos el ya rotado, la imagen se
    iria emborronando poco a poco."""

    def __init__(self, pixmap_base, parent=None):
        super().__init__(parent)
        self._pixmap_base = pixmap_base
        self._angulo = 0
        self._actualizar_icono()

    def _get_angulo(self):
        return self._angulo

    def _set_angulo(self, valor):
        self._angulo = valor
        self._actualizar_icono()

    # Property es lo que le permite a QPropertyAnimation "mover" este
    # valor solo poco a poco, en vez de saltar de 0 a 180 de un jalon.
    angulo = Property(float, _get_angulo, _set_angulo)

    def _actualizar_icono(self):
        transformacion = QTransform().rotate(self._angulo)
        pixmap_rotado = self._pixmap_base.transformed(
            transformacion, Qt.SmoothTransformation
        )
        self.setIcon(QIcon(pixmap_rotado))

class PanelNavegacion(QWidget):
    # Se emite con el INDICE del paso elegido (0 a 6) cuando el
    # usuario da clic en un renglon de la lista.
    paso_elegido = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(230)
        self._construir_ui()
    
    def _get_ancho(self):
        return self.width()

    def _set_ancho(self, valor):
        self.setFixedWidth(valor)

    ancho = Property(int, _get_ancho, _set_ancho)

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._colapsado = False
        self._ancho_expandido = 230
        self._ancho_colapsado = 56

        fila_titulo = QHBoxLayout()
        fila_titulo.setContentsMargins(10, 6, 6, 6)
        self.titulo = QLabel("🧭  Flujo de Analisis")
        self.titulo.setStyleSheet("font-weight: bold; font-size: 13px;")
        fila_titulo.addWidget(self.titulo, stretch=1)

        pixmap_flecha = iconos.pixmap_desde_svg("colapsar")
        self.boton_colapsar = BotonFlechaRotable(pixmap_flecha)
        self.boton_colapsar.setFixedSize(24, 24)
        self.boton_colapsar.setFlat(True)
        self.boton_colapsar.clicked.connect(self._alternar_colapso)
        fila_titulo.addWidget(self.boton_colapsar)

        # Animacion flecha colapsar del panel
        self._animacion_flecha = QPropertyAnimation(self.boton_colapsar, b"angulo")
        self._animacion_flecha.setDuration(200)
        self._animacion_flecha.setEasingCurve(QEasingCurve.InOutQuad)

        # Animacion Panel
        self._animacion_ancho = QPropertyAnimation(self, b"ancho")
        self._animacion_ancho.setDuration(220)
        self._animacion_ancho.setEasingCurve(QEasingCurve.InOutQuad)
        self._animacion_ancho.finished.connect(self._al_terminar_animacion_menu)

        contenedor_titulo = QWidget()
        contenedor_titulo.setLayout(fila_titulo)
        contenedor_titulo.setStyleSheet(
            "background-color: #eaf1fb; border-bottom: 1px solid #d0d7e2;"
        )
        layout.addWidget(contenedor_titulo)

        self.lista = QListWidget()
        self.lista.setFrameShape(QFrame.NoFrame)
        self.lista.setIconSize(QSize(20, 20))
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
        self._textos_pasos = [texto for _icono, texto in PASOS]
        for i, (nombre_icono, texto) in enumerate(PASOS):
            icono = iconos.icono_desde_svg(nombre_icono)
            item = QListWidgetItem(icono, f"{i + 1}   {texto}")
            self.lista.addItem(item)
        self.lista.currentRowChanged.connect(self.paso_elegido.emit)
        layout.addWidget(self.lista, stretch=1)

        self.pie = QLabel(
            "<b>Algoritmo:</b> Levenberg-Marquardt<br>"
            "<b>Iteraciones max:</b> 300"
        )
        self.pie.setStyleSheet(
            "padding: 10px; font-size: 10px; color: #555; "
            "background-color: #f4f6f9; border-top: 1px solid #d0d7e2;"
        )
        self.pie.setWordWrap(True)
        layout.addWidget(self.pie)

    def _alternar_colapso(self):
        self._colapsado = not self._colapsado

        self._animacion_flecha.stop()
        self._animacion_flecha.setStartValue(self.boton_colapsar.angulo)
        self._animacion_flecha.setEndValue(180 if self._colapsado else 0)
        self._animacion_flecha.start()

        self._animacion_ancho.stop()
        self._animacion_ancho.setStartValue(self.width())

        if self._colapsado:
            # Se oculta el texto ANTES de encoger, para que no se vea
            # cortado a la mitad mientras el menu se achica.
            self.titulo.setVisible(False)
            self.pie.setVisible(False)
            for i in range(self.lista.count()):
                self.lista.item(i).setText("")
            self._animacion_ancho.setEndValue(self._ancho_colapsado)
        else:
            # Al expandir, el texto se muestra hasta que la animacion
            # termina (ver _al_terminar_animacion_menu) -- si se muestra
            # de una vez, se ve apretado mientras el menu todavia esta
            # angosto.
            self._animacion_ancho.setEndValue(self._ancho_expandido)

        self._animacion_ancho.start()

    def _al_terminar_animacion_menu(self):
        """Se llama cuando el menu YA termino de abrirse o cerrarse.
        Solo hace falta mostrar el texto aqui -- ocultarlo ya se hizo de
        una vez al empezar a cerrar (ver _alternar_colapso)."""
        if not self._colapsado:
            self.titulo.setVisible(True)
            self.pie.setVisible(True)
            for i, texto in enumerate(self._textos_pasos):
                self.lista.item(i).setText(f"{i + 1}   {texto}")

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