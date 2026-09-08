# Analizador de EIS - Interfaz de escritorio

Interfaz grafica (PySide6) para el ajuste automatico de circuitos
equivalentes a partir de datos de Espectroscopia de Impedancia
Electroquimica (EIS).

## Instalacion

```bash
pip install -r requirements.txt
```

## Ejecucion

```bash
python3 app.py
```

## Correr las pruebas automatizadas

```bash
pytest
```

Deberia ver algo como `20 passed`. Estas pruebas quedan versionadas
junto con el codigo -- a diferencia de las pruebas manuales que se
hicieron durante el desarrollo (cargar un archivo, hacer clic,
verificar visualmente), estas se pueden volver a correr en cualquier
momento, en cualquier maquina, y sirven como evidencia reproducible
para la documentacion del proyecto (que fue exactamente probado, con
que datos, y que se esperaba que pasara).

## Arquitectura: por que capas

El proyecto esta organizado en **capas**, una forma de dividir el
codigo segun DE QUE SE OCUPA cada parte, no segun que tan grande sea
cada archivo. La regla central es la **direccion de las dependencias**:
cada capa solo puede depender de la que esta "debajo" de ella, nunca al
reves.

```
presentation   (Qt: ventanas, botones, tablas, graficas)
      |
      v
application    (orquesta: "carga este archivo", "corre este analisis")
      |
      v
   domain      (la ciencia de EIS: formulas, ajuste, validacion --
      |         CERO dependencias de Qt o de como se leen archivos)
      v
infrastructure (detalles tecnicos: leer un CSV, un hilo de Qt)
```

**Por que importa esta direccion:** `domain/` no sabe que existe
PySide6, ni matplotlib, ni que los datos vienen de un archivo. Eso
significa que toda la ciencia del proyecto (validacion Kramers-Kronig,
ajuste de circuitos, AIC/BIC) se puede probar con `pytest` sin abrir
NINGUNA ventana -- de hecho, `tests/unit/` lo hace. Si mas adelante
este mismo analisis se quisiera ofrecer por otro medio (una API web,
un script de linea de comandos, un notebook de Jupyter), `domain/` y
`application/` se reutilizarian tal cual; solo habria que escribir una
`presentation/` distinta.

### Mapa de carpetas

```
app/
├── presentation/     Qt: ventanas, widgets, dialogos
│   ├── main_window.py       Ensambla los widgets y conecta senales
│   ├── textos_educativos.py Mensajes amigables (contenido, no logica)
│   └── widgets/
│       ├── panel_archivo.py     Cargar archivo + iniciar analisis
│       ├── tabla_resultados.py  Pestana "Resultados"
│       ├── grafica_nyquist.py   Pestana "Grafica de Nyquist" (grafica
│       │                        interactiva + tabla de datos + selector
│       │                        de circuito + simulador de parametros
│       │                        editables, todo sincronizado)
│       └── circuit_diagram.py   Dibuja el diagrama de un circuito
│
├── application/      Orquestacion (sin Qt, sin matplotlib)
│   ├── eis_service.py       Cargar un archivo (con errores amigables)
│   ├── analysis_service.py  Correr el analisis completo, paso a paso
│   └── export_service.py    Exportar reporte (PENDIENTE, ver abajo)
│
├── domain/           La ciencia de EIS (sin Qt, sin archivos)
│   ├── models.py         Estructuras de datos (dataclasses)
│   ├── circuits.py       Biblioteca de circuitos + formulas
│   ├── impedance.py      Kramers-Kronig, ajuste, AIC/BIC
│   └── validation.py     Filtro de sentido fisico
│
└── infrastructure/   Detalles tecnicos de implementacion
    ├── file_repository.py   Leer un CSV en crudo
    ├── data_loader.py       Interpretar el CSV como datos de EIS
    └── workers.py           QThread para no congelar la ventana

data/
├── examples/datos_prueba.csv   Datos sinteticos para probar la app
├── raw/                        (vacia -- tus datos de laboratorio)
└── processed/                  (vacia -- para resultados exportados)

tests/
├── unit/            Prueban domain/ en aislamiento (rapidas, sin Qt)
├── integration/     Prueban varias capas juntas (incluye la ventana)
└── fixtures/        Generador de datos sinteticos reutilizable
```

### Simulador de parametros: "que pasa si cambio esto"

Cuando eliges un circuito especifico en el selector, ademas del
diagrama y la formula aparece un panel con un campo editable por cada
parametro (Rs, Rct, Q, n, etc.), prellenado con:

- Los valores YA AJUSTADOS, si ya corriste el analisis; o
- La estimacion geometrica inicial (la misma que usa el optimizador
  como punto de partida), si todavia no analizas el archivo.

Al cambiar cualquier valor, se dibuja una curva punteada adicional
("Tu simulacion") sobre la grafica, calculada evaluando DIRECTAMENTE
la formula del circuito con esos numeros -- sin volver a ajustar nada
-- para poder comparar tu intento contra la curva ajustada real (linea
solida). El boton "Restablecer valores" regresa a los valores
ajustados/estimados originales.

Debajo de los campos aparece un indicador de que tan lejos esta tu
simulacion de los datos reales, en porcentaje (0% seria un ajuste
perfecto), y -- si ya corriste el analisis -- el mismo porcentaje para
el ajuste real, con cuantas veces mas error tiene tu intento. El color
del texto (verde/ambar/rojo) da una guia visual rapida, pero el numero
es lo que importa: es un promedio simple de cuanto se aleja cada punto
de la curva respecto al dato medido, deliberadamente MAS SIMPLE que el
AIC/BIC que se usa para comparar circuitos entre si (ese esta
ponderado y pensado para otra cosa: elegir el mejor circuito, no medir
que tan bien le fue a una persona jugando con los numeros).

Cada campo tiene un tooltip (pasa el mouse encima) explicando la
"regla" geometrica especifica que se uso para SU estimacion inicial
-- por ejemplo, Rs sale de la parte real de la impedancia en la
frecuencia mas alta medida, mientras que Rct sale de la posicion del
pico del semicirculo. Esta informacion tambien esta disponible en los
docstrings de `domain/impedance.py::estimar_valores_iniciales`.

### Por que un widget (`grafica_nyquist.py`) es tan grande y no se
partio mas

La grafica, la tabla de datos y el selector de circuito necesitan
avisarse cosas constantemente entre si (clic en un punto debe resaltar
su fila, y viceversa). Partirlos en archivos distintos obligaria a
pasar mensajes de un lado a otro sin ninguna ganancia real -- en la
practica son una sola pieza de interfaz con varias vistas del mismo
dato. Cada widget de `presentation/widgets/` expone una API publica
simple (`mostrar_datos_crudos()`, `mostrar_resultados()`) para que
`main_window.py` no necesite saber COMO esta hecho por dentro.

### Sobre `export_service.py`

Ya esta implementado: genera un reporte en PDF (via `reportlab`, en
`infrastructure/pdf_writer.py`) con el resumen de Kramers-Kronig, la
tabla comparativa de circuitos, los parametros del mejor ajuste, y la
grafica de Nyquist tal como se ve en ese momento en la ventana. El
boton "Exportar reporte PDF..." (panel izquierdo) se habilita cuando
termina un analisis.

Nota de arquitectura: `application/export_service.py` no puede
importar `presentation/textos_educativos.py` (rompería la regla de
capas). Por eso `main_window.py` le PASA los diccionarios de nombres
amigables (`NOMBRES_BONITOS`, `NOMBRES_PARAMETROS_BONITOS`) como
parametros; si se llama sin ellos (por ejemplo, desde un script o una
prueba), el reporte usa los nombres tecnicos crudos -- sigue siendo un
reporte correcto, solo menos pulido.

## Decisiones de diseno (con sus pros y contras)

**Modelos de datos (`domain/models.py`) en vez de diccionarios:**
- Pro: si escribes mal el nombre de un campo (`r.aci` en vez de
  `r.aic`), Python avisa de inmediato en vez de fallar en silencio mas
  adelante con un `KeyError` dificil de rastrear.
- Contra: hubo que cambiar `resultado["aic"]` por `resultado.aic` en
  todo el codigo que ya existia -- mas trabajo de migracion una sola
  vez, a cambio de mas seguridad de ahi en adelante.

**Un solo lienzo (Figure/Canvas) persistente para la grafica de
Nyquist, que se redibuja en vez de crearse de nuevo:**
- Pro: cambiar de circuito en el selector se siente instantaneo (~70ms)
  en vez de crear un widget de Qt nuevo cada vez.
- Contra: hay que tener cuidado de limpiar bien el lienzo (`ax.clear()`)
  antes de cada redibujo, o contenido viejo puede quedar superpuesto.

**QThread en `infrastructure/workers.py`, no en `application/`:**
- Pro: `application/analysis_service.py` no sabe que existe Qt --se
  podria llamar igual desde una consola o un notebook.
- Contra: exige una excepcion deliberada a "presentation solo llama a
  application": la ventana instancia `HiloAnalisis` directamente,
  porque el hilo es un detalle de ESTA interfaz en particular.

## Pendiente / siguientes pasos sugeridos

- Cargar tus datos reales de laboratorio y confirmar que
  `infrastructure/data_loader.py` interprete bien tu formato exacto de
  CSV.
- Si la biblioteca de circuitos crece, valdria la pena revisar la
  duplicacion entre `domain/circuits.py` (topologia para impedance.py)
  y `presentation/widgets/circuit_diagram.py` (topologia para el
  dibujo) -- ver la nota de arquitectura al inicio de ese archivo.
- El reporte PDF exporta la grafica de Nyquist tal como se ve en ese
  momento (modo automatico o un circuito especifico) -- si quieres, se
  podria extender para incluir tambien el diagrama del circuito
  ganador, o varias paginas comparando los 4 circuitos uno por uno.
