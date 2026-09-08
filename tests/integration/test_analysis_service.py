# -*- coding: utf-8 -*-
"""
Prueba de INTEGRACION: el flujo completo de analisis, de punta a
punta, igual que lo usa la interfaz grafica -- carga de archivo real
(infrastructure) + orquestacion (application) + calculos (domain),
todas las capas trabajando juntas. Se diferencia de las pruebas
unitarias en que aqui no se aisla ninguna pieza: si algo en la
conexion entre capas se rompe (una firma de funcion, un import mal
puesto), esta prueba lo deberia detectar.
"""

import os

from app.application import eis_service, analysis_service

RUTA_EJEMPLO = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "examples", "datos_prueba.csv"
)


def test_flujo_completo_con_archivo_de_ejemplo():
    frecuencias, Z = eis_service.cargar_archivo(RUTA_EJEMPLO)
    assert len(frecuencias) > 0

    mensajes_de_progreso = []
    resultado = analysis_service.ejecutar_analisis(
        frecuencias, Z, callback=lambda msg, pct: mensajes_de_progreso.append(pct)
    )

    # Se probaron los 4 circuitos de la biblioteca
    assert len(resultado.resultados) == 4

    # El archivo de ejemplo es un Randles+CPE limpio (1% de ruido):
    # deberia pasar Kramers-Kronig sin problema.
    # (se comprueba con bool(...) porque este valor es un np.bool_, no
    # un bool nativo de Python -- "is True" fallaria aunque el
    # resultado sea correcto, por ser objetos distintos)
    assert bool(resultado.kk_valido)

    # Al menos un circuito deberia pasar el filtro de sentido fisico
    assert len(resultado.validos) > 0
    assert len(resultado.mejores) > 0

    # Los pesos de Akaike deben sumar 1 (son una distribucion de
    # probabilidad sobre los circuitos validos)
    assert abs(sum(resultado.pesos_akaike) - 1.0) < 1e-6

    # Se debio reportar avance en algun momento (para la barra de
    # progreso de la interfaz)
    assert mensajes_de_progreso[-1] == 100


def test_cargar_archivo_inexistente_da_error_amigable():
    try:
        eis_service.cargar_archivo("este_archivo_no_existe.csv")
        assert False, "deberia haber lanzado ErrorCargaArchivo"
    except eis_service.ErrorCargaArchivo as e:
        # El mensaje debe estar pensado para el usuario final, no ser
        # solo la excepcion tecnica cruda.
        assert "no se pudo leer" in str(e).lower()
