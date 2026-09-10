# -*- coding: utf-8 -*-
"""
Servicio de exportacion de resultados a PDF.

Decide QUE contenido lleva un reporte de EIS (que secciones, en que
orden) y arma los "bloques" que espera infrastructure/pdf_writer.py --
pero no sabe nada de COMO se dibuja un PDF (eso es infrastructure) ni
de PySide6 (eso es presentation).

Nota de arquitectura sobre nombres_bonitos/nombres_parametros_bonitos/
ejemplos_sistemas: esta capa (application) NO puede importar
presentation/textos_educativos.py (romperia la regla de que las capas
de abajo no dependen de las de arriba). En vez de eso, quien llama a
exportar_reporte_pdf (la ventana, en presentation/) le PASA esos
diccionarios de nombres/textos ya armados. Si no se pasan, el reporte
usa los nombres tecnicos crudos (Rs, Rct, etc.) y omite la seccion de
ejemplos -- sigue siendo un reporte correcto y completo, solo menos
pulido.
"""

import datetime
import math

from app.domain.circuits import CIRCUITOS
from app.domain.models import ResultadoAnalisis
from app.infrastructure import pdf_writer


def exportar_reporte_pdf(
    resultado: ResultadoAnalisis,
    ruta_salida: str,
    nombre_archivo_datos: str = "",
    ruta_imagen_grafica: str = None,
    nombres_bonitos: dict = None,
    nombres_parametros_bonitos: dict = None,
    ejemplos_sistemas: dict = None,
    texto_comparacion_modelos: str = None,
):
    """
    Genera un PDF con el resumen de Kramers-Kronig, la tabla
    comparativa de circuitos, los parametros del mejor ajuste, en que
    materiales/sistemas reales suele aparecer ese circuito (si se
    provee ejemplos_sistemas), por que ese circuito se considera mejor
    que el segundo mas cercano (si se provee texto_comparacion_modelos),
    y (si se provee) la grafica de Nyquist como imagen.

    Nota de arquitectura sobre texto_comparacion_modelos: por la misma
    razon que nombres_bonitos/ejemplos_sistemas (ver docstring del
    modulo), este texto ya viene REDACTADO por quien llama a esta
    funcion (normalmente main_window.py, usando
    textos_educativos.texto_por_que_es_mejor) -- esta capa
    (application) no puede generar ese texto ella misma porque
    necesitaria importar presentation/textos_educativos.py.

    Devuelve la ruta del archivo generado (la misma que ruta_salida).
    """
    nombres_bonitos = nombres_bonitos or {}
    nombres_parametros_bonitos = nombres_parametros_bonitos or {}
    ejemplos_sistemas = ejemplos_sistemas or {}

    def nombre_bonito(nombre):
        return nombres_bonitos.get(nombre, nombre)

    def nombre_parametro_bonito(nombre):
        return nombres_parametros_bonitos.get(nombre, nombre)

    peso_por_nombre = dict(
        zip((r.nombre for r in resultado.validos), resultado.pesos_akaike)
    )

    bloques = []

    # --- Encabezado del documento ---
    bloques.append({"tipo": "titulo", "texto": "Reporte de Analisis EIS"})
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    bloques.append({
        "tipo": "parrafo",
        "texto": (
            f"<b>Archivo analizado:</b> {nombre_archivo_datos or '(sin nombre)'}"
            f"<br/><b>Generado:</b> {fecha}"
            f"<br/><b>Puntos de datos:</b> {len(resultado.frecuencias)}"
        ),
    })
    bloques.append({"tipo": "espacio", "alto_pt": 14})

    # --- Seccion 1: Kramers-Kronig ---
    bloques.append({
        "tipo": "encabezado",
        "texto": "1. Validacion de consistencia fisica (Kramers-Kronig)",
    })
    estado_kk = (
        "Los datos PASARON la validacion de Kramers-Kronig."
        if resultado.kk_valido
        else "Los datos NO pasaron completamente la validacion de Kramers-Kronig."
    )
    bloques.append({
        "tipo": "parrafo",
        "texto": f"{estado_kk} {resultado.kk_mensaje}",
    })
    bloques.append({
        "tipo": "parrafo",
        "texto": (
            f"Semicirculos detectados como pista inicial: "
            f"{resultado.n_semicirculos} (el analisis igual prueba todos "
            f"los circuitos de la biblioteca)."
        ),
    })
    bloques.append({"tipo": "espacio", "alto_pt": 10})

    # --- Seccion 2: tabla comparativa ---
    bloques.append({
        "tipo": "encabezado", "texto": "2. Comparacion de modelos candidatos",
    })
    filas = []
    for r in resultado.resultados:
        peso = peso_por_nombre.get(r.nombre)
        filas.append([
            nombre_bonito(r.nombre),
            f"{r.aic:.2f}" if math.isfinite(r.aic) else "-",
            f"{r.bic:.2f}" if math.isfinite(r.bic) else "-",
            f"{peso*100:.1f}%" if peso is not None else "-",
            "Valido" if r.valido else "Descartado",
            r.motivo,
        ])
    bloques.append({
        "tipo": "tabla",
        "encabezados": ["Circuito", "AIC", "BIC", "Peso de Akaike", "Estado", "Motivo"],
        "filas": filas,
    })
    bloques.append({"tipo": "espacio", "alto_pt": 10})

    # --- Seccion 3: mejor circuito ---
    bloques.append({
        "tipo": "encabezado", "texto": "3. Modelo seleccionado como mejor ajuste",
    })
    if not resultado.mejores:
        bloques.append({
            "tipo": "parrafo",
            "texto": "Ningun circuito paso el filtro de sentido fisico.",
        })
    else:
        mejor = resultado.mejores[0]
        peso_mejor = peso_por_nombre.get(mejor.nombre, 0)
        bloques.append({
            "tipo": "parrafo",
            "texto": (
                f"<b>{nombre_bonito(mejor.nombre)}</b> -- peso de Akaike: "
                f"{peso_mejor*100:.1f}%"
            ),
        })
        nombres_parametros = CIRCUITOS[mejor.nombre].parametros
        filas_parametros = [
            [nombre_parametro_bonito(np_), f"{v:.5g}"]
            for np_, v in zip(nombres_parametros, mejor.circuit.parameters_)
        ]
        bloques.append({
            "tipo": "tabla",
            "encabezados": ["Parametro", "Valor"],
            "filas": filas_parametros,
        })

        bloques.append({
            "tipo": "parrafo",
            "texto": (
                f"<b>Notacion tecnica (impedance.py):</b> "
                f"{CIRCUITOS[mejor.nombre].circuito}"
            ),
        })

        texto_ejemplos = ejemplos_sistemas.get(mejor.nombre)
        if texto_ejemplos:
            bloques.append({"tipo": "espacio", "alto_pt": 6})
            bloques.append({
                "tipo": "parrafo",
                "texto": (
                    f"<b>¿Donde se ve este circuito en la practica?</b> "
                    f"{texto_ejemplos}"
                ),
            })

        if texto_comparacion_modelos:
            bloques.append({"tipo": "espacio", "alto_pt": 6})
            bloques.append({
                "tipo": "parrafo",
                "texto": texto_comparacion_modelos,
            })

        if len(resultado.empatados) > 1:
            nombres_emp = ", ".join(
                nombre_bonito(r.nombre) for r in resultado.empatados
            )
            bloques.append({"tipo": "espacio", "alto_pt": 6})
            bloques.append({
                "tipo": "parrafo",
                "texto": (
                    f"<i>Aviso de empate estadistico (diferencia de AIC "
                    f"menor a 2, Burnham &amp; Anderson 2002) entre: "
                    f"{nombres_emp}. Estos modelos ajustan practicamente "
                    f"igual de bien -- el 'ganador' podria deberse al "
                    f"ruido de esta medicion.</i>"
                ),
            })

    # --- Seccion 4: grafica de Nyquist ---
    if ruta_imagen_grafica:
        bloques.append({"tipo": "espacio", "alto_pt": 12})
        bloques.append({"tipo": "encabezado", "texto": "4. Grafica de Nyquist"})
        bloques.append({"tipo": "imagen", "ruta": ruta_imagen_grafica, "ancho_cm": 15})

    pdf_writer.escribir_pdf(ruta_salida, bloques, titulo_documento="Reporte de Analisis EIS")
    return ruta_salida