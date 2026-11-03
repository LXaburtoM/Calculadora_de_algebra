"""
Módulo 1: Interfaz Gráfica para Sistemas de Ecuaciones.
Tema: Resolución de SEL por Gauss y Gauss-Jordan con paso a paso (Sesiones 1-5).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QToolButton,
    QTableWidget, QTableWidgetItem, QTextEdit, QTextBrowser, QMessageBox, QHeaderView,
    QComboBox, QFrame, QSplitter, QSizePolicy, QMenu, QApplication, QLineEdit,
    QAbstractItemView, QAbstractItemDelegate
)
from PyQt6.QtGui import QActionGroup
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from fractions import Fraction
from core.parser import parse_expresion, formato_numero
from core.eliminacion_gaussiana import (
   reducir_por_filas, resolver_por_gauss, analizar_forma, clasificar_sistema,
    solucion_general, forma_vectorial, verificar_solucion, verificar_homogenea,
    nombre_var, entradas_principales
)
from core.modelos_aplicados import MODELOS
from gui.componentes import (
    BotonIcono, ControlSegmentado, PestanasSegmentadas, Tarjeta, icono
)

ANCHO_MIN = 5
SEP = "-" * 78
DIM_MAX = 10
ALTO_FILA = 44

METODOS = {"gauss": "Gauss", "gauss_jordan": "Gauss-Jordan"}

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

    def __init__(self, valor, descripcion):
        super().__init__()
        self.addItems([str(i) for i in range(1, DIM_MAX + 1)])
        self.setCurrentIndex(valor - 1)
        self.setToolTip(descripcion)
        self.setAccessibleName(descripcion)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.currentIndexChanged.connect(lambda i: self.valueChanged.emit(i + 1))

    def value(self):
        return self.currentIndex() + 1

    def setValue(self, v):
        self.setCurrentIndex(max(1, min(DIM_MAX, v)) - 1)


class SelectorFormato(ControlSegmentado):
    """Fracción exacta o decimal; responde a isChecked() como el checkbox anterior."""

    def __init__(self):
        super().__init__(["a/b", "0.5"])
        self.setToolTip("Mostrar resultados como fracciones o decimales")

    def isChecked(self):
        return self.indice() == 0


class TablaMatriz(QTableWidget):
    """Tabla de la matriz aumentada: Enter confirma y avanza a la celda siguiente."""

    enter_en_ultima = pyqtSignal()

    def avanzar(self):
        fila, col = self.currentRow(), self.currentColumn()
        col += 1
        if col >= self.columnCount():
            col, fila = 0, fila + 1
        if fila >= self.rowCount():
            self.enter_en_ultima.emit()
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

    def ajustar_altura(self, filas_visibles=8):
        cabecera = max(self.horizontalHeader().height(), self.horizontalHeader().sizeHint().height())
        filas = min(self.rowCount(), filas_visibles)
        self.setFixedHeight(cabecera + ALTO_FILA * filas + 2 * self.frameWidth() + 2)

    def showEvent(self, event):
        super().showEvent(event)
        self.ajustar_altura()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and \
                not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.avanzar()
            return
        super().keyPressEvent(event)


class EcuacionesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.metodo = "gauss_jordan"
        self._ultima_accion = None
        self._crear_barra()
        self.init_ui()

    # ── Barra superior del módulo (la coloca MainWindow) ─────────────

    def _crear_barra(self):
        self.barra_izq = QWidget()
        lay = QHBoxLayout(self.barra_izq)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        dims = QFrame()
        dims.setObjectName("Dims")
        dims.setFixedHeight(32)
        dl = QHBoxLayout(dims)
        dl.setContentsMargins(2, 2, 2, 2)
        dl.setSpacing(0)
        self.spin_m = SelectorDimension(3, "Ecuaciones (filas)")
        self.spin_n = SelectorDimension(3, "Variables (columnas)")
        x = QLabel("×")
        x.setObjectName("DimsX")
        dl.addWidget(self.spin_m)
        dl.addWidget(x)
        dl.addWidget(self.spin_n)
        lay.addWidget(dims)

        self.combo_modelos = QComboBox()
        self.combo_modelos.setToolTip("Plantillas de modelos aplicados")
        self.combo_modelos.addItem("Ejemplos")
        for m in MODELOS:
            self.combo_modelos.addItem(m["nombre"])
        self.combo_modelos.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_modelos.setMinimumContentsLength(12)
        self.combo_modelos.view().setMinimumWidth(380)
        self.combo_modelos.setFixedHeight(32)
        lay.addWidget(self.combo_modelos)

        # Acción principal con menú de métodos
        self.barra_der = QWidget()
        rl = QHBoxLayout(self.barra_der)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)
        self.btn_resolver = QPushButton(METODOS[self.metodo])
        self.btn_resolver.setObjectName("SplitMain")
        self.btn_resolver.setToolTip("Resolver (Ctrl+Enter)")
        self.btn_resolver.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_resolver.clicked.connect(self.accion_principal)
        self.btn_metodos = QToolButton()
        self.btn_metodos.setObjectName("SplitMenu")
        self.btn_metodos.setToolTip("Elegir método")
        self.btn_metodos.setIconSize(QSize(12, 12))
        self.btn_metodos.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_metodos.setCursor(Qt.CursorShape.PointingHandCursor)

        menu = QMenu(self.btn_metodos)
        grupo = QActionGroup(menu)
        self.acciones_metodo = {}
        for clave, nombre in METODOS.items():
            acc = menu.addAction(f"Resolver por {nombre}")
            acc.setCheckable(True)
            acc.setChecked(clave == self.metodo)
            acc.triggered.connect(lambda _, k=clave: self._elegir_metodo(k))
            grupo.addAction(acc)
            self.acciones_metodo[clave] = acc
        menu.addSeparator()
        menu.addAction("¿Está en forma escalonada?", self.analizar_forma_actual)
        self.btn_metodos.setMenu(menu)

        rl.addWidget(self.btn_resolver)
        rl.addWidget(self.btn_metodos)

    def barra_contexto(self):
        return self.barra_izq, self.barra_der

    def accion_principal(self):
        self.resolver_sistema(metodo=self.metodo)

    def _elegir_metodo(self, clave):
        self.metodo = clave
        self.btn_resolver.setText(METODOS[clave])
        self.resolver_sistema(metodo=clave)

    # ── Cuerpo ──────────────────────────────────────────────────────

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        divisor = QSplitter(Qt.Orientation.Horizontal)
        divisor.setHandleWidth(12)
        divisor.setChildrenCollapsible(False)

        izquierda = QWidget()
        izq = QVBoxLayout(izquierda)
        izq.setContentsMargins(0, 0, 0, 0)
        izq.setSpacing(12)
        izq.addWidget(self._crear_tarjeta_matriz())
        izq.addWidget(self._crear_teclado(), 1)

        divisor.addWidget(izquierda)
        divisor.addWidget(self._crear_tarjeta_resultados())
        divisor.setSizes([600, 600])
        layout.addWidget(divisor)

        self.spin_m.valueChanged.connect(self.actualizar_tabla)
        self.spin_n.valueChanged.connect(self.actualizar_tabla)
        self.combo_modelos.currentIndexChanged.connect(self.cargar_modelo_seleccionado)
        self.actualizar_tabla()

    def _crear_tarjeta_matriz(self):
        tarjeta = Tarjeta("[A | b]")
        tarjeta.setToolTip("Acepta enteros, decimales, fracciones (1/2) y funciones (pi, sen, cos…)")
        self.btn_limpiar = BotonIcono("borrar", "Limpiar tabla", 16)
        self.btn_limpiar.clicked.connect(self.limpiar_tabla)
        tarjeta.agregar_a_cabecera(self.btn_limpiar)

        self.tabla = TablaMatriz()
        self.tabla.verticalHeader().setDefaultSectionSize(ALTO_FILA)
        self.tabla.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.tabla.enter_en_ultima.connect(self.accion_principal)
        tarjeta.lay.addWidget(self.tabla)

        # Enunciado del modelo aplicado (visible al elegir un ejemplo)
        self.lbl_modelo_info = QTextBrowser()
        self.lbl_modelo_info.setObjectName("ModelInfo")
        self.lbl_modelo_info.setMaximumHeight(150)
        self.lbl_modelo_info.setVisible(False)
        tarjeta.lay.addWidget(self.lbl_modelo_info)
        return tarjeta

    def _crear_teclado(self):
        tarjeta = Tarjeta()
        tarjeta.setMinimumHeight(250)
        self.selector_teclado = ControlSegmentado(list(TECLAS_FUNCIONES))
        self.selector_teclado.cambiado.connect(self._cambiar_juego_teclas)
        tarjeta.cabecera.addWidget(self.selector_teclado)
        tarjeta.cabecera.addStretch()

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
            b.clicked.connect(lambda _, boton=b: self._insertar(boton.property("ins")))
            grid.addWidget(b, k // 3, k % 3)
            self.teclas_funcion.append(b)
        self._cambiar_juego_teclas(0)

        for etiqueta, ins, fila, col, ancho, tipo in TECLAS_NUMERICAS:
            b = self._tecla(etiqueta, tipo)
            b.clicked.connect(lambda _, t=ins: self._insertar(t))
            grid.addWidget(b, fila, col, 1, ancho)

        self.tecla_borrar = self._tecla("", "op")
        self.tecla_borrar.setToolTip("Borrar")
        self.tecla_borrar.setIconSize(QSize(22, 22))
        self.tecla_borrar.clicked.connect(self._retroceso)
        grid.addWidget(self.tecla_borrar, 0, 9, 2, 1)

        self.tecla_enter = self._tecla("", "enter")
        self.tecla_enter.setToolTip("Siguiente celda (en la última, resuelve)")
        self.tecla_enter.setIconSize(QSize(22, 22))
        self.tecla_enter.clicked.connect(self._enter)
        grid.addWidget(self.tecla_enter, 2, 9, 2, 1)

        tarjeta.lay.addLayout(grid, 1)
        return tarjeta

    def _tecla(self, texto, tipo):
        b = QPushButton(texto)
        b.setObjectName("Key")
        b.setProperty("tipo", tipo)
        b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setMinimumHeight(38)
        b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return b

    def _crear_tarjeta_resultados(self):
        tarjeta = Tarjeta()
        self.tabs = PestanasSegmentadas()
        self.txt_pasos = self._nueva_pestania("Pasos")
        self.txt_formas = self._nueva_pestania("Pivotes")
        self.txt_analisis = self._nueva_pestania("Existencia")
        self.txt_verif = self._nueva_pestania("Verificación")
        tarjeta.cabecera.addWidget(self.tabs.crear_control())
        tarjeta.cabecera.addStretch()

        self.chk_fracciones = SelectorFormato()
        self.chk_fracciones.cambiado.connect(self._repetir_ultima_accion)
        tarjeta.cabecera.addWidget(self.chk_fracciones)

        self.btn_copiar = BotonIcono("copiar", "Copiar pestaña actual", 16)
        self.btn_copiar.clicked.connect(self._copiar_resultado)
        tarjeta.cabecera.addWidget(self.btn_copiar)

        # Resumen de una línea encima del detalle
        self.resumen = QFrame()
        self.resumen.setObjectName("Summary")
        rl = QHBoxLayout(self.resumen)
        rl.setContentsMargins(12, 10, 14, 10)
        rl.setSpacing(10)
        self.punto = QLabel()
        self.punto.setObjectName("Dot")
        self.punto.setFixedSize(8, 8)
        self.lbl_resumen = QLabel()
        self.lbl_resumen.setObjectName("SummaryTitle")
        self.lbl_resumen_valor = QLabel()
        self.lbl_resumen_valor.setObjectName("SummaryValue")
        self.lbl_resumen_valor.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        rl.addWidget(self.punto)
        rl.addWidget(self.lbl_resumen)
        rl.addStretch()
        rl.addWidget(self.lbl_resumen_valor)
        self.resumen.setVisible(False)
        tarjeta.lay.addWidget(self.resumen)

        tarjeta.lay.addWidget(self.tabs, 1)
        return tarjeta

    def _nueva_pestania(self, titulo):
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.tabs.addTab(txt, titulo)
        return txt

    def aplicar_tema(self, paleta):
        for b in (self.btn_limpiar, self.btn_copiar):
            b.aplicar_tema(paleta)
        self.btn_metodos.setIcon(icono("chevron", "#FFFFFF", 12))
        self.tecla_borrar.setIcon(icono("retroceso", paleta["muted"], 22))
        self.tecla_enter.setIcon(icono("enter", "#FFFFFF", 22))

    # ── Teclado ─────────────────────────────────────────────────────

    def _cambiar_juego_teclas(self, indice):
        teclas = list(TECLAS_FUNCIONES.values())[indice]
        for b, (etiqueta, ins) in zip(self.teclas_funcion, teclas):
            b.setText(etiqueta)
            b.setProperty("ins", ins)

    def _celda_actual(self):
        item = self.tabla.currentItem()
        if item is None and self.tabla.rowCount():
            self.tabla.setCurrentCell(0, 0)
            item = self.tabla.currentItem()
        return item

    def _insertar(self, texto):
        editor = self.tabla.editor_activo()
        if editor:
            editor.insert(texto)
            return
        item = self._celda_actual()
        if item is None:
            return
        actual = item.text().strip()
        item.setText(texto if actual in ("", "0") else actual + texto)
        self.tabla.setFocus()

    def _retroceso(self):
        editor = self.tabla.editor_activo()
        if editor:
            editor.backspace()
            return
        item = self._celda_actual()
        if item is not None:
            item.setText(item.text()[:-1] or "0")
        self.tabla.setFocus()

    def _enter(self):
        self.tabla.terminar_edicion()
        self._celda_actual()
        self.tabla.avanzar()
        self.tabla.setFocus()

    # ── Resultados ──────────────────────────────────────────────────

    def _mostrar_resumen(self, estado, titulo, valor=""):
        self.punto.setProperty("estado", estado)
        self.punto.style().unpolish(self.punto)
        self.punto.style().polish(self.punto)
        self.lbl_resumen.setText(titulo)
        self.lbl_resumen_valor.setText(valor)
        self.resumen.setVisible(True)

    def _limpiar_resultados(self):
        """Los resultados dejan de valer cuando cambia la matriz de entrada."""
        self._ultima_accion = None
        self.resumen.setVisible(False)
        for txt in (self.txt_pasos, self.txt_formas, self.txt_analisis, self.txt_verif):
            txt.clear()

    def _repetir_ultima_accion(self):
        if self._ultima_accion == "forma":
            self.analizar_forma_actual()
        elif self._ultima_accion:
            self.resolver_sistema(metodo=self._ultima_accion)

    def _copiar_resultado(self):
        actual = self.tabs.currentWidget()
        if actual is not None:
            QApplication.clipboard().setText(actual.toPlainText())

    # ── Datos de la tabla ───────────────────────────────────────────

    def actualizar_tabla(self):
        m = self.spin_m.value()
        n = self.spin_n.value()

        self.tabla.setRowCount(m)
        self.tabla.setColumnCount(n + 1)

        headers = [nombre_var(j) for j in range(n)] + ["b"]
        self.tabla.setHorizontalHeaderLabels(headers)
        self.tabla.setVerticalHeaderLabels([f"R{i + 1}" for i in range(m)])

        for i in range(m):
            for j in range(n + 1):
                if not self.tabla.item(i, j):
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla.setItem(i, j, item)

        self.tabla.ajustar_altura()
        self._limpiar_resultados()
        if self.tabla.currentItem() is None:
            self.tabla.setCurrentCell(0, 0)

    def limpiar_tabla(self):
        for i in range(self.tabla.rowCount()):
            for j in range(self.tabla.columnCount()):
                self.tabla.item(i, j).setText("0")
        self.lbl_modelo_info.setVisible(False)
        self.combo_modelos.setCurrentIndex(0)
        self.tabla.setCurrentCell(0, 0)
        self._limpiar_resultados()

    def cargar_modelo_seleccionado(self, idx):
        if idx <= 0:
            self.lbl_modelo_info.setVisible(False)
            return

        modelo = MODELOS[idx - 1]
        self.spin_m.setValue(modelo["m"])
        self.spin_n.setValue(modelo["n"])

        for i in range(modelo["m"]):
            for j in range(modelo["n"] + 1):
                val = modelo["matriz"][i][j]
                self.tabla.item(i, j).setText(formato_numero(val, True))

        info_text = (
            f"<b>{modelo['nombre']}</b><br>"
            f"{modelo['descripcion']}<br><br>"
            f"<b>Variables:</b> {', '.join(modelo['variables'])}<br>"
            f"<b>Ecuaciones del modelo:</b><br>• " + "<br>• ".join(modelo["ecuaciones"])
        ).replace("\n", "<br>")
        self.lbl_modelo_info.setHtml(info_text)
        self.lbl_modelo_info.setVisible(True)
        self._limpiar_resultados()

    def leer_matriz(self):
        self.tabla.terminar_edicion()
        m = self.spin_m.value()
        n = self.spin_n.value()
        matriz = []
        errores = []

        for i in range(m):
            fila = []
            for j in range(n + 1):
                item = self.tabla.item(i, j)
                texto = item.text() if item else "0"
                valor, err = parse_expresion(texto)
                if err:
                    col_nombre = nombre_var(j) if j < n else "b"
                    errores.append(f"• Fila {i + 1}, columna '{col_nombre}': {err}")
                    fila.append(Fraction(0))
                else:
                    fila.append(valor)
            matriz.append(fila)

        if errores:
            return None, errores
        return matriz, None

    def _mostrar_errores(self, errores):
        plural = "s" if len(errores) > 1 else ""
        self._mostrar_resumen("error", f"Revisa {len(errores)} celda{plural}")
        msg = "Se encontraron errores en las celdas ingresadas:\n\n" + "\n".join(errores)
        QMessageBox.critical(self, "Error en los Datos", msg)

    # ── Análisis ────────────────────────────────────────────────────

    def analizar_forma_actual(self):
        self._ultima_accion = "forma"
        matriz, errores = self.leer_matriz()
        if errores:
            self._mostrar_errores(errores)
            return

        m = self.spin_m.value()
        n = self.spin_n.value()
        frac = self.chk_fracciones.isChecked()

        analisis = analizar_forma(matriz, m, n + 1)
        principales = analisis["principales"]

        lineas = [
            "ANÁLISIS DE FORMA ESCALONADA DE LA MATRIZ INGRESADA",
            SEP,
            "Matriz evaluada:",
            self._render_matriz(matriz, m, n + 1, principales, frac),
            "",
            "Entradas principales (el primer elemento no nulo de cada fila):",
        ]

        if principales:
            for fila in sorted(principales.keys()):
                col = principales[fila]
                val = formato_numero(matriz[fila][col], frac)
                col_nom = nombre_var(col) if col < n else "b (columna aumentada)"
                lineas.append(f"  • Fila {fila + 1}: valor {val} en columna {col_nom}")
        else:
            lineas.append("  (la matriz es completamente nula)")

        lineas.append("")
        lineas.append("Evaluación de las 5 propiedades formales (Lay, §1.2):")
        for num, desc, cumple, detalle in analisis["propiedades"]:
            simb = "✔" if cumple else "✘"
            lineas.append(f"  [{simb}] Propiedad {num}: {desc}")
            lineas.append(f"      -> {detalle}")

        lineas.append("")
        lineas.append(SEP)
        if analisis["reducida"]:
            lineas.append("DICTAMEN: La matriz está en FORMA ESCALONADA REDUCIDA (RREF).")
            self._mostrar_resumen("ok", "Forma escalonada reducida", "RREF")
        elif analisis["escalonada"]:
            lineas.append("DICTAMEN: La matriz está en FORMA ESCALONADA (REF), pero no reducida.")
            self._mostrar_resumen("aviso", "Forma escalonada, no reducida", "REF")
        else:
            lineas.append("DICTAMEN: La matriz NO está en forma escalonada.")
            self._mostrar_resumen("error", "No está en forma escalonada")
        lineas.append(SEP)

        self.txt_formas.setText("\n".join(lineas))
        self.tabs.setCurrentWidget(self.txt_formas)

    def resolver_sistema(self, metodo="gauss_jordan"):
        self._ultima_accion = metodo
        matriz, errores = self.leer_matriz()
        if errores:
            self._mostrar_errores(errores)
            return

        m = self.spin_m.value()
        n = self.spin_n.value()
        frac = self.chk_fracciones.isChecked()

        # 1. PESTAÑA 1: PROCEDIMIENTO PASO A PASO
        if metodo == "gauss":
            res_gauss = resolver_por_gauss(matriz, m, n, modo_fraccion=frac)
            resultado = res_gauss["resultado_base"]
            pasos_a_mostrar = res_gauss["pasos_gauss"]
            titulo_metodo = "MÉTODO DE ELIMINACIÓN DE GAUSS (Escalonamiento + Sustitución Hacia Atrás)"
        else:
            resultado = reducir_por_filas(matriz, m, n, modo_fraccion=frac, detener_si_inconsistente=True)
            pasos_a_mostrar = resultado["pasos"]
            titulo_metodo = "MÉTODO DE GAUSS-JORDAN (Fase Progresiva + Fase Regresiva a RREF)"

        pivotes_dict = {f: c for (f, c) in resultado["pivotes"]}

        lineas_pasos = [
            titulo_metodo,
            SEP,
            "Aritmética exacta con fracciones — sin redondeo.",
            "",
        ]

        for k, p in enumerate(pasos_a_mostrar, start=1):
            lineas_pasos.append(f"Paso {k}: {p['titulo']}")
            lineas_pasos.append(f"  {p['descripcion']}")
            pivs_hasta_ahora = pivotes_dict if p["fase"] in ("HITO_REF", "REGRESIVA", "HITO_RREF") else None
            lineas_pasos.append(self._render_matriz(p["matriz"], m, n + 1, pivs_hasta_ahora, frac))
            lineas_pasos.append("")

        if metodo == "gauss" and res_gauss["pasos_sustitucion"]:
            lineas_pasos.extend(res_gauss["pasos_sustitucion"])

        self.txt_pasos.setText("\n".join(lineas_pasos))

        # 2. PESTAÑA 2: FORMAS ESCALONADAS Y PIVOTES
        lineas_formas = [
            "IDENTIFICACIÓN DE PIVOTES Y FORMAS ESCALONADAS",
            SEP,
            "1. FORMA ESCALONADA (REF) — resultado de la fase progresiva:",
            self._render_matriz(resultado["ref"], m, n + 1, pivotes_dict, frac),
            "",
        ]

        if resultado["rref"] is not None:
            rref_principales = entradas_principales(resultado["rref"], m, n + 1)
            lineas_formas.extend([
                "2. FORMA ESCALONADA REDUCIDA (RREF) — resultado de la fase regresiva:",
                self._render_matriz(resultado["rref"], m, n + 1, rref_principales, frac),
                "",
            ])

        cols_piv = [c for c in resultado["cols_pivote"] if c < n]
        libres = [j for j in range(n) if j not in cols_piv]

        lineas_formas.extend([
            "3. POSICIONES Y COLUMNAS PIVOTE:",
            f"  • Posiciones pivote (fila, columna): " + (", ".join(f"(R{f+1}, {nombre_var(c) if c < n else 'b'})" for (f, c) in resultado["pivotes"]) if resultado["pivotes"] else "ninguna"),
            f"  • Columnas pivote de A: " + (", ".join(nombre_var(c) for c in cols_piv) if cols_piv else "ninguna"),
            f"  • Columnas libres (variables libres): " + (", ".join(nombre_var(j) for j in libres) if libres else "ninguna (todas son básicas)"),
            f"  • Rango de A: {len(cols_piv)}  (número de pivotes en la matriz de coeficientes)",
        ])
        self.txt_formas.setText("\n".join(lineas_formas))

        # 3. PESTAÑA 3: EXISTENCIA Y UNICIDAD
        clasif = clasificar_sistema(resultado, m, n)
        lineas_analisis = [
            "ANÁLISIS DE EXISTENCIA Y UNICIDAD (Lay, §1.2, Teorema 2)",
            SEP,
            f"Clasificación: {clasif['tipo']} — {clasif['mensaje']}",
            "",
            "Fundamentación teórica:",
            f"  {clasif['detalle']}",
            "",
        ]

        if resultado["consistente"] and resultado["rref"] is not None:
            despejes = solucion_general(resultado["rref"], m, n, resultado["pivotes"])
            lineas_analisis.append("Solución general (variables básicas despejadas):")
            for d in despejes:
                v = nombre_var(d["var"])
                if d["libre"]:
                    lineas_analisis.append(f"  • {v} es libre  ({v} ∈ ℝ)")
                else:
                    c_str = formato_numero(d["const"], frac)
                    parts = []
                    if d["const"] != 0 or not d["coefs"]:
                        parts.append(c_str)
                    for k_col, coef in d["coefs"].items():
                        c_k = formato_numero(coef, frac)
                        vk = nombre_var(k_col)
                        if coef == 1:
                            parts.append(f"+ {vk}")
                        elif coef == -1:
                            parts.append(f"− {vk}")
                        elif coef > 0:
                            parts.append(f"+ ({c_k})·{vk}")
                        else:
                            parts.append(f"− ({formato_numero(abs(coef), frac)})·{vk}")
                    lineas_analisis.append(f"  • {v} = " + " ".join(parts).lstrip("+ "))

            lineas_analisis.append("")
            p_vec, dirs = forma_vectorial(despejes, n, libres)
            lineas_analisis.append("Forma vectorial paramétrica:  x = p + Σ t_k · v_k")
            lineas_analisis.append(self._render_forma_vectorial(p_vec, dirs, n, frac))

        self.txt_analisis.setText("\n".join(lineas_analisis))

        # Resumen de una línea
        if clasif["tipo"] == "INCONSISTENTE":
            self._mostrar_resumen("error", "Sin solución", f"0 = {formato_numero(resultado['ref'][resultado['fila_contradiccion']][n], frac)}")
        elif clasif["tipo"] == "INDETERMINADO":
            self._mostrar_resumen("aviso", "Infinitas soluciones",
                                  "libres: " + ", ".join(nombre_var(j) for j in clasif["libres"]))
        else:
            despejes = solucion_general(resultado["rref"], m, n, resultado["pivotes"])
            self._mostrar_resumen("ok", "Solución única",
                                  "   ".join(f"{nombre_var(d['var'])} = {formato_numero(d['const'], frac)}" for d in despejes))

        # 4. PESTAÑA 4: VERIFICACIÓN
        lineas_verif = [
            "VERIFICACIÓN DE LA SOLUCIÓN POR SUSTITUCIÓN",
            SEP,
        ]

        if not resultado["consistente"]:
            lineas_verif.append("El sistema es INCONSISTENTE. No existe solución que sustituir.")
        elif resultado["rref"] is not None:
            despejes = solucion_general(resultado["rref"], m, n, resultado["pivotes"])
            sol_particular = [d["const"] for d in despejes]
            res_part = verificar_solucion(matriz, sol_particular, m, n)

            lineas_verif.append("1. Comprobación de la solución particular p (con todas las variables libres = 0):")
            lineas_verif.append("   Vector probado p = [" + ", ".join(formato_numero(x, frac) for x in sol_particular) + "]ᵀ")
            lineas_verif.append("")
            for r in res_part:
                simb = "✔ OK" if r["correcto"] else "✘ FALLA"
                lineas_verif.append(f"  [{simb}] {r['ecuacion']}: {r['expresion']} (esperado: {r['esperado']})")

            p_vec, dirs = forma_vectorial(despejes, n, libres)
            if dirs:
                lineas_verif.append("")
                lineas_verif.append("2. Comprobación de los vectores dirección v_k (deben cumplir A · v_k = 0):")
                for k_col, v in dirs:
                    lineas_verif.append(f"  Vector asociado a variable libre {nombre_var(k_col)}:")
                    res_h = verificar_homogenea(matriz, v, m, n)
                    for r in res_h:
                        simb = "✔ OK" if r["correcto"] else "✘ FALLA"
                        lineas_verif.append(f"    [{simb}] {r['ecuacion']}: valor = {r['valor']} (esperado: 0)")

        self.txt_verif.setText("\n".join(lineas_verif))
        self.tabs.setCurrentWidget(self.txt_pasos)

    def _render_matriz(self, matriz, m, n_cols, pivotes=None, modo_fraccion=True):
        ancho = 0
        celdas = []
        for i in range(m):
            fila_strs = []
            for j in range(n_cols):
                s = formato_numero(matriz[i][j], modo_fraccion)
                if pivotes and i in pivotes and pivotes[i] == j:
                    s = f"[{s}]"
                fila_strs.append(s)
                ancho = max(ancho, len(s))
            celdas.append(fila_strs)

        ancho = max(ancho, ANCHO_MIN)
        lineas = []
        for i in range(m):
            coefs = "  ".join(celdas[i][j].rjust(ancho) for j in range(n_cols - 1))
            b_str = celdas[i][-1].rjust(ancho)
            lineas.append(f"  │  {coefs}  │  {b_str}  │")
        return "\n".join(lineas)

    def _render_forma_vectorial(self, p, dirs, n, modo_fraccion):
        p_strs = [formato_numero(x, modo_fraccion) for x in p]
        dir_strs = [[formato_numero(v[i], modo_fraccion) for i in range(n)] for (_, v) in dirs]

        ancho_p = max(len(s) for s in p_strs)
        anchos_d = [max(len(d[i]) for i in range(n)) for d in dir_strs] if dirs else []

        lineas = []
        for i in range(n):
            var_nom = nombre_var(i).rjust(3)
            p_val = p_strs[i].rjust(ancho_p)
            fila = f"  │ {var_nom} │   =   │ {p_val} │"
            for k, (col_libre, _) in enumerate(dirs):
                d_val = dir_strs[k][i].rjust(anchos_d[k])
                vk_nom = nombre_var(col_libre)
                fila += f"   +   {vk_nom} · │ {d_val} │"
            lineas.append(fila)
        return "\n".join(lineas)
