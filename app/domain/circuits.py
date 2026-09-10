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
    "resistencia_pura": DefinicionCircuito(
        nombre="resistencia_pura",
        circuito="R0",
        parametros=["R"],
    ),
    "capacitor_ideal": DefinicionCircuito(
        nombre="capacitor_ideal",
        circuito="C0",
        parametros=["C"],
    ),
    "inductor_ideal": DefinicionCircuito(
        nombre="inductor_ideal",
        circuito="L0",
        parametros=["L"],
    ),
    "rc_serie": DefinicionCircuito(
        nombre="rc_serie",
        circuito="R0-C0",
        parametros=["R", "C"],
    ),
    "rc_paralelo": DefinicionCircuito(
        nombre="rc_paralelo",
        circuito="p(R0,C0)",
        parametros=["R", "C"],
    ),
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
    "randles_warburg_semiinfinito": DefinicionCircuito(
        nombre="randles_warburg_semiinfinito",
        # Aqui SI usamos "Wo" (coth, frontera "abierta"/bloqueante):
        # representa difusion hacia un espacio tan grande que, dentro
        # del rango de frecuencias medido, nunca "se nota" que hay un
        # limite -- a diferencia de randles_warburg (Ws), que asume una
        # barrera que SI se alcanza a ver en la medicion.
        circuito="R0-p(R1-Wo1,CPE1)",
        parametros=["Rs", "Rct", "Wo_mag", "Wo_tau", "Q", "n"],
    ),
    "dos_constantes_tiempo": DefinicionCircuito(
        nombre="dos_constantes_tiempo",
        circuito="R0-p(R1,CPE1)-p(R2,CPE2)",
        parametros=["Rs", "R1", "Q1", "n1", "R2", "Q2", "n2"],
    ),
    "bucle_inductivo": DefinicionCircuito(
        nombre="bucle_inductivo",
        # Tres ramas en paralelo: Rct (transferencia de carga), CPE1
        # (doble capa) y R3-L1 (relajacion de un intermediario
        # adsorbido -- se comporta como una resistencia pura en DC,
        # pero con un retraso dado por L1). Etiquetas "R3"/"L1" (no
        # "R2"/"L2") a proposito, para no chocar con los nombres que
        # ya usa dos_constantes_tiempo (R2 ahi significa algo
        # distinto: la resistencia del SEGUNDO proceso capacitivo).
        circuito="R0-p(R1,CPE1,R3-L1)",
        parametros=["Rs", "Rct", "Q", "n", "R3", "L1"],
    ),
}

# Formulas en HTML simple (no imagen, no LaTeX) -- se explico en una
# sesion anterior por que: renderizar formulas con matplotlib/mathtext
# tiene un costo real, y aqui buscamos que cualquier parte de la
# interfaz pueda mostrar la formula sin ese costo.
FORMULAS_HTML = {
    "resistencia_pura": "Z = R",
    "capacitor_ideal": "Z(&omega;) = 1 &frasl; (j&omega;C)",
    "inductor_ideal": "Z(&omega;) = j&omega;L",
    "rc_serie": "Z(&omega;) = R + 1 &frasl; (j&omega;C)",
    "rc_paralelo": "Z(&omega;) = R &frasl; (1 + j&omega;RC)",
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
    "randles_warburg_semiinfinito": (
        "Z(&omega;) = R<sub>s</sub> + "
        "[1 &frasl; (R<sub>ct</sub>+Z<sub>Wo</sub>) + 1 &frasl; Z<sub>CPE</sub>]<sup>-1</sup>"
    ),
    "dos_constantes_tiempo": (
        "Z(&omega;) = R<sub>s</sub> + "
        "R<sub>1</sub>/(1+R<sub>1</sub>Q<sub>1</sub>(j&omega;)<sup>n1</sup>) + "
        "R<sub>2</sub>/(1+R<sub>2</sub>Q<sub>2</sub>(j&omega;)<sup>n2</sup>)"
    ),
    "bucle_inductivo": (
        "Z(&omega;) = R<sub>s</sub> + "
        "[1&frasl;R<sub>ct</sub> + 1&frasl;Z<sub>CPE</sub> + "
        "1&frasl;(R<sub>3</sub>+j&omega;L<sub>1</sub>)]<sup>-1</sup>"
    ),
}