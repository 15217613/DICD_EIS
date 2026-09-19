# -*- coding: utf-8 -*-
"""
Pagina "Evaluar Residuos": para el circuito elegido, grafica el
RESIDUO (dato medido menos prediccion del modelo) de la parte real e
imaginaria de la impedancia, contra la frecuencia.

Por que un residuo y no solo el error en porcentaje (que ya existe en
grafica_nyquist.py, el "indicador de error" del simulador): un residuo
por punto muestra ADEMAS la FORMA del error -- si los residuos se ven
como ruido disperso alrededor de cero, el modelo describe bien los
datos; si en cambio se ve un patron (una curva, una tendencia), es
señal de que al circuito elegido le esta faltando algo, aunque el
error promedio parezca bajo. Es un chequeo clasico en cualquier ajuste
estadistico, no solo en EIS -- por eso vale la pena tenerlo como su
propio paso del flujo.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from app.domain import circuits as domain_circuits
from app.presentation import textos_educativos


class PanelResiduos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frecuencias_cargadas = None
        self.Z_cargada = None
        self.ultimo_resultado = None
        self._construir_ui()
        self._redibujar()

    # ------------------------------------------------------------------
    # API publica -- misma forma que grafica_bode.py, para que
    # main_window.py trate todos los paneles de manera parecida.
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
        self.figura.savefig(ruta, dpi=dpi, bbox_inches="tight")

    # ------------------------------------------------------------------
    def _construir_ui(self):
        layout = QVBoxLayout(self)

        explicacion = QLabel(
            "Un residuo es la diferencia entre tu dato medido y lo que "
            "predice el modelo. Si los puntos de abajo se ven como ruido "
            "disperso alrededor de la linea en cero, el circuito describe "
            "bien tus datos. Si en cambio ves una curva o una tendencia "
            "clara, es señal de que a este circuito le falta algo, aunque "
            "su error promedio parezca bajo."
        )
        explicacion.setWordWrap(True)
        explicacion.setStyleSheet("color: #555; font-size: 11px;")
        layout.addWidget(explicacion)

        fila_combo = QHBoxLayout()
        fila_combo.addWidget(QLabel("Circuito a evaluar:"))
        self.combo_circuito = QComboBox()
        self.combo_circuito.addItem("Mejor circuito encontrado", None)
        for nombre in domain_circuits.CIRCUITOS:
            self.combo_circuito.addItem(
                textos_educativos.nombre_bonito(nombre), nombre
            )
        self.combo_circuito.currentIndexChanged.connect(self._redibujar)
        fila_combo.addWidget(self.combo_circuito)
        fila_combo.addStretch()
        layout.addLayout(fila_combo)

        self.figura = Figure(figsize=(7, 6))
        self.ax_real = self.figura.add_subplot(211)
        self.ax_imag = self.figura.add_subplot(212)
        self.canvas = FigureCanvasQTAgg(self.figura)
        layout.addWidget(self.canvas, stretch=1)

    def _circuito_a_evaluar(self):
        """Devuelve el ResultadoAjusteCircuito a usar, segun lo elegido
        en el combo -- o None si todavia no hay nada que mostrar."""
        if self.ultimo_resultado is None:
            return None

        nombre_elegido = self.combo_circuito.currentData()
        if nombre_elegido is None:
            mejores = self.ultimo_resultado.mejores
            return mejores[0] if mejores else None
        return self.ultimo_resultado.buscar_circuito(nombre_elegido)

    def _redibujar(self):
        self.ax_real.clear()
        self.ax_imag.clear()

        if self.Z_cargada is None:
            self.ax_real.axis("off")
            self.ax_imag.axis("off")
            self.ax_real.text(
                0.5, 0.5,
                "Aqui apareceran los residuos una vez que corras el "
                "analisis.",
                ha="center", va="center", transform=self.ax_real.transAxes,
                color="#888",
            )
            self.canvas.draw_idle()
            return

        self.ax_real.axis("on")
        self.ax_imag.axis("on")

        resultado_circuito = self._circuito_a_evaluar()
        if resultado_circuito is None or resultado_circuito.circuit is None:
            self.ax_real.text(
                0.5, 0.5,
                'Corre el analisis (o elige un circuito que si se haya '
                'podido ajustar) para ver sus residuos.',
                ha="center", va="center", transform=self.ax_real.transAxes,
                color="#888", wrap=True,
            )
            self.canvas.draw_idle()
            return

        frecuencias = self.frecuencias_cargadas
        Z = self.Z_cargada
        Z_modelo = resultado_circuito.circuit.predict(frecuencias)

        residuo_real = Z.real - Z_modelo.real
        residuo_imag = Z.imag - Z_modelo.imag

        self.ax_real.semilogx(frecuencias, residuo_real, "o", color="#2c5f8a")
        self.ax_real.axhline(0, color="#888", linewidth=1, linestyle="--")
        self.ax_real.set_ylabel("Residuo Z' (Ohms)")
        self.ax_real.grid(True, which="both", alpha=0.3)
        self.ax_real.set_title(
            f"Residuos de: "
            f"{textos_educativos.nombre_bonito(resultado_circuito.nombre)}",
            fontsize=10,
        )

        self.ax_imag.semilogx(frecuencias, residuo_imag, "o", color="#a33")
        self.ax_imag.axhline(0, color="#888", linewidth=1, linestyle="--")
        self.ax_imag.set_xlabel("Frecuencia (Hz)")
        self.ax_imag.set_ylabel("Residuo Z'' (Ohms)")
        self.ax_imag.grid(True, which="both", alpha=0.3)

        self.figura.tight_layout()
        self.canvas.draw_idle()