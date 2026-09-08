# -*- coding: utf-8 -*-
"""
Orquesta el flujo completo de analisis de un archivo de EIS.

Este servicio es el "director de orquesta": no hace ningun calculo por
su cuenta, solo llama EN ORDEN a las funciones de domain/ (que son las
que saben COMO calcular cada cosa) y junta todo en un
ResultadoAnalisis. Separar esto de domain/impedance.py importa por una
razon practica: aqui es donde vive el ORDEN de los pasos y el reporte
de avance (para la barra de progreso), mientras que domain/ solo tiene
funciones puras que no saben que existe un "paso 3 de 8".
"""

import numpy as np

from app.domain import impedance, validation, circuits
from app.domain.models import ResultadoAjusteCircuito, ResultadoAnalisis


def ejecutar_analisis(frecuencias, Z, callback=None, n_mostrar=3):
    """
    Corre el analisis completo sobre datos YA cargados (ver
    application/eis_service.py para cargar el archivo primero).

    callback(mensaje, porcentaje): funcion opcional que se llama en
    cada paso para reportar avance -- pensada para conectarse a una
    barra de progreso, pero no depende de ningun framework de UI en
    particular (podria ser un print() en una consola igual de bien).

    Devuelve un app.domain.models.ResultadoAnalisis.
    """
    def avisar(mensaje, porcentaje):
        if callback is not None:
            callback(mensaje, porcentaje)

    avisar("Usando los datos ya cargados...", 5)

    avisar("Verificando consistencia fisica de los datos (Kramers-Kronig)...", 15)
    kk_valido, kk_mensaje = impedance.validar_kramers_kronig(frecuencias, Z)

    avisar("Detectando numero de semicirculos en la curva...", 20)
    n_semicirculos = impedance.detectar_semicirculos(frecuencias, Z)

    resultados = []
    nombres_circuitos = list(circuits.CIRCUITOS.keys())
    n_circuitos = len(nombres_circuitos)
    for i, nombre_circuito in enumerate(nombres_circuitos):
        porcentaje = 20 + int(60 * (i + 1) / n_circuitos)
        avisar(f"Probando modelo de circuito: {nombre_circuito}...", porcentaje)
        try:
            circuito_ajustado = impedance.ajustar_circuito(
                nombre_circuito, frecuencias, Z
            )
        except Exception as e:
            resultados.append(ResultadoAjusteCircuito(
                nombre=nombre_circuito, circuit=None,
                aic=np.inf, bic=np.inf, valido=False,
                motivo=f"no se pudo ajustar este circuito ({e})",
            ))
            continue

        aic, bic = impedance.calcular_aic_bic(circuito_ajustado, frecuencias, Z)
        valido, motivo = validation.es_fisicamente_valido(
            nombre_circuito, circuito_ajustado
        )
        resultados.append(ResultadoAjusteCircuito(
            nombre=nombre_circuito, circuit=circuito_ajustado,
            aic=aic, bic=bic, valido=valido, motivo=motivo,
        ))

    resultados.sort(key=lambda r: r.aic)
    validos = [r for r in resultados if r.valido]
    descartados = [r for r in resultados if not r.valido]

    resultado = ResultadoAnalisis(
        frecuencias=frecuencias,
        Z=Z,
        kk_valido=kk_valido,
        kk_mensaje=kk_mensaje,
        n_semicirculos=n_semicirculos,
        resultados=resultados,
        validos=validos,
        descartados=descartados,
    )

    if not validos:
        avisar("Ningun circuito paso el filtro de sentido fisico.", 100)
        return resultado

    avisar("Comparando modelos con criterio AIC/BIC...", 85)
    resultado.pesos_akaike = impedance.calcular_pesos_akaike(
        [r.aic for r in validos]
    )

    mejores = validos[:n_mostrar]
    resultado.mejores = mejores

    # Aviso de "empate estadistico": diferencias de AIC menores a 2
    # (Burnham & Anderson, 2002) significan soporte practicamente
    # equivalente entre modelos.
    umbral_empate_aic = 2
    empatados = [mejores[0]]
    for r in validos[1:]:
        if r.aic - mejores[0].aic < umbral_empate_aic:
            empatados.append(r)
        else:
            break
    resultado.empatados = empatados

    avisar("Analisis completo.", 100)
    return resultado
