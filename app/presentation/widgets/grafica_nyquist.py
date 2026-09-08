# -*- coding: utf-8 -*-
"""
Pestana "Grafica de Nyquist": el selector de circuito, la grafica
interactiva (clic en un punto resalta su fila en la tabla, y
viceversa), la tabla de datos crudos, y la franja de diagrama+formula
del circuito elegido.

Es el widget mas grande de la interfaz, y a proposito NO esta partido
en piezas mas pequenas: la grafica, la tabla y el panel de
diagrama/formula necesitan avisarse cosas constantemente entre si
(seleccionar un punto en cualquiera de los dos lados debe reflejarse
en el otro), y partirlos en archivos distintos obligaria a pasar
mensajes de un lado a otro sin ninguna ganancia real -- en la practica
son una sola pieza de interfaz con varias vistas del mismo dato.

Decision de diseno importante: la grafica de Nyquist es un UNICO
lienzo (Figure/Canvas) que se crea UNA sola vez y se REDIBUJA cuando
hace falta (cambiar de circuito, cargar un archivo, terminar un
analisis), en vez de crear una figura nueva cada vez -- eso era lo que
se sentia lento en una version anterior (crear widgets de Qt y
renderizar formulas en LaTeX tiene un costo real).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QGroupBox, QLineEdit, QPushButton,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from app.domain import circuits as domain_circuits
from app.domain import impedance as domain_impedance
from app.presentation import textos_educativos
from app.presentation.widgets import circuit_diagram


class PanelGraficaNyquist(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Estado propio de este widget (la ventana principal no
        # necesita saber nada de esto).
        self.frecuencias_cargadas = None
        self.Z_cargada = None
        self.ultimo_resultado = None      # app.domain.models.ResultadoAnalisis
        self._linea_datos = None          # la linea "clicable" de la grafica actual
        self._marcador_seleccion = None   # circulo rojo que resalta el punto elegido
        self._indice_seleccionado = None  # persiste al cambiar de circuito, para
                                           # poder comparar como le va a ESE punto
                                           # en cada modelo
        self._sincronizando = False       # evita bucles infinitos tabla <-> grafica
        self._valores_parametros = {}     # nombre_circuito -> [valores editables]
        self._inputs_parametros = {}      # indice -> QLineEdit del circuito ACTUAL

        self._construir_ui()
        self._redibujar_grafica_principal()  # estado inicial (sin datos todavia)

    # ------------------------------------------------------------------
    # API publica: la ventana principal llama a estos metodos cuando
    # cambia el archivo cargado o terminan los resultados del analisis.
    # ------------------------------------------------------------------
    def mostrar_datos_crudos(self, frecuencias, Z):
        self.frecuencias_cargadas = frecuencias
        self.Z_cargada = Z
        self._indice_seleccionado = None
        self.ultimo_resultado = None
        self._valores_parametros = {}  # un archivo nuevo invalida cualquier
                                        # simulacion manual del archivo anterior
        self._llenar_tabla_datos(frecuencias, Z)
        self._al_cambiar_circuito_grafica()

    def mostrar_resultados(self, resultado):
        self.ultimo_resultado = resultado
        # Un analisis nuevo invalida las simulaciones manuales previas:
        # asi, la proxima vez que se muestren los parametros de un
        # circuito, arrancan de nuevo desde los valores YA AJUSTADOS
        # (mas utiles como punto de partida que la estimacion inicial
        # cruda que se usaba antes de analizar).
        self._valores_parametros = {}
        # Reutilizamos el mismo manejador del selector: ya sabe redibujar
        # la grafica y refrescar el panel de diagrama/formula segun lo
        # que este elegido en el combo.
        self._al_cambiar_circuito_grafica()

    def limpiar(self):
        self.frecuencias_cargadas = None
        self.Z_cargada = None
        self.ultimo_resultado = None
        self._indice_seleccionado = None
        self._valores_parametros = {}
        self.tabla_datos.setRowCount(0)
        self._redibujar_grafica_principal()

    def guardar_grafica_como_imagen(self, ruta, dpi=150):
        """Guarda la grafica de Nyquist TAL COMO SE VE ahora mismo (con
        cualquier curva que este mostrando: modo automatico o un
        circuito especifico) como un archivo de imagen -- pensado para
        incluirla en el reporte PDF, pero es un metodo de proposito
        general, no sabe nada de PDFs."""
        self.figura_nyquist.savefig(ruta, dpi=dpi, bbox_inches="tight")

    # ------------------------------------------------------------------
    # Construccion de la interfaz
    # ------------------------------------------------------------------
    def _construir_ui(self):
        layout_general = QVBoxLayout(self)

        # --- Selector de circuito ---
        fila_combo = QHBoxLayout()
        fila_combo.addWidget(QLabel("Circuito a mostrar:"))
        self.combo_circuito_grafica = QComboBox()
        self.combo_circuito_grafica.addItem("Automatico (mejores 3)", None)
        for nombre in domain_circuits.CIRCUITOS:
            self.combo_circuito_grafica.addItem(
                textos_educativos.nombre_bonito(nombre), nombre
            )
        self.combo_circuito_grafica.currentIndexChanged.connect(
            self._al_cambiar_circuito_grafica
        )
        fila_combo.addWidget(self.combo_circuito_grafica)
        fila_combo.addStretch()
        layout_general.addLayout(fila_combo)

        # --- Franja compacta: diagrama pequeno + formula (se agrega al
        # layout DESPUES de la grafica y la tabla, mas abajo, para que
        # quede debajo de ambas) ---
        self.panel_info_circuito = QWidget()
        fila_info = QHBoxLayout(self.panel_info_circuito)
        fila_info.setContentsMargins(0, 4, 0, 4)

        self.figura_diagrama_mini = Figure(figsize=(2.4, 1.5))
        self.ax_diagrama_mini = self.figura_diagrama_mini.add_subplot(111)
        self.canvas_diagrama_mini = FigureCanvasQTAgg(self.figura_diagrama_mini)
        self.canvas_diagrama_mini.setFixedSize(220, 140)
        fila_info.addWidget(self.canvas_diagrama_mini)

        self.texto_formula_mini = QLabel()
        self.texto_formula_mini.setTextFormat(Qt.RichText)
        self.texto_formula_mini.setWordWrap(True)
        self.texto_formula_mini.setStyleSheet(
            "padding: 4px 10px; background-color: #f7f7f7; border-radius: 4px;"
        )
        fila_info.addWidget(self.texto_formula_mini, stretch=1)
        self.panel_info_circuito.setVisible(False)

        # --- Panel de parametros editables: "simulador" manual ---
        self.panel_parametros = QGroupBox("Simula: ajusta los parametros y observa")
        layout_parametros = QVBoxLayout(self.panel_parametros)

        self.label_explicacion_parametros = QLabel()
        self.label_explicacion_parametros.setWordWrap(True)
        self.label_explicacion_parametros.setStyleSheet(
            "color: #555; font-size: 11px;"
        )
        layout_parametros.addWidget(self.label_explicacion_parametros)

        self.grid_parametros = QGridLayout()
        self.grid_parametros.setHorizontalSpacing(10)
        layout_parametros.addLayout(self.grid_parametros)

        self.label_error_simulacion = QLabel()
        self.label_error_simulacion.setWordWrap(True)
        self.label_error_simulacion.setStyleSheet(
            "padding: 4px 2px; font-size: 12px;"
        )
        layout_parametros.addWidget(self.label_error_simulacion)

        fila_botones_parametros = QHBoxLayout()
        self.boton_restablecer_parametros = QPushButton("Restablecer valores")
        self.boton_restablecer_parametros.clicked.connect(
            self._restablecer_parametros_actuales
        )
        fila_botones_parametros.addWidget(self.boton_restablecer_parametros)
        fila_botones_parametros.addStretch()
        layout_parametros.addLayout(fila_botones_parametros)

        self.panel_parametros.setVisible(False)

        # --- Grafica (izquierda) + tabla de datos (derecha) ---
        splitter = QSplitter(Qt.Horizontal)

        contenedor_grafica = QWidget()
        layout_grafica = QVBoxLayout(contenedor_grafica)
        layout_grafica.setContentsMargins(0, 0, 0, 0)
        self.figura_nyquist = Figure(figsize=(6, 5))
        self.ax_nyquist = self.figura_nyquist.add_subplot(111)
        self.canvas_nyquist = FigureCanvasQTAgg(self.figura_nyquist)
        self.canvas_nyquist.mpl_connect("pick_event", self._al_hacer_clic_en_grafica)
        layout_grafica.addWidget(self.canvas_nyquist)

        panel_datos = QWidget()
        layout_datos = QVBoxLayout(panel_datos)
        layout_datos.addWidget(QLabel("<b>Datos cargados del archivo</b>"))

        self.label_ayuda_tabla = QLabel(
            "Al cargar un archivo, sus datos apareceran aqui. Haz clic en "
            "un punto de la grafica (o en una fila de esta tabla) para "
            "resaltar el dato correspondiente en ambos lados."
        )
        self.label_ayuda_tabla.setWordWrap(True)
        self.label_ayuda_tabla.setStyleSheet("color: #666; font-size: 11px;")
        layout_datos.addWidget(self.label_ayuda_tabla)

        self.tabla_datos = QTableWidget(0, 4)
        self.tabla_datos.setHorizontalHeaderLabels(["#", "f (Hz)", "Z'", "Z''"])
        self.tabla_datos.horizontalHeaderItem(1).setToolTip("Frecuencia (Hz)")
        self.tabla_datos.horizontalHeaderItem(2).setToolTip("Parte real de Z (Ohms)")
        self.tabla_datos.horizontalHeaderItem(3).setToolTip("Parte imaginaria de Z (Ohms)")
        self.tabla_datos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_datos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_datos.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_datos.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tabla_datos.itemSelectionChanged.connect(self._al_seleccionar_fila_tabla)
        layout_datos.addWidget(self.tabla_datos, stretch=1)

        splitter.addWidget(contenedor_grafica)
        splitter.addWidget(panel_datos)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([700, 420])

        layout_general.addWidget(splitter, stretch=1)
        layout_general.addWidget(self.panel_info_circuito)
        layout_general.addWidget(self.panel_parametros)

    def _llenar_tabla_datos(self, frecuencias, Z):
        self._sincronizando = True
        try:
            self.tabla_datos.setRowCount(len(frecuencias))
            for fila in range(len(frecuencias)):
                valores = [
                    str(fila + 1),
                    f"{frecuencias[fila]:.4g}",
                    f"{Z.real[fila]:.4g}",
                    f"{Z.imag[fila]:.4g}",
                ]
                for col, texto in enumerate(valores):
                    item = QTableWidgetItem(texto)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.tabla_datos.setItem(fila, col, item)
        finally:
            self._sincronizando = False

    # ------------------------------------------------------------------
    # Circuito elegido para explorar sobre la grafica
    # ------------------------------------------------------------------
    def _al_cambiar_circuito_grafica(self):
        nombre = self.combo_circuito_grafica.currentData()
        if nombre is None:
            self.panel_info_circuito.setVisible(False)
            self.panel_parametros.setVisible(False)
        else:
            self._actualizar_info_circuito_mini(nombre)
            self.panel_info_circuito.setVisible(True)
            if self.frecuencias_cargadas is not None:
                self._mostrar_panel_parametros(nombre)
            else:
                self.panel_parametros.setVisible(False)
        self._redibujar_grafica_principal()

    def _actualizar_info_circuito_mini(self, nombre):
        # Dibujar el diagrama es barato (son solo cajas y lineas, sin
        # notacion matematica), asi que se puede redibujar cada vez sin
        # que se sienta lento -- y como reutilizamos el MISMO canvas,
        # tampoco hay costo de crear/destruir widgets de Qt.
        circuit_diagram.dibujar_diagrama(self.ax_diagrama_mini, nombre)
        self.figura_diagrama_mini.tight_layout()
        self.canvas_diagrama_mini.draw_idle()

        formula = domain_circuits.FORMULAS_HTML.get(nombre, "")
        descripcion = textos_educativos.DESCRIPCION_CIRCUITOS.get(nombre, "")
        self.texto_formula_mini.setText(
            f"<b>{textos_educativos.nombre_bonito(nombre)}</b> &nbsp; {formula}"
            f"<br><span style='color:#555; font-size:11px;'>{descripcion}</span>"
        )

    def _buscar_resultado_circuito(self, nombre):
        if self.ultimo_resultado is None:
            return None
        return self.ultimo_resultado.buscar_circuito(nombre)

    # ------------------------------------------------------------------
    # Panel de parametros editables ("simulador" manual, sin re-ajustar)
    # ------------------------------------------------------------------
    def _obtener_valores_parametros(self, nombre):
        """Devuelve la lista de valores ACTUAL para un circuito (la que
        se ve en los campos editables). La primera vez que se pide para
        un circuito dado, se inicializa con los valores ya ajustados (si
        el archivo ya se analizo) o, si no, con la estimacion geometrica
        inicial -- asi siempre hay un punto de partida razonable, nunca
        ceros arbitrarios."""
        if nombre in self._valores_parametros:
            return self._valores_parametros[nombre]

        resultado_circuito = self._buscar_resultado_circuito(nombre)
        if resultado_circuito is not None and resultado_circuito.circuit is not None:
            valores = list(resultado_circuito.circuit.parameters_)
        else:
            valores = domain_impedance.estimar_valores_iniciales(
                nombre, self.frecuencias_cargadas, self.Z_cargada
            )
        self._valores_parametros[nombre] = valores
        return valores

    def _mostrar_panel_parametros(self, nombre):
        self.label_explicacion_parametros.setText(
            textos_educativos.texto_como_se_obtienen_parametros().replace("\n", "<br>")
        )

        # Limpiar los campos del circuito anterior antes de construir
        # los nuevos (cada circuito tiene una cantidad distinta de
        # parametros).
        while self.grid_parametros.count():
            item = self.grid_parametros.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._inputs_parametros = {}

        nombres_parametros = domain_circuits.CIRCUITOS[nombre].parametros
        valores = self._obtener_valores_parametros(nombre)

        columnas_por_fila = 2
        for i, nombre_parametro in enumerate(nombres_parametros):
            fila = i // columnas_por_fila
            col_base = (i % columnas_por_fila) * 2

            etiqueta = QLabel(
                textos_educativos.nombre_parametro_bonito(nombre_parametro) + ":"
            )
            regla = textos_educativos.REGLAS_PARAMETRO.get(nombre_parametro, "")
            etiqueta.setToolTip(regla)

            entrada = QLineEdit(f"{valores[i]:.6g}")
            entrada.setToolTip(regla)
            entrada.editingFinished.connect(
                lambda idx=i, nombre_c=nombre: self._al_editar_parametro(nombre_c, idx)
            )

            self.grid_parametros.addWidget(etiqueta, fila, col_base)
            self.grid_parametros.addWidget(entrada, fila, col_base + 1)
            self._inputs_parametros[i] = entrada

        self.panel_parametros.setVisible(True)

    def _al_editar_parametro(self, nombre, indice):
        entrada = self._inputs_parametros.get(indice)
        if entrada is None:
            return
        texto = entrada.text().strip().replace(",", ".")
        try:
            valor = float(texto)
        except ValueError:
            # Entrada invalida (texto que no es un numero): se marca en
            # rojo suave y NO se redibuja nada -- mejor eso que
            # tronar o simular con un valor inventado.
            entrada.setStyleSheet("background-color: #fde2e2;")
            return

        entrada.setStyleSheet("")
        valores = self._valores_parametros.setdefault(
            nombre, self._obtener_valores_parametros(nombre)
        )
        valores[indice] = valor
        self._redibujar_grafica_principal()

    def _restablecer_parametros_actuales(self):
        nombre = self.combo_circuito_grafica.currentData()
        if nombre is None:
            return
        self._valores_parametros.pop(nombre, None)
        self._mostrar_panel_parametros(nombre)
        self._redibujar_grafica_principal()

    def _actualizar_indicador_error(self, error_manual_pct, error_ajuste_pct):
        """
        Arma el texto que compara, en porcentaje, que tan lejos esta tu
        simulacion manual de los datos reales -- y si existe un ajuste
        real para comparar, lo pone al lado para que sea evidente que
        tan cerca (o lejos) estas del resultado del optimizador.
        """
        if error_manual_pct is None:
            self.label_error_simulacion.setText("")
            return

        # Color segun que tan lejos esta (esto es solo una guia visual
        # rapida, no un umbral cientifico riguroso).
        if error_manual_pct < 5:
            color = "#1a7f37"  # verde: muy cerca de los datos
        elif error_manual_pct < 20:
            color = "#9a6700"  # ambar: razonablemente cerca
        else:
            color = "#c1121f"  # rojo: bastante lejos

        texto = (
            f"<span style='color:{color}; font-weight:bold;'>"
            f"Tu simulacion se aleja en promedio un {error_manual_pct:.1f}% "
            f"de tus datos reales.</span>"
        )

        if error_ajuste_pct is not None:
            texto += (
                f" El ajuste real (linea solida) se aleja solo un "
                f"{error_ajuste_pct:.1f}%."
            )
            if error_manual_pct > 0 and error_ajuste_pct > 0:
                veces = error_manual_pct / error_ajuste_pct
                if veces > 1.05:
                    texto += f" (tu simulacion tiene {veces:.1f}x mas error)."

        self.label_error_simulacion.setText(texto)

    # ------------------------------------------------------------------
    # Grafica de Nyquist (un solo lienzo persistente, se REDIBUJA)
    # ------------------------------------------------------------------
    def _redibujar_grafica_principal(self):
        ax = self.ax_nyquist
        ax.clear()
        self._marcador_seleccion = None

        if self.Z_cargada is None:
            ax.axis("off")
            ax.text(
                0.5, 0.5,
                "Aqui aparecera la grafica de Nyquist al cargar un "
                "archivo.\n\nPodras hacer clic sobre un punto para ver a "
                "que dato del archivo corresponde.",
                ha="center", va="center", transform=ax.transAxes,
                color="#888", wrap=True,
            )
            self._linea_datos = None
            self.canvas_nyquist.draw_idle()
            return

        ax.axis("on")
        Z = self.Z_cargada
        (self._linea_datos,) = ax.plot(
            Z.real, -Z.imag, "o", picker=5, label="Datos experimentales"
        )

        nombre_elegido = self.combo_circuito_grafica.currentData()
        if nombre_elegido is None:
            # Modo automatico: las mejores curvas que encontro el
            # analisis (si ya se corrio uno).
            self.label_error_simulacion.setText("")
            if self.ultimo_resultado is not None:
                for r in self.ultimo_resultado.mejores:
                    Z_ajuste = r.circuit.predict(self.frecuencias_cargadas)
                    ax.plot(
                        Z_ajuste.real, -Z_ajuste.imag, "-",
                        label=textos_educativos.nombre_bonito(r.nombre),
                    )
        else:
            # Modo "explorar un circuito especifico": se dibuja el
            # ajuste real (si existe) Y la simulacion manual con los
            # valores de los campos editables, para poder comparar
            # ambas directamente sobre los mismos datos.
            error_ajuste_pct = None
            error_manual_pct = None

            resultado_circuito = self._buscar_resultado_circuito(nombre_elegido)
            if resultado_circuito is not None and resultado_circuito.circuit is not None:
                Z_ajuste = resultado_circuito.circuit.predict(self.frecuencias_cargadas)
                ax.plot(
                    Z_ajuste.real, -Z_ajuste.imag, "-", color="firebrick",
                    linewidth=2,
                    label=textos_educativos.nombre_bonito(nombre_elegido) + " (ajuste)",
                )
                error_ajuste_pct = domain_impedance.calcular_error_relativo_porcentual(
                    Z_ajuste, Z
                )
            elif self.ultimo_resultado is not None:
                ax.text(
                    0.02, 0.02, "Este circuito no se pudo ajustar a tus datos.",
                    transform=ax.transAxes, fontsize=8, color="#a33",
                )
            else:
                ax.text(
                    0.02, 0.02, 'Sin ajustar todavia -- da clic en "Analizar".',
                    transform=ax.transAxes, fontsize=8, color="#888",
                )

            valores_manuales = self._valores_parametros.get(nombre_elegido)
            if valores_manuales is not None:
                try:
                    Z_manual = domain_impedance.calcular_impedancia_con_parametros(
                        nombre_elegido, self.frecuencias_cargadas, valores_manuales
                    )
                    ax.plot(
                        Z_manual.real, -Z_manual.imag, "--", color="darkorange",
                        linewidth=2, label="Tu simulacion",
                    )
                    error_manual_pct = domain_impedance.calcular_error_relativo_porcentual(
                        Z_manual, Z
                    )
                except Exception:
                    # Con valores extremos (por ejemplo n negativo) la
                    # formula puede fallar -- se prefiere no mostrar la
                    # curva de simulacion a que la ventana truene.
                    pass

            self._actualizar_indicador_error(error_manual_pct, error_ajuste_pct)


        ax.set_xlabel("Z' (Ohms)")
        ax.set_ylabel("-Z'' (Ohms)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        self.figura_nyquist.tight_layout()

        # Si ya habia un punto resaltado (de antes de cambiar de
        # circuito o de redibujar por un nuevo analisis), lo volvemos a
        # dibujar -- asi puedes comparar como le va a ESE punto en
        # particular entre distintos modelos, sin perder la seleccion.
        self._dibujar_marcador_seleccion()

        self.canvas_nyquist.draw_idle()

    def _al_hacer_clic_en_grafica(self, event):
        if event.artist is not self._linea_datos:
            return
        if len(event.ind) == 0:
            return
        # Si el clic quedo cerca de varios puntos a la vez, nos
        # quedamos con el primero. Con un radio de deteccion pequeno
        # (5 pixeles) casi siempre es un solo punto.
        indice = int(event.ind[0])
        self._resaltar_punto(indice)

    def _al_seleccionar_fila_tabla(self):
        if self._sincronizando:
            return
        filas = self.tabla_datos.selectionModel().selectedRows()
        if not filas:
            return
        indice = filas[0].row()
        self._resaltar_punto(indice)

    def _resaltar_punto(self, indice):
        """
        Resalta el mismo dato en los dos lados a la vez: selecciona la
        fila en la tabla Y dibuja un circulo rojo alrededor del punto
        en la grafica. La bandera _sincronizando evita que, al
        seleccionar la fila por codigo, se dispare de nuevo el evento
        de seleccion y se vuelva un bucle infinito.
        """
        if self.frecuencias_cargadas is None or not (
            0 <= indice < len(self.frecuencias_cargadas)
        ):
            return

        self._indice_seleccionado = indice

        self._sincronizando = True
        try:
            self.tabla_datos.selectRow(indice)
            item = self.tabla_datos.item(indice, 0)
            if item is not None:
                self.tabla_datos.scrollToItem(item)
        finally:
            self._sincronizando = False

        self._dibujar_marcador_seleccion()
        self.canvas_nyquist.draw_idle()

        frecuencia = self.frecuencias_cargadas[indice]
        z_real = self.Z_cargada.real[indice]
        z_imag = self.Z_cargada.imag[indice]
        self.label_ayuda_tabla.setText(
            f"Punto seleccionado (#{indice + 1}): "
            f"frecuencia = {frecuencia:.4g} Hz, "
            f"Z' = {z_real:.4g} Ohms, "
            f"Z'' = {z_imag:.4g} Ohms"
        )

    def _dibujar_marcador_seleccion(self):
        """Dibuja (o mueve) el circulo rojo sobre self._indice_seleccionado,
        usando los datos crudos directamente -- no depende de la linea
        de la grafica, asi que funciona sin importar que circuito este
        elegido en el selector."""
        if self._indice_seleccionado is None or self.Z_cargada is None:
            return
        idx = self._indice_seleccionado
        if not (0 <= idx < len(self.Z_cargada)):
            return

        x = self.Z_cargada.real[idx]
        y = -self.Z_cargada.imag[idx]
        if self._marcador_seleccion is None:
            (self._marcador_seleccion,) = self.ax_nyquist.plot(
                [x], [y], "o", markersize=16, markerfacecolor="none",
                markeredgecolor="red", markeredgewidth=2.5, zorder=10,
            )
        else:
            self._marcador_seleccion.set_data([x], [y])
            self._marcador_seleccion.set_visible(True)
