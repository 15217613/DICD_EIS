# -*- coding: utf-8 -*-
"""
Iconos de linea simple (SVG dibujados a mano, sin depender de archivos
externos ni de una libreria de iconos con licencia que revisar) para
el menu lateral de navegacion.

Por que SVG y no una imagen (.png): un SVG es texto (numeros que
describen lineas), asi que se puede "pintar" del color que se quiera
en el momento (por ejemplo, mas oscuro si el paso esta seleccionado)
sin tener que guardar una imagen distinta por cada color.
"""

from PySide6.QtCore import QByteArray, Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

ICONOS_SVG = {
    "importar": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 3v10M8 7l4-4 4 4"/>
        <path d="M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"/></svg>""",

    "validar": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 3l7 3v6c0 4-3 7-7 9-4-2-7-5-7-9V6l7-3z"/>
        <path d="M9 12l2 2 4-4"/></svg>""",

    "explorar": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 17l5-6 4 3 6-8"/><path d="M3 21h18"/></svg>""",

    "modelar": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2" y="9" width="6" height="6" rx="1"/>
        <rect x="16" y="9" width="6" height="6" rx="1"/>
        <path d="M8 12h8"/></svg>""",

    "residuos": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 3v18h18"/>
        <circle cx="7" cy="15" r="1"/><circle cx="11" cy="10" r="1"/>
        <circle cx="15" cy="13" r="1"/><circle cx="19" cy="7" r="1"/></svg>""",

    "pedagogia": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M2 9l10-5 10 5-10 5-10-5z"/>
        <path d="M6 11v5c0 1.5 3 3 6 3s6-1.5 6-3v-5"/></svg>""",

    "informe": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M6 2h9l3 3v17H6z"/><path d="M15 2v3h3"/>
        <path d="M9 12h6M9 16h6"/></svg>""",

    "colapsar": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M11 6l-6 6 6 6M18 6l-6 6 6 6"/></svg>""",
}


def pixmap_desde_svg(nombre, color="#43474d", tamano=20):
    """Igual que icono_desde_svg, pero devuelve el QPixmap crudo (sin
    envolver en QIcon) -- lo necesitamos asi para poder rotarlo."""
    svg_texto = ICONOS_SVG[nombre].replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(svg_texto.encode("utf-8")))
    pixmap = QPixmap(tamano, tamano)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def icono_desde_svg(nombre, color="#43474d", tamano=20):
    """Convierte uno de los SVG de arriba en un QIcon del color pedido."""
    return QIcon(pixmap_desde_svg(nombre, color, tamano))