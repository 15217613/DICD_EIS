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
    "dos_constantes_tiempo": (
        "Circuito con dos constantes de tiempo. Representa DOS procesos "
        "distintos ocurriendo a distinta velocidad (por ejemplo, una "
        "pelicula/recubrimiento y, debajo, el metal base). Es el modelo "
        "mas complejo de la biblioteca y el mas dificil de ajustar con "
        "confianza cuando los dos procesos ocurren a velocidades "
        "parecidas."
    ),
}

NOMBRES_BONITOS = {
    "randles_simple": "Randles simple",
    "randles_cpe": "Randles con CPE",
    "randles_warburg": "Randles con Warburg (difusion)",
    "dos_constantes_tiempo": "Dos constantes de tiempo",
}

NOMBRES_PARAMETROS_BONITOS = {
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
}

# ---------------------------------------------------------------------------
# De donde sale cada parametro: la "regla" geometrica usada para el
# VALOR INICIAL (antes de que el optimizador lo refine). Se usan como
# tooltip en cada campo editable, para que el usuario entienda que no
# son numeros arbitrarios.
# ---------------------------------------------------------------------------
REGLAS_PARAMETRO = {
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
    return (
        f"El modelo que mejor describe tus datos es: {bonito}.\n"
        f"Con un {peso_akaike*100:.1f}% de probabilidad relativa de ser el "
        "mejor modelo entre los que se probaron (peso de Akaike).\n\n"
        f"{DESCRIPCION_CIRCUITOS.get(nombre_circuito, '')}"
    )


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

<h2>¿Que es la validacion de Kramers-Kronig?</h2>
<p>Es una prueba matematica independiente de cualquier circuito: revisa
si tus datos son "internamente consistentes" con las leyes fisicas que
debe cumplir cualquier sistema estable y lineal. Si tus datos NO pasan
esta prueba, el problema esta en la MEDICION (ruido, inestabilidad),
no en el circuito que elijas despues.</p>
"""
