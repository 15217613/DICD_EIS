# -*- coding: utf-8 -*-
"""
Punto de entrada de la aplicacion.

Para ejecutar el programa:
    python3 app.py

Este archivo es intencionalmente muy corto: solo crea la aplicacion de
Qt y abre la ventana principal (capa de presentacion). Toda la logica
real vive en app/ (domain, application, infrastructure, presentation),
organizada por capas -- ver README.md para el mapa completo.
"""

# -*- coding: utf-8 -*-
import sys
from PySide6.QtWidgets import QApplication

from app.presentation.main_window import VentanaPrincipal
from app.presentation.tema import HOJA_DE_ESTILOS


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(HOJA_DE_ESTILOS)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()