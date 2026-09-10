# -*- coding: utf-8 -*-
"""
Calculos puros de EIS (Espectroscopia de Impedancia Electroquimica).

Esta es la capa de dominio: NO importa PySide6, NO importa matplotlib,
NO sabe leer archivos. Solo recibe arreglos de numeros (frecuencias e
impedancias) y devuelve numeros o circuitos ajustados. Esto es a
proposito -- permite probar toda la ciencia del proyecto (via
tests/unit/) sin necesitar abrir ninguna ventana.

Lo que SI resuelve la libreria impedance.py (la usamos tal cual):
- Definicion de circuitos
- Ajuste con ponderacion por modulo (Levenberg-Marquardt)

Lo que NO resuelve impedance.py (es el aporte propio del proyecto):
- Deteccion del numero de semicirculos
- Valores iniciales a partir de la geometria de la curva
- Comparacion de circuitos con AIC/BIC
"""

import numpy as np
import warnings
from scipy.signal import savgol_filter, find_peaks
from impedance.models.circuits import CustomCircuit
from impedance.validation import linKK, circuit_elements

from app.domain.circuits import CIRCUITOS

# WORKAROUND: la funcion interna eval_linKK() de impedance.py (v1.7.1)
# usa eval() con circuit_elements como espacio de nombres, pero ese
# diccionario no incluye 'np' -- causa un NameError al llamar linKK().
# Lo agregamos aqui para no tener que modificar el codigo fuente de la
# libreria.
circuit_elements["np"] = np

# Circuitos que llevan un elemento tipo Warburg (Ws o Wo) con un
# parametro Wo_tau dificil de estimar de entrada -- comparten la MISMA
# estrategia de estimacion inicial (la formula geometrica no depende
# de si la frontera de difusion es abierta o cerrada) y la MISMA
# necesidad de probar varios puntos de partida al ajustar (ver
# ajustar_circuito), porque Wo_tau puede tener 200%+ de error de
# partida en cualquiera de los dos casos.
CIRCUITOS_CON_WARBURG = ("randles_warburg", "randles_warburg_semiinfinito")


# ---------------------------------------------------------------------------
# Validacion de consistencia fisica (Kramers-Kronig)
# ---------------------------------------------------------------------------
def validar_kramers_kronig(frecuencias, Z, umbral=0.02):
    """
    Usa el metodo lin-KK (ya incluido en impedance.py) para revisar si
    los datos son fisicamente validos: ajusta un circuito generico de
    muchos elementos R-C en serie (sin relacion con la biblioteca de
    circuitos "de verdad" -- es solo una prueba de consistencia) y ve
    que tan bien reproduce los datos.

    umbral: error relativo maximo aceptable (0.02 = 2%).

    Devuelve (valido: bool, mensaje: str)
    """
    M, mu, Z_fit, resids_real, resids_imag = linKK(
        frecuencias, Z, c=0.85, max_M=100, fit_type="complex"
    )
    error_relativo = np.sqrt(resids_real**2 + resids_imag**2) / np.abs(Z)
    error_maximo = np.max(error_relativo)

    valido = error_maximo < umbral
    mensaje = (
        f"lin-KK uso {M} elementos RC, error relativo maximo = "
        f"{error_maximo*100:.2f}% (umbral: {umbral*100:.0f}%)"
    )
    return valido, mensaje


# ---------------------------------------------------------------------------
# Deteccion del numero de semicirculos
# ---------------------------------------------------------------------------
def detectar_semicirculos(frecuencias, Z):
    """
    Suaviza la parte imaginaria y cuenta picos (filtrando por
    prominencia para ignorar ruido), para estimar cuantos procesos
    (semicirculos) hay en los datos. Solo se usa como PISTA -- el flujo
    principal siempre prueba TODOS los circuitos de la biblioteca.

    Devuelve un numero entero: 1, 2, etc. (minimo 1, nunca 0).
    """
    Z_imag_suave = savgol_filter(-Z.imag, window_length=7, polyorder=2)
    altura_minima = 0.15 * np.max(Z_imag_suave)
    picos, _ = find_peaks(Z_imag_suave, prominence=altura_minima)
    return max(len(picos), 1)


# ---------------------------------------------------------------------------
# Estimacion de valores iniciales por geometria de la curva
# ---------------------------------------------------------------------------
def estimar_valores_iniciales_multiples_dos_tc(frecuencias, Z):
    """
    MEJORA para dos_constantes_tiempo: genera VARIOS candidatos de
    "valle" entre los dos semicirculos en vez de confiar en uno solo, y
    deja que ajustar_circuito pruebe todos y se quede con el que de
    menor error tras el ajuste.

    Devuelve una LISTA de listas de valores iniciales (un candidato
    por cada posible valle).
    """
    Rs_inicial = Z.real[np.argmax(frecuencias)]
    Z_imag_suave = savgol_filter(-Z.imag, window_length=7, polyorder=2)
    omega = 2 * np.pi * frecuencias

    minimos_locales, _ = find_peaks(-Z_imag_suave)
    candidatos_valle = list(minimos_locales) + [len(frecuencias) // 2]
    candidatos_valle = sorted(set(
        idx for idx in candidatos_valle if 2 < idx < len(frecuencias) - 3
    ))
    if not candidatos_valle:
        candidatos_valle = [len(frecuencias) // 2]

    guesses = []
    for idx_valle in candidatos_valle:
        idx_pico1 = np.argmax(Z_imag_suave[:idx_valle + 1])
        R1 = max(2 * (Z.real[idx_pico1] - Rs_inicial), 1e-2)
        n1 = 0.8
        Q1 = 1 / (omega[idx_pico1] ** n1 * R1)

        idx_pico2 = idx_valle + np.argmax(Z_imag_suave[idx_valle:])
        R2 = max(2 * (Z.real[idx_pico2] - Z.real[idx_valle]), 1e-2)
        n2 = 0.8
        Q2 = 1 / (omega[idx_pico2] ** n2 * R2)

        guesses.append([Rs_inicial, R1, Q1, n1, R2, Q2, n2])

    return guesses


def estimar_valores_iniciales(nombre_circuito, frecuencias, Z):
    """
    Calcula valores de partida a partir de la forma de la curva, en el
    orden que espera el circuito de impedance.py correspondiente.
    """
    omega = 2 * np.pi * frecuencias

    Rs_inicial = Z.real[np.argmax(frecuencias)]

    idx_pico_global = np.argmax(-Z.imag)
    Rct_inicial = 2 * (Z.real[idx_pico_global] - Rs_inicial)
    Rct_inicial = max(Rct_inicial, 1e-2)

    if nombre_circuito == "resistencia_pura":
        # Z = R para cualquier frecuencia -- la resistencia no depende
        # de omega, asi que el mejor "punto de partida" es simplemente
        # el promedio de la parte real de todos los datos.
        return [float(np.mean(Z.real))]

    elif nombre_circuito == "capacitor_ideal":
        # Z = -j/(omega*C) => C = -1/(omega*Z.imag). Se usa la mediana
        # sobre todos los puntos (no un solo punto) para que un dato
        # ruidoso aislado no arruine la estimacion.
        C_estimados = -1.0 / (omega * Z.imag)
        return [max(float(np.median(C_estimados)), 1e-12)]

    elif nombre_circuito == "inductor_ideal":
        # Z = j*omega*L => L = Z.imag/omega.
        L_estimados = Z.imag / omega
        return [max(float(np.median(L_estimados)), 1e-12)]

    elif nombre_circuito == "rc_serie":
        # A diferencia de resistencia_pura, aqui SI hay un elemento
        # capacitivo en la misma rama -- y como el ruido sintetico (y
        # el ruido real de un instrumento) es proporcional a |Z|, a
        # bajas frecuencias |Z| se dispara (1/(omega*C) crece sin
        # limite) y el ruido sobre la parte real se vuelve enorme
        # comparado con R. Por eso NO se puede promediar Z.real de
        # todas las frecuencias como en resistencia_pura -- hay que
        # usar la MISMA idea que ya se usa para Rs_inicial arriba: un
        # solo punto en la frecuencia MAS ALTA, donde el capacitor casi
        # no aporta y la parte real es casi pura R con poco ruido
        # relativo (confirmado con pruebas: promediar todo daba un
        # error de mas de 900%, usar la frecuencia mas alta lo baja a
        # menos de 1%).
        R_inicial = Z.real[np.argmax(frecuencias)]
        C_estimados = -1.0 / (omega * Z.imag)
        C_inicial = max(float(np.median(C_estimados)), 1e-12)
        return [R_inicial, C_inicial]

    elif nombre_circuito == "rc_paralelo":
        # Es la misma forma de semicirculo que randles_simple, pero
        # SIN resistencia de solucion en serie (Rs=0 implicito) --
        # por eso el pico del semicirculo cae directo en R/2 (no en
        # Rs + R/2), y R = 2 x (Z' en el pico).
        idx_pico = np.argmax(-Z.imag)
        R_inicial = max(2 * Z.real[idx_pico], 1e-2)
        C_inicial = 1 / (omega[idx_pico] * R_inicial)
        return [R_inicial, C_inicial]

    elif nombre_circuito == "randles_simple":
        idx_pico = np.argmax(-Z.imag)
        Cdl_inicial = 1 / (omega[idx_pico] * Rct_inicial)
        return [Rs_inicial, Rct_inicial, Cdl_inicial]

    elif nombre_circuito == "randles_cpe":
        idx_pico = np.argmax(-Z.imag)
        n_inicial = 0.8
        Q_inicial = 1 / (omega[idx_pico] ** n_inicial * Rct_inicial)
        return [Rs_inicial, Rct_inicial, Q_inicial, n_inicial]

    elif nombre_circuito in CIRCUITOS_CON_WARBURG:
        # randles_warburg (Ws, frontera cerrada) y
        # randles_warburg_semiinfinito (Wo, frontera abierta) comparten
        # esta misma estimacion: la geometria de la curva no distingue
        # todavia que tipo de frontera es -- eso lo decide el ajuste
        # numerico, no la estimacion inicial.
        idx_pico = np.argmax(-Z.imag)
        n_inicial = 0.8
        Q_inicial = 1 / (omega[idx_pico] ** n_inicial * Rct_inicial)

        Z_real_baja_frec = Z.real[np.argmin(frecuencias)]
        Wo_mag_inicial = max(Z_real_baja_frec - Rs_inicial - Rct_inicial, 1e-3)

        omega_min = omega[np.argmin(frecuencias)]
        Wo_tau_inicial = 1 / omega_min

        return [Rs_inicial, Rct_inicial, Wo_mag_inicial, Wo_tau_inicial,
                Q_inicial, n_inicial]

    elif nombre_circuito == "dos_constantes_tiempo":
        Z_imag_suave = savgol_filter(-Z.imag, window_length=7, polyorder=2)

        altura_minima = 0.15 * np.max(Z_imag_suave)
        picos, _ = find_peaks(Z_imag_suave, prominence=altura_minima)

        if len(picos) < 2:
            idx_valle = len(frecuencias) // 2
        else:
            picos_ordenados_por_altura = picos[np.argsort(Z_imag_suave[picos])[::-1]]
            dos_picos_reales = np.sort(picos_ordenados_por_altura[:2])
            tramo = Z_imag_suave[dos_picos_reales[0]:dos_picos_reales[1]]
            idx_valle = dos_picos_reales[0] + np.argmin(tramo)

        idx_pico1 = np.argmax(Z_imag_suave[:idx_valle + 1])
        R1_inicial = max(2 * (Z.real[idx_pico1] - Rs_inicial), 1e-2)
        n1_inicial = 0.8
        Q1_inicial = 1 / (omega[idx_pico1] ** n1_inicial * R1_inicial)

        idx_pico2 = idx_valle + np.argmax(Z_imag_suave[idx_valle:])
        R2_inicial = max(2 * (Z.real[idx_pico2] - Z.real[idx_valle]), 1e-2)
        n2_inicial = 0.8
        Q2_inicial = 1 / (omega[idx_pico2] ** n2_inicial * R2_inicial)

        return [Rs_inicial, R1_inicial, Q1_inicial, n1_inicial,
                R2_inicial, Q2_inicial, n2_inicial]

    elif nombre_circuito == "bucle_inductivo":
        # Pico del semicirculo capacitivo -- np.argmax(-Z.imag) nunca
        # cae en la zona del bucle inductivo, porque ahi -Z.imag es
        # NEGATIVO (Z.imag positivo), asi que el maximo siempre esta
        # en la parte capacitiva de la curva, sin importar que tan
        # grande sea el bucle.
        idx_pico = np.argmax(-Z.imag)
        n_inicial = 0.8
        Q_inicial = 1 / (omega[idx_pico] ** n_inicial * Rct_inicial)

        # A frecuencia muy baja, el inductor L1 actua como corto
        # circuito y el CPE se comporta como circuito abierto (un
        # capacitor ideal no deja pasar corriente en DC) -- solo
        # quedan Rct y R3 en paralelo. Con el valor medido en la
        # frecuencia mas baja se puede despejar R3.
        Z_real_baja_frec = Z.real[np.argmin(frecuencias)]
        paralelo_estimado = max(Z_real_baja_frec - Rs_inicial, 1e-2)
        if paralelo_estimado < Rct_inicial:
            R3_inicial = 1 / (1 / paralelo_estimado - 1 / Rct_inicial)
        else:
            # La geometria no dio un valor util (paso raro, ej. datos
            # muy ruidosos) -- se usa un valor de respaldo razonable
            # en vez de que el calculo de division truene.
            R3_inicial = Rct_inicial * 5
        R3_inicial = max(R3_inicial, 1e-2)

        # La frecuencia donde la curva cruza el eje (de capacitivo a
        # inductivo) marca la escala de tiempo de la rama R3-L1:
        # tau = L1/R3, entonces L1 = R3 / omega_cruce.
        indices_bucle = np.where(Z.imag > 0)[0]
        if len(indices_bucle) > 0:
            omega_cruce = np.max(omega[indices_bucle])
        else:
            # Si el bucle no se alcanza a ver en el rango medido (por
            # ejemplo, si el barrido no bajo lo suficiente en
            # frecuencia), se usa la frecuencia mas baja disponible
            # como aproximacion de respaldo.
            omega_cruce = omega[np.argmin(frecuencias)]
        L1_inicial = max(R3_inicial / omega_cruce, 1e-6)

        return [Rs_inicial, Rct_inicial, Q_inicial, n_inicial,
                R3_inicial, L1_inicial]

    raise ValueError(f"Circuito desconocido: {nombre_circuito}")


# ---------------------------------------------------------------------------
# Simulacion manual: evaluar la formula con valores fijos, SIN ajustar
# ---------------------------------------------------------------------------
def calcular_impedancia_con_parametros(nombre_circuito, frecuencias, valores):
    """
    Evalua la formula de impedancia de un circuito con valores de
    parametro dados por el usuario, SIN correr ningun ajuste numerico.
    Es la base de la exploracion interactiva: cuando alguien mueve un
    parametro en la interfaz, esta funcion responde al instante porque
    solo evalua una formula matematica -- no busca el minimo de nada.

    valores: lista de numeros en el mismo orden que
    CIRCUITOS[nombre_circuito].parametros

    Devuelve Z (array de numeros complejos), del mismo tamano que
    frecuencias.
    """
    info = CIRCUITOS[nombre_circuito]
    circuito = CustomCircuit(circuit=info.circuito, initial_guess=list(valores))
    with warnings.catch_warnings():
        # impedance.py avisa "Simulating circuit based on initial
        # parameters" cada vez que se usa use_initial=True -- aqui es
        # exactamente la intencion, asi que se silencia para no llenar
        # la consola si el usuario mueve un parametro muchas veces.
        warnings.simplefilter("ignore", UserWarning)
        return circuito.predict(frecuencias, use_initial=True)


# ---------------------------------------------------------------------------
# Ajuste de circuitos (Levenberg-Marquardt via impedance.py)
# ---------------------------------------------------------------------------
def ajustar_circuito(nombre_circuito, frecuencias, Z):
    """
    Construye el CustomCircuit con los valores iniciales estimados y lo
    ajusta con weight_by_modulus=True (pondera cada punto por 1/|Z|,
    para que puntos de magnitud muy distinta -- comunes en EIS, donde
    |Z| puede variar varios ordenes de magnitud entre la frecuencia
    mas alta y la mas baja -- pesen de forma comparable en el ajuste).
    maxfev=300 evita que un ajuste degenerado tarde 25+ segundos
    (confirmado con pruebas de robustez), a costa de que ese caso
    especifico ajuste con menos precision -- pero de todas formas se
    descarta despues por AIC o por el filtro de sentido fisico.

    AVISO IMPORTANTE (descubierto al agregar rc_serie): esta funcion
    NO tenia weight_by_modulus=True hasta ahora -- el docstring decia
    que la ponderacion "ya venia incluida por defecto en .fit()", pero
    eso era incorrecto: el default real de impedance.py es False, y en
    ningun lado del codigo se pasaba explicitamente True. El problema
    quedaba oculto porque los circuitos tipo Randles (con una rama
    R-CPE en paralelo) tienen |Z| ACOTADO en todas las frecuencias (va
    de Rs a Rs+Rct, sin dispararse a infinito), asi que un ajuste sin
    ponderar igual quedaba razonablemente bien. Pero circuitos como
    rc_serie o capacitor_ideal SI tienen |Z| que crece sin limite a
    bajas frecuencias (nada los detiene) -- ahi, sin ponderar, el error
    total queda dominado por esos pocos puntos enormes y el optimizador
    practicamente ignora ajustar bien los demas parametros (se
    confirmo: rc_serie recuperaba R con mas de 900% de error sin esta
    correccion, y menos de 3% con ella). Ademas, esto ahora es
    consistente con calcular_aic_bic() mas abajo, que YA calculaba su
    propio error ponderado por 1/|Z| -- antes el ajuste y la metrica
    de comparacion usaban criterios distintos sin que nadie lo hubiera
    notado.

    Devuelve el objeto circuit ya ajustado.
    """
    info = CIRCUITOS[nombre_circuito]
    valores_iniciales = estimar_valores_iniciales(nombre_circuito, frecuencias, Z)

    if nombre_circuito in CIRCUITOS_CON_WARBURG:
        # Wo_tau (el tiempo caracteristico de difusion) es el
        # parametro mas dificil de adivinar de toda la biblioteca --
        # puede tener 200%+ de error de partida sin importar si la
        # frontera es abierta (Wo) o cerrada (Ws). Por eso se prueban
        # varias escalas de tiempo distintas y se deja el ajuste que
        # de menor error, en vez de confiar en una sola estimacion.
        # Cada intento esta protegido con try/except (igual que ya se
        # hace en dos_constantes_tiempo mas abajo): un factor que
        # falla no debe tumbar los demas.
        #
        # ACTUALIZACION (la nota de robustez original aqui quedo
        # OBSOLETA): se habia documentado que el caso Wo_mag >= Rct
        # solo convergia 1/10 veces. Eso resulto ser un sintoma del
        # bug de weight_by_modulus (ver docstring de ajustar_circuito
        # mas abajo) -- una vez agregado weight_by_modulus=True a los
        # tres .fit() de esta funcion, el mismo caso "dificil" pasa a
        # converger 10/10 veces. Se deja este parrafo como registro de
        # que la fragilidad observada no era un problema intrinseco
        # del elemento Wo, sino del ajuste sin ponderar.
        idx_wo_tau = info.parametros.index("Wo_tau")
        Wo_tau_base = valores_iniciales[idx_wo_tau]
        mejor_circuit = None
        mejor_error = np.inf
        for factor in [0.1, 1.0, 5.0]:
            guess = list(valores_iniciales)
            guess[idx_wo_tau] = Wo_tau_base * factor
            try:
                circuit = CustomCircuit(circuit=info.circuito, initial_guess=guess,
                                         name=nombre_circuito)
                circuit.fit(frecuencias, Z, maxfev=300, weight_by_modulus=True)
            except Exception:
                continue
            Z_modelo = circuit.predict(frecuencias)
            peso = 1 / np.abs(Z)
            error = np.sum(((Z_modelo.real - Z.real) * peso) ** 2
                          + ((Z_modelo.imag - Z.imag) * peso) ** 2)
            if error < mejor_error:
                mejor_error = error
                mejor_circuit = circuit
        if mejor_circuit is None:
            raise RuntimeError(
                "ningun punto de partida de Wo_tau logro converger "
                f"para {nombre_circuito}"
            )
        return mejor_circuit

    if nombre_circuito == "dos_constantes_tiempo":
        candidatos = estimar_valores_iniciales_multiples_dos_tc(frecuencias, Z)
        mejor_circuit = None
        mejor_error = np.inf
        for guess in candidatos:
            try:
                circuit = CustomCircuit(circuit=info.circuito, initial_guess=guess,
                                         name=nombre_circuito)
                circuit.fit(frecuencias, Z, maxfev=300, weight_by_modulus=True)
            except Exception:
                continue
            Z_modelo = circuit.predict(frecuencias)
            peso = 1 / np.abs(Z)
            error = np.sum(((Z_modelo.real - Z.real) * peso) ** 2
                          + ((Z_modelo.imag - Z.imag) * peso) ** 2)
            if error < mejor_error:
                mejor_error = error
                mejor_circuit = circuit
        if mejor_circuit is None:
            raise RuntimeError("ningun candidato de valle logro converger")
        return mejor_circuit

    circuit = CustomCircuit(
        circuit=info.circuito,
        initial_guess=valores_iniciales,
        name=nombre_circuito,
    )
    circuit.fit(frecuencias, Z, maxfev=300, weight_by_modulus=True)
    return circuit


# ---------------------------------------------------------------------------
# Comparacion de modelos: AIC / BIC / pesos de Akaike
# ---------------------------------------------------------------------------
def calcular_error_relativo_porcentual(Z_modelo, Z_datos):
    """
    Que tan lejos esta, en promedio, una curva de modelo de los datos
    medidos, expresado como un porcentaje facil de interpretar.

    Esto NO es el mismo numero que usa calcular_aic_bic internamente
    (ese esta ponderado y pensado para COMPARAR circuitos entre si).
    Este es mas simple a proposito: el promedio de cuanto se aleja,
    en porcentaje, cada punto del modelo respecto al dato real --
    pensado para que una persona entienda de un vistazo que tan buena
    es una simulacion, sin tener que interpretar un numero abstracto.

    Devuelve un porcentaje (float). 0% seria un ajuste perfecto; mas
    alto es peor.
    """
    diferencia_relativa = np.abs(Z_modelo - Z_datos) / np.abs(Z_datos)
    return float(np.mean(diferencia_relativa) * 100)


def calcular_aic_bic(circuit, frecuencias, Z):
    """impedance.py no trae AIC/BIC, asi que se calculan aqui a partir
    de la prediccion del circuito ya ajustado."""
    Z_modelo = circuit.predict(frecuencias)
    peso = 1 / np.abs(Z)
    error_real = (Z_modelo.real - Z.real) * peso
    error_imag = (Z_modelo.imag - Z.imag) * peso
    error_total = np.sum(error_real ** 2 + error_imag ** 2)

    n_datos = len(frecuencias)
    n_parametros = len(circuit.parameters_)

    aic = n_datos * np.log(error_total / n_datos) + 2 * n_parametros
    bic = n_datos * np.log(error_total / n_datos) + n_parametros * np.log(n_datos)
    return aic, bic


def calcular_pesos_akaike(lista_aic):
    """
    Convierte una lista de valores AIC en "pesos de Akaike": la
    probabilidad relativa de que cada modelo sea el mejor, dado el
    conjunto de modelos comparados (Burnham & Anderson, 2002).

    Devuelve una lista de pesos (entre 0 y 1) que suman 1, en el mismo
    orden que lista_aic.
    """
    aic_arr = np.array(lista_aic)
    delta_aic = aic_arr - aic_arr.min()
    verosimilitud_relativa = np.exp(-0.5 * delta_aic)
    pesos = verosimilitud_relativa / verosimilitud_relativa.sum()
    return pesos.tolist()