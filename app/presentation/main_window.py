# -*- coding: utf-8 -*-
"""
Ventana principal de la interfaz grafica.

Esta es la capa de PRESENTACION, y dentro de ella, esta clase es
deliberadamente "delgada": no construye botones ni tablas directamente,
solo ARMA la ventana juntando los widgets autosuficientes de
app.presentation.widgets y conecta sus senales entre si y con la capa
de aplicacion. Cada widget no sabe nada de los otros -- esta clase es
la unica que conoce a todos, y por eso es quien coordina.

La ventana llama a la capa de aplicacion (app.application) para cargar
archivos y correr el analisis -- nunca a domain/ ni a infrastructure/
directamente, con una sola excepcion deliberada:
app.infrastructure.workers.HiloAnalisis, porque un QThread es en si
mismo un detalle de como esta implementada ESTA interfaz (Qt).

CAMBIO DE ESTA VERSION: antes la navegacion era con pestanas arriba
(QTabWidget). Ahora es un menu lateral izquierdo (PanelNavegacion) que
sigue el flujo de trabajo pedido: Importar Datos -> Validar (K-K) ->
Explorar Espectros -> Modelar Circuito -> Evaluar Residuos ->
Interpretar y Pedagogia -> Generar Informe. Por dentro sigue siendo un
QStackedWidget (una sola pantalla que cambia) -- el menu lateral solo
decide cual pagina de ese stack se ve.

Nota sobre "dos graficas de Nyquist": el selector de circuito, el
diagrama y el simulador de parametros viven pegados a la grafica de
Nyquist (ver grafica_nyquist.py). Como "Explorar Espectros" (solo ver
curvas) y "Modelar Circuito" (elegir circuito y ajustar parametros)
ahora son pasos SEPARADOS del flujo, se usan DOS instancias de
PanelGraficaNyquist: self.panel_grafica_exploracion (solo lectura, sin
selector) para el paso 3, y self.panel_grafica (completo, con
selector+diagrama+parametros) para el paso 4 -- ambas reciben los
mismos datos y resultados, solo que se muestran en pasos distintos.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QTabWidget, QSplitter, QTextBrowser, QMessageBox, QFileDialog,
)
from PySide6.QtCore import Qt

from app.application import eis_service, export_service
from app.infrastructure.workers import HiloAnalisis
from app.presentation import textos_educativos
from app.presentation.widgets.panel_archivo import PanelArchivo
from app.presentation.widgets.panel_generador_sintetico import PanelGeneradorSintetico
from app.presentation.widgets.panel_navegacion import PanelNavegacion
from app.presentation.widgets.panel_validacion_kk import PanelValidacionKK
from app.presentation.widgets.grafica_nyquist import PanelGraficaNyquist
from app.presentation.widgets.grafica_bode import PanelGraficaBode
from app.presentation.widgets.tabla_resultados import PanelResultados
from app.presentation.widgets.panel_residuos import PanelResiduos
from app.presentation.widgets.panel_generar_informe import PanelGenerarInforme

import os
import tempfile

# Indices del stack -- se nombran para no repetir "numeros magicos"
# por todo el archivo, y para que quede claro que el ORDEN aqui debe
# coincidir con el orden de PASOS en panel_navegacion.py.
PASO_IMPORTAR = 0
PASO_VALIDAR_KK = 1
PASO_EXPLORAR = 2
PASO_MODELAR = 3
PASO_RESIDUOS = 4
PASO_APRENDER = 5
PASO_INFORME = 6


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "Analizador de EIS - Ajuste automatico de circuitos equivalentes"
        )
        self.resize(1400, 780)

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
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # --- Menu lateral (el "Flujo de Analisis" de la imagen) ---
        self.panel_navegacion = PanelNavegacion()
        self.panel_navegacion.paso_elegido.connect(self._al_elegir_paso)
        layout_principal.addWidget(self.panel_navegacion)

        # --- Widgets de contenido (uno por paso del flujo) ---
        self.panel_archivo = PanelArchivo()
        self.panel_archivo.archivo_elegido.connect(self._al_elegir_archivo)
        self.panel_archivo.analizar_solicitado.connect(self._iniciar_analisis)
        self.panel_archivo.exportar_solicitado.connect(self._exportar_reporte)

        self.panel_generador_sintetico = PanelGeneradorSintetico()
        self.panel_generador_sintetico.datos_generados.connect(
            self._al_generar_datos_sinteticos
        )

        self.panel_validacion_kk = PanelValidacionKK()

        # Version "solo lectura" (sin selector de circuito) para
        # Explorar Espectros -- ver la nota de arquitectura al inicio
        # del archivo.
        self.panel_grafica_exploracion = PanelGraficaNyquist(permitir_modelado=False)
        self.panel_bode = PanelGraficaBode()

        # Version completa (con selector+diagrama+parametros) para
        # Modelar Circuito.
        self.panel_grafica = PanelGraficaNyquist(permitir_modelado=True)
        self.panel_resultados = PanelResultados()

        self.panel_residuos = PanelResiduos()

        self.tab_aprender = QTextBrowser()
        self.tab_aprender.setHtml(textos_educativos.TEXTO_APRENDER_HTML)

        self.panel_generar_informe = PanelGenerarInforme()
        self.panel_generar_informe.exportar_solicitado.connect(self._exportar_reporte)

        # --- Paso 1: Importar Datos = archivo real + generador
        # didactico de datos sinteticos, en pestanas internas (mismo
        # patron que la pagina de Explorar Espectros mas abajo). ---
        pagina_importar = QTabWidget()
        pagina_importar.addTab(self.panel_archivo, "📁  Importar Archivo Real")
        pagina_importar.addTab(
            self.panel_generador_sintetico, "🧪  Generador Didactico (Sintetico)"
        )

        # --- Paso 3: Explorar Espectros = Nyquist + Bode en pestanas
        # internas (aqui SI usamos un QTabWidget chico, nada mas para
        # alternar entre las dos vistas del mismo dato -- no tiene
        # relacion con el flujo general de la izquierda). ---
        pagina_explorar = QTabWidget()
        pagina_explorar.addTab(self.panel_grafica_exploracion, "Nyquist")
        pagina_explorar.addTab(self.panel_bode, "Bode")

        # --- Paso 4: Modelar Circuito = grafica+selector+parametros
        # (arriba) + tabla comparativa de circuitos (abajo), en un
        # splitter para que se pueda ajustar cuanto espacio ocupa cada
        # parte. ---
        pagina_modelar = QWidget()
        layout_modelar = QVBoxLayout(pagina_modelar)
        layout_modelar.setContentsMargins(4, 4, 4, 4)
        splitter_modelar = QSplitter(Qt.Vertical)
        splitter_modelar.addWidget(self.panel_grafica)
        splitter_modelar.addWidget(self.panel_resultados)
        splitter_modelar.setStretchFactor(0, 3)
        splitter_modelar.setStretchFactor(1, 2)
        layout_modelar.addWidget(splitter_modelar)

        # --- Stack: una sola pantalla visible a la vez, en el MISMO
        # orden que panel_navegacion.PASOS. ---
        self.stack = QStackedWidget()
        self.stack.addWidget(pagina_importar)              # 0 Importar Datos
        self.stack.addWidget(self.panel_validacion_kk)     # 1 Validar (K-K)
        self.stack.addWidget(pagina_explorar)              # 2 Explorar Espectros
        self.stack.addWidget(pagina_modelar)               # 3 Modelar Circuito
        self.stack.addWidget(self.panel_residuos)          # 4 Evaluar Residuos
        self.stack.addWidget(self.tab_aprender)            # 5 Interpretar y Pedagogia
        self.stack.addWidget(self.panel_generar_informe)   # 6 Generar Informe

        layout_principal.addWidget(self.stack, stretch=1)

        self.panel_navegacion.seleccionar_paso(PASO_IMPORTAR)

    # ------------------------------------------------------------------
    # Navegacion
    # ------------------------------------------------------------------
    def _al_elegir_paso(self, indice):
        self.stack.setCurrentIndex(indice)

    def _ir_al_paso(self, indice):
        """Cambia de pantalla POR CODIGO (ej. al terminar un analisis) y
        refleja el cambio en el menu, sin que eso dispare de nuevo
        _al_elegir_paso (ver PanelNavegacion.seleccionar_paso)."""
        self.stack.setCurrentIndex(indice)
        self.panel_navegacion.seleccionar_paso(indice)

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
        self.panel_archivo.mostrar_archivo_cargado(
            os.path.basename(ruta), ruta, len(frecuencias)
        )
        self._distribuir_datos_nuevos(frecuencias, Z)

    def _al_generar_datos_sinteticos(self, frecuencias, Z, descripcion):
        """
        Igual que _al_elegir_archivo, pero el origen de los datos es el
        Generador Didactico (ver panel_generador_sintetico.py) en vez
        de un archivo real -- de aqui en adelante, la aplicacion no
        distingue entre los dos: ambos entran a la MISMA tuberia de
        analisis.
        """
        self.ruta_archivo = None  # no hay archivo real que reportar en el PDF
        self.panel_archivo.mostrar_archivo_cargado(descripcion, "", len(frecuencias))
        self._distribuir_datos_nuevos(frecuencias, Z)

    def _distribuir_datos_nuevos(self, frecuencias, Z):
        """Un conjunto de datos nuevo (venga de un archivo real o del
        generador sintetico) invalida cualquier resultado anterior --
        se avisa a TODAS las paginas que dependen de datos/resultados."""
        self.frecuencias_cargadas = frecuencias
        self.Z_cargada = Z
        self.ultimo_resultado = None

        self.panel_validacion_kk.limpiar()
        self.panel_grafica_exploracion.mostrar_datos_crudos(frecuencias, Z)
        self.panel_bode.mostrar_datos_crudos(frecuencias, Z)
        self.panel_grafica.mostrar_datos_crudos(frecuencias, Z)
        self.panel_residuos.mostrar_datos_crudos(frecuencias, Z)
        self.panel_generar_informe.habilitar(False)

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
        self.panel_validacion_kk.mostrar(resultado)
        self.panel_resultados.mostrar(resultado)
        self.panel_grafica_exploracion.mostrar_resultados(resultado)
        self.panel_bode.mostrar_resultados(resultado)
        self.panel_grafica.mostrar_resultados(resultado)
        self.panel_residuos.mostrar_resultados(resultado)

        hay_reporte_posible = len(resultado.mejores) > 0
        self.panel_archivo.habilitar_exportar(hay_reporte_posible)
        self.panel_generar_informe.habilitar(hay_reporte_posible)

        # Al terminar, se avanza automaticamente al siguiente paso
        # logico del flujo (validar los datos) -- el usuario sigue
        # pudiendo moverse libremente por el menu desde ahi.
        self._ir_al_paso(PASO_VALIDAR_KK)

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

                ruta_imagen_bode = os.path.join(carpeta_temporal, "grafica_bode.png")
                self.panel_bode.guardar_grafica_como_imagen(ruta_imagen_bode)

                export_service.exportar_reporte_pdf(
                    self.ultimo_resultado,
                    ruta_salida,
                    nombre_archivo_datos=os.path.basename(self.ruta_archivo or ""),
                    ruta_imagen_grafica=ruta_imagen,
                    ruta_imagen_bode=ruta_imagen_bode,
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