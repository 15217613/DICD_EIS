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

    if nombre_circuito == "randles_simple":
        idx_pico = np.argmax(-Z.imag)
        Cdl_inicial = 1 / (omega[idx_pico] * Rct_inicial)
        return [Rs_inicial, Rct_inicial, Cdl_inicial]

    elif nombre_circuito == "randles_cpe":
        idx_pico = np.argmax(-Z.imag)
        n_inicial = 0.8
        Q_inicial = 1 / (omega[idx_pico] ** n_inicial * Rct_inicial)
        return [Rs_inicial, Rct_inicial, Q_inicial, n_inicial]

    elif nombre_circuito == "randles_warburg":
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
    ajusta. La ponderacion por modulo ya viene incluida por defecto en
    .fit(). maxfev=300 evita que un ajuste degenerado tarde 25+
    segundos (confirmado con pruebas de robustez), a costa de que ese
    caso especifico ajuste con menos precision -- pero de todas formas
    se descarta despues por AIC o por el filtro de sentido fisico.

    Devuelve el objeto circuit ya ajustado.
    """
    info = CIRCUITOS[nombre_circuito]
    valores_iniciales = estimar_valores_iniciales(nombre_circuito, frecuencias, Z)

    if nombre_circuito == "randles_warburg":
        idx_wo_tau = info.parametros.index("Wo_tau")
        Wo_tau_base = valores_iniciales[idx_wo_tau]
        mejor_circuit = None
        mejor_error = np.inf
        for factor in [0.1, 1.0, 5.0]:
            guess = list(valores_iniciales)
            guess[idx_wo_tau] = Wo_tau_base * factor
            circuit = CustomCircuit(circuit=info.circuito, initial_guess=guess,
                                     name=nombre_circuito)
            circuit.fit(frecuencias, Z, maxfev=300)
            Z_modelo = circuit.predict(frecuencias)
            peso = 1 / np.abs(Z)
            error = np.sum(((Z_modelo.real - Z.real) * peso) ** 2
                          + ((Z_modelo.imag - Z.imag) * peso) ** 2)
            if error < mejor_error:
                mejor_error = error
                mejor_circuit = circuit
        return mejor_circuit

    if nombre_circuito == "dos_constantes_tiempo":
        candidatos = estimar_valores_iniciales_multiples_dos_tc(frecuencias, Z)
        mejor_circuit = None
        mejor_error = np.inf
        for guess in candidatos:
            try:
                circuit = CustomCircuit(circuit=info.circuito, initial_guess=guess,
                                         name=nombre_circuito)
                circuit.fit(frecuencias, Z, maxfev=300)
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
    circuit.fit(frecuencias, Z, maxfev=300)
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
