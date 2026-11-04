"""
Componentes de entrada compartidos por los módulos.
Tema: tablas de matrices, teclado matemático, selectores compactos y resumen de resultados (PyQt6).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QGridLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QFrame, QSizePolicy, QApplication, QLineEdit, QHeaderView,
    QAbstractItemView, QAbstractItemDelegate
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from gui.componentes import ControlSegmentado, Tarjeta, icono

DIM_MAX = 10
ALTO_FILA = 44
ALTO_FILA_MAX = 64

# Teclas de funciones: (etiqueta, texto que se inserta). Usan la sintaxis de core/parser.py
TECLAS_FUNCIONES = {
    "Básico": [
        ("a²", "^2"), ("aᵇ", "^"), ("|a|", "abs("),
        ("√", "raiz("), ("ⁿ√", "^(1/"), ("π", "pi"),
        ("sen", "sen("), ("cos", "cos("), ("tan", "tan("),
        ("(", "("), (")", ")"), ("e", "E"),
    ],
    "Funciones": [
        ("ln", "ln("), ("log", "log("), ("eˣ", "E^"),
        ("sec", "sec("), ("csc", "csc("), ("cot", "cot("),
        ("x⁻¹", "^(-1)"), ("10ˣ", "10^"), ("|a|", "abs("),
        ("(", "("), (")", ")"), ("π", "pi"),
    ],
    "Trig": [
        ("arcsen", "arcsen("), ("arccos", "arccos("), ("arctan", "arctan("),
        ("sen", "sen("), ("cos", "cos("), ("tan", "tan("),
        ("arccot", "arccot("), ("cot", "cot("), ("π/2", "pi/2"),
        ("(", "("), (")", ")"), ("π", "pi"),
    ],
}

# Bloque numérico: (etiqueta, inserción, fila, columna, ancho, tipo)
TECLAS_NUMERICAS = [
    ("7", "7", 0, 4, 1, "num"), ("8", "8", 0, 5, 1, "num"), ("9", "9", 0, 6, 1, "num"), ("÷", "/", 0, 7, 1, "op"),
    ("4", "4", 1, 4, 1, "num"), ("5", "5", 1, 5, 1, "num"), ("6", "6", 1, 6, 1, "num"), ("×", "*", 1, 7, 1, "op"),
    ("1", "1", 2, 4, 1, "num"), ("2", "2", 2, 5, 1, "num"), ("3", "3", 2, 6, 1, "num"), ("−", "-", 2, 7, 1, "op"),
    ("0", "0", 3, 4, 2, "num"), (".", ".", 3, 6, 1, "num"), ("+", "+", 3, 7, 1, "op"),
]


class SelectorDimension(QComboBox):
    """Selector compacto de 1 a DIM_MAX con la misma interfaz que QSpinBox."""

    valueChanged = pyqtSignal(int)

    def __init__(self, valor, descripcion, maximo=DIM_MAX):
        super().__init__()
        self.maximo = maximo
        self.addItems([str(i) for i in range(1, maximo + 1)])
        self.setCurrentIndex(valor - 1)
        self.setToolTip(descripcion)
        self.setAccessibleName(descripcion)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.currentIndexChanged.connect(lambda i: self.valueChanged.emit(i + 1))

    def value(self):
        return self.currentIndex() + 1

    def setValue(self, v):
        self.setCurrentIndex(max(1, min(self.maximo, v)) - 1)


def grupo_dimensiones(partes):
    """Agrupa selectores y textos cortos (p. ej. ["ℝ", sel_n, "→ ℝ", sel_m]) en una sola pastilla."""
    marco = QFrame()
    marco.setObjectName("Dims")
    marco.setFixedHeight(32)
    lay = QHBoxLayout(marco)
    lay.setContentsMargins(2, 2, 6, 2)
    lay.setSpacing(0)
    for p in partes:
        if isinstance(p, str):
            lbl = QLabel(p)
            lbl.setObjectName("DimsX")
            lay.addWidget(lbl)
        else:
            lay.addWidget(p)
    return marco


class SelectorFormato(ControlSegmentado):
    """Fracción exacta o decimal; responde a isChecked() como el checkbox anterior."""

    def __init__(self):
        super().__init__(["a/b", "0.5"])
        self.setToolTip("Mostrar resultados como fracciones o decimales")

    def isChecked(self):
        return self.indice() == 0


class TablaMatriz(QTableWidget):
    """Tabla de valores: Enter confirma la celda y avanza a la siguiente.

    Con `expandir=True` la tabla toma el espacio vertical libre: las filas crecen
    hasta ALTO_FILA_MAX y, si no caben, aparece la barra de desplazamiento.
    """

    fin_de_tabla = pyqtSignal()
    enfocada = pyqtSignal()

    def __init__(self, filas_visibles=8, expandir=False, parent=None):
        super().__init__(parent)
        self.filas_visibles = filas_visibles
        self.expandir = expandir
        self.verticalHeader().setDefaultSectionSize(ALTO_FILA)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding if expandir else QSizePolicy.Policy.Fixed)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def redimensionar(self, filas, columnas, encabezados, etiquetas_filas):
        """Cambia el tamaño conservando los valores existentes; las celdas nuevas valen 0."""
        self.setRowCount(filas)
        self.setColumnCount(columnas)
        self.setHorizontalHeaderLabels(encabezados)
        self.setVerticalHeaderLabels(etiquetas_filas)
        for i in range(filas):
            for j in range(columnas):
                if not self.item(i, j):
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.setItem(i, j, item)
        self.ajustar_altura()
        if self.currentItem() is None:
            self.setCurrentCell(0, 0)

    def limpiar(self):
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                self.item(i, j).setText("0")
        self.setCurrentCell(0, 0)

    def ajustar_altura(self):
        cabecera = 0
        if not self.horizontalHeader().isHidden():
            cabecera = max(self.horizontalHeader().height(), self.horizontalHeader().sizeHint().height())
        base = cabecera + 2 * self.frameWidth() + 4
        filas = min(self.rowCount(), self.filas_visibles)
        if self.expandir:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.setMinimumHeight(base + ALTO_FILA * filas)
            self.setMaximumHeight(base + ALTO_FILA_MAX * self.rowCount())
            self._repartir_filas()
            self._ajustar_tarjeta()
            return
        caben = self.rowCount() <= self.filas_visibles
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff if caben else Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setFixedHeight(base + ALTO_FILA * filas)

    def _ajustar_tarjeta(self):
        padre = self.parentWidget()
        if hasattr(padre, "ajustar_a_contenido"):
            padre.ajustar_a_contenido()

    def _repartir_filas(self):
        if self.rowCount():
            alto = self.viewport().height() // self.rowCount()
            self.verticalHeader().setDefaultSectionSize(max(ALTO_FILA, min(ALTO_FILA_MAX, alto)))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.expandir:
            self._repartir_filas()

    def showEvent(self, event):
        super().showEvent(event)
        self.ajustar_altura()

    def avanzar(self):
        fila, col = self.currentRow(), self.currentColumn() + 1
        if col >= self.columnCount():
            col, fila = 0, fila + 1
        if fila >= self.rowCount():
            self.fin_de_tabla.emit()
            return
        self.setCurrentCell(fila, col)

    def editor_activo(self):
        w = QApplication.focusWidget()
        if isinstance(w, QLineEdit) and self.state() == QAbstractItemView.State.EditingState:
            return w
        return None

    def terminar_edicion(self):
        editor = self.editor_activo()
        if editor:
            self.commitData(editor)
            self.closeEditor(editor, QAbstractItemDelegate.EndEditHint.NoHint)

    def closeEditor(self, editor, hint):
        if hint == QAbstractItemDelegate.EndEditHint.SubmitModelCache:
            super().closeEditor(editor, QAbstractItemDelegate.EndEditHint.NoHint)
            self.avanzar()
            return
        super().closeEditor(editor, hint)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and \
                not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.avanzar()
            return
        super().keyPressEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self.currentItem() is None and self.rowCount():
            self.setCurrentCell(0, 0)
        self.enfocada.emit()

    def focusOutEvent(self, event):
        # Solo la tabla en uso muestra la celda resaltada; la posición se conserva
        super().focusOutEvent(event)
        if self.state() != QAbstractItemView.State.EditingState:
            fila, col = self.currentRow(), self.currentColumn()
            self.clearSelection()
            self.selectionModel().setCurrentIndex(
                self.model().index(fila, col), self.selectionModel().SelectionFlag.NoUpdate)


class TecladoMatematico(Tarjeta):
    """Teclado de símbolos que escribe en la última tabla usada.

    Las tablas se recorren en el orden en que se registran: al terminar una,
    ↵ pasa a la siguiente; al terminar la última se emite `fin_de_entrada`.
    """

    fin_de_entrada = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tablas = []
        self.activa = None
        # Tamaño acotado: el espacio extra de la ventana es para la matriz, no para las teclas
        self.setMinimumHeight(200)
        self.setMaximumHeight(300)

        self.selector = ControlSegmentado(list(TECLAS_FUNCIONES))
        self.selector.cambiado.connect(self._cambiar_juego)
        self.cabecera.addWidget(self.selector)
        self.cabecera.addStretch()

        grid = QGridLayout()
        grid.setSpacing(6)
        grid.setColumnMinimumWidth(3, 4)
        grid.setColumnMinimumWidth(8, 4)
        for c in (0, 1, 2, 4, 5, 6, 7):
            grid.setColumnStretch(c, 10)
        grid.setColumnStretch(9, 13)

        self.teclas_funcion = []
        for k in range(12):
            b = self._tecla("", "fn")
            b.clicked.connect(lambda _, boton=b: self.insertar(boton.property("ins")))
            grid.addWidget(b, k // 3, k % 3)
            self.teclas_funcion.append(b)
        self._cambiar_juego(0)

        for etiqueta, ins, fila, col, ancho, tipo in TECLAS_NUMERICAS:
            b = self._tecla(etiqueta, tipo)
            b.clicked.connect(lambda _, t=ins: self.insertar(t))
            grid.addWidget(b, fila, col, 1, ancho)

        self.tecla_borrar = self._tecla("", "op")
        self.tecla_borrar.setToolTip("Borrar")
        self.tecla_borrar.setIconSize(QSize(22, 22))
        self.tecla_borrar.clicked.connect(self.retroceso)
        grid.addWidget(self.tecla_borrar, 0, 9, 2, 1)

        self.tecla_enter = self._tecla("", "enter")
        self.tecla_enter.setToolTip("Siguiente celda (al final, calcula)")
        self.tecla_enter.setIconSize(QSize(22, 22))
        self.tecla_enter.clicked.connect(self.enter)
        grid.addWidget(self.tecla_enter, 2, 9, 2, 1)

        self.lay.addLayout(grid, 1)

    def _tecla(self, texto, tipo):
        b = QPushButton(texto)
        b.setObjectName("Key")
        b.setProperty("tipo", tipo)
        b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setMinimumHeight(32)
        b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return b

    def _cambiar_juego(self, indice):
        for b, (etiqueta, ins) in zip(self.teclas_funcion, list(TECLAS_FUNCIONES.values())[indice]):
            b.setText(etiqueta)
            b.setProperty("ins", ins)

    def aplicar_tema(self, paleta):
        self.tecla_borrar.setIcon(icono("retroceso", paleta["muted"], 22))
        self.tecla_enter.setIcon(icono("enter", "#FFFFFF", 22))

    # ── Tablas conectadas ───────────────────────────────────────────

    def registrar(self, *tablas):
        for t in tablas:
            self.tablas.append(t)
            t.enfocada.connect(lambda tabla=t: self._activar(tabla))
            t.fin_de_tabla.connect(lambda tabla=t: self._siguiente_tabla(tabla))
        if self.activa is None and self.tablas:
            self.activa = self.tablas[0]
        # Al inicio solo la primera tabla muestra la celda resaltada
        for t in self.tablas[1:]:
            t.clearSelection()

    def _activar(self, tabla):
        self.activa = tabla
        for otra in self.tablas:
            if otra is not tabla:
                otra.clearSelection()

    def _siguiente_tabla(self, tabla):
        # Las tablas ocultas (p. ej. B cuando la operación no la usa) se saltan
        pendientes = [t for t in self.tablas[self.tablas.index(tabla) + 1:] if t.isVisible()]
        if pendientes:
            siguiente = pendientes[0]
            siguiente.setFocus()
            siguiente.setCurrentCell(0, 0)
            self._activar(siguiente)
        else:
            self.fin_de_entrada.emit()

    def _celda(self):
        tabla = self.activa
        if tabla is None:
            return None, None
        if tabla.currentItem() is None and tabla.rowCount():
            tabla.setCurrentCell(0, 0)
        return tabla, tabla.currentItem()

    # ── Acciones de las teclas ──────────────────────────────────────

    def insertar(self, texto):
        tabla, item = self._celda()
        if tabla is None:
            return
        editor = tabla.editor_activo()
        if editor:
            editor.insert(texto)
            return
        if item is not None:
            actual = item.text().strip()
            item.setText(texto if actual in ("", "0") else actual + texto)
        tabla.setFocus()

    def retroceso(self):
        tabla, item = self._celda()
        if tabla is None:
            return
        editor = tabla.editor_activo()
        if editor:
            editor.backspace()
            return
        if item is not None:
            item.setText(item.text()[:-1] or "0")
        tabla.setFocus()

    def enter(self):
        tabla, _ = self._celda()
        if tabla is None:
            return
        tabla.terminar_edicion()
        tabla.setFocus()
        tabla.avanzar()


class Resumen(QFrame):
    """Línea de resultado: punto de estado, título y valor a la derecha."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Summary")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 10, 14, 10)
        lay.setSpacing(10)
        self.punto = QLabel()
        self.punto.setObjectName("Dot")
        self.punto.setFixedSize(8, 8)
        self.titulo = QLabel()
        self.titulo.setObjectName("SummaryTitle")
        self.valor = QLabel()
        self.valor.setObjectName("SummaryValue")
        self.valor.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(self.punto)
        lay.addWidget(self.titulo)
        lay.addStretch()
        lay.addWidget(self.valor)
        self.setVisible(False)

    def mostrar(self, estado, titulo, valor=""):
        self.punto.setProperty("estado", estado)
        self.punto.style().unpolish(self.punto)
        self.punto.style().polish(self.punto)
        self.titulo.setText(titulo)
        self.valor.setText(valor)
        # El ancho se recalcula con la fuente ya aplicada por el estilo
        for lbl in (self.titulo, self.valor):
            lbl.ensurePolished()
            lbl.setMinimumWidth(lbl.sizeHint().width())
        self.setVisible(True)


def boton_principal(texto, tooltip, al_pulsar):
    """Botón rojo de la acción principal del módulo, para la barra superior."""
    b = QPushButton(texto)
    b.setObjectName("PrimaryButton")
    b.setToolTip(tooltip)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.clicked.connect(al_pulsar)
    return b


def contenedor_fila(*widgets, espacio=8):
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(espacio)
    for x in widgets:
        lay.addWidget(x)
    return w
