# -*- coding: utf-8 -*-
"""
Pestana "Resultados": resumen general (Kramers-Kronig, semicirculos),
tabla comparativa de los 4 circuitos, y el detalle del circuito
ganador.

Es un widget de solo LECTURA: recibe un app.domain.models.ResultadoAnalisis
ya calculado (a traves de mostrar()) y solo se encarga de presentarlo
con claridad -- no tiene logica de negocio propia, no decide nada.
"""

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextBrowser, QTableWidget,
    QTableWidgetItem, QHeaderView,
)

from app.domain import circuits as domain_circuits
from app.presentation import textos_educativos


class PanelResultados(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)

        self.texto_resumen = QTextBrowser()
        self.texto_resumen.setMaximumHeight(160)

        self.tabla_ranking = QTableWidget(0, 5)
        self.tabla_ranking.setHorizontalHeaderLabels(
            ["Circuito", "AIC", "BIC", "Peso de Akaike", "Estado"]
        )
        self.tabla_ranking.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tabla_ranking.horizontalHeader().setStretchLastSection(True)
        self.tabla_ranking.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_ranking.setMaximumHeight(160)

        self.texto_mejor = QTextBrowser()

        layout.addWidget(QLabel("<b>Resumen general</b>"))
        layout.addWidget(self.texto_resumen)
        layout.addWidget(QLabel("<b>Comparacion de modelos candidatos</b>"))
        layout.addWidget(self.tabla_ranking)
        layout.addWidget(QLabel("<b>Mejor modelo encontrado</b>"))
        layout.addWidget(self.texto_mejor, stretch=1)

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------
    def mostrar(self, resultado):
        peso_por_nombre = dict(zip(
            (r.nombre for r in resultado.validos), resultado.pesos_akaike
        ))
        self._llenar_resumen(resultado)
        self._llenar_tabla_ranking(resultado, peso_por_nombre)
        self._llenar_mejor_circuito(resultado, peso_por_nombre)

    # ------------------------------------------------------------------
    def _llenar_resumen(self, resultado):
        partes = [
            "<p>" + textos_educativos.texto_kramers_kronig(
                resultado.kk_valido, resultado.kk_mensaje
            ).replace("\n", "<br>") + "</p>",
            "<p>" + textos_educativos.texto_semicirculos(
                resultado.n_semicirculos
            ) + "</p>",
        ]
        self.texto_resumen.setHtml("".join(partes))

    def _llenar_tabla_ranking(self, resultado, peso_por_nombre):
        resultados = resultado.resultados
        self.tabla_ranking.setRowCount(len(resultados))

        for fila, r in enumerate(resultados):
            nombre_item = QTableWidgetItem(textos_educativos.nombre_bonito(r.nombre))
            aic_texto = f"{r.aic:.2f}" if np.isfinite(r.aic) else "-"
            bic_texto = f"{r.bic:.2f}" if np.isfinite(r.bic) else "-"
            peso = peso_por_nombre.get(r.nombre)
            peso_texto = f"{peso*100:.1f}%" if peso is not None else "-"
            estado_texto = "Valido" if r.valido else "Descartado"

            items = [
                nombre_item,
                QTableWidgetItem(aic_texto),
                QTableWidgetItem(bic_texto),
                QTableWidgetItem(peso_texto),
                QTableWidgetItem(estado_texto),
            ]
            items[-1].setToolTip(r.motivo)
            for col, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla_ranking.setItem(fila, col, item)

    def _llenar_mejor_circuito(self, resultado, peso_por_nombre):
        mejores = resultado.mejores
        if not mejores:
            self.texto_mejor.setHtml(
                "<p>" + textos_educativos.texto_sin_modelos_validos() + "</p>"
            )
            return

        mejor = mejores[0]
        peso_mejor = peso_por_nombre.get(mejor.nombre, 0)
        html = "<p>" + textos_educativos.texto_mejor_circuito(
            mejor.nombre, peso_mejor
        ).replace("\n", "<br>") + "</p>"

        html += "<p><b>Parametros ajustados:</b></p><ul>"
        nombres_parametros = domain_circuits.CIRCUITOS[mejor.nombre].parametros
        for nombre_p, valor in zip(nombres_parametros, mejor.circuit.parameters_):
            etiqueta = textos_educativos.nombre_parametro_bonito(nombre_p)
            html += f"<li>{etiqueta}: {valor:.5g}</li>"
        html += "</ul>"

        empatados = resultado.empatados
        if len(empatados) > 1:
            nombres_emp = [r.nombre for r in empatados]
            pesos_emp = [peso_por_nombre.get(n, 0) for n in nombres_emp]
            html += "<p>" + textos_educativos.texto_empate(
                nombres_emp, pesos_emp
            ).replace("\n", "<br>") + "</p>"

        self.texto_mejor.setHtml(html)
