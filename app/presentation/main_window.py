# -*- coding: utf-8 -*-
"""
Ventana principal de la interfaz grafica.

Esta es la capa de PRESENTACION, y dentro de ella, esta clase es
deliberadamente "delgada": no construye botones ni tablas directamente,
solo ARMA la ventana juntando tres widgets autosuficientes
(app.presentation.widgets: PanelArchivo, PanelGraficaNyquist,
PanelResultados) y conecta sus senales entre si y con la capa de
aplicacion. Cada widget no sabe nada de los otros -- esta clase es la
unica que conoce a los tres, y por eso es quien coordina.

La ventana llama a la capa de aplicacion (app.application) para cargar
archivos y correr el analisis -- nunca a domain/ ni a infrastructure/
directamente, con una sola excepcion deliberada:
app.infrastructure.workers.HiloAnalisis, porque un QThread es en si
mismo un detalle de como esta implementada ESTA interfaz (Qt).
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QTabWidget, QTextBrowser,
    QMessageBox, QFileDialog,
)

from app.application import eis_service, export_service
from app.infrastructure.workers import HiloAnalisis
from app.presentation import textos_educativos
from app.presentation.widgets.panel_archivo import PanelArchivo
from app.presentation.widgets.grafica_nyquist import PanelGraficaNyquist
from app.presentation.widgets.tabla_resultados import PanelResultados

import os
import tempfile

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "Analizador de EIS - Ajuste automatico de circuitos equivalentes"
        )
        self.resize(1300, 750)

        self.ruta_archivo = None
        self.frecuencias_cargadas = None
        self.Z_cargada = None
        self.hilo = None
        self.ultimo_resultado = None

        self._construir_ui()

    # ------------------------------------------------------------------
    # Construccion de la interfaz: solo ensambla los widgets y conecta
    # sus senales -- ningun widget de bajo nivel (botones, tablas) se
    # crea aqui directamente.
    # ------------------------------------------------------------------
    def _construir_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QHBoxLayout(central)

        self.panel_archivo = PanelArchivo()
        self.panel_archivo.setMaximumWidth(340)
        self.panel_archivo.archivo_elegido.connect(self._al_elegir_archivo)
        self.panel_archivo.analizar_solicitado.connect(self._iniciar_analisis)
        self.panel_archivo.exportar_solicitado.connect(self._exportar_reporte)

        self.panel_resultados = PanelResultados()
        self.panel_grafica = PanelGraficaNyquist()
        self.tab_aprender = QTextBrowser()
        self.tab_aprender.setHtml(textos_educativos.TEXTO_APRENDER_HTML)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.panel_resultados, "Resultados")
        self.tabs.addTab(self.panel_grafica, "Grafica de Nyquist")
        self.tabs.addTab(self.tab_aprender, "Aprender")

        layout_principal.addWidget(self.panel_archivo)
        layout_principal.addWidget(self.tabs, stretch=1)

    # ------------------------------------------------------------------
    # Manejo del archivo
    # ------------------------------------------------------------------
    def _al_elegir_archivo(self, ruta):
        """
        Lee el archivo INMEDIATAMENTE al seleccionarlo (no hasta que se
        de clic en "Analizar"), para poder mostrar la tabla de datos
        crudos de una vez y avisar de inmediato si el archivo tiene un
        problema de formato, sin esperar a correr todo el analisis.
        """
        try:
            frecuencias, Z = eis_service.cargar_archivo(ruta)
        except eis_service.ErrorCargaArchivo as e:
            QMessageBox.warning(self, "No se pudo leer el archivo", str(e))
            return

        self.ruta_archivo = ruta
        self.frecuencias_cargadas = frecuencias
        self.Z_cargada = Z
        self.ultimo_resultado = None

        self.panel_archivo.mostrar_archivo_cargado(
            os.path.basename(ruta), ruta, len(frecuencias)
        )
        self.panel_grafica.mostrar_datos_crudos(frecuencias, Z)

    # ------------------------------------------------------------------
    # Analisis en segundo plano
    # ------------------------------------------------------------------
    def _iniciar_analisis(self):
        if self.frecuencias_cargadas is None:
            return
        self.panel_archivo.habilitar_analizar(False)
        self.panel_archivo.reiniciar_progreso()

        self.hilo = HiloAnalisis(self.frecuencias_cargadas, self.Z_cargada)
        self.hilo.progreso.connect(self.panel_archivo.actualizar_progreso)
        self.hilo.terminado.connect(self._mostrar_resultados)
        self.hilo.fallo.connect(self._mostrar_error)
        self.hilo.finished.connect(lambda: self.panel_archivo.habilitar_analizar(True))
        self.hilo.start()

    def _mostrar_error(self, mensaje):
        QMessageBox.critical(self, "No se pudo completar el analisis", mensaje)

    def _mostrar_resultados(self, resultado):
        self.ultimo_resultado = resultado
        self.panel_resultados.mostrar(resultado)
        self.panel_grafica.mostrar_resultados(resultado)
        self.panel_archivo.habilitar_exportar(len(resultado.mejores) > 0)
        self.tabs.setCurrentWidget(self.panel_resultados)

    # ------------------------------------------------------------------
    # Exportar reporte PDF
    # ------------------------------------------------------------------
    def _exportar_reporte(self):
        if self.ultimo_resultado is None:
            return

        nombre_sugerido = "reporte_eis.pdf"
        if self.ruta_archivo:
            base = os.path.splitext(os.path.basename(self.ruta_archivo))[0]
            nombre_sugerido = f"reporte_{base}.pdf"

        ruta_salida, _ = QFileDialog.getSaveFileName(
            self, "Guardar reporte PDF", nombre_sugerido, "Archivos PDF (*.pdf)"
        )
        if not ruta_salida:
            return
        if not ruta_salida.lower().endswith(".pdf"):
            ruta_salida += ".pdf"

        try:
            with tempfile.TemporaryDirectory() as carpeta_temporal:
                ruta_imagen = os.path.join(carpeta_temporal, "grafica_nyquist.png")
                self.panel_grafica.guardar_grafica_como_imagen(ruta_imagen)

                export_service.exportar_reporte_pdf(
                    self.ultimo_resultado,
                    ruta_salida,
                    nombre_archivo_datos=os.path.basename(self.ruta_archivo or ""),
                    ruta_imagen_grafica=ruta_imagen,
                    nombres_bonitos=textos_educativos.NOMBRES_BONITOS,
                    nombres_parametros_bonitos=textos_educativos.NOMBRES_PARAMETROS_BONITOS,
                    ejemplos_sistemas=textos_educativos.EJEMPLOS_SISTEMAS,
                    texto_comparacion_modelos=textos_educativos.texto_por_que_es_mejor(
                        self.ultimo_resultado
                    ),
                )
        except Exception as e:
            QMessageBox.critical(
                self, "No se pudo generar el reporte",
                f"Ocurrio un problema al generar el PDF.\n\nDetalle: {e}",
            )
            return

        QMessageBox.information(
            self, "Reporte generado",
            f"El reporte se guardo correctamente en:\n{ruta_salida}",
        )