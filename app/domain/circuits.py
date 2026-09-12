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
    "randles_cpe_warburg": DefinicionCircuito(
        nombre="randles_cpe_warburg",
        # A diferencia de randles_warburg (Ws) y randles_warburg_semiinfinito
        # (Wo), que representan difusion en una capa de espesor FINITO
        # (con un solo parametro extra de "tiempo caracteristico"), "W"
        # es el Warburg semi-infinito CLASICO de los libros de texto:
        # un solo parametro (Aw), sin limite de espesor, que da una
        # linea recta a 45 grados en el diagrama de Nyquist que NUNCA
        # se dobla de vuelta (a diferencia de Ws/Wo, que si se doblan
        # eventualmente a frecuencias muy bajas).
        circuito="R0-p(R1-W1,CPE1)",
        parametros=["Rs", "Rct", "Aw", "Q", "n"],
    ),
    "dos_constantes_tiempo": DefinicionCircuito(
        nombre="dos_constantes_tiempo",
        circuito="R0-p(R1,CPE1)-p(R2,CPE2)",
        parametros=["Rs", "R1", "Q1", "n1", "R2", "Q2", "n2"],
    ),
    "tres_constantes_tiempo": DefinicionCircuito(
        nombre="tres_constantes_tiempo",
        # ADVERTENCIA (ver textos_educativos.py para el detalle
        # completo): confirmado con pruebas, este circuito es MAS
        # sensible al ruido que dos_constantes_tiempo, y tiene una
        # fragilidad particular: si las tres resistencias NO son de
        # magnitud comparable entre si, el proceso mas grande "esconde"
        # visualmente a los mas chicos (su semicirculo nunca se
        # distingue como un bulto separado, sin importar que tan bien
        # separadas esten las frecuencias caracteristicas) y la
        # deteccion de valles puede fallar del todo. Cuando las tres
        # resistencias SI son comparables, el nivel de fragilidad es
        # similar al de dos_constantes_tiempo/pelicula_transf_difusion
        # (fragil pero usable). Se implementa de todas formas, con
        # advertencia visible en la interfaz, confiando en que el
        # filtro de AIC/BIC y de sentido fisico descarten los ajustes
        # que salgan mal.
        circuito="R0-p(R1,CPE1)-p(R2,CPE2)-p(R3,CPE3)",
        parametros=["Rs", "R1", "Q1", "n1", "R2", "Q2", "n2", "R3", "Q3", "n3"],
    ),
    "bucle_inductivo": DefinicionCircuito(
        nombre="bucle_inductivo",
        # Tres ramas en paralelo: Rct (transferencia de carga), CPE1
        # (doble capa) y Rad-Lad (relajacion de un intermediario
        # adsorbido -- se comporta como una resistencia pura en DC,
        # pero con un retraso dado por Lad). Nombres "Rad"/"Lad" (no
        # numeros genericos "R3"/"L1") a proposito: asi no chocan con
        # ningun circuito futuro que use R1/R2/R3 para "proceso 1/2/3"
        # (como tres_constantes_tiempo), y de paso son mas claros --
        # "ad" de "adsorcion", mismo estilo que Rpo/Ccoat en los
        # circuitos de pelicula.
        circuito="R0-p(R1,CPE1,R3-L1)",
        parametros=["Rs", "Rct", "Q", "n", "Rad", "Lad"],
    ),
    "pelicula_rc": DefinicionCircuito(
        nombre="pelicula_rc",
        # Topologia IDENTICA a randles_simple (Rs + R en paralelo con
        # C) -- lo que cambia es la INTERPRETACION fisica: aqui R es
        # la resistencia de PORO de un recubrimiento (Rpo, el camino
        # ionico que se abre a traves de defectos/poros de la pintura
        # o capa protectora) y C es la capacitancia del recubrimiento
        # mismo (Ccoat), no de una doble capa electroquimica. Se deja
        # como entrada SEPARADA de randles_simple (en vez de solo
        # reutilizarlo) para que el nombre, la descripcion y los
        # parametros bonitos reflejen el contexto de recubrimientos.
        circuito="R0-p(R1,C1)",
        parametros=["Rs", "Rpo", "Ccoat"],
    ),
    "pelicula_cpe": DefinicionCircuito(
        nombre="pelicula_cpe",
        # Igual que pelicula_rc, pero con CPE en vez de capacitor
        # ideal -- topologia identica a randles_cpe. Mas realista para
        # recubrimientos con cierta rugosidad o porosidad no uniforme.
        circuito="R0-p(R1,CPE1)",
        parametros=["Rs", "Rpo", "Qcoat", "ncoat"],
    ),
    "pelicula_transferencia_carga": DefinicionCircuito(
        nombre="pelicula_transferencia_carga",
        # Dos procesos en serie, AMBOS con capacitor ideal (no CPE):
        # el recubrimiento (Rpo, Ccoat) y, debajo, la transferencia de
        # carga en el metal donde el recubrimiento ya fallo (Rct,
        # Cdl). Topologia identica a dos_constantes_tiempo_rc (mismo
        # string), pero con nombres de parametro orientados a
        # recubrimientos en vez de "proceso 1 / proceso 2" generico.
        circuito="R0-p(R1,C1)-p(R2,C2)",
        parametros=["Rs", "Rpo", "Ccoat", "Rct", "Cdl"],
    ),
    "pelicula_cpe_transferencia": DefinicionCircuito(
        nombre="pelicula_cpe_transferencia",
        # Topologia identica a dos_constantes_tiempo (mismo string:
        # dos ramas R-CPE en serie), con nombres orientados a
        # recubrimientos: el recubrimiento (Rpo, Qcoat, ncoat) y la
        # transferencia de carga debajo (Rct, Qdl, ndl).
        circuito="R0-p(R1,CPE1)-p(R2,CPE2)",
        parametros=["Rs", "Rpo", "Qcoat", "ncoat", "Rct", "Qdl", "ndl"],
    ),
    "pelicula_transf_difusion": DefinicionCircuito(
        nombre="pelicula_transf_difusion",
        # El mas completo de los circuitos de recubrimiento: capa
        # (Rpo, Ccoat) en serie con transferencia de carga + difusion
        # (Rct-Aw en paralelo con Cdl) -- para cuando, ademas de que
        # el recubrimiento fallo y hay corrosion activa, el transporte
        # de especies quimicas (por ejemplo, oxigeno disuelto) tambien
        # limita el proceso.
        circuito="R0-p(R1,C1)-p(R2-W1,C2)",
        parametros=["Rs", "Rpo", "Ccoat", "Rct", "Aw", "Cdl"],
    ),
    "dos_constantes_tiempo_rc": DefinicionCircuito(
        nombre="dos_constantes_tiempo_rc",
        # Version con capacitores IDEALES de dos_constantes_tiempo
        # (que usa CPE) -- topologia identica a
        # pelicula_transferencia_carga (mismo string), pero con
        # nombres genericos de "proceso 1 / proceso 2" en vez de
        # contexto especifico de recubrimientos, para usarse cuando
        # los dos procesos no son necesariamente capa+metal.
        circuito="R0-p(R1,C1)-p(R2,C2)",
        parametros=["Rs", "R1", "C1", "R2", "C2"],
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
    "randles_cpe_warburg": (
        "Z(&omega;) = R<sub>s</sub> + "
        "[1&frasl;(R<sub>ct</sub>+A<sub>w</sub>(1-j)/&radic;&omega;) + "
        "1&frasl;Z<sub>CPE</sub>]<sup>-1</sup>"
    ),
    "pelicula_rc": (
        "Z(&omega;) = R<sub>s</sub> + "
        "R<sub>po</sub> / (1 + j&omega;R<sub>po</sub>C<sub>coat</sub>)"
    ),
    "pelicula_cpe": (
        "Z(&omega;) = R<sub>s</sub> + "
        "R<sub>po</sub> / (1 + R<sub>po</sub>&middot;Q<sub>coat</sub>&middot;(j&omega;)<sup>ncoat</sup>)"
    ),
    "pelicula_transferencia_carga": (
        "Z(&omega;) = R<sub>s</sub> + "
        "R<sub>po</sub>/(1+j&omega;R<sub>po</sub>C<sub>coat</sub>) + "
        "R<sub>ct</sub>/(1+j&omega;R<sub>ct</sub>C<sub>dl</sub>)"
    ),
    "pelicula_cpe_transferencia": (
        "Z(&omega;) = R<sub>s</sub> + "
        "R<sub>po</sub>/(1+R<sub>po</sub>Q<sub>coat</sub>(j&omega;)<sup>ncoat</sup>) + "
        "R<sub>ct</sub>/(1+R<sub>ct</sub>Q<sub>dl</sub>(j&omega;)<sup>ndl</sup>)"
    ),
    "pelicula_transf_difusion": (
        "Z(&omega;) = R<sub>s</sub> + "
        "R<sub>po</sub>/(1+j&omega;R<sub>po</sub>C<sub>coat</sub>) + "
        "[1&frasl;(R<sub>ct</sub>+Z<sub>W</sub>) + j&omega;C<sub>dl</sub>]<sup>-1</sup>"
    ),
    "dos_constantes_tiempo_rc": (
        "Z(&omega;) = R<sub>s</sub> + "
        "R<sub>1</sub>/(1+j&omega;R<sub>1</sub>C<sub>1</sub>) + "
        "R<sub>2</sub>/(1+j&omega;R<sub>2</sub>C<sub>2</sub>)"
    ),
    "tres_constantes_tiempo": (
        "Z(&omega;) = R<sub>s</sub> + "
        "R<sub>1</sub>/(1+R<sub>1</sub>Q<sub>1</sub>(j&omega;)<sup>n1</sup>) + "
        "R<sub>2</sub>/(1+R<sub>2</sub>Q<sub>2</sub>(j&omega;)<sup>n2</sup>) + "
        "R<sub>3</sub>/(1+R<sub>3</sub>Q<sub>3</sub>(j&omega;)<sup>n3</sup>)"
    ),
}