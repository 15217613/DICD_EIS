# -*- coding: utf-8 -*-
"""
Textos amigables y educativos que usa la interfaz grafica.

Por que este archivo esta separado de motor_eis.py y de ventana_principal.py:
si mas adelante quieres cambiar la redaccion de un mensaje (hacerlo mas
formal, mas corto, agregar una aclaracion, etc.) para tu documentacion o
para tus pruebas con estudiantes, puedes editar SOLO este archivo sin
riesgo de romper ningun calculo ni ningun boton de la ventana.
"""

# ---------------------------------------------------------------------------
# Descripcion de cada circuito de la biblioteca, en lenguaje sencillo.
# ---------------------------------------------------------------------------
DESCRIPCION_CIRCUITOS = {
    "resistencia_pura": (
        "Resistencia pura. El circuito mas simple posible: la "
        "impedancia es un numero real fijo (R) que NO cambia con la "
        "frecuencia. En la grafica de Nyquist se ve como un solo "
        "punto sobre el eje horizontal, sin ninguna curva. Sirve como "
        "punto de referencia para entender el resto de los circuitos: "
        "todos los demas 'construyen' sobre esta idea basica."
    ),
    "capacitor_ideal": (
        "Capacitor ideal. La impedancia depende completamente de la "
        "frecuencia y es puramente imaginaria (no tiene parte real). "
        "En la grafica de Nyquist se ve como una linea vertical recta "
        "que sube conforme baja la frecuencia -- a diferencia de un "
        "CPE, que es un capacitor 'imperfecto', este es el caso "
        "matematicamente ideal."
    ),
    "inductor_ideal": (
        "Inductor ideal. Tambien es puramente imaginario, pero con el "
        "signo contrario al capacitor: en vez de subir conforme baja "
        "la frecuencia, la impedancia sube conforme SUBE la "
        "frecuencia. En la grafica de Nyquist aparece del lado "
        "opuesto (por debajo del eje horizontal), en vez de por "
        "encima como los elementos capacitivos."
    ),
    "rc_serie": (
        "Resistencia y capacitor en serie. Combina los dos elementos "
        "mas basicos uno despues del otro: en la grafica de Nyquist "
        "se ve como una linea vertical (igual que el capacitor solo), "
        "pero desplazada hacia la derecha una distancia igual a R. Es "
        "el modelo tipico de un instrumento o cable con resistencia "
        "propia conectado a un capacitor."
    ),
    "rc_paralelo": (
        "Resistencia y capacitor en paralelo. A diferencia del caso en "
        "serie, aqui la combinacion produce un semicirculo perfecto en "
        "la grafica de Nyquist -- es la misma forma que "
        "randles_simple, pero SIN una resistencia de solucion (Rs) en "
        "serie antes del semicirculo. Es el circuito de Debye clasico, "
        "usado como base teorica para explicar de donde sale la forma "
        "de semicirculo que se repite en casi todos los demas "
        "circuitos de la biblioteca."
    ),
    "randles_simple": (
        "Circuito de Randles simple. Es el modelo mas basico: representa "
        "una resistencia de la solucion (Rs) en serie con un proceso de "
        "transferencia de carga (Rct) y una capacitancia de doble capa "
        "ideal (Cdl). Se usa cuando la superficie del electrodo se "
        "comporta de forma casi perfecta, sin rugosidad ni heterogeneidad "
        "importante."
    ),
    "randles_cpe": (
        "Circuito de Randles con CPE (elemento de fase constante). Es "
        "igual al anterior, pero cambia el capacitor ideal por un CPE, "
        "que representa una superficie NO ideal (rugosa, porosa o poco "
        "uniforme). Es el modelo mas comun en corrosion y sensores "
        "reales, porque casi ninguna superficie es perfectamente lisa."
    ),
    "randles_warburg": (
        "Circuito de Randles con Warburg finito. Agrega un elemento que "
        "representa la difusion de especies quimicas hacia o desde la "
        "superficie (por ejemplo, iones que tardan en llegar al "
        "electrodo). Aparece cuando, ademas de la reaccion en la "
        "superficie, el transporte de materia tambien limita el proceso."
    ),
    "randles_warburg_semiinfinito": (
        "Circuito de Randles con Warburg semi-infinito (frontera "
        "abierta). Es muy parecido al Warburg finito, pero representa "
        "difusion hacia un espacio TAN grande que, dentro del tiempo "
        "que dura la medicion, nunca se nota que existe un limite del "
        "otro lado (por ejemplo, difusion hacia el volumen de una "
        "solucion, en vez de hacia una capa delgada con un borde "
        "definido)."
    ),
    "bucle_inductivo": (
        "Circuito con bucle inductivo. Agrega una tercera rama (R3 en "
        "serie con L1) en paralelo con la transferencia de carga y el "
        "CPE. Esta rama representa la relajacion de un intermediario "
        "quimico ADSORBIDO en la superficie del electrodo -- un "
        "compuesto que se forma y se consume durante la reaccion, y "
        "cuya concentracion tarda un poco en 'ponerse al dia' con los "
        "cambios de la senal aplicada. En la grafica de Nyquist, esto "
        "se ve como un semicirculo capacitivo normal que, a bajas "
        "frecuencias, se dobla hacia abajo formando un bucle -- algo "
        "que NINGUN otro circuito de la biblioteca puede representar."
    ),
    "dos_constantes_tiempo": (
        "Circuito con dos constantes de tiempo. Representa DOS procesos "
        "distintos ocurriendo a distinta velocidad (por ejemplo, una "
        "pelicula/recubrimiento y, debajo, el metal base). Es el modelo "
        "mas complejo de la biblioteca y el mas dificil de ajustar con "
        "confianza cuando los dos procesos ocurren a velocidades "
        "parecidas."
    ),
}

# ---------------------------------------------------------------------------
# En que materiales/dispositivos/sistemas reales se suele encontrar cada
# circuito. Esto es DISTINTO de DESCRIPCION_CIRCUITOS (que explica que
# representa cada elemento matematicamente): aqui el enfoque es "donde
# lo veria un estudiante en la practica", para conectar la formula con
# algo tangible del mundo real -- util para el marco pedagogico del
# proyecto (automatizar el calculo no sirve de nada si el estudiante no
# entiende PARA QUE sirve el modelo en un sistema real).
# ---------------------------------------------------------------------------
EJEMPLOS_SISTEMAS = {
    "resistencia_pura": (
        "En la practica es raro medir un sistema que sea PURAMENTE "
        "esto -- se usa mas como resistencia de calibracion en "
        "laboratorio (una resistencia patron para verificar que el "
        "equipo de EIS este bien calibrado) o como aproximacion de la "
        "resistencia de un cable o conector metalico simple."
    ),
    "capacitor_ideal": (
        "Se usa como aproximacion de dielectricos casi perfectos: "
        "capacitores ceramicos o de pelicula de buena calidad, o "
        "membranas aislantes muy uniformes. En electroquimica real es "
        "raro verlo puro -- casi siempre aparece como CPE, porque casi "
        "ninguna superficie es perfectamente uniforme."
    ),
    "inductor_ideal": (
        "Aparece por efectos del propio CABLEADO o instrumento de "
        "medicion a frecuencias muy altas (inductancia parasita de los "
        "cables), mas que por el sistema electroquimico en si. Tambien "
        "se usa como bloque basico dentro de circuitos mas complejos "
        "que si representan quimica real, como el de bucle inductivo "
        "mencionado para corrosion con intermediarios adsorbidos."
    ),
    "rc_serie": (
        "Modelo simplificado de un cable o electrodo con resistencia "
        "propia conectado a un capacitor de medicion, o de un sistema "
        "de dos terminales simple en un laboratorio de electronica "
        "basica. Sirve mas como circuito de calibracion o ensenanza "
        "que como modelo de un sistema electroquimico real."
    ),
    "rc_paralelo": (
        "Es la base teorica de PRACTICAMENTE todos los sistemas "
        "electroquimicos con un solo proceso: dielectricos con "
        "perdidas, materiales con relajacion tipo Debye, y la version "
        "'ideal' de lo que randles_simple representa con mas detalle "
        "(agregandole la resistencia de la solucion). Si tus datos se "
        "ven como un semicirculo que empieza justo en el origen (sin "
        "desplazamiento), este circuito puede describirlos mejor que "
        "randles_simple."
    ),
    "randles_simple": (
        "Se ve en sistemas casi ideales, con superficies muy lisas y "
        "limpias: electrodos de metales nobles (oro, platino) en un "
        "electrolito simple, celdas de laboratorio recien pulidas, o "
        "sistemas de referencia usados para calibrar un equipo. En la "
        "practica es poco comun encontrarlo en materiales reales de uso "
        "diario, porque casi ninguna superficie es tan perfecta."
    ),
    "randles_cpe": (
        "Es el mas comun en la practica. Aparece en corrosion de "
        "metales con una capa de oxido natural (acero, aluminio, "
        "cobre), en recubrimientos y pinturas anticorrosivas, en "
        "electrodos porosos de baterias y supercapacitores, y en "
        "biosensores (por ejemplo, electrodos en contacto con tejido o "
        "fluidos biologicos). La rugosidad o porosidad de casi "
        "cualquier superficie real es justo lo que representa el CPE."
    ),
    "randles_warburg": (
        "Aparece cuando, ademas de la reaccion en la superficie, el "
        "transporte de iones tambien limita el proceso: baterias de "
        "litio durante la carga/descarga, supercapacitores, celdas de "
        "combustible, y sensores electroquimicos donde el analito tarda "
        "en llegar al electrodo (por ejemplo, sensores de glucosa). "
        "Tambien se ve en corrosion bajo peliculas o recubrimientos "
        "gruesos, donde las especies quimicas tardan en difundirse a "
        "traves de la capa."
    ),
    "randles_warburg_semiinfinito": (
        "Aparece en sistemas donde la difusion ocurre hacia un volumen "
        "grande, sin una barrera cercana: electrodos sumergidos "
        "directamente en una solucion (no en una capa delgada), "
        "sensores electroquimicos en fluidos abiertos (por ejemplo, "
        "agua de rio o sangre en flujo libre), y algunas baterias o "
        "celdas de combustible durante las primeras etapas de "
        "descarga, antes de que el efecto de los bordes o separadores "
        "internos se vuelva importante. La diferencia practica con "
        "randles_warburg es sutil: ambos representan difusion, pero "
        "este se usa cuando NO hay evidencia de que la difusion "
        "'choque' contra un limite dentro del rango de frecuencias "
        "medido."
    ),
    "bucle_inductivo": (
        "Es el circuito clasico para corrosion de aceros al carbono y "
        "otros metales en medios ACIDOS, donde la reaccion pasa por "
        "un intermediario adsorbido (por ejemplo, especies tipo "
        "Fe(OH)ads en la disolucion de hierro). Tambien se reporta en "
        "corrosion bajo deposito y en algunos recubrimientos "
        "organicos danados donde hay una reaccion redox intermedia "
        "activa bajo la pelicula. Si tu grafica de Nyquist muestra un "
        "semicirculo que se 'dobla' hacia abajo del eje a bajas "
        "frecuencias (en vez de simplemente cerrarse), es una senal "
        "fuerte de que este circuito -- y no cualquier variante de "
        "Randles -- es el que corresponde a tu sistema."
    ),
    "dos_constantes_tiempo": (
        "Tipico de sistemas con DOS capas o interfaces distintas "
        "trabajando a velocidades diferentes: metal recubierto con "
        "pintura o un recubrimiento protector (una constante de tiempo "
        "para el recubrimiento, otra para el metal debajo si el "
        "recubrimiento ya empezo a fallar), materiales compuestos con "
        "dos fases, o membranas biologicas con dos barreras (por "
        "ejemplo, una membrana celular y una capa adicional de "
        "biopelicula)."
    ),
}

NOMBRES_BONITOS = {
    "resistencia_pura": "Resistencia pura",
    "capacitor_ideal": "Capacitor ideal",
    "inductor_ideal": "Inductor ideal",
    "rc_serie": "RC en serie",
    "rc_paralelo": "RC en paralelo",
    "randles_simple": "Randles simple",
    "randles_cpe": "Randles con CPE",
    "randles_warburg": "Randles con Warburg (difusion)",
    "randles_warburg_semiinfinito": "Randles con Warburg semi-infinito",
    "dos_constantes_tiempo": "Dos constantes de tiempo",
    "bucle_inductivo": "Con bucle inductivo (intermediario adsorbido)",
}

NOMBRES_PARAMETROS_BONITOS = {
    "R": "Resistencia (R)",
    "C": "Capacitancia (C)",
    "L": "Inductancia (L)",
    "Rs": "Resistencia de la solucion (Rs)",
    "Rct": "Resistencia de transferencia de carga (Rct)",
    "Cdl": "Capacitancia de doble capa (Cdl)",
    "Q": "Magnitud del CPE (Q)",
    "n": "Exponente del CPE (n)",
    "Wo_mag": "Magnitud de difusion (Wo)",
    "Wo_tau": "Tiempo caracteristico de difusion (tau)",
    "R1": "Resistencia del proceso 1 (R1)",
    "Q1": "Magnitud del CPE del proceso 1 (Q1)",
    "n1": "Exponente del CPE del proceso 1 (n1)",
    "R2": "Resistencia del proceso 2 (R2)",
    "Q2": "Magnitud del CPE del proceso 2 (Q2)",
    "n2": "Exponente del CPE del proceso 2 (n2)",
    "R3": "Resistencia de la relajacion adsorbida (R3)",
    "L1": "Inductancia de la relajacion adsorbida (L1)",
}

# ---------------------------------------------------------------------------
# De donde sale cada parametro: la "regla" geometrica usada para el
# VALOR INICIAL (antes de que el optimizador lo refine). Se usan como
# tooltip en cada campo editable, para que el usuario entienda que no
# son numeros arbitrarios.
# ---------------------------------------------------------------------------
REGLAS_PARAMETRO = {
    "R": (
        "Estimacion inicial: depende de la forma del circuito. Si R "
        "es el UNICO elemento (resistencia pura), se usa el promedio "
        "de la parte real de todos los puntos -- ahi no hay riesgo de "
        "ruido amplificado, porque no hay ningun capacitor que dispare "
        "el ruido a bajas frecuencias. Si R esta junto con un "
        "capacitor en la misma rama (RC en serie), se usa un solo "
        "punto en la frecuencia MAS ALTA (la misma idea que Rs), "
        "porque ahi el capacitor casi no aporta y el ruido relativo es "
        "mucho menor. Si R produce un semicirculo (RC en paralelo), se "
        "usa la posicion del pico: R = 2 x (Z' en el pico) -- la misma "
        "idea que se usa para Rct."
    ),
    "C": (
        "Estimacion inicial: depende de la forma del circuito. Si C "
        "es puramente imaginario (capacitor ideal, RC en serie), se "
        "despeja C directamente de Z = -j/(omega x C) en cada punto, "
        "usando la MEDIANA de esas estimaciones. Si C forma parte de "
        "un semicirculo (RC en paralelo), se usa la condicion del pico "
        "(omega x R x C = 1), la misma idea que se usa para Cdl."
    ),
    "L": (
        "Estimacion inicial: se despeja L directamente de la formula "
        "Z = j x omega x L en cada punto medido, y se usa la mediana "
        "de esas estimaciones."
    ),
    "Rs": (
        "Estimacion inicial: se toma la parte real de la impedancia en "
        "la frecuencia MAS ALTA medida. A esa velocidad los efectos "
        "capacitivos casi desaparecen, asi que lo que queda es "
        "practicamente pura resistencia de la solucion."
    ),
    "Rct": (
        "Estimacion inicial: se usa la posicion del PICO del "
        "semicirculo. Ahi, la parte real de la impedancia es igual a "
        "Rs + Rct/2 (una propiedad geometrica de cualquier "
        "semicirculo), asi que Rct = 2 x (Z' en el pico - Rs)."
    ),
    "Cdl": (
        "Estimacion inicial: en la frecuencia donde ocurre el pico del "
        "semicirculo se cumple que omega x Rct x Cdl = 1 (la condicion "
        "que define esa cima), asi que Cdl se despeja de ahi."
    ),
    "Q": (
        "Estimacion inicial: misma idea que Cdl, pero usando la "
        "frecuencia elevada al exponente n (que arranca en 0.8, un "
        "valor tipico de superficies no ideales)."
    ),
    "n": (
        "Se arranca con n=0.8 (tipico de superficies rugosas o "
        "porosas) como punto de partida para el optimizador."
    ),
    "Wo_mag": (
        "Estimacion inicial: se mide cuanta resistencia EXTRA aparece "
        "en la frecuencia mas baja medida, mas alla de lo que ya "
        "explican Rs y Rct -- esa resistencia adicional se atribuye a "
        "la difusion."
    ),
    "Wo_tau": (
        "Estimacion inicial: es el parametro MAS DIFICIL de estimar de "
        "toda la biblioteca (puede tener 200%+ de error de partida). "
        "Se aproxima como el inverso de la frecuencia mas baja medida "
        "-- la escala de tiempo mas lenta que alcanzaste a 'ver' en el "
        "experimento -- y por eso el ajuste prueba varias escalas "
        "distintas antes de quedarse con la mejor."
    ),
}
REGLAS_PARAMETRO["R1"] = REGLAS_PARAMETRO["R2"] = REGLAS_PARAMETRO["Rct"].replace(
    "Rct", "R1/R2"
)
REGLAS_PARAMETRO["Q1"] = REGLAS_PARAMETRO["Q2"] = REGLAS_PARAMETRO["Q"]
REGLAS_PARAMETRO["n1"] = REGLAS_PARAMETRO["n2"] = REGLAS_PARAMETRO["n"]
REGLAS_PARAMETRO["R3"] = (
    "Estimacion inicial: a frecuencia muy baja, el inductor L1 se "
    "comporta como un corto circuito y el CPE como un circuito "
    "abierto -- solo quedan Rct y R3 en paralelo. Con el valor medido "
    "en la frecuencia mas baja se despeja R3, conociendo ya el valor "
    "estimado de Rct."
)
REGLAS_PARAMETRO["L1"] = (
    "Estimacion inicial: se busca la frecuencia donde la curva cruza "
    "el eje (donde termina el semicirculo capacitivo y empieza el "
    "bucle inductivo) -- esa frecuencia marca la escala de tiempo de "
    "la relajacion (tau = L1/R3), asi que L1 se despeja de ahi usando "
    "el R3 ya estimado."
)


def texto_como_se_obtienen_parametros():
    return (
        "¿De donde salen estos numeros? En dos pasos:\n\n"
        "1) Estimacion inicial geometrica: cada parametro tiene una "
        "'regla' basada en la forma de tu curva de Nyquist (por "
        "ejemplo, donde esta el pico del semicirculo). Pasa el mouse "
        "sobre el nombre de cada parametro para ver su regla especifica.\n\n"
        "2) Ajuste fino (Levenberg-Marquardt): el algoritmo de "
        "impedance.py parte de esa estimacion inicial y la mueve poco "
        "a poco, minimizando el error entre la curva del modelo y tus "
        "datos reales (con mas peso en los puntos de menor magnitud). "
        "El numero final que ves es el resultado de ese ajuste, no la "
        "estimacion inicial cruda.\n\n"
        "Puedes modificar los valores de abajo para simular el "
        "circuito con OTROS parametros y ver de inmediato como cambia "
        "la curva -- eso NO vuelve a ajustar nada, solo evalua la "
        "formula con los numeros que pongas, asi que puedes comparar "
        "tu intento contra el resultado real del ajuste."
    )


def nombre_bonito(nombre_circuito):
    return NOMBRES_BONITOS.get(nombre_circuito, nombre_circuito)


def nombre_parametro_bonito(nombre_parametro):
    return NOMBRES_PARAMETROS_BONITOS.get(nombre_parametro, nombre_parametro)


def ejemplos_sistemas(nombre_circuito):
    """Devuelve el texto de 'donde se ve esto en la practica' para un
    circuito dado, o una cadena vacia si no hay texto registrado (por
    ejemplo, si en el futuro se agrega un circuito nuevo a la
    biblioteca y todavia no se redacta su ejemplo)."""
    return EJEMPLOS_SISTEMAS.get(nombre_circuito, "")


def texto_notacion_impedance():
    """
    Explica, UNA sola vez (se reutiliza como tooltip en varios lugares
    de la interfaz), que significa la notacion tecnica que usa la
    libreria impedance.py para describir un circuito como texto (por
    ejemplo "R0-p(R1,CPE1)") -- distinta de la formula matematica en
    FORMULAS_HTML, que ya esta en notacion de impedancia electrica
    tradicional (Z(omega) = ...).
    """
    return (
        "Notacion de la libreria impedance.py: los elementos separados "
        "por un guion (-) estan en SERIE. 'p(a,b)' significa que a y b "
        "estan en PARALELO. Los numeros (R0, R1, CPE1...) distinguen "
        "elementos del mismo tipo cuando hay mas de uno. CPE = elemento "
        "de fase constante (superficie no ideal). Ws = elemento de "
        "Warburg finito (difusion limitada por una barrera)."
    )


# ---------------------------------------------------------------------------
# Mensajes segun el resultado de cada paso del analisis.
# ---------------------------------------------------------------------------
def texto_kramers_kronig(valido, mensaje_tecnico):
    if valido:
        return (
            "✅ Tus datos pasaron la prueba de Kramers-Kronig.\n"
            "Esto quiere decir que son fisicamente consistentes: el sistema "
            "probablemente se mantuvo estable durante toda la medicion, sin "
            "cambios raros a la mitad del experimento.\n\n"
            f"Detalle tecnico: {mensaje_tecnico}"
        )
    return (
        "⚠️ Tus datos NO pasaron completamente la prueba de Kramers-Kronig.\n"
        "Esto es una senal de alerta, no necesariamente un error grave: "
        "puede deberse a ruido excesivo, a que el sistema cambio un poco "
        "durante la medicion, o a una medicion muy larga en un sistema "
        "inestable. Los resultados del ajuste que siguen pueden ser menos "
        "confiables de lo normal.\n\n"
        f"Detalle tecnico: {mensaje_tecnico}"
    )


def texto_semicirculos(n_semicirculos):
    return (
        f"Se detectaron aproximadamente {n_semicirculos} semicirculo(s) en "
        "tu curva de Nyquist. Esto es solo una PISTA inicial -- el programa "
        "de todas formas va a probar los cuatro modelos de circuito de la "
        "biblioteca y va a dejar que la estadistica (AIC/BIC) decida cual "
        "es el que realmente describe mejor tus datos."
    )


def texto_resultado_circuito(nombre_circuito, aic, bic, valido, motivo):
    bonito = nombre_bonito(nombre_circuito)
    if valido:
        return f"{bonito}: se ajusto correctamente (AIC={aic:.1f}, BIC={bic:.1f})."
    return (
        f"{bonito}: se descarto. Motivo: {motivo}. "
        "Esto no significa que el programa haya fallado -- significa que, "
        "para tus datos, este modelo dio parametros sin sentido fisico "
        "(por ejemplo una resistencia negativa), asi que se elimina de la "
        "comparacion aunque matematicamente el ajuste numerico haya corrido."
    )


def texto_mejor_circuito(nombre_circuito, peso_akaike):
    bonito = nombre_bonito(nombre_circuito)
    ejemplos = ejemplos_sistemas(nombre_circuito)
    texto = (
        f"El modelo que mejor describe tus datos es: {bonito}.\n"
        f"Con un {peso_akaike*100:.1f}% de probabilidad relativa de ser el "
        "mejor modelo entre los que se probaron (peso de Akaike).\n\n"
        f"{DESCRIPCION_CIRCUITOS.get(nombre_circuito, '')}"
    )
    if ejemplos:
        texto += f"\n\n¿Donde se ve esto en la practica? {ejemplos}"
    return texto


def texto_por_que_es_mejor(resultado):
    """
    Explica, usando los numeros REALES de este analisis (no en
    abstracto), por que el circuito ganador se considera mejor que el
    segundo mas cercano -- que tan grande es la diferencia de AIC entre
    ambos, que tan fuerte es esa evidencia segun las reglas estandar de
    interpretacion (Burnham & Anderson, 2002), y que dice el peso de
    Akaike en terminos de porcentaje.

    Si la diferencia de AIC es menor a 2 (el mismo umbral que usa
    texto_empate), esta funcion devuelve cadena vacia -- ese caso ya lo
    cubre el aviso de empate, y repetir la explicacion aqui seria
    confuso (un mensaje diciendo "es mucho mejor" y otro diciendo "es
    un empate" al mismo tiempo).

    resultado: un app.domain.models.ResultadoAnalisis ya con
    pesos_akaike calculado.
    """
    validos = resultado.validos
    if len(validos) < 2:
        return ""  # no hay con que comparar (o gano por default)

    mejor, segundo = validos[0], validos[1]
    delta_aic = segundo.aic - mejor.aic
    umbral_empate_aic = 2
    if delta_aic < umbral_empate_aic:
        return ""

    peso_por_nombre = dict(zip((r.nombre for r in validos), resultado.pesos_akaike))
    peso_mejor = peso_por_nombre.get(mejor.nombre, 0)
    peso_segundo = peso_por_nombre.get(segundo.nombre, 0)

    # Umbrales de interpretacion de Burnham & Anderson (2002): que tan
    # fuerte es la evidencia segun que tan grande es la diferencia de
    # AIC. Son reglas de "dedo" ampliamente citadas en la literatura de
    # seleccion de modelos, no un limite matematico exacto.
    if delta_aic < 4:
        fuerza = "evidencia moderada"
        interpretacion = (
            "hay una diferencia real entre los dos modelos, pero todavia "
            "no es enorme"
        )
    elif delta_aic < 10:
        fuerza = "evidencia considerable"
        interpretacion = "el segundo modelo tiene bastante menos soporte que el ganador"
    else:
        fuerza = "evidencia muy fuerte"
        interpretacion = (
            f"el modelo {nombre_bonito(segundo.nombre)} practicamente se "
            "puede descartar frente al ganador"
        )

    texto = (
        f"¿Por que se eligio {nombre_bonito(mejor.nombre)} y no "
        f"{nombre_bonito(segundo.nombre)} (el segundo mas cercano)? "
        f"Su AIC ({mejor.aic:.1f}) es mas bajo que el del segundo "
        f"({segundo.aic:.1f}) -- una diferencia (&Delta;AIC) de "
        f"{delta_aic:.1f}. Segun las reglas usuales de interpretacion "
        f"(Burnham &amp; Anderson, 2002), esto es {fuerza}: {interpretacion}. "
        f"En terminos de probabilidad relativa (peso de Akaike), "
        f"{nombre_bonito(mejor.nombre)} tiene un {peso_mejor*100:.1f}% "
        f"contra solo {peso_segundo*100:.1f}% de {nombre_bonito(segundo.nombre)}."
    )

    # Chequeo de honestidad cientifica: BIC penaliza MAS fuerte que AIC
    # a los modelos con mas parametros, asi que a veces no esta de
    # acuerdo con AIC sobre cual es el mejor. Si eso pasa, se lo
    # decimos al usuario en vez de ocultarlo -- es el mismo espiritu
    # que el aviso de empate estadistico.
    ordenados_por_bic = sorted(validos, key=lambda r: r.bic)
    if ordenados_por_bic[0].nombre == mejor.nombre:
        texto += (
            " El criterio BIC (que penaliza mas fuerte los modelos con "
            "mas parametros) coincide: tambien ubica a este circuito "
            "como el mejor, lo que da mas confianza en la eleccion."
        )
    else:
        texto += (
            " <b>Aviso:</b> el criterio BIC (mas estricto con el numero "
            f"de parametros) en realidad favorece a "
            f"{nombre_bonito(ordenados_por_bic[0].nombre)} en vez de a "
            f"{nombre_bonito(mejor.nombre)}. Esto puede pasar cuando el "
            "modelo ganador usa parametros extra que ayudan un poco al "
            "ajuste, pero no lo suficiente como para justificar esa "
            "complejidad adicional segun un criterio mas estricto. Vale "
            "la pena tener en cuenta ambos circuitos antes de concluir."
        )

    return texto


def texto_empate(nombres_empatados, pesos):
    lista = ", ".join(
        f"{nombre_bonito(n)} ({p*100:.0f}%)" for n, p in zip(nombres_empatados, pesos)
    )
    return (
        "⚖️ Aviso de empate estadistico.\n"
        f"Estos modelos ajustan practicamente igual de bien: {lista}.\n\n"
        "La diferencia entre ellos es menor al umbral que se considera "
        "significativo (segun Burnham & Anderson, 2002), asi que el "
        "'ganador' podria deberse al ruido de esta medicion en particular, "
        "no a que sea realmente el mejor modelo fisico.\n\n"
        "Recomendacion: si sabes algo adicional de tu sistema real (por "
        "ejemplo, si esperas difusion o no, o si hay una sola capa o dos), "
        "usa ese conocimiento para elegir entre ellos -- no te bases solo "
        "en este numero."
    )


def texto_sin_modelos_validos():
    return (
        "❌ Ningun circuito de la biblioteca paso el filtro de sentido "
        "fisico con estos datos.\n"
        "Esto puede pasar si los datos tienen mucho ruido, si el rango de "
        "frecuencias medido es muy corto, o si tu sistema necesita un "
        "circuito que todavia no esta en la biblioteca. Revisa la grafica "
        "de Nyquist para ver si la forma de la curva tiene sentido antes "
        "de repetir la medicion."
    )


# ---------------------------------------------------------------------------
# Contenido estatico de la pestana "Aprender" (introduccion conceptual).
# ---------------------------------------------------------------------------
TEXTO_APRENDER_HTML = """
<h2>¿Que es la Espectroscopia de Impedancia Electroquimica (EIS)?</h2>
<p>Es una tecnica que consiste en aplicarle a un sistema electroquimico
(por ejemplo, un metal en una solucion) una pequena senal electrica que
cambia de frecuencia, y medir como responde. De esa respuesta se obtiene
la <b>impedancia</b>: una medida de que tanto "se resiste" el sistema a
que pase corriente, y como esa resistencia cambia segun la velocidad
(frecuencia) de la senal.</p>

<h2>¿Que es un diagrama de Nyquist?</h2>
<p>Es la forma mas comun de graficar los datos de EIS: se pone la parte
real de la impedancia en el eje horizontal y la parte imaginaria (con el
signo invertido) en el eje vertical. Cada punto representa una
frecuencia distinta. La FORMA de la curva (semicirculos, lineas rectas,
etc.) da pistas sobre que procesos fisicos y quimicos estan ocurriendo.</p>

<h2>¿Que es un circuito equivalente?</h2>
<p>Es un modelo matematico hecho con componentes electricos "de
juguete" (resistencias, capacitores, etc.) que, conectados de cierta
forma, producen una curva de impedancia parecida a la que mide tu
equipo. No es un circuito real que exista dentro de la celda: es una
manera de traducir un fenomeno quimico (una reaccion, una capa porosa,
la difusion de iones) a un lenguaje matematico que se puede ajustar a
los datos.</p>

<h2>¿Por que el programa prueba varios circuitos y no uno solo?</h2>
<p>Porque, sin saberlo de antemano, no hay forma de estar seguro de
cual circuito describe mejor TU sistema en particular. El programa
ajusta los cuatro modelos de la biblioteca y usa un criterio
estadistico (AIC/BIC) para comparar cual explica los datos con la
menor cantidad de "excusas" (parametros) posible.</p>

<h2>¿Que es el criterio AIC/BIC?</h2>
<p>Son numeros que penalizan a un modelo por cada parametro extra que
usa. La idea es simple: un modelo con mas parametros casi siempre va a
ajustar un poco mejor los datos, pero eso no significa que sea el
modelo "correcto" -- puede estar sobreajustando el ruido. AIC y BIC
premian el balance entre "ajusta bien" y "no usa parametros de mas".
Un AIC mas bajo es mejor.</p>

<h2>¿Que es el "peso de Akaike"?</h2>
<p>Es una forma de convertir las diferencias de AIC entre modelos en un
porcentaje de probabilidad relativa. Si dos modelos tienen pesos
parecidos (por ejemplo 55% y 40%), significa que los datos no alcanzan
para distinguir con seguridad cual es el mejor -- es un "empate
estadistico", y el programa te lo va a avisar cuando pase.</p>

<h2>¿Que tan grande debe ser la diferencia de AIC para que importe?</h2>
<p>No cualquier diferencia de AIC significa que un modelo es
claramente mejor -- hace falta una regla para saber cuando la
diferencia (llamada &Delta;AIC, "delta AIC") es lo bastante grande
como para confiar en ella. Las reglas mas citadas en la literatura
(Burnham &amp; Anderson, 2002) son:</p>
<ul>
<li><b>&Delta;AIC menor a 2:</b> los modelos son practicamente
indistinguibles -- es un empate estadistico.</li>
<li><b>&Delta;AIC entre 4 y 7:</b> evidencia considerable a favor del
modelo con menor AIC; el otro modelo tiene bastante menos soporte.</li>
<li><b>&Delta;AIC mayor a 10:</b> evidencia muy fuerte; el modelo con
mayor AIC practicamente se puede descartar.</li>
</ul>
<p>Cuando el programa elige un "mejor circuito", usa exactamente estas
reglas para explicarte que tan solida es esa eleccion -- no solo te
dice CUAL circuito gano, sino QUE TAN CONVENCIDO deberias estar de esa
eleccion.</p>

<h2>¿Por que a veces AIC y BIC no estan de acuerdo?</h2>
<p>BIC penaliza MAS fuerte que AIC a los modelos que usan mas
parametros (la formula de BIC crece mas rapido con cada parametro
extra cuando hay muchos datos). Esto significa que, en ocasiones,
AIC puede favorecer un circuito con un parametro adicional (porque
ese parametro ayudo un poco a explicar los datos), mientras que BIC
prefiere el circuito mas simple (porque no considera que esa mejora
compense la complejidad extra). Cuando esto pasa, el programa te lo
avisa explicitamente en vez de ocultarlo -- ninguno de los dos
criterios es "el correcto" de forma absoluta, asi que ver ambos te da
una vision mas completa.</p>

<h2>¿Que es la validacion de Kramers-Kronig?</h2>
<p>Es una prueba matematica independiente de cualquier circuito: revisa
si tus datos son "internamente consistentes" con las leyes fisicas que
debe cumplir cualquier sistema estable y lineal. Si tus datos NO pasan
esta prueba, el problema esta en la MEDICION (ruido, inestabilidad),
no en el circuito que elijas despues.</p>
"""