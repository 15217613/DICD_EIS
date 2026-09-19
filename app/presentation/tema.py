# -*- coding: utf-8 -*-
"""
Paleta de colores y hoja de estilos (QSS) de toda la interfaz.

Por que este archivo existe separado: es contenido de PRESENTACION
puro (como se ve la ventana), igual que textos_educativos.py es
contenido de que le decimos al usuario -- ninguno de los dos tiene
logica de negocio. Si algun dia se quiere cambiar un color, se cambia
UNA vez aqui y toda la app se actualiza sola, en vez de tener que
buscar codigos de color sueltos regados en cada widget.

QSS es el lenguaje de estilos de Qt -- se parece mucho a CSS (el que
se usa en paginas web), pero aplicado a botones, pestañas, tablas, etc.
de una ventana de escritorio en vez de un navegador.
"""

# ---------------------------------------------------------------------------
# Los 4 colores base. Todo lo demas en este archivo se construye a
# partir de estos -- si cambias uno aqui, cambia en TODA la interfaz.
# ---------------------------------------------------------------------------
PRIMARIO = "#0F2942"    # azul marino oscuro -- encabezados, pestañas activas
SECUNDARIO = "#2563EB"  # azul brillante -- botones de accion principal
TERCIARIO = "#0D9488"   # verde azulado -- barra de progreso, aciertos/exito
NEUTRO = "#64748B"      # gris azulado -- bordes, texto secundario

# Un par de tonos auxiliares que NO son parte de los 4 colores
# "oficiales", pero hacen falta para que se vea bien un boton al
# pasar el mouse encima (hover) o al estar deshabilitado. Se derivan
# a mano (no automaticamente) para tener control exacto de como se ven.
SECUNDARIO_HOVER = "#1D4ED8"   # SECUNDARIO un poco mas oscuro
FONDO_VENTANA = "#F5F6F8"      # gris casi blanco, para el fondo general
FONDO_PESTANA_INACTIVA = "#E2E8F0"

HOJA_DE_ESTILOS = f"""
/* Fondo general de la ventana */
QMainWindow, QWidget {{
    background-color: {FONDO_VENTANA};
}}

/* Cajas con borde y titulo (ej. "Archivo de datos", "Simula...") */
QGroupBox {{
    font-weight: bold;
    color: {PRIMARIO};
    border: 1px solid {NEUTRO};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}}

/* Botones: el color secundario es el que mas "llama la atencion",
   por eso se usa en los botones de accion (Cargar, Analizar,
   Exportar) -- son las acciones que el usuario dispara a proposito. */
QPushButton {{
    background-color: {SECUNDARIO};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {SECUNDARIO_HOVER};
}}
QPushButton:disabled {{
    background-color: {NEUTRO};
    color: #E5E7EB;
}}

/* Pestañas (Resultados / Nyquist / Bode / Aprender) */
QTabWidget::pane {{
    border: 1px solid {NEUTRO};
    border-radius: 4px;
}}
QTabBar::tab {{
    background-color: {FONDO_PESTANA_INACTIVA};
    color: {PRIMARIO};
    padding: 8px 18px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {PRIMARIO};
    color: white;
}}

/* Barra de progreso del analisis: el color terciario (verde azulado)
   se reserva para "algo va bien / algo se completo", que es
   justamente lo que representa una barra de progreso avanzando. */
QProgressBar {{
    border: 1px solid {NEUTRO};
    border-radius: 4px;
    text-align: center;
    color: {PRIMARIO};
}}
QProgressBar::chunk {{
    background-color: {TERCIARIO};
    border-radius: 3px;
}}

/* Encabezados de tablas (ranking de circuitos, tabla de datos) */
QHeaderView::section {{
    background-color: {PRIMARIO};
    color: white;
    padding: 5px;
    border: none;
}}

/* Tablas: filas alternadas usando el neutro muy suave, para que sea
   facil seguir una fila larga con la vista sin marcarla de un color
   fuerte. */
QTableWidget {{
    gridline-color: {NEUTRO};
    alternate-background-color: #EEF1F5;
}}

/* Combos (selector de circuito) */
QComboBox {{
    border: 1px solid {NEUTRO};
    border-radius: 4px;
    padding: 4px 8px;
}}
QComboBox:focus {{
    border: 1px solid {SECUNDARIO};
}}
"""