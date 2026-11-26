"""
Módulo 8: Interfaz Gráfica para Métodos Iterativos (Jacobi y Gauss-Seidel).
Tema: Solución aproximada de sistemas de ecuaciones lineales Ax = b,
      análisis de dominancia diagonal, reordenamiento de ecuaciones,
      comparación de convergencia y contraste con solución exacta.
Asignatura: Álgebra Lineal (MTM0120) - Universidad Americana (UAM).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from __future__ import annotations

import math
from typing import Any
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QSplitter, QMessageBox, QFrame, QTextEdit,
    QScrollArea, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView,
    QApplication, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from core.metodos_iterativos import (
    metodo_jacobi, metodo_gauss_seidel, analizar_diagonal_y_convergencia,
    evaluar_reordenamiento_filas, comparar_jacobi_y_seidel, CASOS_PRUEBA,
    ResultadoMetodoIterativo
)
from core.parser import parse_expresion, formato_numero
from gui.componentes import ControlSegmentado, PestanasSegmentadas, Tarjeta, BotonIcono, EstadoVacio
from gui.entrada import (
    SelectorDimension, TablaMatriz, Resumen, boton_principal, contenedor_fila
)

SEP = "=" * 78
SUBSEP = "-" * 78

OPCIONES_METODO = ["Ambos (Comparativa)", "Jacobi", "Gauss-Seidel"]


def _nombre_var(indice: int) -> str:
    """Retorna x1, x2, x3... o x, y, z para n pequeño."""
    if indice == 0:
        return "x₁"
    elif indice == 1:
        return "x₂"
    elif indice == 2:
        return "x₃"
    elif indice == 3:
        return "x₄"
    elif indice == 4:
        return "x₅"
    elif indice == 5:
        return "x₆"
    elif indice == 6:
        return "x₇"
    elif indice == 7:
        return "x₈"
    return f"x_{indice+1}"


class IterativosWidget(QWidget):
    """
    Widget principal del Módulo 8: Métodos Numéricos Iterativos (Jacobi y Gauss-Seidel).
    Permite configurar Ax = b, vector inicial x0, tolerancia y máximo de iteraciones,
    evaluar reordenamiento de filas, inspeccionar tablas completas de iteraciones,
    analizar gráficas de error semilogarítmicas y validar con la solución exacta de referencia.
    """

    def __init__(self):
        super().__init__()
        self._resultado_jacobi: ResultadoMetodoIterativo | None = None
        self._resultado_seidel: ResultadoMetodoIterativo | None = None
        self._ultimo_analisis: dict[str, Any] | None = None
        self._ultimo_reordenamiento: dict[str, Any] | None = None
        self._paleta_tema: dict[str, Any] | None = None

        self._crear_barra()
        self.init_ui()

    # ── Barra superior del módulo (controlada por MainWindow) ─────────────

    def _crear_barra(self):
        self.barra_izq = QWidget()
        lay_izq = QHBoxLayout(self.barra_izq)
        lay_izq.setContentsMargins(0, 0, 0, 0)
        lay_izq.setSpacing(8)

        lbl_dim = QLabel("Dimensión n:")
        self.spin_n = SelectorDimension(3, "Dimensión del sistema (n × n)", maximo=8, minimo=2)
        self.spin_n.valueChanged.connect(self._al_cambiar_dimension)
        lay_izq.addWidget(lbl_dim)
        lay_izq.addWidget(self.spin_n)

        self.combo_casos = QComboBox()
        self.combo_casos.setToolTip("Cargar casos de prueba obligatorios para la defensa")
        self.combo_casos.addItem("Casos de prueba...")
        for c in CASOS_PRUEBA:
            self.combo_casos.addItem(c["nombre"])
        self.combo_casos.currentIndexChanged.connect(self._cargar_caso_seleccionado)
        self.combo_casos.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_casos.setMinimumContentsLength(16)
        self.combo_casos.setFixedHeight(32)
        lay_izq.addWidget(self.combo_casos)

        # Selector de método visible
        self.selector_metodo = ControlSegmentado(OPCIONES_METODO)
        self.selector_metodo.setToolTip("Seleccionar método(s) a calcular")

        self.btn_ejecutar = boton_principal(
            "Calcular",
            "Ejecutar métodos iterativos (Ctrl+Enter)",
            self.accion_principal
        )
        self.barra_der = contenedor_fila(self.selector_metodo, self.btn_ejecutar)

    def barra_contexto(self):
        return self.barra_izq, self.barra_der

    def accion_principal(self):
        self.ejecutar_calculo()

    # ── Construcción de la interfaz ───────────────────────────────────

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        divisor = QSplitter(Qt.Orientation.Horizontal)
        divisor.setHandleWidth(12)
        divisor.setChildrenCollapsible(False)

        divisor.addWidget(self._crear_panel_izquierdo())
        divisor.addWidget(self._crear_panel_derecho())
        divisor.setSizes([550, 750])

        layout.addWidget(divisor)
        self._actualizar_tablas_dimension(3)

    # ── Panel Izquierdo: Entradas y Diagnóstico ───────────────────────

    def _crear_panel_izquierdo(self) -> QWidget:
        contenedor = QWidget()
        lay = QVBoxLayout(contenedor)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        # 1. Tarjeta Matriz A y Vector b en forma aumentada [A | b]
        tarjeta_matriz = Tarjeta("Sistema de Ecuaciones [A | b]")
        tarjeta_matriz.setToolTip("Matriz cuadrada de coeficientes A y vector b de términos independientes")

        btn_limpiar = BotonIcono("borrar", "Limpiar matriz y vector b", 16)
        btn_limpiar.clicked.connect(self._limpiar_tabla_ab)
        tarjeta_matriz.cabecera.addWidget(btn_limpiar)

        self.tabla_ab = TablaMatriz(filas_visibles=5, expandir=False)
        tarjeta_matriz.lay.addWidget(self.tabla_ab)

        # Descripción del caso cargado (si aplica)
        self.lbl_info_caso = QLabel()
        self.lbl_info_caso.setObjectName("ModelInfo")
        self.lbl_info_caso.setWordWrap(True)
        self.lbl_info_caso.setVisible(False)
        tarjeta_matriz.lay.addWidget(self.lbl_info_caso)

        lay.addWidget(tarjeta_matriz)

        # 2. Tarjeta Vector Inicial x^(0)
        tarjeta_x0 = Tarjeta("Vector Inicial x⁽⁰⁾")
        tarjeta_x0.setToolTip("Aproximación inicial para comenzar las iteraciones (por defecto ceros)")

        btn_ceros = QPushButton("Todo 0")
        btn_ceros.setToolTip("Inicializar x⁽⁰⁾ con ceros")
        btn_ceros.setFixedHeight(26)
        btn_ceros.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ceros.clicked.connect(self._llenar_x0_ceros)
        tarjeta_x0.cabecera.addWidget(btn_ceros)

        btn_unos = QPushButton("Todo 1")
        btn_unos.setToolTip("Inicializar x⁽⁰⁾ con unos")
        btn_unos.setFixedHeight(26)
        btn_unos.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_unos.clicked.connect(self._llenar_x0_unos)
        tarjeta_x0.cabecera.addWidget(btn_unos)

        self.tabla_x0 = TablaMatriz(filas_visibles=1, expandir=False, encabezado_filas=False)
        tarjeta_x0.lay.addWidget(self.tabla_x0)
        lay.addWidget(tarjeta_x0)

        # 3. Tarjeta Parámetros Numéricos
        tarjeta_params = Tarjeta("Parámetros Numéricos")
        grid_params = QGridLayout()
        grid_params.setSpacing(8)

        lbl_tol = QLabel("Tolerancia (ε):")
        self.txt_tol = QLineEdit("0.0001")
        self.txt_tol.setPlaceholderText("Ej: 0.0001 o 1e-4")

        lbl_max = QLabel("Máximo de iteraciones:")
        self.txt_max_iter = QLineEdit("100")
        self.txt_max_iter.setPlaceholderText("Ej: 100")

        grid_params.addWidget(lbl_tol, 0, 0)
        grid_params.addWidget(self.txt_tol, 0, 1)
        grid_params.addWidget(lbl_max, 1, 0)
        grid_params.addWidget(self.txt_max_iter, 1, 1)
        tarjeta_params.lay.addLayout(grid_params)
        lay.addWidget(tarjeta_params)

        # 4. Tarjeta Diagnóstico y Asistente de Reordenamiento
        tarjeta_diag = Tarjeta("Estructura de Diagonal y Reordenamiento")
        lay_diag = QVBoxLayout()
        lay_diag.setSpacing(6)

        fila_btn_diag = QHBoxLayout()
        self.btn_evaluar_diag = QPushButton("🔍 Evaluar Diagonal y Reordenamiento")
        self.btn_evaluar_diag.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_evaluar_diag.clicked.connect(self._evaluar_diagonal_gui)
        fila_btn_diag.addWidget(self.btn_evaluar_diag)

        self.btn_aplicar_reord = QPushButton("⚡ Aplicar Reordenamiento")
        self.btn_aplicar_reord.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_aplicar_reord.setToolTip("Permutar las ecuaciones en la tabla según el ordenamiento óptimo encontrado")
        self.btn_aplicar_reord.setEnabled(False)
        self.btn_aplicar_reord.clicked.connect(self._aplicar_reordenamiento_a_tabla)
        fila_btn_diag.addWidget(self.btn_aplicar_reord)
        lay_diag.addLayout(fila_btn_diag)

        self.lbl_estado_diag = QLabel("Presione 'Evaluar Diagonal' para analizar ceros, dominancia y radio espectral.")
        self.lbl_estado_diag.setWordWrap(True)
        self.lbl_estado_diag.setObjectName("DiagInfo")
        lay_diag.addWidget(self.lbl_estado_diag)

        tarjeta_diag.lay.addLayout(lay_diag)
        lay.addWidget(tarjeta_diag)

        lay.addStretch()
        return contenedor

    # ── Panel Derecho: Resultados, Tablas y Gráficas ──────────────────

    def _crear_panel_derecho(self) -> QWidget:
        tarjeta_res = Tarjeta("Resultados y Análisis Comparativo")

        self.resumen = Resumen()
        tarjeta_res.lay.addWidget(self.resumen)

        self.tabs = PestanasSegmentadas()

        # Pestaña 1: Resumen & Comparación
        self.txt_comparacion = QTextEdit()
        self.txt_comparacion.setReadOnly(True)
        self.txt_comparacion.setFont(QFont("Consolas", 10))
        EstadoVacio(self.txt_comparacion, "Configure el sistema y presione 'Calcular' para ver la comparación.")
        self.tabs.addTab(self.txt_comparacion, "Comparación")

        # Pestaña 2: Tabla Jacobi
        self.panel_tabla_j = self._crear_panel_tabla_metodo("Jacobi")
        self.tabs.addTab(self.panel_tabla_j, "Tabla Jacobi")

        # Pestaña 3: Tabla Gauss-Seidel
        self.panel_tabla_gs = self._crear_panel_tabla_metodo("Gauss-Seidel")
        self.tabs.addTab(self.panel_tabla_gs, "Tabla Gauss-Seidel")

        # Pestaña 4: Gráfica Comparativa (Matplotlib)
        self.panel_grafica = self._crear_panel_grafica()
        self.tabs.addTab(self.panel_grafica, "Gráfica de Error")

        # Pestaña 5: Fórmulas y Paso a Paso
        self.txt_pasos = QTextEdit()
        self.txt_pasos.setReadOnly(True)
        self.txt_pasos.setFont(QFont("Consolas", 10))
        EstadoVacio(self.txt_pasos, "Aquí se detallará el desarrollo analítico y las fórmulas de iteración.")
        self.tabs.addTab(self.txt_pasos, "Paso a Paso")

        # Control de pestañas en la cabecera
        tarjeta_res.cabecera.addWidget(self.tabs.crear_control())
        tarjeta_res.cabecera.addStretch()

        self.btn_copiar = BotonIcono("copiar", "Copiar contenido de la pestaña activa", 16)
        self.btn_copiar.clicked.connect(self._copiar_pestana_activa)
        tarjeta_res.cabecera.addWidget(self.btn_copiar)

        tarjeta_res.lay.addWidget(self.tabs, 1)
        return tarjeta_res

    def _crear_panel_tabla_metodo(self, metodo: str) -> QWidget:
        contenedor = QWidget()
        lay = QVBoxLayout(contenedor)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        barra_herramientas = QHBoxLayout()
        lbl_info = QLabel(f"Historial iterativo paso a paso ({metodo}):")
        barra_herramientas.addWidget(lbl_info)
        barra_herramientas.addStretch()

        btn_copiar_csv = QPushButton("Copiar CSV")
        btn_copiar_csv.setFixedHeight(26)
        btn_copiar_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_copiar_csv.clicked.connect(lambda: self._copiar_tabla_como_csv(metodo))
        barra_herramientas.addWidget(btn_copiar_csv)

        btn_guardar_csv = QPushButton("Guardar CSV...")
        btn_guardar_csv.setFixedHeight(26)
        btn_guardar_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_guardar_csv.clicked.connect(lambda: self._guardar_tabla_csv(metodo))
        barra_herramientas.addWidget(btn_guardar_csv)

        lay.addLayout(barra_herramientas)

        tabla = QTableWidget()
        tabla.setAlternatingRowColors(True)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabla.verticalHeader().setVisible(False)
        fuente = tabla.font()
        fuente.setFeature(QFont.Tag("tnum"), 1)
        tabla.setFont(fuente)

        if metodo == "Jacobi":
            self.tabla_widget_j = tabla
        else:
            self.tabla_widget_gs = tabla

        lay.addWidget(tabla, 1)
        return contenedor

    def _crear_panel_grafica(self) -> QWidget:
        contenedor = QWidget()
        lay = QVBoxLayout(contenedor)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        self.figura = Figure(figsize=(6, 4.5), dpi=100)
        self.canvas = FigureCanvas(self.figura)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setFixedHeight(34)

        lay.addWidget(self.toolbar)
        lay.addWidget(self.canvas, 1)

        self._dibujar_grafica_vacia()
        return contenedor

    # ── Redimensionamiento y Población de Tablas ─────────────────────

    def _al_cambiar_dimension(self, n: int):
        self._actualizar_tablas_dimension(n)
        self._limpiar_resultados()

    def _actualizar_tablas_dimension(self, n: int):
        encabezados_ab = [_nombre_var(j) for j in range(n)] + ["b"]
        filas_ab = [f"Ec. {i+1}" for i in range(n)]
        self.tabla_ab.redimensionar(n, n + 1, encabezados_ab, filas_ab)

        encabezados_x0 = [f"{_nombre_var(j)}⁽⁰⁾" for j in range(n)]
        self.tabla_x0.redimensionar(1, n, encabezados_x0, ["x⁽⁰⁾"])

        # Por defecto inicializar x0 en ceros
        for j in range(n):
            if not self.tabla_x0.item(0, j) or self.tabla_x0.item(0, j).text().strip() == "":
                item = QTableWidgetItem("0")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_x0.setItem(0, j, item)

    def _limpiar_tabla_ab(self):
        self.tabla_ab.limpiar()
        self.combo_casos.setCurrentIndex(0)
        self.lbl_info_caso.setVisible(False)
        self._limpiar_resultados()

    def _llenar_x0_ceros(self):
        n = self.spin_n.value()
        for j in range(n):
            item = self.tabla_x0.item(0, j)
            if item:
                item.setText("0")
            else:
                self.tabla_x0.setItem(0, j, QTableWidgetItem("0"))

    def _llenar_x0_unos(self):
        n = self.spin_n.value()
        for j in range(n):
            item = self.tabla_x0.item(0, j)
            if item:
                item.setText("1")
            else:
                self.tabla_x0.setItem(0, j, QTableWidgetItem("1"))

    def _limpiar_resultados(self):
        self._resultado_jacobi = None
        self._resultado_seidel = None
        self._ultimo_reordenamiento = None
        self.btn_aplicar_reord.setEnabled(False)
        self.lbl_estado_diag.setText("Presione 'Evaluar Diagonal' para analizar ceros, dominancia y radio espectral.")
        self.resumen.setVisible(False)
        self.txt_comparacion.clear()
        self.txt_pasos.clear()
        self.tabla_widget_j.setRowCount(0)
        self.tabla_widget_gs.setRowCount(0)
        self._dibujar_grafica_vacia()

    def _cargar_caso_seleccionado(self, idx: int):
        if idx <= 0:
            self.lbl_info_caso.setVisible(False)
            return

        caso = CASOS_PRUEBA[idx - 1]
        A = np.array(caso["A"])
        b = np.array(caso["b"])
        x0 = np.array(caso.get("x0", [0.0] * len(b)))
        n = len(b)

        self.spin_n.setValue(n)

        # Llenar matriz A y vector b
        for i in range(n):
            for j in range(n):
                val = A[i, j]
                self.tabla_ab.item(i, j).setText(formato_numero(val, True))
            self.tabla_ab.item(i, n).setText(formato_numero(b[i], True))

        # Llenar vector inicial x0
        for j in range(n):
            self.tabla_x0.item(0, j).setText(formato_numero(x0[j], True))

        # Llenar parámetros
        self.txt_tol.setText(str(caso.get("tol", 1e-4)))
        self.txt_max_iter.setText(str(caso.get("max_iter", 100)))

        # Mostrar información del caso
        self.lbl_info_caso.setText(
            f"<b>{caso['nombre']}</b><br>"
            f"<i>Categoría: {caso['categoria']}</i><br>"
            f"{caso['descripcion'].replace(chr(10), '<br>')}"
        )
        self.lbl_info_caso.setVisible(True)
        self._limpiar_resultados()
        self._evaluar_diagonal_gui()

    # ── Lectura de Datos de la GUI ────────────────────────────────────

    def _leer_sistema_desde_gui(self) -> tuple[np.ndarray | None, np.ndarray | None, np.ndarray | None, float, int, str | None]:
        n = self.spin_n.value()
        A_lista = []
        b_lista = []

        # Leer matriz aumentada [A | b]
        for i in range(n):
            fila_a = []
            for j in range(n):
                item = self.tabla_ab.item(i, j)
                txt = item.text() if item else "0"
                val, err = parse_expresion(txt)
                if err:
                    return None, None, None, 0.0, 0, f"Error en elemento A[{i+1}, {j+1}]: {err}"
                fila_a.append(float(val) if val is not None else 0.0)
            A_lista.append(fila_a)

            item_b = self.tabla_ab.item(i, n)
            txt_b = item_b.text() if item_b else "0"
            val_b, err_b = parse_expresion(txt_b)
            if err_b:
                return None, None, None, 0.0, 0, f"Error en término independiente b[{i+1}]: {err_b}"
            b_lista.append(float(val_b) if val_b is not None else 0.0)

        # Leer vector inicial x0
        x0_lista = []
        for j in range(n):
            item_x = self.tabla_x0.item(0, j)
            txt_x = item_x.text() if item_x else "0"
            val_x, err_x = parse_expresion(txt_x)
            if err_x:
                return None, None, None, 0.0, 0, f"Error en vector inicial x⁽⁰⁾[{j+1}]: {err_x}"
            x0_lista.append(float(val_x) if val_x is not None else 0.0)

        # Leer tolerancia
        try:
            tol_str = self.txt_tol.text().strip().replace(",", ".")
            tol = float(tol_str)
            if tol <= 0:
                return None, None, None, 0.0, 0, "La tolerancia ε debe ser un número positivo (ej: 0.0001)."
        except ValueError:
            return None, None, None, 0.0, 0, "Valor de tolerancia inválido. Ingrese un decimal (ej: 0.0001 o 1e-4)."

        # Leer máximo de iteraciones
        try:
            max_iter = int(self.txt_max_iter.text().strip())
            if max_iter < 1:
                return None, None, None, 0.0, 0, "El máximo de iteraciones debe ser un entero mayor o igual a 1."
        except ValueError:
            return None, None, None, 0.0, 0, "Número máximo de iteraciones inválido. Ingrese un entero positivo."

        return np.array(A_lista), np.array(b_lista), np.array(x0_lista), tol, max_iter, None

    # ── Evaluación de Diagonal y Reordenamiento ───────────────────────

    def _evaluar_diagonal_gui(self):
        A, b, _, _, _, err = self._leer_sistema_desde_gui()
        if err:
            QMessageBox.critical(self, "Error en los datos", err)
            return

        reord = evaluar_reordenamiento_filas(A, b)
        self._ultimo_reordenamiento = reord
        analisis = reord["analisis"]
        self._ultimo_analisis = analisis

        n = analisis["n"]
        partes = []

        # 1. Ceros en la diagonal
        if analisis["tiene_ceros"]:
            filas_c = [str(idx + 1) for idx in analisis["ceros_indices"]]
            partes.append(f"❌ <b>Ceros en diagonal:</b> Se detectaron ceros en las filas: {', '.join(filas_c)}.")
        else:
            partes.append("✅ <b>Ceros en diagonal:</b> Ninguno (diagonal sin ceros).")

        # 2. Dominancia diagonal
        if analisis["es_estrictamente_dominante"]:
            partes.append("✅ <b>Dominancia:</b> Estrictamente diagonal dominante (garantiza convergencia).")
        elif analisis["es_debilmente_dominante"]:
            partes.append("ℹ️ <b>Dominancia:</b> Débilmente diagonal dominante.")
        else:
            partes.append("⚠️ <b>Dominancia:</b> NO es diagonal dominante (condición suficiente no cumplida).")

        # 3. Radios espectrales
        if analisis["rho_jacobi"] is not None and analisis["rho_seidel"] is not None:
            rho_j = analisis["rho_jacobi"]
            rho_gs = analisis["rho_seidel"]
            conv_j = "Convergente (ρ<1) ✅" if rho_j < 1.0 else "Divergente (ρ≥1) ⚠️"
            conv_gs = "Convergente (ρ<1) ✅" if rho_gs < 1.0 else "Divergente (ρ≥1) ⚠️"
            partes.append(f"📐 <b>Radio espectral:</b> ρ(T_J) = {rho_j:.4f} [{conv_j}], ρ(T_GS) = {rho_gs:.4f} [{conv_gs}].")

        # 4. Resultado del reordenamiento
        if reord["requiere_reordenamiento"] and reord["es_posible"]:
            partes.append(f"<br>💡 <b>Oportunidad de Reordenamiento:</b> {reord['mensaje']}")
            if reord["cambios"]:
                partes.append("<b>Intercambios sugeridos:</b><br>" + "<br>".join(f"• {c}" for c in reord["cambios"]))
            self.btn_aplicar_reord.setEnabled(True)
        elif not reord["es_posible"]:
            partes.append(f"<br>❌ {reord['mensaje']}")
            self.btn_aplicar_reord.setEnabled(False)
        else:
            partes.append(f"<br>ℹ️ {reord['mensaje']}")
            self.btn_aplicar_reord.setEnabled(False)

        self.lbl_estado_diag.setText("<br>".join(partes))

    def _aplicar_reordenamiento_a_tabla(self):
        if not self._ultimo_reordenamiento or not self._ultimo_reordenamiento["es_posible"]:
            return

        A_nuevo = self._ultimo_reordenamiento["A_reordenada"]
        b_nuevo = self._ultimo_reordenamiento["b_reordenado"]
        n = len(b_nuevo)

        for i in range(n):
            for j in range(n):
                self.tabla_ab.item(i, j).setText(formato_numero(A_nuevo[i, j], True))
            self.tabla_ab.item(i, n).setText(formato_numero(b_nuevo[i], True))

        self.resumen.mostrar("ok", "Reordenamiento Aplicado", "Filas permutadas con éxito en la tabla")
        self._evaluar_diagonal_gui()

    # ── Ejecución de los Métodos Iterativos ───────────────────────────

    def ejecutar_calculo(self):
        A, b, x0, tol, max_iter, err = self._leer_sistema_desde_gui()
        if err:
            QMessageBox.critical(self, "Error en los datos de entrada", err)
            return

        # Comprobar ceros en la diagonal antes de iniciar el cálculo
        diag = np.diag(A)
        indices_cero = [i + 1 for i, d in enumerate(diag) if math.isclose(d, 0.0, abs_tol=1e-12)]
        if indices_cero:
            self._evaluar_diagonal_gui()
            reord_sug = ""
            if self._ultimo_reordenamiento and self._ultimo_reordenamiento["es_posible"]:
                reord_sug = (
                    "💡 OPORTUNIDAD: Se detectó una permutación de ecuaciones válida.\n"
                    "Presione el botón '⚡ Aplicar Reordenamiento' en el panel izquierdo para reorganizar\n"
                    "el sistema automáticamente y luego vuelva a presionar 'Calcular'."
                )
            else:
                reord_sug = (
                    "❌ No existe ningún reordenamiento de ecuaciones matemáticamente posible que elimine\n"
                    "los ceros de la diagonal principal. El sistema no admite solución iterativa en esta forma."
                )

            msg_cero = (
                f"{SEP}\n"
                f"❌ ADVERTENCIA: CEROS EN LA DIAGONAL PRINCIPAL (FILAS: {indices_cero})\n"
                f"{SEP}\n\n"
                "Los métodos iterativos de Jacobi y Gauss-Seidel requieren dividir entre los coeficientes\n"
                "de la diagonal principal (a_ii). La presencia de ceros en la diagonal hace imposible\n"
                "el cálculo (división por cero).\n\n"
                f"{reord_sug}\n\n"
                f"{SEP}"
            )
            self.resumen.mostrar("error", "Cero en Diagonal Principal", f"Filas: {indices_cero}")
            self.txt_comparacion.setPlainText(msg_cero)
            self.txt_pasos.setPlainText(msg_cero)
            self.tabs.setCurrentIndex(0)
            return

        # Ejecutar métodos según el selector
        modo = self.selector_metodo.indice()  # 0: Ambos, 1: Jacobi, 2: Gauss-Seidel

        res_j = None
        res_gs = None

        if modo in (0, 1):
            res_j = metodo_jacobi(A, b, x0, tol, max_iter)
            self._resultado_jacobi = res_j

        if modo in (0, 2):
            res_gs = metodo_gauss_seidel(A, b, x0, tol, max_iter)
            self._resultado_seidel = res_gs

        # Si el usuario eligió solo uno, computamos internamente el otro para poder
        # ofrecer la comparativa completa y la gráfica comparativa solicitada en el programa.
        if modo == 1:
            res_gs = metodo_gauss_seidel(A, b, x0, tol, max_iter)
            self._resultado_seidel = res_gs
        elif modo == 2:
            res_j = metodo_jacobi(A, b, x0, tol, max_iter)
            self._resultado_jacobi = res_j

        # Generar comparación y análisis
        comp = comparar_jacobi_y_seidel(res_j, res_gs, A, b)
        self._mostrar_resumen_y_comparacion(res_j, res_gs, comp, A, b)
        self._poblar_tabla_widget(self.tabla_widget_j, res_j)
        self._poblar_tabla_widget(self.tabla_widget_gs, res_gs)
        self._actualizar_grafica(res_j, res_gs, tol)
        self._generar_paso_a_paso(A, b, x0, res_j, res_gs)

    # ── Presentación de Resultados en Pestañas ────────────────────────

    def _mostrar_resumen_y_comparacion(
        self,
        res_j: ResultadoMetodoIterativo,
        res_gs: ResultadoMetodoIterativo,
        comp: dict[str, Any],
        A: np.ndarray,
        b: np.ndarray
    ):
        n = len(b)
        nombres = [_nombre_var(i) for i in range(n)]

        # Estado del pill de resumen superior
        if res_j.convergio and res_gs.convergio:
            self.resumen.mostrar("ok", "Convergencia Exitosa", f"Jacobi: {res_j.num_iteraciones} iters | Gauss-Seidel: {res_gs.num_iteraciones} iters")
        elif res_gs.convergio or res_j.convergio:
            metodo_ok = "Gauss-Seidel" if res_gs.convergio else "Jacobi"
            self.resumen.mostrar("warn", "Convergencia Parcial", f"Solo {metodo_ok} alcanzó la tolerancia requerida")
        else:
            self.resumen.mostrar("error", "No Convergencia / Divergencia", "Ningún método satisfizo la tolerancia")

        lineas: list[str] = [
            SEP,
            "         COMPARACIÓN EXHAUSTIVA DE MÉTODOS ITERATIVOS (PROGRAMA 8)",
            SEP,
            f"Veredicto: {comp['veredicto']}",
            SUBSEP,
            "",
            "1. RESUMEN DE RENDIMIENTO Y CONVERGENCIA:",
            f"   • Método de Jacobi:",
            f"     - Iteraciones requeridas: {res_j.num_iteraciones}",
            f"     - Estado: {res_j.mensaje}",
            f"     - Tiempo de cómputo: {res_j.tiempo_ms:.2f} ms",
            f"     - Error final ||x^(k) - x^(k-1)||_∞: {res_j.error_final:.6e}" if not math.isnan(res_j.error_final) else "     - Error final: N/A",
            f"     - Residuo final ||Ax - b||_∞: {res_j.residuo_final:.6e}",
            "",
            f"   • Método de Gauss-Seidel:",
            f"     - Iteraciones requeridas: {res_gs.num_iteraciones}",
            f"     - Estado: {res_gs.mensaje}",
            f"     - Tiempo de cómputo: {res_gs.tiempo_ms:.2f} ms",
            f"     - Error final ||x^(k) - x^(k-1)||_∞: {res_gs.error_final:.6e}" if not math.isnan(res_gs.error_final) else "     - Error final: N/A",
            f"     - Residuo final ||Ax - b||_∞: {res_gs.residuo_final:.6e}",
            SUBSEP,
            "",
            "2. SOLUCIONES APROXIMADAS OBTENIDAS:",
        ]

        # Vector de solución Jacobi
        sol_j_str = ", ".join(f"{nombre} = {val:+.6f}" for nombre, val in zip(nombres, res_j.x_final))
        sol_gs_str = ", ".join(f"{nombre} = {val:+.6f}" for nombre, val in zip(nombres, res_gs.x_final))
        lineas.append(f"   • Solución Jacobi:       [{sol_j_str}]")
        lineas.append(f"   • Solución Gauss-Seidel: [{sol_gs_str}]")

        if comp["diff_entre_metodos"] is not None:
            lineas.append(f"   • Diferencia máxima entre ambos métodos ||x_J - x_GS||_∞: {comp['diff_entre_metodos']:.6e}")
            if comp["vector_diferencia"] is not None:
                vec_d_str = ", ".join(f"Δ{nombre} = {d:.6e}" for nombre, d in zip(nombres, comp["vector_diferencia"]))
                lineas.append(f"     Vector de diferencias: [{vec_d_str}]")

        lineas.extend([
            "",
            SUBSEP,
            "3. VALIDACIÓN DE RESULTADOS CON SOLUCIÓN DE REFERENCIA (REQUISITO 5):",
            "   (La función de referencia se utiliza exclusivamente para comprobar la precisión",
            "    de las aproximaciones numéricas, nunca para sustituir la implementación iterativa)",
        ])

        if comp["x_ref"] is not None:
            sol_ref_str = ", ".join(f"{nombre} = {val:+.6f}" for nombre, val in zip(nombres, comp["x_ref"]))
            lineas.append(f"   • Solución exacta de referencia (numpy.linalg.solve):")
            lineas.append(f"     [{sol_ref_str}]")
            lineas.append(f"   • Residuo de la solución de referencia: {comp['residuo_ref']:.6e}")
            if comp["cond_matriz"] is not None:
                lineas.append(f"   • Número de condición de la matriz A: cond(A) = {comp['cond_matriz']:.4f}")

            if comp["error_ref_j"] is not None:
                lineas.append(f"   • Discrepancia Jacobi vs Referencia ||x_J - x_ref||_∞: {comp['error_ref_j']:.6e}")
            if comp["error_ref_gs"] is not None:
                lineas.append(f"   • Discrepancia Gauss-Seidel vs Referencia ||x_GS - x_ref||_∞: {comp['error_ref_gs']:.6e}")
        else:
            lineas.append("   ⚠️ La matriz A es singular o está mal condicionada; no se pudo obtener solución de referencia única.")

        lineas.extend([
            "",
            SUBSEP,
            "4. DIAGNÓSTICO MATEMÁTICO DE CONVERGENCIA:",
        ])

        analisis = analizar_diagonal_y_convergencia(A)
        lineas.append(f"   {analisis['mensaje_dominancia'].replace(chr(10), chr(10) + '   ')}")
        lineas.append("")
        lineas.append("   Desglose de dominancia fila por fila:")
        for det in analisis["detalles_filas"]:
            cumple = "CUMPLE (|a_ii| > ∑|a_ij|) ✅" if det["estricta"] else "NO CUMPLE ⚠️"
            lineas.append(
                f"   • Fila {det['fila']}: |a_{{{det['fila']},{det['fila']}}}| = {det['abs_a_ii']:.4f}  vs  "
                f"∑ fuera = {det['suma_fuera']:.4f}  ==> Margen: {det['diferencia']:+.4f}  [{cumple}]"
            )

        if analisis["rho_jacobi"] is not None and analisis["rho_seidel"] is not None:
            lineas.append("")
            lineas.append("   Radios espectrales teóricos (Condición Necesaria y Suficiente):")
            lineas.append(f"   • Jacobi:       ρ(T_J)  = {analisis['rho_jacobi']:.6f}  (Converge si y solo si < 1)")
            lineas.append(f"   • Gauss-Seidel: ρ(T_GS) = {analisis['rho_seidel']:.6f}  (Converge si y solo si < 1)")

        lineas.append(SEP)
        self.txt_comparacion.setPlainText("\n".join(lineas))

    def _poblar_tabla_widget(self, tabla: QTableWidget, res: ResultadoMetodoIterativo | None):
        if not res or not res.historial:
            tabla.setRowCount(0)
            return

        n = len(res.historial[0].x)
        encabezados = ["k"] + [_nombre_var(j) for j in range(n)] + ["||x⁽ᵏ⁾ - x⁽ᵏ⁻¹⁾||_∞", "||Ax⁽ᵏ⁾ - b||_∞"]
        tabla.setColumnCount(len(encabezados))
        tabla.setHorizontalHeaderLabels(encabezados)
        tabla.setRowCount(len(res.historial))

        for fila_idx, reg in enumerate(res.historial):
            # Iteración k
            item_k = QTableWidgetItem(str(reg.k))
            item_k.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tabla.setItem(fila_idx, 0, item_k)

            # Variables x_1, x_2, ..., x_n
            for col_x, val in enumerate(reg.x):
                item_x = QTableWidgetItem(f"{val:.6f}")
                item_x.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                tabla.setItem(fila_idx, 1 + col_x, item_x)

            # Error
            if math.isnan(reg.error):
                txt_err = "—"
            else:
                txt_err = f"{reg.error:.6e}"
            item_err = QTableWidgetItem(txt_err)
            item_err.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tabla.setItem(fila_idx, 1 + n, item_err)

            # Residuo
            item_res = QTableWidgetItem(f"{reg.residuo:.6e}")
            item_res.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tabla.setItem(fila_idx, 2 + n, item_res)

        tabla.resizeColumnsToContents()

    def _dibujar_grafica_vacia(self):
        self.figura.clear()
        ax = self.figura.add_subplot(111)
        ax.set_title("Gráfica Comparativa del Error (||x⁽ᵏ⁾ - x⁽ᵏ⁻¹⁾||_∞ vs Iteración k)", fontsize=11)
        ax.set_xlabel("Número de Iteración (k)")
        ax.set_ylabel("Error entre iteraciones (Escala Logarítmica)")
        ax.text(
            0.5, 0.5, "Ejecute los métodos para visualizar las curvas de convergencia.",
            ha="center", va="center", transform=ax.transAxes, color="#888888", fontsize=11
        )
        self._estilizar_ejes(ax)
        self.canvas.draw()

    def _estilizar_ejes(self, ax):
        """Aplica colores adaptativos según el tema activo."""
        paleta = self._paleta_tema
        if paleta:
            bg_color = paleta.get("surface", "#141416")
            input_color = paleta.get("input", "#101012")
            text_color = paleta.get("text", "#F2F2F4")
            sep_color = paleta.get("sep", "#232327")
            muted_color = paleta.get("muted", "#9B9BA1")

            self.figura.patch.set_facecolor(bg_color)
            ax.set_facecolor(input_color)
            ax.tick_params(colors=muted_color)
            ax.xaxis.label.set_color(text_color)
            ax.yaxis.label.set_color(text_color)
            ax.title.set_color(text_color)
            for spine in ax.spines.values():
                spine.set_color(sep_color)
            ax.grid(True, linestyle="--", alpha=0.4, color=sep_color)
        else:
            ax.grid(True, linestyle="--", alpha=0.5)

    def _actualizar_grafica(
        self,
        res_j: ResultadoMetodoIterativo,
        res_gs: ResultadoMetodoIterativo,
        tol: float
    ):
        self.figura.clear()
        ax = self.figura.add_subplot(111)

        datos_graficables = False

        # Datos de Jacobi
        if res_j and len(res_j.historial) > 1:
            iters_j = [r.k for r in res_j.historial[1:] if not math.isnan(r.error) and r.error > 0]
            errs_j = [r.error for r in res_j.historial[1:] if not math.isnan(r.error) and r.error > 0]
            if iters_j:
                ax.plot(
                    iters_j, errs_j, marker="o", markersize=4,
                    linewidth=2.0, color="#2B82D9", label=f"Jacobi ({res_j.num_iteraciones} iters)"
                )
                datos_graficables = True

        # Datos de Gauss-Seidel
        if res_gs and len(res_gs.historial) > 1:
            iters_gs = [r.k for r in res_gs.historial[1:] if not math.isnan(r.error) and r.error > 0]
            errs_gs = [r.error for r in res_gs.historial[1:] if not math.isnan(r.error) and r.error > 0]
            if iters_gs:
                ax.plot(
                    iters_gs, errs_gs, marker="s", markersize=4,
                    linewidth=2.0, color="#E0393E", label=f"Gauss-Seidel ({res_gs.num_iteraciones} iters)"
                )
                datos_graficables = True

        if datos_graficables:
            # Línea horizontal para la tolerancia requerida
            ax.axhline(tol, color="#5BB98C", linestyle="--", linewidth=1.5, label=f"Tolerancia ε = {tol}")
            ax.set_yscale("log")
            ax.set_title("Convergencia del Error: Jacobi vs Gauss-Seidel (Semilog-y)", fontsize=11, fontweight="bold")
            ax.set_xlabel("Número de Iteración (k)")
            ax.set_ylabel("Error ||x⁽ᵏ⁾ - x⁽ᵏ⁻¹⁾||_∞ (log)")
            ax.legend(loc="upper right", framealpha=0.8)
        else:
            ax.text(
                0.5, 0.5, "Los métodos no generaron iteraciones con errores válidos para graficar.",
                ha="center", va="center", transform=ax.transAxes, color="#888888", fontsize=11
            )

        self._estilizar_ejes(ax)
        self.canvas.draw()

    def _generar_paso_a_paso(
        self,
        A: np.ndarray,
        b: np.ndarray,
        x0: np.ndarray,
        res_j: ResultadoMetodoIterativo,
        res_gs: ResultadoMetodoIterativo
    ):
        n = len(b)
        nombres = [_nombre_var(i) for i in range(n)]

        lineas: list[str] = [
            SEP,
            "     DESARROLLO ANALÍTICO Y FÓRMULAS DE ITERACIÓN (PASO A PASO)",
            SEP,
            "1. DESPEJE ALGEBRAICO DEL SISTEMA Ax = b:",
            "   Para cada ecuación i, se despeja la variable correspondiente sobre la diagonal a_ii:",
            ""
        ]

        for i in range(n):
            a_ii = A[i, i]
            b_i = b[i]
            terminos = []
            for j in range(n):
                if j != i:
                    coef = A[i, j]
                    signo = "-" if coef >= 0 else "+"
                    terminos.append(f"{signo} {abs(coef):.4f}·{nombres[j]}")
            resto = " ".join(terminos)
            lineas.append(f"   • {nombres[i]} = (1 / {a_ii:.4f}) · [ {b_i:+.4f} {resto} ]")

        lineas.extend([
            "",
            SUBSEP,
            "2. PRIMERA ITERACIÓN (k = 1) - COMPARACIÓN DETALLADA:",
            f"   Vector inicial: x⁽⁰⁾ = [{', '.join(f'{nombres[i]} = {x0[i]:.4f}' for i in range(n))}]",
            "",
            "   A) MÉTODO DE JACOBI (Actualización Simultánea):",
            "      Cada x_i⁽¹⁾ se calcula usando EXCLUSIVAMENTE los valores de x⁽⁰⁾:"
        ])

        # Mostrar cálculo de Jacobi paso a paso para k=1
        for i in range(n):
            a_ii = A[i, i]
            b_i = b[i]
            partes_num = []
            suma_val = 0.0
            for j in range(n):
                if j != i:
                    c = A[i, j]
                    v = x0[j]
                    partes_num.append(f"({c:+.2f})·({v:.2f})")
                    suma_val += c * v
            num_final = b_i - suma_val
            val_final = num_final / a_ii
            lineas.append(f"      • {nombres[i]}⁽¹⁾ = [ {b_i:.2f} - ({' + '.join(partes_num)}) ] / {a_ii:.2f} = {num_final:.4f} / {a_ii:.2f} = {val_final:.6f}")

        lineas.extend([
            "",
            "   B) MÉTODO DE GAUSS-SEIDEL (Actualización Inmediata/Sucesiva):",
            "      Cada x_i⁽¹⁾ utiliza INMEDIATAMENTE los nuevos valores ya calculados en esta iteración:"
        ])

        # Mostrar cálculo de Gauss-Seidel paso a paso para k=1
        x_trabajo = x0.copy()
        for i in range(n):
            a_ii = A[i, i]
            b_i = b[i]
            partes_num = []
            suma_val = 0.0
            for j in range(n):
                if j != i:
                    c = A[i, j]
                    v = x_trabajo[j]
                    etiqueta = "recién calculado" if j < i else "del paso anterior"
                    partes_num.append(f"({c:+.2f})·{nombres[j]}[{v:.4f} ({etiqueta})]")
                    suma_val += c * v
            num_final = b_i - suma_val
            val_final = num_final / a_ii
            x_trabajo[i] = val_final
            lineas.append(f"      • {nombres[i]}⁽¹⁾ = [ {b_i:.2f} - ∑ ] / {a_ii:.2f} = {val_final:.6f}")

        lineas.extend([
            "",
            SUBSEP,
            "3. EXPLICACIÓN DE LA DIFERENCIA ALGORÍTMICA:",
            "   • En Jacobi, los componentes se calculan de manera independiente y en paralelo,",
            "     por lo que la convergencia suele requerir el doble de iteraciones.",
            "   • En Gauss-Seidel, la incorporación inmediata de la información más reciente",
            "     acelera la marcha hacia la solución (reduciendo a la mitad las iteraciones en",
            "     la mayoría de sistemas simétricos o estrictamente dominantes).",
            SEP
        ])

        self.txt_pasos.setPlainText("\n".join(lineas))

    # ── Exportación y Copiado ─────────────────────────────────────────

    def _copiar_pestana_activa(self):
        idx = self.tabs.currentIndex()
        if idx == 0:
            QApplication.clipboard().setText(self.txt_comparacion.toPlainText())
        elif idx == 1:
            self._copiar_tabla_como_csv("Jacobi")
        elif idx == 2:
            self._copiar_tabla_como_csv("Gauss-Seidel")
        elif idx == 4:
            QApplication.clipboard().setText(self.txt_pasos.toPlainText())
        else:
            QMessageBox.information(self, "Copiar", "Para la gráfica, utilice el botón de guardado en la barra superior de la misma.")

    def _copiar_tabla_como_csv(self, metodo: str):
        res = self._resultado_jacobi if metodo == "Jacobi" else self._resultado_seidel
        if not res or not res.historial:
            QMessageBox.warning(self, "Tabla vacía", "Ejecute el cálculo antes de copiar la tabla.")
            return

        df = res.a_dataframe([_nombre_var(i) for i in range(len(res.x_final))])
        csv_texto = df.to_csv(index=False)
        QApplication.clipboard().setText(csv_texto)
        QMessageBox.information(self, "Copiado", f"Tabla de {metodo} copiada al portapapeles en formato CSV.")

    def _guardar_tabla_csv(self, metodo: str):
        res = self._resultado_jacobi if metodo == "Jacobi" else self._resultado_seidel
        if not res or not res.historial:
            QMessageBox.warning(self, "Tabla vacía", "Ejecute el cálculo antes de guardar la tabla.")
            return

        ruta, _ = QFileDialog.getSaveFileName(self, f"Guardar Tabla de {metodo}", f"tabla_{metodo.lower()}.csv", "Archivos CSV (*.csv)")
        if not ruta:
            return

        df = res.a_dataframe([_nombre_var(i) for i in range(len(res.x_final))])
        df.to_csv(ruta, index=False)
        QMessageBox.information(self, "Guardado exitoso", f"Tabla guardada en:\n{ruta}")

    # ── Adaptación de Tema (Claro / Oscuro) ───────────────────────────

    def aplicar_tema(self, paleta: dict[str, Any]):
        self._paleta_tema = paleta
        self.btn_copiar.aplicar_tema(paleta)
        if hasattr(self, "canvas") and hasattr(self, "figura"):
            if self._resultado_jacobi and self._resultado_seidel:
                tol_val = float(self.txt_tol.text().strip().replace(",", ".") or "1e-4")
                self._actualizar_grafica(self._resultado_jacobi, self._resultado_seidel, tol_val)
            else:
                self._dibujar_grafica_vacia()
