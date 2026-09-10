# -*- coding: utf-8 -*-
"""
Dibujo del diagrama de circuito (cajas y cables), para la pestana de
Grafica de Nyquist. Esto es puramente de PRESENTACION: sabe como
DIBUJAR la topologia de un circuito, pero la formula matematica y la
definicion tecnica del circuito (que va a impedance.py) viven en
domain/circuits.py -- este archivo no hace ningun calculo.

Decision de diseno importante (con su contra): en vez de dibujar
simbolos electricos "reales" (la zigzag de una resistencia, las placas
de un capacitor), cada elemento se dibuja como una caja con su nombre
adentro. Esto es MUCHO mas simple de programar y mantener, y sigue
comunicando con claridad la topologia (que esta en serie, que esta en
paralelo) -- el precio es que no se ve como un diagrama de libro de
texto de electronica.

Nota de arquitectura: la topologia (TOPOLOGIAS de abajo) esta
duplicada conceptualmente respecto a domain/circuits.CIRCUITOS (que
tambien describe, en otro formato, como esta armado cada circuito para
impedance.py). Una version mas "pura" de capas separadas evitaria esta
duplicacion generando el dibujo automaticamente a partir de la cadena
de texto del circuito (ej. "R0-p(R1,CPE1)"); no se hizo asi para no
arriesgar romper el dibujo ya probado visualmente en una sesion
anterior. Si la biblioteca de circuitos crece, vale la pena revisar
esto.
"""

from matplotlib.patches import Rectangle

# Topologia de cada circuito: una lista de "etapas".
#   ("serie", "Rs")                    -> un elemento en serie
#   ("paralelo", [["Rct","Wo"], ["Q"]]) -> dos (o mas) ramas en paralelo,
#                                          cada rama es una lista de
#                                          elementos en serie DENTRO de
#                                          esa rama
TOPOLOGIAS = {
    "resistencia_pura": [
        ("serie", "R"),
    ],
    "capacitor_ideal": [
        ("serie", "C"),
    ],
    "inductor_ideal": [
        ("serie", "L"),
    ],
    "rc_serie": [
        ("serie", "R"),
        ("serie", "C"),
    ],
    "rc_paralelo": [
        ("paralelo", [["R"], ["C"]]),
    ],
    "randles_simple": [
        ("serie", "Rs"),
        ("paralelo", [["Rct"], ["Cdl"]]),
    ],
    "randles_cpe": [
        ("serie", "Rs"),
        ("paralelo", [["Rct"], ["Q"]]),
    ],
    "randles_warburg": [
        ("serie", "Rs"),
        ("paralelo", [["Rct", "Wo"], ["Q"]]),
    ],
    "randles_warburg_semiinfinito": [
        # Misma topologia visual que randles_warburg -- el dibujo (que
        # esta en serie, que esta en paralelo) no distingue si el
        # elemento Warburg es "Ws" (frontera cerrada) o "Wo" (frontera
        # abierta); esa diferencia es matematica, no estructural, asi
        # que se reutiliza la caja generica "Wo" (rotulada como "W" en
        # ETIQUETAS_CAJA) para ambos.
        ("serie", "Rs"),
        ("paralelo", [["Rct", "Wo"], ["Q"]]),
    ],
    "dos_constantes_tiempo": [
        ("serie", "Rs"),
        ("paralelo", [["R1"], ["Q1"]]),
        ("paralelo", [["R2"], ["Q2"]]),
    ],
    "bucle_inductivo": [
        ("serie", "Rs"),
        # Tres ramas en paralelo -- _dibujar_paralelo ya soporta
        # cualquier cantidad de ramas (no solo 2), asi que no hizo
        # falta tocar el motor de dibujo, solo agregar esta entrada.
        ("paralelo", [["Rct"], ["Q"], ["R3", "L1"]]),
    ],
}

# Como se rotula cada elemento dentro de su caja del diagrama.
ETIQUETAS_CAJA = {
    "R": "R", "C": "C", "L": "L",
    "Rs": "Rs", "Rct": "Rct", "Cdl": "Cdl",
    "Q": "CPE", "Wo": "W",
    "R1": "R1", "Q1": "CPE1", "R2": "R2", "Q2": "CPE2",
    "R3": "R3", "L1": "L1",
}


def _caja(ax, x_inicio, y, etiqueta, ancho=0.8, alto=0.5, cable=0.15):
    """Dibuja un cable de entrada, una caja con su etiqueta, y un cable
    de salida. Devuelve la posicion x donde quedo el cable de salida,
    para que el siguiente elemento sepa donde empezar."""
    ax.plot([x_inicio, x_inicio + cable], [y, y], color="black", linewidth=1.6)
    x_caja = x_inicio + cable
    rect = Rectangle((x_caja, y - alto / 2), ancho, alto,
                      fill=False, linewidth=1.6, edgecolor="black")
    ax.add_patch(rect)
    ax.text(x_caja + ancho / 2, y, etiqueta, ha="center", va="center", fontsize=10)
    x_fin_caja = x_caja + ancho
    ax.plot([x_fin_caja, x_fin_caja + cable], [y, y], color="black", linewidth=1.6)
    return x_fin_caja + cable


def _dibujar_rama(ax, x_inicio, y, elementos):
    x = x_inicio
    for elemento in elementos:
        x = _caja(ax, x, y, ETIQUETAS_CAJA.get(elemento, elemento))
    return x


def _dibujar_paralelo(ax, x_inicio, y0, ramas, separacion=1.1):
    n = len(ramas)
    ys = [y0 + (i - (n - 1) / 2) * separacion for i in range(n)]

    x_finales = [_dibujar_rama(ax, x_inicio, y, rama) for y, rama in zip(ys, ramas)]
    x_fin_comun = max(x_finales) + 0.2

    for y, x_fin in zip(ys, x_finales):
        if x_fin < x_fin_comun:
            ax.plot([x_fin, x_fin_comun], [y, y], color="black", linewidth=1.6)

    ax.plot([x_inicio, x_inicio], [min(ys), max(ys)], color="black", linewidth=1.6)
    ax.plot([x_fin_comun, x_fin_comun], [min(ys), max(ys)], color="black", linewidth=1.6)

    return x_fin_comun


def dibujar_diagrama(ax, nombre_circuito):
    """Dibuja el diagrama de bloques del circuito en los ejes dados."""
    ax.clear()
    ax.axis("off")
    ax.set_aspect("equal")

    topologia = TOPOLOGIAS[nombre_circuito]
    x = 0.3
    y0 = 0.0
    ax.plot([0, x], [y0, y0], color="black", linewidth=1.6)

    for tipo, contenido in topologia:
        if tipo == "serie":
            x = _caja(ax, x, y0, ETIQUETAS_CAJA.get(contenido, contenido))
        else:
            x = _dibujar_paralelo(ax, x, y0, contenido)

    ax.plot([x, x + 0.3], [y0, y0], color="black", linewidth=1.6)
    ax.set_xlim(-0.2, x + 0.5)
    ax.set_ylim(-1.2, 1.2)