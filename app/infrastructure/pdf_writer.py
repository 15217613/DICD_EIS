# -*- coding: utf-8 -*-
"""
Escritor de PDF generico: convierte una lista de "bloques" de
contenido (titulos, parrafos, tablas, imagenes) en un archivo PDF, con
reportlab. NO sabe nada de EIS ni de circuitos -- por eso vive en
infrastructure/, no en application/: es un detalle tecnico de COMO se
genera un PDF (que libreria, como se ve una tabla), reemplazable el
dia de manana sin que application/export_service.py tenga que cambiar
su logica de que contenido incluir.

Formato de cada bloque (un diccionario con la llave "tipo"):
    {"tipo": "titulo", "texto": "..."}
    {"tipo": "encabezado", "texto": "..."}
    {"tipo": "parrafo", "texto": "..."}          (acepta <b>, <i>, <br/>)
    {"tipo": "tabla", "encabezados": [...], "filas": [[...], ...]}
    {"tipo": "imagen", "ruta": "...", "ancho_cm": 16}
    {"tipo": "espacio", "alto_pt": 12}
    {"tipo": "salto_pagina"}
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,
)
from PIL import Image as ImagenPIL


def _fila_imagen(ruta, ancho_cm):
    """Calcula el alto en cm que le corresponde a una imagen para
    respetar su proporcion original, dado un ancho fijo -- asi nunca
    se ve estirada o achatada."""
    with ImagenPIL.open(ruta) as img:
        ancho_px, alto_px = img.size
    ancho = ancho_cm * cm
    alto = ancho * (alto_px / ancho_px)
    return ancho, alto


def escribir_pdf(ruta_salida, bloques, titulo_documento="Reporte"):
    """
    Escribe 'bloques' (ver formato arriba) como un archivo PDF en
    ruta_salida.
    """
    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=letter,
        title=titulo_documento,
        topMargin=2 * cm, bottomMargin=2 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm,
    )
    estilos = getSampleStyleSheet()
    historia = []

    for bloque in bloques:
        tipo = bloque["tipo"]

        if tipo == "titulo":
            historia.append(Paragraph(bloque["texto"], estilos["Title"]))

        elif tipo == "encabezado":
            historia.append(Paragraph(bloque["texto"], estilos["Heading2"]))

        elif tipo == "parrafo":
            historia.append(Paragraph(bloque["texto"], estilos["Normal"]))

        elif tipo == "tabla":
            datos = [bloque["encabezados"]] + [
                [str(valor) for valor in fila] for fila in bloque["filas"]
            ]
            tabla = Table(datos, hAlign="LEFT")
            tabla.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#f2f2f2")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            historia.append(tabla)

        elif tipo == "imagen":
            ancho_cm = bloque.get("ancho_cm", 16)
            ancho, alto = _fila_imagen(bloque["ruta"], ancho_cm)
            historia.append(Image(bloque["ruta"], width=ancho, height=alto))

        elif tipo == "espacio":
            historia.append(Spacer(1, bloque.get("alto_pt", 12)))

        elif tipo == "salto_pagina":
            historia.append(PageBreak())

        else:
            raise ValueError(f"tipo de bloque de PDF desconocido: {tipo!r}")

    doc.build(historia)
