"""
Módulo 4: Interfaz Gráfica para Determinantes y Regla de Cramer.
Tema: Expansión por cofactores, reducción por fila y Regla de Cramer (Sesión 11).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QCheckBox,
    QTextEdit, QMessageBox, QGroupBox, QHeaderView, QTabWidget
)
from PyQt6.QtCore import Qt
from fractions import Fraction
from core.parser import formato_numero
from core.algebra_avanzada import (
    determinante_cofactores, determinante_reduccion, regla_de_cramer
)
from core.validadores import (
    leer_matriz_segura, leer_vector_seguro, mostrar_error, formatear_matriz
)

SEP = "-" * 78


class DeterminantesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        encabezado = QLabel("Determinantes y Regla de Cramer")
        encabezado.setObjectName("SectionHeader")
        encabezado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(encabezado)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._crear_tab_determinantes(), "1. Determinantes")
        self.tabs.addTab(self._crear_tab_cramer(), "2. Regla de Cramer")
        layout.addWidget(self.tabs)

    # ── Pestaña 1: Determinantes ─────────────────────────────────────

    def _crear_tab_determinantes(self):
        """Construye la pestaña de cálculo de determinantes."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        ctrl_box = QGroupBox("Configuración de la Matriz Cuadrada (n x n)")
        ctrl_lay = QHBoxLayout(ctrl_box)
        ctrl_lay.addWidget(QLabel("Dimensión n:"))
        self.spin_det_n = QSpinBox()
        self.spin_det_n.setRange(1, 8)
        self.spin_det_n.setValue(3)
        self.spin_det_n.valueChanged.connect(self._actualizar_tabla_det)
        ctrl_lay.addWidget(self.spin_det_n)
        self.chk_frac_det = QCheckBox("Fracciones")
        self.chk_frac_det.setChecked(True)
        ctrl_lay.addWidget(self.chk_frac_det)
        ctrl_lay.addStretch()
        btn_cof = QPushButton("▶ Cofactores (Laplace)")
        btn_cof.clicked.connect(lambda: self._calcular_det("cofactores"))
        ctrl_lay.addWidget(btn_cof)
        btn_red = QPushButton("▶ Reducción (Fila)")
        btn_red.setObjectName("PrimaryButton")
        btn_red.clicked.connect(lambda: self._calcular_det("reduccion"))
        ctrl_lay.addWidget(btn_red)
        layout.addWidget(ctrl_box)

        mat_box = QGroupBox("Matriz A")
        mat_lay = QVBoxLayout(mat_box)
        self.tabla_det = QTableWidget()
        mat_lay.addWidget(self.tabla_det)
        layout.addWidget(mat_box)

        res_box = QGroupBox("Procedimiento y Resultado")
        res_lay = QVBoxLayout(res_box)
        self.txt_det = QTextEdit()
        self.txt_det.setReadOnly(True)
        res_lay.addWidget(self.txt_det)
        layout.addWidget(res_box)

        self._actualizar_tabla_det()
        return tab

    def _actualizar_tabla_det(self):
        """Redimensiona la tabla de determinantes."""
        n = self.spin_det_n.value()
        self.tabla_det.setRowCount(n)
        self.tabla_det.setColumnCount(n)
        for i in range(n):
            for j in range(n):
                if not self.tabla_det.item(i, j):
                    it = QTableWidgetItem("0")
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla_det.setItem(i, j, it)
        self.tabla_det.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

    def _calcular_det(self, metodo):
        """Calcula el determinante por el método elegido."""
        n = self.spin_det_n.value()
        frac = self.chk_frac_det.isChecked()
        A, errores = leer_matriz_segura(self.tabla_det, n, n, "A")
        if mostrar_error(self, errores):
            return

        lineas = [f"CÁLCULO DEL DETERMINANTE POR {metodo.upper()}", SEP, ""]
        if metodo == "cofactores":
            det, pasos = determinante_cofactores(A)
            lineas.append(pasos)
        else:
            det, pasos = determinante_reduccion(A)
            lineas.extend(pasos)

        lineas.append(SEP)
        lineas.append(f"|A| = {formato_numero(det, frac)}")
        self.txt_det.setText("\n".join(lineas))

    # ── Pestaña 2: Regla de Cramer ───────────────────────────────────

    def _crear_tab_cramer(self):
        """Construye la pestaña de la Regla de Cramer."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        ctrl_box = QGroupBox("Configuración del Sistema Ax = b (n ecuaciones, n incógnitas)")
        ctrl_lay = QHBoxLayout(ctrl_box)
        ctrl_lay.addWidget(QLabel("Dimensión n:"))
        self.spin_cr_n = QSpinBox()
        self.spin_cr_n.setRange(2, 8)
        self.spin_cr_n.setValue(3)
        self.spin_cr_n.valueChanged.connect(self._actualizar_tablas_cramer)
        ctrl_lay.addWidget(self.spin_cr_n)
        self.chk_frac_cr = QCheckBox("Fracciones")
        self.chk_frac_cr.setChecked(True)
        ctrl_lay.addWidget(self.chk_frac_cr)
        ctrl_lay.addStretch()
        btn_cr = QPushButton("▶ Resolver por Cramer")
        btn_cr.setObjectName("PrimaryButton")
        btn_cr.clicked.connect(self._resolver_cramer)
        ctrl_lay.addWidget(btn_cr)
        layout.addWidget(ctrl_box)

        tablas_layout = QHBoxLayout()

        mat_box = QGroupBox("Matriz A (Coeficientes)")
        mat_lay = QVBoxLayout(mat_box)
        self.tabla_cr_A = QTableWidget()
        mat_lay.addWidget(self.tabla_cr_A)
        tablas_layout.addWidget(mat_box)

        vec_box = QGroupBox("Vector b (Términos independientes)")
        vec_lay = QVBoxLayout(vec_box)
        self.tabla_cr_b = QTableWidget()
        vec_lay.addWidget(self.tabla_cr_b)
        tablas_layout.addWidget(vec_box)

        layout.addLayout(tablas_layout)

        res_box = QGroupBox("Solución paso a paso")
        res_lay = QVBoxLayout(res_box)
        self.txt_cramer = QTextEdit()
        self.txt_cramer.setReadOnly(True)
        res_lay.addWidget(self.txt_cramer)
        layout.addWidget(res_box)

        self._actualizar_tablas_cramer()
        return tab

    def _actualizar_tablas_cramer(self):
        """Redimensiona las tablas de Cramer (A y b)."""
        n = self.spin_cr_n.value()
        # Tabla A (n x n)
        self.tabla_cr_A.setRowCount(n)
        self.tabla_cr_A.setColumnCount(n)
        self.tabla_cr_A.setHorizontalHeaderLabels([f"x{j+1}" for j in range(n)])
        self.tabla_cr_A.setVerticalHeaderLabels([f"Ec{i+1}" for i in range(n)])
        for i in range(n):
            for j in range(n):
                if not self.tabla_cr_A.item(i, j):
                    it = QTableWidgetItem("0")
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla_cr_A.setItem(i, j, it)
        self.tabla_cr_A.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        # Tabla b (n x 1)
        self.tabla_cr_b.setRowCount(n)
        self.tabla_cr_b.setColumnCount(1)
        self.tabla_cr_b.setHorizontalHeaderLabels(["b"])
        self.tabla_cr_b.setVerticalHeaderLabels([f"Ec{i+1}" for i in range(n)])
        for i in range(n):
            if not self.tabla_cr_b.item(i, 0):
                it = QTableWidgetItem("0")
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_cr_b.setItem(i, 0, it)
        self.tabla_cr_b.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

    def _resolver_cramer(self):
        """Lee A y b, aplica Cramer y muestra el procedimiento."""
        n = self.spin_cr_n.value()
        frac = self.chk_frac_cr.isChecked()
        A, errA = leer_matriz_segura(self.tabla_cr_A, n, n, "A")
        b, errB = leer_vector_seguro(self.tabla_cr_b, n, "b")
        errores = errA + errB
        if mostrar_error(self, errores):
            return

        soluciones, pasos, error = regla_de_cramer(A, b, n)

        lineas = ["SOLUCIÓN DEL SISTEMA POR REGLA DE CRAMER", SEP, ""]
        lineas.append("Matriz A:")
        lineas.append(formatear_matriz(A, frac))
        lineas.append("")
        b_str = ", ".join(formato_numero(bi, frac) for bi in b)
        lineas.append(f"Vector b = [ {b_str} ]")
        lineas.append(SEP)
        lineas.extend(pasos)
        lineas.append(SEP)

        if error:
            lineas.append(f"ERROR: {error}")
        else:
            lineas.append("SOLUCIÓN FINAL:")
            for i in range(n):
                lineas.append(
                    f"   x{i+1} = {formato_numero(soluciones[i], frac)}"
                )

        self.txt_cramer.setText("\n".join(lineas))
