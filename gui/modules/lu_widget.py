"""
Módulo 5: Interfaz Gráfica para Factorización LU y Solución Ax = b.
Tema: Descomposición LU (A = L·U) y resolución de sistemas lineales (Sesión 12).
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
    leer_matriz_segura, leer_vector_seguro, mostrar_error, formatear_matriz
)

SEP = "=" * 78
SUBSEP = "-" * 78

LOGO_ASCII_LU = """
╔════════════════════════════════════════════════════════════════════════════╗
║    ███████╗ █████╗  ██████╗████████╗ ██████╗ ██████╗     ██╗     ██╗   ██╗ ║
║    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗    ██║     ██║   ██║ ║
║    █████╗  ███████║██║        ██║   ██║   ██║██████╔╝    ██║     ██║   ██║ ║
║    ██╔══╝  ██╔══██║██║        ██║   ██║   ██║██╔══██╗    ██║     ██║   ██║ ║
║    ██║     ██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║    ███████╗╚██████╔╝ ║
║    ╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚══════╝ ╚═════╝  ║
║         DESCOMPOSICIÓN A = L · U  &  RESOLUCIÓN EN 2 ETAPAS (Ax = b)       ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

TEOREMAS_LU = """
================================================================================
                    TEOREMAS CLAVE DEL MÓDULO: FACTORIZACIÓN LU
================================================================================

1. TEOREMA DE FACTORIZACIÓN LU:
   Sea A una matriz m x n. Si A puede reducirse a una matriz escalonada U usando
   ÚNICAMENTE operaciones elementales de reemplazo de filas (Fi ← Fi - l·Fj) sin
   intercambios ni escalamiento de filas, entonces A admite una factorización:
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
   Si en algún paso de la diagonal aparece un cero que requiera intercambio de
   filas, la matriz NO admite factorización LU estándar. Requiere pivoteo
   parcial, originando la factorización P · A = L · U.
================================================================================
"""


class LUWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ultima_matriz_L = None
        self.ultima_matriz_U = None
        self.ultimo_vector_x = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        encabezado = QLabel("Factorización LU y Solución Ax = b")
        encabezado.setObjectName("SectionHeader")
        encabezado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(encabezado)

        # Barra de Controles y Opciones
        ctrl_box = QGroupBox("Configuración del Sistema")
        ctrl_lay = QHBoxLayout(ctrl_box)

        ctrl_lay.addWidget(QLabel("Filas m:"))
        self.spin_m = QSpinBox()
        self.spin_m.setRange(2, 8)
        self.spin_m.setValue(3)
        self.spin_m.valueChanged.connect(self._actualizar_tablas)
        ctrl_lay.addWidget(self.spin_m)

        ctrl_lay.addWidget(QLabel("Cols n:"))
        self.spin_n = QSpinBox()
        self.spin_n.setRange(2, 8)
        self.spin_n.setValue(3)
        self.spin_n.valueChanged.connect(self._actualizar_tablas)
        ctrl_lay.addWidget(self.spin_n)

        self.chk_frac = QCheckBox("Fracciones")
        self.chk_frac.setChecked(True)
        ctrl_lay.addWidget(self.chk_frac)

        ctrl_lay.addSpacing(15)

        # Botón 0: Teoremas Clave (Exigido en rúbrica)
        btn_teoremas = QPushButton("0. Ver Teoremas Clave del Módulo")
        btn_teoremas.clicked.connect(self._mostrar_teoremas_lu)
        ctrl_lay.addWidget(btn_teoremas)

        ctrl_lay.addStretch()

        # Selector de ejemplos predefinidos
        self.combo_ejemplos = QComboBox()
        self.combo_ejemplos.addItems([
            "-- Cargar Ejemplo --",
            "Ejemplo 1: Sistema 3x3 invertible estándar",
            "Ejemplo 2: Matriz 3x3 que requiere pivoteo (PA=LU)",
            "Ejemplo 3: Matriz rectangular 4x3"
        ])
        self.combo_ejemplos.currentIndexChanged.connect(self._cargar_ejemplo)
        ctrl_lay.addWidget(self.combo_ejemplos)

        btn_resolver = QPushButton("▶ Factorizar LU y Resolver")
        btn_resolver.setObjectName("PrimaryButton")
        btn_resolver.clicked.connect(self._calcular_lu)
        ctrl_lay.addWidget(btn_resolver)

        layout.addWidget(ctrl_box)

        # Tablas de Entrada (Matriz A y Vector b)
        tablas_layout = QHBoxLayout()

        box_A = QGroupBox("Matriz A (m x n)")
        lay_A = QVBoxLayout(box_A)
        self.tabla_A = QTableWidget()
        lay_A.addWidget(self.tabla_A)
        tablas_layout.addWidget(box_A, stretch=3)

        box_b = QGroupBox("Vector b (m x 1)")
        lay_b = QVBoxLayout(box_b)
        self.tabla_b = QTableWidget()
        lay_b.addWidget(self.tabla_b)
        tablas_layout.addWidget(box_b, stretch=1)

        layout.addLayout(tablas_layout)

        # Área de Despliegue de Resultados y Consola
        res_box = QGroupBox("Procedimiento Detallado, Factorización y Comprobación")
        res_lay = QVBoxLayout(res_box)
        self.txt_salida = QTextEdit()
        self.txt_salida.setReadOnly(True)
        self.txt_salida.setFontFamily("Consolas")
        res_lay.addWidget(self.txt_salida)
        layout.addWidget(res_box)

        self._actualizar_tablas()
        self._mostrar_bienvenida()

    def _mostrar_bienvenida(self):
        """Muestra el logotipo ASCII al iniciar el módulo."""
        self.txt_salida.setText(LOGO_ASCII_LU + "\nIngrese los coeficientes de A y el vector b y presione '▶ Factorizar LU y Resolver'.\n")

    def _mostrar_teoremas_lu(self):
        """Muestra la ventana emergente con los teoremas clave del módulo."""
        QMessageBox.information(self, "0. Teoremas Clave del Módulo LU", TEOREMAS_LU)

    def _actualizar_tablas(self):
        """Redimensiona la tabla de la matriz A y el vector b."""
        m = self.spin_m.value()
        n = self.spin_n.value()

        # Tabla A (m x n)
        self.tabla_A.setRowCount(m)
        self.tabla_A.setColumnCount(n)
        self.tabla_A.setHorizontalHeaderLabels([f"x{j+1}" for j in range(n)])
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
        self.tabla_b.setVerticalHeaderLabels([f"F{i+1}" for i in range(m)])
        for i in range(m):
            if not self.tabla_b.item(i, 0):
                it = QTableWidgetItem("0")
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_b.setItem(i, 0, it)
        self.tabla_b.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _cargar_ejemplo(self, idx):
        """Carga matrices de prueba predefinidas en la interfaz."""
        if idx == 1:  # 3x3 estándar
            self.spin_m.setValue(3)
            self.spin_n.setValue(3)
            A = [[2, 4, -2], [4, 9, -3], [-2, -3, 7]]
            b = [2, 8, 10]
            for i in range(3):
                for j in range(3):
                    self.tabla_A.item(i, j).setText(str(A[i][j]))
                self.tabla_b.item(i, 0).setText(str(b[i]))
        elif idx == 2:  # Requiere permutación
            self.spin_m.setValue(3)
            self.spin_n.setValue(3)
            A = [[0, 2, 1], [1, 1, 1], [2, 1, 0]]
            b = [1, 2, 3]
            for i in range(3):
                for j in range(3):
                    self.tabla_A.item(i, j).setText(str(A[i][j]))
                self.tabla_b.item(i, 0).setText(str(b[i]))
        elif idx == 3:  # Rectangular 4x3
            self.spin_m.setValue(4)
            self.spin_n.setValue(3)
            A = [[1, 2, 1], [2, 5, 3], [3, 7, 5], [1, 3, 2]]
            b = [4, 9, 14, 5]
            for i in range(4):
                for j in range(3):
                    self.tabla_A.item(i, j).setText(str(A[i][j]))
                self.tabla_b.item(i, 0).setText(str(b[i]))

    def _calcular_lu(self):
        """Ejecuta la descomposición LU y resuelve el sistema Ax = b."""
        m = self.spin_m.value()
        n = self.spin_n.value()
        frac = self.chk_frac.isChecked()

        matriz_A, errA = leer_matriz_segura(self.tabla_A, m, n, "A")
        vector_b, errB = leer_vector_seguro(self.tabla_b, m, "b")
        errores = errA + errB
        if mostrar_error(self, errores):
            return

        salida = [LOGO_ASCII_LU, SEP, "REPORTE OFICIAL: FACTORIZACIÓN LU Y SOLUCIÓN DEL SISTEMA", SEP, ""]
        salida.append("1. MATRIZ ORIGINAL A:")
        salida.append(formatear_matriz(matriz_A, frac))
        salida.append("")
        b_str = ", ".join(formato_numero(bi, frac) for bi in vector_b)
        salida.append(f"Vector b = [ {b_str} ]ᵀ\n")

        # ── 1. Factorización LU ───────────────────────────────────────
        matriz_L, matriz_U, pasos_lu, err_lu = factorizacion_lu(matriz_A, m, n)
        salida.extend(pasos_lu)
        salida.append("")

        if err_lu:
            salida.append(SEP)
            salida.append(f"ALERTA: {err_lu}")
            salida.append(SEP)
            self.txt_salida.setText("\n".join(salida))
            return

        self.ultima_matriz_L = matriz_L
        self.ultima_matriz_U = matriz_U

        salida.append(SUBSEP)
        salida.append(f"MATRIZ TRIANGULAR INFERIOR L ({m}×{m}):")
        salida.append(formatear_matriz(matriz_L, frac))
        salida.append("")
        salida.append(f"MATRIZ TRIANGULAR SUPERIOR U ({m}×{n}):")
        salida.append(formatear_matriz(matriz_U, frac))
        salida.append(SUBSEP)

        # ── 2. Resolución de Ax = b (para matrices cuadradas) ─────────
        if m != n:
            salida.append("\nNOTA: La matriz A es rectangular (m ≠ n).")
            salida.append("La factorización A = L·U fue obtenida con éxito, pero la resolución en dos etapas")
            salida.append("(Ly = b y Ux = y) mediante sustitución estándar está diseñada para matrices cuadradas.")
        else:
            vector_y, vector_x, pasos_sol, err_sol = resolver_sistema_lu(matriz_L, matriz_U, vector_b, n)
            salida.append("")
            salida.extend(pasos_sol)
            salida.append("")

            if err_sol:
                salida.append(SEP)
                salida.append(f"ERROR: {err_sol}")
                salida.append(SEP)
            else:
                self.ultimo_vector_x = vector_x
                y_str = ", ".join(formato_numero(yi, frac) for yi in vector_y)
                x_str = ", ".join(formato_numero(xi, frac) for xi in vector_x)
                salida.append(SUBSEP)
                salida.append(f"VECTOR INTERMEDIO y (Solución de L·y = b):  [ {y_str} ]ᵀ")
                salida.append(f"VECTOR SOLUCIÓN x (Solución de U·x = y):     [ {x_str} ]ᵀ")
                salida.append(SUBSEP)
                salida.append("")

                # ── 3. Comprobación de A·x == b ──────────────────────
                es_exacta, _, pasos_verif = verificar_solucion_ax_b(matriz_A, vector_x, vector_b, n)
                salida.extend(pasos_verif)

        salida.append(SEP)
        self.txt_salida.setText("\n".join(salida))
