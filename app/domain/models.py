# -*- coding: utf-8 -*-
"""
Modelos del dominio: estructuras de datos que representan conceptos de
EIS (Espectroscopia de Impedancia Electroquimica), sin ninguna
dependencia de PySide6, matplotlib, ni de como se leen los archivos.

Por que dataclasses y no diccionarios (como se hacia antes): con un
diccionario, escribir mal una llave (por ejemplo "aic" en vez de "AIC")
no lanza ningun error hasta que accedes al valor y sale None o KeyError
en un lugar inesperado. Con una dataclass, el editor y Python avisan de
inmediato si un campo no existe -- son "contratos" explicitos de que
datos trae cada objeto.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any

import numpy as np


@dataclass
class DefinicionCircuito:
    """Describe UN circuito de la biblioteca: su topologia (en el
    formato de texto que entiende impedance.py) y el orden de sus
    parametros. Es informacion fija, no cambia con los datos del
    usuario -- por eso vive en el dominio, no en un resultado."""

    nombre: str
    circuito: str            # ej. "R0-p(R1,C1)"
    parametros: List[str]    # ej. ["Rs", "Rct", "Cdl"], en el orden que
                              # espera CustomCircuit de impedance.py


@dataclass
class ResultadoAjusteCircuito:
    """El resultado de ajustar UN circuito especifico a los datos de
    un archivo: si funciono, que tan bien, y si tiene sentido fisico."""

    nombre: str
    circuit: Optional[Any]   # instancia de CustomCircuit (impedance.py),
                              # o None si el ajuste fallo por completo
    aic: float
    bic: float
    valido: bool
    motivo: str               # explica por que se descarto (o "OK")


@dataclass
class ResultadoAnalisis:
    """El resultado COMPLETO de analizar un archivo: los datos
    originales, la validacion de consistencia fisica, y como le fue a
    cada circuito de la biblioteca."""

    frecuencias: np.ndarray
    Z: np.ndarray
    kk_valido: bool
    kk_mensaje: str
    n_semicirculos: int
    resultados: List[ResultadoAjusteCircuito] = field(default_factory=list)
    validos: List[ResultadoAjusteCircuito] = field(default_factory=list)
    descartados: List[ResultadoAjusteCircuito] = field(default_factory=list)
    pesos_akaike: List[float] = field(default_factory=list)
    mejores: List[ResultadoAjusteCircuito] = field(default_factory=list)
    empatados: List[ResultadoAjusteCircuito] = field(default_factory=list)

    def buscar_circuito(self, nombre: str) -> Optional[ResultadoAjusteCircuito]:
        """Busca el resultado de un circuito especifico por nombre.
        Metodo de conveniencia usado por la interfaz para la pestana
        de exploracion de circuitos."""
        for r in self.resultados:
            if r.nombre == nombre:
                return r
        return None
