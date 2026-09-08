# -*- coding: utf-8 -*-
"""
Biblioteca de circuitos equivalentes: su topologia (para impedance.py)
y su formula matematica. Esto es conocimiento de dominio puro -- son
hechos sobre EIS que no cambian sin importar como se muestren en
pantalla ni que archivo este cargado.

Los NOMBRES bonitos para mostrar en pantalla, las descripciones en
lenguaje amigable y los mensajes educativos NO estan aqui -- esos son
contenido de interfaz (como hablarle al usuario), y viven en
presentation/textos_educativos.py. Aqui solo esta la definicion
tecnica/matematica de cada circuito.
"""

from app.domain.models import DefinicionCircuito

CIRCUITOS = {
    "randles_simple": DefinicionCircuito(
        nombre="randles_simple",
        circuito="R0-p(R1,C1)",
        parametros=["Rs", "Rct", "Cdl"],
    ),
    "randles_cpe": DefinicionCircuito(
        nombre="randles_cpe",
        circuito="R0-p(R1,CPE1)",
        parametros=["Rs", "Rct", "Q", "n"],
    ),
    "randles_warburg": DefinicionCircuito(
        nombre="randles_warburg",
        # OJO: usamos "Ws" (tanh, frontera "corta"/transmisiva), no
        # "Wo" (coth, frontera "abierta"/bloqueante) -- confirmado con
        # datos simulados que "Ws" coincide con nuestra formula.
        circuito="R0-p(R1-Ws1,CPE1)",
        parametros=["Rs", "Rct", "Wo_mag", "Wo_tau", "Q", "n"],
    ),
    "dos_constantes_tiempo": DefinicionCircuito(
        nombre="dos_constantes_tiempo",
        circuito="R0-p(R1,CPE1)-p(R2,CPE2)",
        parametros=["Rs", "R1", "Q1", "n1", "R2", "Q2", "n2"],
    ),
}

# Formulas en HTML simple (no imagen, no LaTeX) -- se explico en una
# sesion anterior por que: renderizar formulas con matplotlib/mathtext
# tiene un costo real, y aqui buscamos que cualquier parte de la
# interfaz pueda mostrar la formula sin ese costo.
FORMULAS_HTML = {
    "randles_simple": (
        "Z(&omega;) = R<sub>s</sub> + "
        "R<sub>ct</sub> / (1 + j&omega;R<sub>ct</sub>C<sub>dl</sub>)"
    ),
    "randles_cpe": (
        "Z(&omega;) = R<sub>s</sub> + "
        "R<sub>ct</sub> / (1 + R<sub>ct</sub>&middot;Q&middot;(j&omega;)<sup>n</sup>)"
    ),
    "randles_warburg": (
        "Z(&omega;) = R<sub>s</sub> + "
        "[1 &frasl; (R<sub>ct</sub>+Z<sub>W</sub>) + 1 &frasl; Z<sub>CPE</sub>]<sup>-1</sup>"
    ),
    "dos_constantes_tiempo": (
        "Z(&omega;) = R<sub>s</sub> + "
        "R<sub>1</sub>/(1+R<sub>1</sub>Q<sub>1</sub>(j&omega;)<sup>n1</sup>) + "
        "R<sub>2</sub>/(1+R<sub>2</sub>Q<sub>2</sub>(j&omega;)<sup>n2</sup>)"
    ),
}
