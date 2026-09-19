# -*- coding: utf-8 -*-
"""
Pagina "Validar (K-K)": muestra, sola, la validacion de consistencia
fisica de Kramers-Kronig y la deteccion de semicirculos.

Antes este texto vivia mezclado al principio de la pestana
"Resultados" (ver presentation/widgets/tabla_resultados.py). Se separa
en su propia pantalla para que el flujo de la izquierda (ver
panel_navegacion.py) tenga un paso propio de "validar los datos" antes
de pasar a explorar graficas o modelar circuitos -- es la MISMA
informacion (se reutilizan las mismas funciones de
textos_educativos.py), solo que ahora tiene su propio lugar en el
flujo. Nota de diseno: tabla_resultados.py TAMBIEN sigue mostrando este
mismo texto arriba de su tabla -- se dejo asi a proposito (pequena
duplicacion) en vez de tocar ese widget ya probado.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser

from app.presentation import textos_educativos


class PanelValidacionKK(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Validacion de Kramers-Kronig</b>"))
        self.texto = QTextBrowser()
        layout.addWidget(self.texto, stretch=1)
        self.limpiar()

    # ------------------------------------------------------------------
    # API publica -- misma forma que los demas paneles (mostrar_*,
    # limpiar) para que main_window.py los trate de manera uniforme.
    # ------------------------------------------------------------------
    def mostrar(self, resultado):
        partes = [
            "<p>" + textos_educativos.texto_kramers_kronig(
                resultado.kk_valido, resultado.kk_mensaje
            ).replace("\n", "<br>") + "</p>",
            "<p>" + textos_educativos.texto_semicirculos(
                resultado.n_semicirculos
            ) + "</p>",
        ]
        self.texto.setHtml("".join(partes))

    def limpiar(self):
        self.texto.setHtml(
            "<p style='color:#888;'>Carga un archivo y corre el analisis "
            "para ver aqui el resultado de la validacion de "
            "Kramers-Kronig.</p>"
        )