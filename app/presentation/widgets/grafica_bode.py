# -*- coding: utf-8 -*-
"""
Pestana "Grafica de Bode": muestra magnitud y fase de la impedancia
contra la frecuencia, en dos graficas apiladas.

Por que un archivo aparte de grafica_nyquist.py: Bode y Nyquist son
dos vistas del MISMO dato, pero no necesitan avisarse cosas en tiempo
real entre si (a diferencia de la tabla y la grafica de Nyquist, que
si lo hacen constantemente) -- asi que separarlos en su propia
pestana mantiene cada archivo mas simple.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from app.domain import circuits as domain_circuits
from app.domain import impedance as domain_impedance
from app.presentation import textos_educativos


class PanelGraficaBode(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frecuencias_cargadas = None
        self.Z_cargada = None
        self.ultimo_resultado = None
        self._construir_ui()
        self._redibujar()

    # ------------------------------------------------------------------
    # API publica -- misma forma que PanelGraficaNyquist, para que
    # main_window.py pueda tratar ambos paneles de manera parecida.
    # ------------------------------------------------------------------
    def mostrar_datos_crudos(self, frecuencias, Z):
        self.frecuencias_cargadas = frecuencias
        self.Z_cargada = Z
        self.ultimo_resultado = None
        self._redibujar()

    def mostrar_resultados(self, resultado):
        self.ultimo_resultado = resultado
        self._redibujar()

    def limpiar(self):
        self.frecuencias_cargadas = None
        self.Z_cargada = None
        self.ultimo_resultado = None
        self._redibujar()

    def guardar_grafica_como_imagen(self, ruta, dpi=150):
        """Igual que en Nyquist -- pensado para incluirla en el reporte
        PDF si mas adelante se decide agregar esa seccion."""
        self.figura.savefig(ruta, dpi=dpi, bbox_inches="tight")

    # ------------------------------------------------------------------
    def _construir_ui(self):
        layout = QVBoxLayout(self)

        fila_combo = QHBoxLayout()
        fila_combo.addWidget(QLabel("Circuito a mostrar:"))
        self.combo_circuito = QComboBox()
        self.combo_circuito.addItem("Automatico (mejores 3)", None)
        for nombre in domain_circuits.CIRCUITOS:
            self.combo_circuito.addItem(
                textos_educativos.nombre_bonito(nombre), nombre
            )
        self.combo_circuito.currentIndexChanged.connect(self._redibujar)
        fila_combo.addWidget(self.combo_circuito)
        fila_combo.addStretch()
        layout.addLayout(fila_combo)

        self.figura = Figure(figsize=(7, 6))
        self.ax_magnitud = self.figura.add_subplot(211)
        self.ax_fase = self.figura.add_subplot(212)
        self.canvas = FigureCanvasQTAgg(self.figura)
        layout.addWidget(self.canvas, stretch=1)

    def _buscar_resultado_circuito(self, nombre):
        if self.ultimo_resultado is None:
            return None
        return self.ultimo_resultado.buscar_circuito(nombre)

    def _redibujar(self):
        self.ax_magnitud.clear()
        self.ax_fase.clear()

        if self.Z_cargada is None:
            self.ax_magnitud.axis("off")
            self.ax_fase.axis("off")
            self.ax_magnitud.text(
                0.5, 0.5,
                "Aqui aparecera la grafica de Bode al cargar un archivo.",
                ha="center", va="center", transform=self.ax_magnitud.transAxes,
                color="#888",
            )
            self.canvas.draw_idle()
            return

        self.ax_magnitud.axis("on")
        self.ax_fase.axis("on")

        frecuencias = self.frecuencias_cargadas
        Z = self.Z_cargada
        magnitud, fase = domain_impedance.calcular_magnitud_fase(Z)

        self.ax_magnitud.loglog(frecuencias, magnitud, "o", label="Datos experimentales")
        self.ax_fase.semilogx(frecuencias, fase, "o", label="Datos experimentales")

        nombre_elegido = self.combo_circuito.currentData()
        if nombre_elegido is None:
            # Modo automatico: las mejores curvas del ultimo analisis.
            if self.ultimo_resultado is not None:
                for r in self.ultimo_resultado.mejores:
                    Z_ajuste = r.circuit.predict(frecuencias)
                    mag_a, fase_a = domain_impedance.calcular_magnitud_fase(Z_ajuste)
                    etiqueta = textos_educativos.nombre_bonito(r.nombre)
                    self.ax_magnitud.loglog(frecuencias, mag_a, "-", label=etiqueta)
                    self.ax_fase.semilogx(frecuencias, fase_a, "-", label=etiqueta)
        else:
            resultado_circuito = self._buscar_resultado_circuito(nombre_elegido)
            if resultado_circuito is not None and resultado_circuito.circuit is not None:
                Z_ajuste = resultado_circuito.circuit.predict(frecuencias)
                mag_a, fase_a = domain_impedance.calcular_magnitud_fase(Z_ajuste)
                etiqueta = textos_educativos.nombre_bonito(nombre_elegido) + " (ajuste)"
                self.ax_magnitud.loglog(
                    frecuencias, mag_a, "-", color="firebrick", linewidth=2, label=etiqueta
                )
                self.ax_fase.semilogx(
                    frecuencias, fase_a, "-", color="firebrick", linewidth=2, label=etiqueta
                )

        self.ax_magnitud.set_ylabel("|Z| (Ohms)")
        self.ax_magnitud.grid(True, which="both", alpha=0.3)
        self.ax_magnitud.legend(fontsize=8)

        self.ax_fase.set_xlabel("Frecuencia (Hz)")
        self.ax_fase.set_ylabel("Fase (grados)")
        self.ax_fase.grid(True, which="both", alpha=0.3)
        self.ax_fase.legend(fontsize=8)

        self.figura.tight_layout()
        self.canvas.draw_idle()