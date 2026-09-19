# -*- coding: utf-8 -*-
"""
Widget "Generador Didactico": permite elegir uno de los circuitos ya
existentes en la biblioteca, ajustar sus parametros, y generar un
archivo de datos SINTETICO (con ruido controlado) que entra a la misma
tuberia de analisis que un archivo real -- pensado para que un
estudiante genere un caso con "respuesta correcta" conocida de
antemano y luego compare si el analisis automatico la recupera.

Decision de diseno clave: la VISTA PREVIA (el canvas de la izquierda)
SIEMPRE dibuja la curva TEORICA/LIMPIA -- se redibuja al vuelo cada vez
que se cambia un parametro, el circuito o el rango de frecuencias, sin
generar ningun numero aleatorio todavia. Solo al dar clic en "Generar
y Cargar" se agrega el ruido (una sola vez, con la semilla que el
usuario haya puesto o una aleatoria) y se manda la senal
datos_generados con el resultado -- asi el usuario ve COMO SE VERIA su
circuito antes de comprometerse con una version ruidosa en particular.

Por que un widget nuevo y no reutilizar el simulador de parametros que
ya vive en grafica_nyquist.py: ese simulador siempre necesita datos YA
cargados (compara tu simulacion contra algo medido). Aqui es al reves:
todavia no hay ningun dato, el circuito y sus parametros SON el punto
de partida. Combinarlos hubiera significado llenar ese widget de
condicionales ("si hay datos cargados... si no...") -- se prefirio
un widget chico y enfocado, aunque repita un poco de codigo (mismo
criterio que ya se uso para permitir_modelado en grafica_nyquist.py).
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QGroupBox, QSplitter,
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from app.application import synthetic_data_service
from app.domain import circuits as domain_circuits
from app.domain import impedance as domain_impedance
from app.presentation import textos_educativos
from app.presentation.widgets import circuit_diagram


class PanelGeneradorSintetico(QWidget):
    # Se emite con (frecuencias, Z_con_ruido, descripcion) cuando el
    # usuario da clic en "Generar y Cargar Datos". descripcion es un
    # texto corto para mostrar en vez de un nombre de archivo (ej.
    # "Datos sinteticos: Randles con CPE").
    datos_generados = Signal(object, object, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._inputs_parametros = {}   # indice -> QLineEdit
        self._nombre_actual = None
        self._construir_ui()
        self._al_cambiar_circuito()

    # ------------------------------------------------------------------
    def _construir_ui(self):
        layout_general = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # --- Columna izquierda: controles ---
        columna_izquierda = QWidget()
        layout_izq = QVBoxLayout(columna_izquierda)

        fila_combo = QHBoxLayout()
        fila_combo.addWidget(QLabel("Circuito a simular:"))
        self.combo_circuito = QComboBox()
        for nombre in domain_circuits.CIRCUITOS:
            self.combo_circuito.addItem(
                textos_educativos.nombre_bonito(nombre), nombre
            )
        self.combo_circuito.currentIndexChanged.connect(self._al_cambiar_circuito)
        fila_combo.addWidget(self.combo_circuito, stretch=1)
        layout_izq.addLayout(fila_combo)

        # Franja de diagrama + formula (misma idea que en
        # grafica_nyquist.py, para que el usuario reconozca de
        # inmediato que circuito eligio).
        fila_info = QHBoxLayout()
        self.figura_diagrama = Figure(figsize=(2.2, 1.4))
        self.ax_diagrama = self.figura_diagrama.add_subplot(111)
        self.canvas_diagrama = FigureCanvasQTAgg(self.figura_diagrama)
        self.canvas_diagrama.setFixedSize(200, 130)
        fila_info.addWidget(self.canvas_diagrama)
        self.label_formula = QLabel()
        self.label_formula.setTextFormat(Qt.RichText)
        self.label_formula.setWordWrap(True)
        self.label_formula.setStyleSheet(
            "padding: 4px 8px; background-color: #f7f7f7; border-radius: 4px;"
        )
        fila_info.addWidget(self.label_formula, stretch=1)
        layout_izq.addLayout(fila_info)

        # Parametros electroquimicos editables.
        grupo_parametros = QGroupBox("Parametros del circuito")
        layout_parametros = QVBoxLayout(grupo_parametros)
        self.grid_parametros = QGridLayout()
        self.grid_parametros.setHorizontalSpacing(10)
        layout_parametros.addLayout(self.grid_parametros)
        boton_restablecer = QPushButton("Restablecer valores tipicos")
        boton_restablecer.clicked.connect(self._restablecer_parametros)
        layout_parametros.addWidget(boton_restablecer)
        layout_izq.addWidget(grupo_parametros)

        # Rango de frecuencias y ruido -- los "artefactos" del barrido.
        grupo_muestreo = QGroupBox("Ventana espectral, muestreo y ruido")
        layout_muestreo = QGridLayout(grupo_muestreo)
        layout_muestreo.addWidget(QLabel("Frecuencia inicial (Hz):"), 0, 0)
        self.input_f_inicial = QLineEdit("100000")
        layout_muestreo.addWidget(self.input_f_inicial, 0, 1)
        layout_muestreo.addWidget(QLabel("Frecuencia final (Hz):"), 0, 2)
        self.input_f_final = QLineEdit("0.01")
        layout_muestreo.addWidget(self.input_f_final, 0, 3)
        layout_muestreo.addWidget(QLabel("Puntos por decada:"), 1, 0)
        self.input_puntos_decada = QLineEdit("10")
        layout_muestreo.addWidget(self.input_puntos_decada, 1, 1)
        layout_muestreo.addWidget(QLabel("Ruido gaussiano (% RMS):"), 1, 2)
        self.input_ruido = QLineEdit("1.0")
        layout_muestreo.addWidget(self.input_ruido, 1, 3)
        for entrada in (self.input_f_inicial, self.input_f_final,
                        self.input_puntos_decada, self.input_ruido):
            entrada.editingFinished.connect(self._redibujar_vista_previa)
        layout_izq.addWidget(grupo_muestreo)

        self.label_error = QLabel()
        self.label_error.setStyleSheet("color: #c1121f; font-size: 11px;")
        self.label_error.setWordWrap(True)
        layout_izq.addWidget(self.label_error)

        self.boton_generar = QPushButton("⚡ Generar y Cargar Datos")
        self.boton_generar.setMinimumHeight(36)
        self.boton_generar.setStyleSheet(
            "font-weight: bold; background-color: #1a5bb8; color: white;"
        )
        self.boton_generar.clicked.connect(self._al_generar)
        layout_izq.addWidget(self.boton_generar)
        layout_izq.addStretch()

        # --- Columna derecha: vista previa (Nyquist) ---
        columna_derecha = QWidget()
        layout_der = QVBoxLayout(columna_derecha)
        layout_der.addWidget(QLabel(
            "<b>Vista previa</b> -- asi se veria la curva de este "
            "circuito, ANTES de generar el archivo con ruido:"
        ))
        self.figura_preview = Figure(figsize=(5, 5))
        self.ax_preview = self.figura_preview.add_subplot(111)
        self.canvas_preview = FigureCanvasQTAgg(self.figura_preview)
        layout_der.addWidget(self.canvas_preview, stretch=1)

        splitter.addWidget(columna_izquierda)
        splitter.addWidget(columna_derecha)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        layout_general.addWidget(splitter)

    # ------------------------------------------------------------------
    # Circuito elegido: refresca diagrama, formula, y campos de
    # parametros con los valores tipicos de domain/circuits.py.
    # ------------------------------------------------------------------
    def _al_cambiar_circuito(self):
        self._nombre_actual = self.combo_circuito.currentData()
        if self._nombre_actual is None:
            return

        circuit_diagram.dibujar_diagrama(self.ax_diagrama, self._nombre_actual)
        self.figura_diagrama.tight_layout()
        self.canvas_diagrama.draw_idle()

        formula = domain_circuits.FORMULAS_HTML.get(self._nombre_actual, "")
        self.label_formula.setText(
            f"<b>{textos_educativos.nombre_bonito(self._nombre_actual)}</b>"
            f"<br>{formula}"
        )

        self._restablecer_parametros()

    def _restablecer_parametros(self):
        if self._nombre_actual is None:
            return

        while self.grid_parametros.count():
            item = self.grid_parametros.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._inputs_parametros = {}

        nombres_parametros = domain_circuits.CIRCUITOS[self._nombre_actual].parametros
        valores = domain_circuits.valores_por_defecto(self._nombre_actual)

        columnas_por_fila = 2
        for i, nombre_parametro in enumerate(nombres_parametros):
            fila = i // columnas_por_fila
            col_base = (i % columnas_por_fila) * 2

            etiqueta = QLabel(
                textos_educativos.nombre_parametro_bonito(nombre_parametro) + ":"
            )
            entrada = QLineEdit(f"{valores[i]:.6g}")
            entrada.editingFinished.connect(self._redibujar_vista_previa)

            self.grid_parametros.addWidget(etiqueta, fila, col_base)
            self.grid_parametros.addWidget(entrada, fila, col_base + 1)
            self._inputs_parametros[i] = entrada

        self._redibujar_vista_previa()

    # ------------------------------------------------------------------
    def _leer_valores_parametros(self):
        """Devuelve la lista de valores actuales de los campos, o None
        si alguno no es un numero valido (y marca ese campo en rojo)."""
        valores = []
        todo_valido = True
        for i in sorted(self._inputs_parametros):
            entrada = self._inputs_parametros[i]
            texto = entrada.text().strip().replace(",", ".")
            try:
                valor = float(texto)
                entrada.setStyleSheet("")
                valores.append(valor)
            except ValueError:
                entrada.setStyleSheet("background-color: #fde2e2;")
                todo_valido = False
        return valores if todo_valido else None

    def _leer_ventana_frecuencias(self):
        try:
            f_inicial = float(self.input_f_inicial.text().strip().replace(",", "."))
            f_final = float(self.input_f_final.text().strip().replace(",", "."))
            puntos_por_decada = int(float(
                self.input_puntos_decada.text().strip().replace(",", ".")
            ))
            ruido_pct = float(self.input_ruido.text().strip().replace(",", "."))
        except ValueError:
            return None
        return f_inicial, f_final, puntos_por_decada, ruido_pct

    # ------------------------------------------------------------------
    # Vista previa: SOLO la curva teorica, sin ruido -- se redibuja al
    # vuelo con cada cambio, sin generar ningun numero aleatorio.
    # ------------------------------------------------------------------
    def _redibujar_vista_previa(self, Z_con_ruido=None):
        self.label_error.setText("")
        ax = self.ax_preview
        ax.clear()

        valores = self._leer_valores_parametros()
        ventana = self._leer_ventana_frecuencias()
        if valores is None or ventana is None or self._nombre_actual is None:
            ax.axis("off")
            ax.text(
                0.5, 0.5, "Revisa que todos los campos tengan numeros validos.",
                ha="center", va="center", transform=ax.transAxes, color="#a33",
                wrap=True,
            )
            self.canvas_preview.draw_idle()
            return

        f_inicial, f_final, puntos_por_decada, _ruido_pct = ventana
        try:
            frecuencias = synthetic_data_service.generar_frecuencias(
                f_inicial, f_final, puntos_por_decada
            )
            Z_teorico = domain_impedance.calcular_impedancia_con_parametros(
                self._nombre_actual, frecuencias, valores
            )
        except Exception as e:
            ax.axis("off")
            ax.text(
                0.5, 0.5, f"No se pudo calcular la curva:\n{e}",
                ha="center", va="center", transform=ax.transAxes, color="#a33",
                wrap=True,
            )
            self.canvas_preview.draw_idle()
            return

        ax.axis("on")
        ax.plot(
            Z_teorico.real, -Z_teorico.imag, "-", color="darkorange", linewidth=2,
            label="Curva teorica (sin ruido)",
        )
        if Z_con_ruido is not None:
            ax.plot(
                Z_con_ruido.real, -Z_con_ruido.imag, "o", color="#2c5f8a",
                markersize=4, alpha=0.7, label="Datos sinteticos generados",
            )
        ax.set_xlabel("Z' (Ohms)")
        ax.set_ylabel("-Z'' (Ohms)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        self.figura_preview.tight_layout()
        self.canvas_preview.draw_idle()

    # ------------------------------------------------------------------
    def _al_generar(self):
        self.label_error.setText("")
        valores = self._leer_valores_parametros()
        ventana = self._leer_ventana_frecuencias()
        if valores is None or ventana is None or self._nombre_actual is None:
            self.label_error.setText(
                "Revisa que todos los campos tengan numeros validos antes "
                "de generar."
            )
            return

        f_inicial, f_final, puntos_por_decada, ruido_pct = ventana
        try:
            frecuencias, Z_teorico, Z_con_ruido = (
                synthetic_data_service.generar_datos_sinteticos(
                    self._nombre_actual, valores, f_inicial, f_final,
                    puntos_por_decada=puntos_por_decada,
                    ruido_relativo=max(ruido_pct, 0) / 100.0,
                )
            )
        except synthetic_data_service.ErrorGeneracionSintetica as e:
            self.label_error.setText(str(e))
            return

        self._redibujar_vista_previa(Z_con_ruido=Z_con_ruido)

        descripcion = (
            f"Datos sinteticos: {textos_educativos.nombre_bonito(self._nombre_actual)}"
        )
        self.datos_generados.emit(frecuencias, Z_con_ruido, descripcion)