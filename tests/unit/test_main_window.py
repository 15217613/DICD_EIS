# -*- coding: utf-8 -*-
"""
Prueba de INTEGRACION de la interfaz grafica: no prueba que los
resultados sean correctos (eso ya lo cubre
tests/integration/test_analysis_service.py), sino que la VENTANA arma
bien sus widgets y que las senales conectan con quien deben -- el tipo
de bug que un refactor de arquitectura como este puede introducir
facilmente (una senal mal conectada, un import roto) y que las pruebas
puramente de dominio no detectarian.

Se usa QT_QPA_PLATFORM=offscreen (definido en tests/conftest.py) para
poder crear ventanas de Qt sin una pantalla real.

CAMBIO EN ESTA VERSION: la navegacion paso de pestanas arriba
(QTabWidget) a un menu lateral + QStackedWidget (ver
presentation/main_window.py y presentation/widgets/panel_navegacion.py).
Solo la prueba que revisaba los textos de las pestanas cambio de forma
-- el resto de las pruebas sigue usando los mismos atributos
(panel_archivo, panel_grafica, panel_bode) porque esos widgets no
cambiaron de comportamiento, solo de lugar en la pantalla.
"""

import os

import pytest
from PySide6.QtWidgets import QApplication

from app.presentation.main_window import VentanaPrincipal
from app.presentation.widgets.panel_navegacion import PASOS

RUTA_EJEMPLO = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "examples", "datos_prueba.csv"
)


@pytest.fixture
def qapp():
    """Una unica QApplication para las pruebas de este archivo -- Qt no
    permite crear mas de una en el mismo proceso."""
    app = QApplication.instance() or QApplication([])
    yield app


def test_ventana_se_construye_con_su_menu_de_7_pasos(qapp):
    """
    Reemplaza a la antigua test_ventana_se_construye_con_sus_tres_pestanas:
    ya no hay pestanas arriba, ahora hay un menu lateral
    (panel_navegacion) con los 7 pasos del flujo, y un stack con esa
    misma cantidad de paginas.
    """
    ventana = VentanaPrincipal()
    assert ventana.panel_navegacion.lista.count() == len(PASOS)
    assert ventana.stack.count() == len(PASOS)

    textos_esperados = [texto for _icono, texto in PASOS]
    for i, texto_esperado in enumerate(textos_esperados):
        assert texto_esperado in ventana.panel_navegacion.lista.item(i).text()


def test_elegir_un_paso_en_el_menu_cambia_la_pagina_visible(qapp):
    ventana = VentanaPrincipal()
    ventana.panel_navegacion.lista.setCurrentRow(3)  # "Modelar Circuito"
    assert ventana.stack.currentIndex() == 3


def test_cargar_archivo_llena_la_tabla_de_datos(qapp):
    ventana = VentanaPrincipal()
    ventana._al_elegir_archivo(RUTA_EJEMPLO)
    assert ventana.panel_grafica.tabla_datos.rowCount() > 0
    assert ventana.frecuencias_cargadas is not None


def test_archivo_invalido_no_rompe_la_ventana(qapp, monkeypatch):
    # QMessageBox.warning() abre un dialogo MODAL que espera un clic
    # real -- en una prueba automatizada nadie va a hacer ese clic, asi
    # que sin este parche la prueba se quedaria colgada para siempre.
    # Lo reemplazamos por una funcion que no hace nada, solo para
    # confirmar que el codigo LLEGA a mostrar el aviso sin tronar.
    from PySide6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)

    ventana = VentanaPrincipal()
    ventana._al_elegir_archivo("archivo_que_no_existe.csv")
    assert ventana.frecuencias_cargadas is None


def test_analisis_completo_conecta_resultados_con_la_ventana(qapp):
    """
    Prueba de extremo a extremo con el hilo real de analisis (no un
    doble/mock), esperando a que termine con un bucle de eventos
    corto. Verifica que, al terminar, tanto el panel de resultados
    como el panel de la grafica de "Modelar Circuito" recibieron el
    resultado, y que la ventana salto sola al paso "Validar (K-K)".
    """
    ventana = VentanaPrincipal()
    ventana._al_elegir_archivo(RUTA_EJEMPLO)
    ventana._iniciar_analisis()

    # Esperamos a que el hilo en segundo plano termine (con limite de
    # tiempo, para no colgar la prueba si algo sale mal).
    terminado = ventana.hilo.wait(15000)
    qapp.processEvents()

    assert terminado, "el analisis no termino dentro del tiempo esperado"
    assert ventana.ultimo_resultado is not None
    assert len(ventana.ultimo_resultado.mejores) > 0
    assert ventana.panel_grafica.ultimo_resultado is ventana.ultimo_resultado
    assert ventana.stack.currentIndex() == 1  # salto automatico a Validar (K-K)


def test_simulador_de_parametros_permite_explorar_antes_de_analizar(qapp):
    """
    El panel de parametros editables debe poder usarse ANTES de correr
    el analisis completo, prellenado con la estimacion geometrica
    inicial -- no debe exigir que ya exista un ajuste.
    """
    ventana = VentanaPrincipal()
    ventana._al_elegir_archivo(RUTA_EJEMPLO)
    panel = ventana.panel_grafica

    idx = [
        panel.combo_circuito_grafica.itemData(i)
        for i in range(panel.combo_circuito_grafica.count())
    ].index("randles_cpe")
    panel.combo_circuito_grafica.setCurrentIndex(idx)
    qapp.processEvents()

    assert "randles_cpe" in panel._valores_parametros
    assert len(panel._inputs_parametros) == 4


def test_editar_un_parametro_dibuja_la_curva_de_simulacion(qapp):
    ventana = VentanaPrincipal()
    ventana._al_elegir_archivo(RUTA_EJEMPLO)
    panel = ventana.panel_grafica

    idx = [
        panel.combo_circuito_grafica.itemData(i)
        for i in range(panel.combo_circuito_grafica.count())
    ].index("randles_cpe")
    panel.combo_circuito_grafica.setCurrentIndex(idx)
    qapp.processEvents()

    valor_original = panel._valores_parametros["randles_cpe"][1]
    panel._inputs_parametros[1].setText(str(valor_original * 1.5))
    panel._al_editar_parametro("randles_cpe", 1)
    qapp.processEvents()

    etiquetas = [linea.get_label() for linea in panel.ax_nyquist.get_lines()]
    assert "Tu simulacion" in etiquetas


def test_entrada_invalida_en_parametro_no_rompe_la_ventana(qapp):
    ventana = VentanaPrincipal()
    ventana._al_elegir_archivo(RUTA_EJEMPLO)
    panel = ventana.panel_grafica

    idx = [
        panel.combo_circuito_grafica.itemData(i)
        for i in range(panel.combo_circuito_grafica.count())
    ].index("randles_cpe")
    panel.combo_circuito_grafica.setCurrentIndex(idx)
    qapp.processEvents()

    panel._inputs_parametros[0].setText("no es un numero")
    panel._al_editar_parametro("randles_cpe", 0)  # no debe lanzar excepcion
    qapp.processEvents()

    # El valor invalido NO debe haberse guardado como parametro real.
    assert isinstance(panel._valores_parametros["randles_cpe"][0], float)


def test_restablecer_regresa_a_los_valores_ajustados(qapp):
    ventana = VentanaPrincipal()
    ventana._al_elegir_archivo(RUTA_EJEMPLO)
    ventana._iniciar_analisis()
    terminado = ventana.hilo.wait(15000)
    qapp.processEvents()
    assert terminado

    panel = ventana.panel_grafica
    idx = [
        panel.combo_circuito_grafica.itemData(i)
        for i in range(panel.combo_circuito_grafica.count())
    ].index("randles_cpe")
    panel.combo_circuito_grafica.setCurrentIndex(idx)
    qapp.processEvents()

    resultado_cpe = ventana.ultimo_resultado.buscar_circuito("randles_cpe")

    panel._inputs_parametros[0].setText("99999")
    panel._al_editar_parametro("randles_cpe", 0)
    qapp.processEvents()

    panel._restablecer_parametros_actuales()
    qapp.processEvents()

    valor_restablecido = panel._valores_parametros["randles_cpe"][0]
    assert abs(valor_restablecido - resultado_cpe.circuit.parameters_[0]) < 1e-6


def test_indicador_de_error_compara_simulacion_contra_ajuste_real(qapp):
    """
    Al empeorar deliberadamente un parametro, el indicador debe: (1)
    mostrar un porcentaje de error MAYOR para la simulacion que para el
    ajuste real, y (2) mencionar cuantas veces mas error tiene.
    """
    ventana = VentanaPrincipal()
    ventana._al_elegir_archivo(RUTA_EJEMPLO)
    ventana._iniciar_analisis()
    terminado = ventana.hilo.wait(15000)
    qapp.processEvents()
    assert terminado

    panel = ventana.panel_grafica
    idx = [
        panel.combo_circuito_grafica.itemData(i)
        for i in range(panel.combo_circuito_grafica.count())
    ].index("randles_cpe")
    panel.combo_circuito_grafica.setCurrentIndex(idx)
    qapp.processEvents()

    # Recien elegido el circuito (valores = los ajustados), el error de
    # "tu simulacion" deberia ser practicamente igual al del ajuste.
    texto_inicial = panel.label_error_simulacion.text()
    assert "%" in texto_inicial

    valor_original = panel._valores_parametros["randles_cpe"][1]
    panel._inputs_parametros[1].setText(str(valor_original * 2))
    panel._al_editar_parametro("randles_cpe", 1)
    qapp.processEvents()

    texto_tras_editar = panel.label_error_simulacion.text()
    assert "mas error" in texto_tras_editar
    assert "El ajuste real" in texto_tras_editar


def test_indicador_de_error_se_limpia_en_modo_automatico(qapp):
    ventana = VentanaPrincipal()
    ventana._al_elegir_archivo(RUTA_EJEMPLO)
    panel = ventana.panel_grafica

    idx = [
        panel.combo_circuito_grafica.itemData(i)
        for i in range(panel.combo_circuito_grafica.count())
    ].index("randles_cpe")
    panel.combo_circuito_grafica.setCurrentIndex(idx)
    qapp.processEvents()
    assert panel.label_error_simulacion.text() != ""

    panel.combo_circuito_grafica.setCurrentIndex(0)  # "Automatico"
    qapp.processEvents()
    assert panel.label_error_simulacion.text() == ""


def test_boton_exportar_deshabilitado_hasta_terminar_el_analisis(qapp):
    ventana = VentanaPrincipal()
    ventana._al_elegir_archivo(RUTA_EJEMPLO)
    assert ventana.panel_archivo.boton_exportar.isEnabled() is False
    assert ventana.panel_generar_informe.boton_exportar.isEnabled() is False

    ventana._iniciar_analisis()
    terminado = ventana.hilo.wait(15000)
    qapp.processEvents()
    assert terminado
    assert ventana.panel_archivo.boton_exportar.isEnabled() is True
    assert ventana.panel_generar_informe.boton_exportar.isEnabled() is True


def test_exploracion_de_espectros_es_de_solo_lectura(qapp):
    """
    Nueva prueba: la instancia de PanelGraficaNyquist usada en
    "Explorar Espectros" no debe permitir elegir un circuito -- su
    combo existe por dentro (para no romper el resto del codigo) pero
    nunca se agrega a la pantalla, asi que el usuario no puede tocarlo
    y siempre se queda en "Automatico".
    """
    ventana = VentanaPrincipal()
    ventana._al_elegir_archivo(RUTA_EJEMPLO)
    panel_exploracion = ventana.panel_grafica_exploracion
    assert panel_exploracion.combo_circuito_grafica.currentData() is None
    assert panel_exploracion.panel_parametros.isVisible() is False


def test_generador_sintetico_carga_datos_en_la_ventana(qapp):
    """
    El Generador Didactico (pestana nueva dentro de "Importar Datos")
    debe poder generar datos y que le lleguen a la ventana exactamente
    igual que si vinieran de un archivo real -- misma tuberia, mismos
    atributos (frecuencias_cargadas, Z_cargada), sin necesitar ningun
    archivo en disco.
    """
    ventana = VentanaPrincipal()
    panel = ventana.panel_generador_sintetico

    idx = [
        panel.combo_circuito.itemData(i)
        for i in range(panel.combo_circuito.count())
    ].index("randles_cpe")
    panel.combo_circuito.setCurrentIndex(idx)
    qapp.processEvents()

    panel._al_generar()
    qapp.processEvents()

    assert ventana.frecuencias_cargadas is not None
    assert ventana.Z_cargada is not None
    assert ventana.ruta_archivo is None  # no vino de un archivo real
    assert "sinteticos" in ventana.panel_archivo.label_archivo.text().lower()
    # Tambien debe habersele avisado a la grafica de exploracion, igual
    # que con un archivo real.
    assert ventana.panel_grafica_exploracion.Z_cargada is not None


def test_generador_sintetico_con_parametro_invalido_no_carga_nada(qapp):
    ventana = VentanaPrincipal()
    panel = ventana.panel_generador_sintetico

    panel._inputs_parametros[0].setText("no es un numero")
    panel._al_generar()
    qapp.processEvents()

    assert panel.label_error.text() != ""
    assert ventana.frecuencias_cargadas is None


def test_exportar_reporte_genera_pdf_real(qapp, monkeypatch, tmp_path):
    """
    Prueba de extremo a extremo del boton "Exportar reporte PDF...":
    simula la eleccion de archivo del dialogo (que normalmente exige un
    clic real) y confirma que efectivamente aparece un PDF en disco.
    """
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    ruta_salida = str(tmp_path / "reporte_prueba.pdf")
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", lambda *a, **k: (ruta_salida, "")
    )
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a, **k: None)

    ventana = VentanaPrincipal()
    ventana._al_elegir_archivo(RUTA_EJEMPLO)
    ventana._iniciar_analisis()
    terminado = ventana.hilo.wait(15000)
    qapp.processEvents()
    assert terminado

    ventana._exportar_reporte()

    assert os.path.exists(ruta_salida)
    with open(ruta_salida, "rb") as f:
        assert f.read(5) == b"%PDF-"