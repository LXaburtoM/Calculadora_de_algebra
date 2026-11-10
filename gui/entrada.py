"""
Componentes de entrada compartidos por los módulos.
Tema: tablas de matrices, teclado matemático, selectores compactos y resumen de resultados (PyQt6).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QToolButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFrame, QSizePolicy, QApplication, QLineEdit,
    QHeaderView, QAbstractItemView, QAbstractItemDelegate, QTextEdit, QSplitter,
    QStyledItemDelegate, QStyleOptionViewItem, QStyle
)
from PyQt6.QtGui import QPen, QColor, QFont
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from fractions import Fraction
from PyQt6.QtWidgets import QMessageBox
from core.parser import parse_expresion
from gui.componentes import BotonIcono, ControlSegmentado, Tarjeta, EstadoVacio, icono
from gui.animaciones import aparecer, NORMAL
from gui import sonido

DIM_MAX = 10
ALTO_FILA = 44
ALTO_FILA_MAX = 64
ALTO_TECLADO = 216   # igual en todos los módulos: el espacio libre es para la matriz

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

    def __init__(self, valor, descripcion, maximo=DIM_MAX, minimo=1):
        super().__init__()
        self.minimo, self.maximo = minimo, maximo
        self.addItems([str(i) for i in range(minimo, maximo + 1)])
        self.setCurrentIndex(valor - minimo)
        self.setToolTip(descripcion)
        self.setAccessibleName(descripcion)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.currentIndexChanged.connect(lambda i: self.valueChanged.emit(i + minimo))

    def set_maximo(self, maximo):
        """Cambia el valor máximo conservando la selección si sigue siendo válida."""
        actual = min(self.value(), maximo)
        self.blockSignals(True)
        self.clear()
        self.maximo = maximo
        self.addItems([str(i) for i in range(self.minimo, maximo + 1)])
        self.setCurrentIndex(actual - self.minimo)
        self.blockSignals(False)

    def value(self):
        return self.currentIndex() + self.minimo

    def setValue(self, v):
        self.setCurrentIndex(max(self.minimo, min(self.maximo, v)) - self.minimo)


def grupo_dimensiones(partes):
    """Agrupa selectores y textos cortos (p. ej. ["ℝ", sel_n, "→ ℝ", sel_m]) en una sola pastilla."""
    marco = QFrame()
    marco.setObjectName("Dims")
    marco.setFixedHeight(32)
    lay = QHBoxLayout(marco)
    lay.setContentsMargins(2, 2, 8, 2)
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


def _partes_numero(texto):
    """Separa '12.5' en ('12', '.5') y '3/4' en ('3', '/4') para alinear por el separador."""
    for i, caracter in enumerate(texto):
        if caracter in "./,":
            return texto[:i], texto[i:]
    return texto, ""


class DelegadoCuadricula(QStyledItemDelegate):
    """Dibuja las celdas: números alineados por el separador decimal y solo líneas internas.

    La cuadrícula de Qt pinta también el borde derecho e inferior de la última
    columna y fila, que se superponen con el marco redondeado de la tabla y se
    ven como líneas dobles.
    """

    def __init__(self, tabla):
        super().__init__(tabla)
        self.tabla = tabla
        self.color = QColor("#2A2B30")

    def _anchos_columna(self, columna, metricas):
        """Ancho máximo de la parte entera y de la parte decimal en la columna."""
        izq = der = 0
        for fila in range(self.tabla.rowCount()):
            item = self.tabla.item(fila, columna)
            entero, decimal = _partes_numero(item.text() if item else "")
            izq = max(izq, metricas.horizontalAdvance(entero))
            der = max(der, metricas.horizontalAdvance(decimal))
        return izq, der

    def paint(self, pintor, opcion, indice):
        opt = QStyleOptionViewItem(opcion)
        self.initStyleOption(opt, indice)
        texto, opt.text = opt.text, ""
        estilo = opt.widget.style() if opt.widget else QApplication.style()
        estilo.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, pintor, opt.widget)

        # Bloque centrado en la celda con el separador en la misma x para toda la columna
        r = opcion.rect
        metricas = opt.fontMetrics
        izq, der = self._anchos_columna(indice.column(), metricas)
        separador = r.center().x() - (izq + der) // 2 + izq
        entero, decimal = _partes_numero(texto)
        pintor.save()
        pintor.setFont(opt.font)
        pintor.setPen(opt.palette.color(opt.palette.ColorRole.Text))
        alto = r.height()
        pintor.drawText(separador - metricas.horizontalAdvance(entero), r.top(), metricas.horizontalAdvance(entero), alto,
                        Qt.AlignmentFlag.AlignVCenter, entero)
        if decimal:
            pintor.drawText(separador, r.top(), metricas.horizontalAdvance(decimal), alto,
                            Qt.AlignmentFlag.AlignVCenter, decimal)
        pintor.restore()
        pintor.save()
        pintor.setPen(QPen(self.color, 1))
        if indice.column() < self.tabla.columnCount() - 1:
            pintor.drawLine(r.topRight(), r.bottomRight())
        if indice.row() < self.tabla.rowCount() - 1:
            pintor.drawLine(r.bottomLeft(), r.bottomRight())
        pintor.restore()


class TablaMatriz(QTableWidget):
    """Tabla de valores: Enter confirma la celda y avanza a la siguiente.

    Con `expandir=True` la tabla toma el espacio vertical libre: las filas crecen
    hasta ALTO_FILA_MAX y, si no caben, aparece la barra de desplazamiento.
    """

    fin_de_tabla = pyqtSignal()
    enfocada = pyqtSignal()

    def __init__(self, filas_visibles=8, expandir=False, encabezado_filas=True, parent=None):
        super().__init__(parent)
        self.filas_visibles = filas_visibles
        self.expandir = expandir
        # En vectores de una fila el título de la tarjeta ya dice qué es (v₁, u, b…)
        self.verticalHeader().setVisible(encabezado_filas)
        self.verticalHeader().setDefaultSectionSize(ALTO_FILA)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding if expandir else QSizePolicy.Policy.Fixed)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setShowGrid(False)
        fuente = self.font()
        fuente.setFeature(QFont.Tag("tnum"), 1)   # cifras de ancho fijo: las columnas no bailan
        self.setFont(fuente)
        self.delegado = DelegadoCuadricula(self)
        self.setItemDelegate(self.delegado)

    def aplicar_tema(self, paleta):
        self.delegado.color = QColor(paleta["sep"])
        self.viewport().update()

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
            self._ubicar(0, 0)

    def _ubicar(self, fila, col):
        """Mueve la celda actual sin resaltarla; el resaltado aparece al enfocar la tabla."""
        modelo = self.selectionModel()
        modelo.setCurrentIndex(self.model().index(fila, col), modelo.SelectionFlag.NoUpdate)

    def limpiar(self):
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                self.item(i, j).setText("0")
        self.setCurrentCell(0, 0)

    def ajustar_altura(self):
        cabecera = 0
        if not self.horizontalHeader().isHidden():
            cabecera = max(self.horizontalHeader().height(), self.horizontalHeader().sizeHint().height())
        base = cabecera + 2 * self.frameWidth()
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
        if not self.rowCount():
            return
        disponible = self.viewport().height()
        alto = disponible // self.rowCount()
        if alto < ALTO_FILA:
            # No caben todas: se reparte el alto entre las filas que sí caben completas
            visibles = max(1, disponible // ALTO_FILA)
            alto = disponible // visibles
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
        if self.rowCount():
            fila, col = max(self.currentRow(), 0), max(self.currentColumn(), 0)
            self.setCurrentCell(fila, col)
        self.enfocada.emit()

    def focusOutEvent(self, event):
        # Solo la tabla en uso muestra la celda resaltada; la posición se conserva
        super().focusOutEvent(event)
        if self.state() != QAbstractItemView.State.EditingState:
            fila, col = self.currentRow(), self.currentColumn()
            self.clearSelection()
            self._ubicar(fila, col)


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
        self.setFixedHeight(ALTO_TECLADO)

        self.selector = ControlSegmentado(list(TECLAS_FUNCIONES))
        self.selector.cambiado.connect(self._cambiar_juego)
        self.cabecera.addWidget(self.selector)
        self.cabecera.addStretch()

        grid = QGridLayout()
        grid.setSpacing(8)
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
        b.setMinimumHeight(30)
        b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        b.pressed.connect(sonido.reproducir)
        return b

    def _cambiar_juego(self, indice):
        for b, (etiqueta, ins) in zip(self.teclas_funcion, list(TECLAS_FUNCIONES.values())[indice]):
            b.setText(etiqueta)
            b.setProperty("ins", ins)

    def aplicar_tema(self, paleta):
        self.tecla_borrar.setIcon(icono("retroceso", paleta["muted"], 22))
        self.tecla_enter.setIcon(icono("enter", paleta.get("on_red", "#FFFFFF"), 22))

    # ── Tablas conectadas ───────────────────────────────────────────

    def registrar(self, *tablas):
        for t in tablas:
            self.tablas.append(t)
            t.enfocada.connect(lambda tabla=t: self._activar(tabla))
            t.fin_de_tabla.connect(lambda tabla=t: self._siguiente_tabla(tabla))
        if self.activa is None and self.tablas:
            self.activa = self.tablas[0]

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
        lay.setContentsMargins(12, 8, 16, 8)
        lay.setSpacing(8)
        self.punto = QLabel()
        self.punto.setObjectName("Dot")
        self.punto.setFixedSize(8, 8)
        self.titulo = QLabel()
        self.titulo.setObjectName("SummaryTitle")
        self.valor = QLabel()
        self.valor.setObjectName("SummaryValue")
        self.valor.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
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
        if self.isHidden():
            self.setVisible(True)
            aparecer(self, NORMAL)


def boton_principal(texto, tooltip, al_pulsar):
    """Botón rojo de la acción principal del módulo, para la barra superior."""
    b = QPushButton(texto)
    b.setObjectName("PrimaryButton")
    b.setToolTip(tooltip)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.pressed.connect(sonido.reproducir)
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


# ── Piezas de página para módulos con secciones ─────────────────────

class TarjetaResultado(Tarjeta):
    """Resultado de una sección: resumen, acciones sobre el resultado (Ans) y detalle."""

    def __init__(self, formato=True, mensaje_vacio="Los resultados aparecerán aquí al calcular.", parent=None):
        super().__init__("Resultado", parent)
        self.cabecera.addStretch()
        self.formato = SelectorFormato() if formato else None
        if self.formato:
            self.cabecera.addWidget(self.formato)
        self.texto = QTextEdit()
        self.texto.setReadOnly(True)
        self.texto.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.estado_vacio = EstadoVacio(self.texto, mensaje_vacio)
        self.btn_copiar = BotonIcono("copiar", "Copiar resultado", 16)
        self.btn_copiar.clicked.connect(lambda: QApplication.clipboard().setText(self.texto.toPlainText()))
        self.cabecera.addWidget(self.btn_copiar)
        self.resumen = Resumen()
        self.lay.addWidget(self.resumen)
        self.acciones = QWidget()
        fila = QHBoxLayout(self.acciones)
        fila.setContentsMargins(0, 0, 0, 0)
        fila.setSpacing(4)
        fila.addStretch()
        self.acciones.setVisible(False)
        self.lay.addWidget(self.acciones)
        self.lay.addWidget(self.texto, 1)

    def agregar_accion(self, texto, tooltip, accion):
        """Botón de 1 clic que actúa sobre el último resultado; visible cuando hay uno."""
        b = QToolButton()
        b.setText(texto)
        b.setToolTip(tooltip)
        b.setObjectName("ActionChip")
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.clicked.connect(accion)
        fila = self.acciones.layout()
        fila.insertWidget(fila.count() - 1, b)
        return b

    def aplicar_tema(self, paleta):
        self.btn_copiar.aplicar_tema(paleta)


def tarjeta_tabla(titulo, tabla, tooltip=""):
    t = Tarjeta(titulo)
    if tooltip:
        t.setToolTip(tooltip)
    t.lay.addWidget(tabla)
    return t


def pagina_seccion(controles, columna, resultados):
    """Fila de controles de la sección + [columna de entrada | resultados].

    `columna` es una lista de (widget, estiramiento); None como widget añade un espacio.
    """
    pagina = QWidget()
    lay = QVBoxLayout(pagina)
    lay.setContentsMargins(12, 8, 12, 12)
    lay.setSpacing(8)
    fila = QHBoxLayout()
    fila.setSpacing(8)
    for c in controles:
        fila.addWidget(c)
    fila.addStretch()
    lay.addLayout(fila)

    divisor = QSplitter(Qt.Orientation.Horizontal)
    divisor.setHandleWidth(12)
    divisor.setChildrenCollapsible(False)
    col = QWidget()
    cl = QVBoxLayout(col)
    cl.setContentsMargins(0, 0, 0, 0)
    cl.setSpacing(12)
    for w, estira in columna:
        if w is None:
            cl.addStretch(estira)
        else:
            cl.addWidget(w, estira)
    divisor.addWidget(col)
    divisor.addWidget(resultados)
    divisor.setSizes([600, 600])
    lay.addWidget(divisor, 1)
    return pagina


# ── Lectura de tablas y errores ─────────────────────────────────────

def leer_matriz_segura(tabla, filas, columnas, etiqueta="A"):
    """Lee una matriz de una tabla validando cada celda.
    Retorna (matriz, lista_de_errores).
    """
    matriz = []
    errores = []
    for i in range(filas):
        fila = []
        for j in range(columnas):
            item = tabla.item(i, j)
            texto = item.text() if item else "0"
            val, err = parse_expresion(texto)
            if err:
                errores.append(f"{etiqueta}[{i+1},{j+1}]: {err}")
            fila.append(val if val is not None else Fraction(0))
        matriz.append(fila)
    return matriz, errores


def mostrar_error(parent, errores):
    """Muestra un QMessageBox con la lista de errores si hay alguno.
    Retorna True si hubo errores (para cortar el flujo).
    """
    if errores:
        QMessageBox.critical(parent, "Error en los datos", "\n".join(errores))
        return True
    return False
