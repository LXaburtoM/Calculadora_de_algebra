"""
Módulo 5: Interfaz Gráfica para Factorización LU y Solución Ax = b.
Tema: Descomposición LU (A = L·U) y resolución en 2 etapas (Sesión 12).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QCheckBox,
    QTextEdit, QMessageBox, QGroupBox, QHeaderView, QComboBox
)
from PyQt6.QtCore import Qt
from fractions import Fraction
from core.parser import formato_numero
from core.factorizacion_lu import (
    factorizacion_lu, resolver_sistema_lu, verificar_solucion_ax_b
)
from core.validadores import (
    leer_matriz_segura, leer_vector_seguro, mostrar_error
)

SEP = "=" * 78
SUBSEP = "-" * 78

TEOREMAS_LU = """
================================================================================
                    TEOREMAS CLAVE DEL MÓDULO: FACTORIZACIÓN LU
================================================================================

1. TEOREMA DE FACTORIZACIÓN LU:
   Sea A una matriz m x n. Si A puede reducirse a una forma escalonada U usando
   ÚNICAMENTE operaciones de reemplazo de filas (Fi ← Fi - l·Fj) sin
   intercambios ni escalamiento, entonces A admite una descomposición:
                              A = L · U
   donde:
   • L es una matriz triangular inferior m x m con unos (1) en la diagonal
     principal (triangular inferior unitaria).
   • U es una matriz triangular superior / escalonada m x n.
   • Cada entrada L[i,j] (i > j) almacena el multiplicador exacto l = a_ij / pivote.

2. RESOLUCIÓN DE Ax = b EN DOS ETAPAS (DOBLE SUSTITUCIÓN):
   Dado que A = L · U, el sistema Ax = b equivale a L(Ux) = b:
   • Etapa 1: Resolver L · y = b mediante Sustitución Hacia Adelante (progresiva).
   • Etapa 2: Resolver U · x = y mediante Sustitución Hacia Atrás (regresiva).

3. EFICIENCIA COMPUTACIONAL:
   • Factorizar A = L · U requiere O(2/3 n³) operaciones (se realiza UNA sola vez).
   • Resolver para cualquier nuevo vector b toma únicamente O(2n²) operaciones.
   • Comparación: La Eliminación Gaussiana tradicional requiere O(2/3 n³) para
     CADA nuevo vector b. LU optimiza drásticamente el costo computacional.

4. CONDICIÓN DE PIVOTEO (PERMUTACIÓN):
   Si en algún paso de la diagonal de U aparece un cero que requiera intercambio
   de filas, la matriz NO admite factorización LU estándar. Requiere pivoteo
   parcial, originando la factorización P · A = L · U.
================================================================================
"""


class LUWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ultima_matriz_L = None
        self.ultima_matriz_U = None
        self.matriz_A_factorizada = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        encabezado = QLabel("Factorización LU y Solución Ax = b")
        encabezado.setObjectName("SectionHeader")
        encabezado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(encabezado)

        # ── 1. Barra de Controles y Parámetros (Estilo Oficial del Proyecto) ──
        ctrl_box = QGroupBox("Configuración del Sistema")
        ctrl_lay = QHBoxLayout(ctrl_box)

        ctrl_lay.addWidget(QLabel("Filas m:"))
        self.spin_m = QSpinBox()
        self.spin_m.setRange(2, 6)
        self.spin_m.setValue(3)
        self.spin_m.valueChanged.connect(self._actualizar_tablas)
        ctrl_lay.addWidget(self.spin_m)

        ctrl_lay.addWidget(QLabel("Columnas n:"))
        self.spin_n = QSpinBox()
        self.spin_n.setRange(2, 6)
        self.spin_n.setValue(3)
        self.spin_n.valueChanged.connect(self._actualizar_tablas)
        ctrl_lay.addWidget(self.spin_n)

        self.chk_frac = QCheckBox("Fracciones")
        self.chk_frac.setChecked(True)
        ctrl_lay.addWidget(self.chk_frac)

        ctrl_lay.addSpacing(10)

        # Botón 0: Teoremas Clave del Módulo (Exigido en rúbrica)
        btn_teoremas = QPushButton("0. Ver Teoremas Clave")
        btn_teoremas.clicked.connect(self._mostrar_teoremas_lu)
        ctrl_lay.addWidget(btn_teoremas)

        # Selector de ejemplos predefinidos
        self.combo_ejemplos = QComboBox()
        self.combo_ejemplos.addItems([
            "-- Cargar Ejemplo --",
            "Ejemplo 1: Sistema 3x3 estándar",
            "Ejemplo 2: Matriz que requiere pivoteo (PA=LU)",
            "Ejemplo 3: Matriz rectangular 4x3"
        ])
        self.combo_ejemplos.currentIndexChanged.connect(self._cargar_ejemplo)
        ctrl_lay.addWidget(self.combo_ejemplos)

        ctrl_lay.addStretch()

        # Botón 1: Factorizar A = LU
        self.btn_factorizar = QPushButton("▶ 1. Factorizar A = LU")
        self.btn_factorizar.clicked.connect(self._ejecutar_factorizacion)
        ctrl_lay.addWidget(self.btn_factorizar)

        # Botón 2: Resolver Ax = b con LU
        self.btn_resolver = QPushButton("▶ 2. Resolver Ax = b con LU")
        self.btn_resolver.setObjectName("PrimaryButton")
        self.btn_resolver.clicked.connect(self._ejecutar_resolucion)
        ctrl_lay.addWidget(self.btn_resolver)

        layout.addWidget(ctrl_box)

        # ── 2. Tablas de Entrada (Matriz A y Vector b) ────────────────
        tablas_layout = QHBoxLayout()

        box_A = QGroupBox("Matriz A (m × n)")
        lay_A = QVBoxLayout(box_A)
        self.tabla_A = QTableWidget()
        lay_A.addWidget(self.tabla_A)
        tablas_layout.addWidget(box_A, stretch=3)

        box_b = QGroupBox("Vector de términos independientes b (m × 1)")
        lay_b = QVBoxLayout(box_b)
        self.tabla_b = QTableWidget()
        lay_b.addWidget(self.tabla_b)
        tablas_layout.addWidget(box_b, stretch=1)

        layout.addLayout(tablas_layout)

        # ── 3. Área de Procedimiento y Resultados ─────────────────────
        res_box = QGroupBox("Procedimiento y Resultados")
        res_lay = QVBoxLayout(res_box)

        barra_res = QHBoxLayout()
        lbl_info = QLabel("Detalle de operaciones elementales, matrices L, U y comprobaciones")
        barra_res.addWidget(lbl_info)
        barra_res.addStretch()

        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.clicked.connect(self._limpiar_consola)
        barra_res.addWidget(btn_limpiar)
        res_lay.addLayout(barra_res)

        self.txt_salida = QTextEdit()
        self.txt_salida.setReadOnly(True)
        res_lay.addWidget(self.txt_salida)

        layout.addWidget(res_box)

        self._actualizar_tablas()
        self._cargar_ejemplo_defecto()

    def _mostrar_teoremas_lu(self):
        """Muestra la ventana emergente con los teoremas clave del módulo."""
        QMessageBox.information(self, "0. Teoremas Clave del Módulo LU", TEOREMAS_LU)

    def _limpiar_consola(self):
        """Limpia el área de texto."""
        self.txt_salida.clear()

    def _actualizar_tablas(self):
        """Redimensiona las tablas de A y b según m y n."""
        m = self.spin_m.value()
        n = self.spin_n.value()

        # Tabla A (m x n)
        self.tabla_A.setRowCount(m)
        self.tabla_A.setColumnCount(n)
        self.tabla_A.setHorizontalHeaderLabels([f"Col {j+1}" for j in range(n)])
        self.tabla_A.setVerticalHeaderLabels([f"F{i+1}" for i in range(m)])
        for i in range(m):
            for j in range(n):
                if not self.tabla_A.item(i, j):
                    it = QTableWidgetItem("0")
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla_A.setItem(i, j, it)
        self.tabla_A.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Tabla b (m x 1)
        self.tabla_b.setRowCount(m)
        self.tabla_b.setColumnCount(1)
        self.tabla_b.setHorizontalHeaderLabels(["b"])
        self.tabla_b.setVerticalHeaderLabels([f"b{i+1}" for i in range(m)])
        for i in range(m):
            if not self.tabla_b.item(i, 0):
                it = QTableWidgetItem("0")
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_b.setItem(i, 0, it)
        self.tabla_b.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _cargar_ejemplo_defecto(self):
        """Carga una matriz estándar por defecto."""
        A = [["2", "1", "-1"], ["1", "3", "2"], ["1", "0", "2"]]
        b = ["8", "13", "7"]
        for i in range(3):
            for j in range(3):
                self.tabla_A.setItem(i, j, QTableWidgetItem(A[i][j]))
            self.tabla_b.setItem(i, 0, QTableWidgetItem(b[i]))

    def _cargar_ejemplo(self, idx):
        """Carga ejemplos de prueba en la interfaz."""
        if idx == 1:  # 3x3 estándar
            self.spin_m.setValue(3)
            self.spin_n.setValue(3)
            self._actualizar_tablas()
            self._cargar_ejemplo_defecto()
        elif idx == 2:  # Requiere permutación
            self.spin_m.setValue(3)
            self.spin_n.setValue(3)
            self._actualizar_tablas()
            A = [["0", "2", "1"], ["1", "1", "1"], ["2", "1", "0"]]
            b = ["1", "2", "3"]
            for i in range(3):
                for j in range(3):
                    self.tabla_A.setItem(i, j, QTableWidgetItem(A[i][j]))
                self.tabla_b.setItem(i, 0, QTableWidgetItem(b[i]))
        elif idx == 3:  # Rectangular 4x3
            self.spin_m.setValue(4)
            self.spin_n.setValue(3)
            self._actualizar_tablas()
            A = [["1", "2", "1"], ["2", "5", "3"], ["3", "7", "5"], ["1", "3", "2"]]
            b = ["4", "9", "14", "5"]
            for i in range(4):
                for j in range(3):
                    self.tabla_A.setItem(i, j, QTableWidgetItem(A[i][j]))
                self.tabla_b.setItem(i, 0, QTableWidgetItem(b[i]))

    # ── BOTÓN 1: FACTORIZAR A = LU ───────────────────────────────────

    def _ejecutar_factorizacion(self):
        """Calcula únicamente la factorización A = LU con evolución paso a paso."""
        m = self.spin_m.value()
        n = self.spin_n.value()
        frac = self.chk_frac.isChecked()

        matriz_A, errA = leer_matriz_segura(self.tabla_A, m, n, "A")
        if mostrar_error(self, errA):
            return

        matriz_L, matriz_U, pasos, err_lu = factorizacion_lu(matriz_A, m, n, frac)

        lineas = [
            SEP,
            "                 1. FACTORIZACIÓN DE MATRIZ: A = L · U",
            SEP,
            ""
        ]
        lineas.extend(pasos)

        if err_lu:
            lineas.append("\n" + SEP)
            lineas.append(f"ALERTA: {err_lu}")
            lineas.append(SEP)
            self.ultima_matriz_L = None
            self.ultima_matriz_U = None
            self.matriz_A_factorizada = None
        else:
            self.ultima_matriz_L = matriz_L
            self.ultima_matriz_U = matriz_U
            self.matriz_A_factorizada = matriz_A

        self.txt_salida.setText("\n".join(lineas))

    # ── BOTÓN 2: RESOLVER Ax = b CON LU ──────────────────────────────

    def _ejecutar_resolucion(self):
        """Resuelve el sistema Ax = b utilizando la factorización LU en dos etapas."""
        m = self.spin_m.value()
        n = self.spin_n.value()
        frac = self.chk_frac.isChecked()

        if m != n:
            QMessageBox.warning(
                self, "Dimensiones no cuadradas",
                "Para resolver el sistema Ax = b con factorización LU, "
                "la matriz debe ser cuadrada (m = n)."
            )
            return

        matriz_A, errA = leer_matriz_segura(self.tabla_A, m, n, "A")
        vector_b, errB = leer_vector_seguro(self.tabla_b, m, "b")
        errores = errA + errB
        if mostrar_error(self, errores):
            return

        # Si no se ha factorizado la matriz actual, se factoriza primero
        if (self.ultima_matriz_L is None or self.matriz_A_factorizada != matriz_A):
            matriz_L, matriz_U, _, err_lu = factorizacion_lu(matriz_A, m, n, frac)
            if err_lu:
                QMessageBox.critical(self, "Error en Factorización", err_lu)
                return
            self.ultima_matriz_L = matriz_L
            self.ultima_matriz_U = matriz_U
            self.matriz_A_factorizada = matriz_A

        vector_y, vector_x, pasos_sol, err_sol = resolver_sistema_lu(
            self.ultima_matriz_L, self.ultima_matriz_U, vector_b, n, frac
        )

        if err_sol:
            QMessageBox.critical(self, "Error al resolver sistema", err_sol)
            return

        _, _, pasos_verif = verificar_solucion_ax_b(matriz_A, vector_x, vector_b, n, frac)

        lineas = []
        lineas.extend(pasos_sol)
        lineas.append("")
        lineas.extend(pasos_verif)

        texto_actual = self.txt_salida.toPlainText().strip()
        if texto_actual and "1. FACTORIZACIÓN" in texto_actual:
            self.txt_salida.append("\n\n" + "\n".join(lineas))
        else:
            self.txt_salida.setText("\n".join(lineas))
