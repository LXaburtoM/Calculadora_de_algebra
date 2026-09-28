"""
Módulo de Interfaz Gráfica para Operaciones en Rn y Operaciones Matriciales.

Organizado en 3 pestañas:
  Pestaña 1 - Operaciones Vectoriales : suma, resta y escalar x vector
  Pestaña 2 - Operaciones Matriciales : suma, resta, escalar x matriz, A·B
  Pestaña 3 - Combinación Lineal      : verifica si b pertenece a span{v1,...,vk}
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QCheckBox,
    QTextEdit, QMessageBox, QGroupBox, QHeaderView, QTabWidget,
    QComboBox, QLineEdit, QSizePolicy
)
from PyQt6.QtCore import Qt
from fractions import Fraction

from core.parser import parse_expresion, formato_numero
from core.eliminacion_gaussiana import nombre_var
from core.algebra_avanzada import inversa_matriz, evaluar_independencia_lineal
from core.operaciones_matriciales import (
    sumar_vectores, restar_vectores, escalar_por_vector,
    sumar_matrices, restar_matrices, escalar_por_matriz,
    multiplicar_matrices, transpuesta_matriz, es_combinacion_lineal
)

SEP = "â”€" * 78


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Clase Principal del Módulo
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class OperacionesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        encabezado = QLabel(
            "Operaciones en â„ⁿ y Operaciones Matriciales Básicas"
        )
        encabezado.setObjectName("SectionHeader")
        encabezado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(encabezado)

        # Pestañas principales
        self.tabs = QTabWidget()
        self.tabs.addTab(self._crear_tab_vectores(),  "1. Operaciones Vectoriales")
        self.tabs.addTab(self._crear_tab_matrices(),  "2. Operaciones Matriciales")
        self.tabs.addTab(self._crear_tab_comb_lineal(), "3. Combinación Lineal")
        layout.addWidget(self.tabs)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # PESTAÁ‘A 1: OPERACIONES VECTORIALES
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _crear_tab_vectores(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # --- Controles superiores ---
        ctrl_box = QGroupBox("Configuración")
        ctrl_layout = QHBoxLayout(ctrl_box)

        ctrl_layout.addWidget(QLabel("Operación:"))
        self.combo_vec_op = QComboBox()
        self.combo_vec_op.addItems([
            "Suma  (v₁ + vâ‚‚)",
            "Resta  (v₁ âˆ’ vâ‚‚)",
            "Escalar Á— Vector  (c · v₁)",
        ])
        self.combo_vec_op.currentIndexChanged.connect(self._actualizar_modo_vec)
        ctrl_layout.addWidget(self.combo_vec_op)

        ctrl_layout.addWidget(QLabel("Dimensión n:"))
        self.spin_vec_n = QSpinBox()
        self.spin_vec_n.setRange(1, 10)
        self.spin_vec_n.setValue(3)
        self.spin_vec_n.valueChanged.connect(self._actualizar_tablas_vec)
        ctrl_layout.addWidget(self.spin_vec_n)

        ctrl_layout.addWidget(QLabel("Escalar c:"))
        self.le_escalar_vec = QLineEdit("2")
        self.le_escalar_vec.setFixedWidth(70)
        self.le_escalar_vec.setEnabled(False)
        ctrl_layout.addWidget(self.le_escalar_vec)

        self.chk_frac_vec = QCheckBox("Fracciones")
        self.chk_frac_vec.setChecked(True)
        ctrl_layout.addWidget(self.chk_frac_vec)

        ctrl_layout.addStretch()
        btn_calc_vec = QPushButton("▶ Calcular")
        btn_calc_vec.setObjectName("PrimaryButton")
        btn_calc_vec.clicked.connect(self._calcular_vectores)
        ctrl_layout.addWidget(btn_calc_vec)
        layout.addWidget(ctrl_box)

        # --- Tablas de vectores ---
        tablas_layout = QHBoxLayout()

        vec1_box = QGroupBox("Vector v₁")
        vec1_lay = QVBoxLayout(vec1_box)
        self.tabla_v1 = QTableWidget()
        vec1_lay.addWidget(self.tabla_v1)
        tablas_layout.addWidget(vec1_box)

        vec2_box = QGroupBox("Vector vâ‚‚  (no aplica en escalarÁ—v)")
        vec2_lay = QVBoxLayout(vec2_box)
        self.tabla_v2 = QTableWidget()
        vec2_lay.addWidget(self.tabla_v2)
        tablas_layout.addWidget(vec2_box)

        layout.addLayout(tablas_layout)

        # --- Resultado ---
        res_box = QGroupBox("Resultado")
        res_lay = QVBoxLayout(res_box)
        self.txt_vec = QTextEdit()
        self.txt_vec.setReadOnly(True)
        res_lay.addWidget(self.txt_vec)
        layout.addWidget(res_box)

        self._actualizar_tablas_vec()
        return tab

    def _actualizar_modo_vec(self, idx):
        """Habilita/deshabilita vâ‚‚ y el campo escalar según la operación."""
        es_escalar = (idx == 2)
        self.le_escalar_vec.setEnabled(es_escalar)
        self.tabla_v2.setEnabled(not es_escalar)

    def _actualizar_tablas_vec(self):
        n = self.spin_vec_n.value()
        for tabla in (self.tabla_v1, self.tabla_v2):
            tabla.setRowCount(n)
            tabla.setColumnCount(1)
            tabla.setHorizontalHeaderLabels(["valor"])
            tabla.setVerticalHeaderLabels([nombre_var(i) for i in range(n)])
            for i in range(n):
                if not tabla.item(i, 0):
                    it = QTableWidgetItem("0")
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    tabla.setItem(i, 0, it)
            tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _leer_vector(self, tabla, n, etiqueta):
        """Lee un vector de n componentes desde una tabla de 1 columna."""
        v = []
        errores = []
        for i in range(n):
            item = tabla.item(i, 0)
            val, err = parse_expresion(item.text() if item else "0")
            if err:
                errores.append(f"â€¢ {etiqueta} componente {i+1}: {err}")
            v.append(val if val is not None else Fraction(0))
        return v, errores

    def _calcular_vectores(self):
        n = self.spin_vec_n.value()
        frac = self.chk_frac_vec.isChecked()
        idx = self.combo_vec_op.currentIndex()

        v1, errores = self._leer_vector(self.tabla_v1, n, "v₁")

        if idx == 2:   # Escalar Á— vector
            esc_txt = self.le_escalar_vec.text().strip()
            esc_val, err = parse_expresion(esc_txt)
            if err:
                errores.append(f"â€¢ Escalar c: {err}")
            if errores:
                QMessageBox.critical(self, "Error en los datos", "\n".join(errores))
                return

            resultado, pasos, error = escalar_por_vector(esc_val, v1)
            op_str = f"{formato_numero(esc_val, frac)} · v₁"
        else:
            v2, err2 = self._leer_vector(self.tabla_v2, n, "vâ‚‚")
            errores.extend(err2)
            if errores:
                QMessageBox.critical(self, "Error en los datos", "\n".join(errores))
                return

            if idx == 0:
                resultado, pasos, error = sumar_vectores(v1, v2)
                op_str = "v₁ + vâ‚‚"
            else:
                resultado, pasos, error = restar_vectores(v1, v2)
                op_str = "v₁ âˆ’ vâ‚‚"

        if error:
            QMessageBox.critical(self, "Error", error)
            return

        lineas = [
            f"OPERACIÓN VECTORIAL:  {op_str}",
            SEP,
            "",
            "CÁLCULO COMPONENTE A COMPONENTE:",
        ]
        lineas.extend(pasos)
        lineas.append("")
        lineas.append(SEP)
        comp_str = ",  ".join(formato_numero(x, frac) for x in resultado)
        lineas.append(f"RESULTADO:  [ {comp_str} ]áµ€")
        self.txt_vec.setText("\n".join(lineas))

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # PESTAÁ‘A 2: OPERACIONES MATRICIALES
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _crear_tab_matrices(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # --- Ejemplos de Clase (Sesión 9) ---
        ejemplos_box = QGroupBox("Ejemplos de Clase (Sesión 9)")
        ejemplos_lay = QHBoxLayout(ejemplos_box)
        ejemplos_lay.addWidget(QLabel("Cargar Ejemplo:"))
        self.combo_ejemplos = QComboBox()
        self.combo_ejemplos.addItems([
            "-- Seleccione --",
            "Ejemplo 1: Suma de Matrices (A + B)",
            "Ejemplo 2: Multiplicación Fila-Columna (A · B)",
            "Ejemplo 3: Matriz Transpuesta (Aáµ€)"
        ])
        ejemplos_lay.addWidget(self.combo_ejemplos)
        btn_cargar = QPushButton("Cargar y Resolver")
        btn_cargar.setObjectName("PrimaryButton")
        btn_cargar.clicked.connect(self._cargar_ejemplo)
        ejemplos_lay.addWidget(btn_cargar)
        ejemplos_lay.addStretch()
        layout.addWidget(ejemplos_box)

        # --- Controles ---
        ctrl_box = QGroupBox("Configuración")
        ctrl_layout = QHBoxLayout(ctrl_box)

        ctrl_layout.addWidget(QLabel("Operación:"))
        self.combo_mat_op = QComboBox()
        self.combo_mat_op.addItems([
            "Suma  (A + B)",
            "Resta  (A âˆ’ B)",
            "Escalar Á— Matriz  (c · A)",
            "Multiplicación  (A · B)",
            "Transpuesta  (Aáµ€)",
        ])
        self.combo_mat_op.currentIndexChanged.connect(self._actualizar_modo_mat)
        ctrl_layout.addWidget(self.combo_mat_op)

        ctrl_layout.addWidget(QLabel("A: filas"))
        self.spin_mA = QSpinBox(); self.spin_mA.setRange(1, 8); self.spin_mA.setValue(2)
        self.spin_mA.valueChanged.connect(self._actualizar_tablas_mat)
        ctrl_layout.addWidget(self.spin_mA)

        ctrl_layout.addWidget(QLabel("cols"))
        self.spin_nA = QSpinBox(); self.spin_nA.setRange(1, 8); self.spin_nA.setValue(2)
        self.spin_nA.valueChanged.connect(self._actualizar_tablas_mat)
        ctrl_layout.addWidget(self.spin_nA)

        ctrl_layout.addWidget(QLabel("  B: filas"))
        self.spin_mB = QSpinBox(); self.spin_mB.setRange(1, 8); self.spin_mB.setValue(2)
        self.spin_mB.valueChanged.connect(self._actualizar_tablas_mat)
        ctrl_layout.addWidget(self.spin_mB)

        ctrl_layout.addWidget(QLabel("cols"))
        self.spin_nB = QSpinBox(); self.spin_nB.setRange(1, 8); self.spin_nB.setValue(2)
        self.spin_nB.valueChanged.connect(self._actualizar_tablas_mat)
        ctrl_layout.addWidget(self.spin_nB)

        ctrl_layout.addWidget(QLabel("  Escalar c:"))
        self.le_escalar_mat = QLineEdit("2")
        self.le_escalar_mat.setFixedWidth(60)
        self.le_escalar_mat.setEnabled(False)
        ctrl_layout.addWidget(self.le_escalar_mat)

        self.chk_frac_mat = QCheckBox("Fracciones")
        self.chk_frac_mat.setChecked(True)
        ctrl_layout.addWidget(self.chk_frac_mat)

        btn_calc_mat = QPushButton("▶ Calcular")
        btn_calc_mat.setObjectName("PrimaryButton")
        btn_calc_mat.clicked.connect(self._calcular_matrices)
        ctrl_layout.addWidget(btn_calc_mat)
        layout.addWidget(ctrl_box)

        # --- Tablas A y B ---
        tablas_layout = QHBoxLayout()

        boxA = QGroupBox("Matriz A")
        layA = QVBoxLayout(boxA)
        self.tabla_A = QTableWidget()
        layA.addWidget(self.tabla_A)
        tablas_layout.addWidget(boxA)

        boxB = QGroupBox("Matriz B  (no aplica en escalarÁ—A o Aáµ€)")
        layB = QVBoxLayout(boxB)
        self.tabla_B = QTableWidget()
        layB.addWidget(self.tabla_B)
        tablas_layout.addWidget(boxB)
        layout.addLayout(tablas_layout)

        # --- Resultado ---
        res_box = QGroupBox("Resultado")
        res_lay = QVBoxLayout(res_box)
        self.txt_mat = QTextEdit()
        self.txt_mat.setReadOnly(True)
        res_lay.addWidget(self.txt_mat)
        layout.addWidget(res_box)

        self._actualizar_tablas_mat()
        return tab

    def _cargar_ejemplo(self):
        idx = self.combo_ejemplos.currentIndex()
        if idx == 0: return

        if idx == 1: # Suma de matrices
            self.combo_mat_op.setCurrentIndex(0)
            self.spin_mA.setValue(2); self.spin_nA.setValue(2)
            self.spin_mB.setValue(2); self.spin_nB.setValue(2)
            self._llenar_matriz(self.tabla_A, [[1, 4], [2, 5]])
            self._llenar_matriz(self.tabla_B, [[-1, 3], [0, 2]])
        elif idx == 2: # Multiplicación de matrices
            self.combo_mat_op.setCurrentIndex(3)
            self.spin_mA.setValue(2); self.spin_nA.setValue(3)
            self.spin_mB.setValue(3); self.spin_nB.setValue(2)
            self._llenar_matriz(self.tabla_A, [[1, -1, 2], [0, 3, 4]])
            self._llenar_matriz(self.tabla_B, [[2, 1], [-1, 0], [3, 5]])
        elif idx == 3: # Transpuesta
            self.combo_mat_op.setCurrentIndex(4)
            self.spin_mA.setValue(2); self.spin_nA.setValue(3)
            self._llenar_matriz(self.tabla_A, [[1, 2, 3], [4, 5, 6]])

        self._calcular_matrices()

    def _llenar_matriz(self, tabla, datos):
        m = len(datos)
        n = len(datos[0])
        for i in range(m):
            for j in range(n):
                if tabla.item(i, j):
                    tabla.item(i, j).setText(str(datos[i][j]))

    def _actualizar_modo_mat(self, idx):
        """Ajusta qué controles están activos según la operación elegida."""
        es_escalar = (idx == 2)
        es_transpuesta = (idx == 4)
        es_inversa = (idx == 5)
        self.le_escalar_mat.setEnabled(es_escalar)
        self.tabla_B.setEnabled(not es_escalar and not es_transpuesta and not es_inversa)
        self.spin_mB.setEnabled(not es_escalar and not es_transpuesta and not es_inversa)
        self.spin_nB.setEnabled(not es_escalar and not es_transpuesta and not es_inversa)

    def _actualizar_tablas_mat(self):
        mA, nA = self.spin_mA.value(), self.spin_nA.value()
        mB, nB = self.spin_mB.value(), self.spin_nB.value()
        self._resize_table(self.tabla_A, mA, nA)
        self._resize_table(self.tabla_B, mB, nB)

    def _resize_table(self, tabla, m, n):
        tabla.setRowCount(m)
        tabla.setColumnCount(n)
        tabla.setHorizontalHeaderLabels([nombre_var(j) for j in range(n)])
        tabla.setVerticalHeaderLabels([f"R{i+1}" for i in range(m)])
        for i in range(m):
            for j in range(n):
                if not tabla.item(i, j):
                    it = QTableWidgetItem("0")
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    tabla.setItem(i, j, it)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _leer_matriz(self, tabla, m, n, etiqueta):
        """Lee una matriz mÁ—n desde una QTableWidget."""
        M = []
        errores = []
        for i in range(m):
            fila = []
            for j in range(n):
                item = tabla.item(i, j)
                val, err = parse_expresion(item.text() if item else "0")
                if err:
                    errores.append(f"â€¢ {etiqueta}[{i+1},{j+1}]: {err}")
                fila.append(val if val is not None else Fraction(0))
            M.append(fila)
        return M, errores

    def _formatear_matriz(self, M, m, n, frac):
        """Devuelve la matriz como texto alineado."""
        txts = [[formato_numero(M[i][j], frac) for j in range(n)] for i in range(m)]
        ancho = max(3, max(len(c) for fila in txts for c in fila) + 1)
        lineas = []
        for fila in txts:
            celdas = [c.rjust(ancho) for c in fila]
            lineas.append("   [ " + "  ".join(celdas) + " ]")
        return "\n".join(lineas)

    def _calcular_matrices(self):
        idx = self.combo_mat_op.currentIndex()
        mA, nA = self.spin_mA.value(), self.spin_nA.value()
        mB, nB = self.spin_mB.value(), self.spin_nB.value()
        frac = self.chk_frac_mat.isChecked()

        A, errA = self._leer_matriz(self.tabla_A, mA, nA, "A")
        errores = list(errA)

        if idx == 2:  # Escalar Á— Matriz
            esc_val, err = parse_expresion(self.le_escalar_mat.text().strip())
            if err:
                errores.append(f"â€¢ Escalar c: {err}")
            if errores:
                QMessageBox.critical(self, "Error en los datos", "\n".join(errores))
                return
            resultado, pasos, error = escalar_por_matriz(esc_val, A, mA, nA)
            op_str = f"{formato_numero(esc_val, frac)} · A"
            dim_res = f"{mA}Á—{nA}"
        elif idx == 4: # Transpuesta
            resultado, pasos, error = transpuesta_matriz(A, mA, nA)
            op_str = "Aáµ€"
            dim_res = f"{nA}Á—{mA}"
        else:
            B, errB = self._leer_matriz(self.tabla_B, mB, nB, "B")
            errores.extend(errB)
            if errores:
                QMessageBox.critical(self, "Error en los datos", "\n".join(errores))
                return

            if idx == 0:
                resultado, pasos, error = sumar_matrices(A, B, mA, nA, mB, nB)
                op_str = "A + B"
                dim_res = f"{mA}Á—{nA}"
            elif idx == 1:
                resultado, pasos, error = restar_matrices(A, B, mA, nA, mB, nB)
                op_str = "A âˆ’ B"
                dim_res = f"{mA}Á—{nA}"
            else:   # idx == 3: Multiplicación A·B
                resultado, pasos, error = multiplicar_matrices(A, B, mA, nA, nB)
                op_str = "A · B"
                dim_res = f"{mA}Á—{nB}"

        if error:
            QMessageBox.critical(self, "Error de dimensiones", error)
            return

        lineas = [
            f"OPERACIÓN MATRICIAL:  {op_str}",
            SEP,
            "",
            "CÁLCULO ENTRADA POR ENTRADA:",
        ]
        lineas.extend(pasos)
        lineas.append("")
        lineas.append(SEP)
        lineas.append(f"RESULTADO  C  ({dim_res}):")
        lineas.append(self._formatear_matriz(resultado, len(resultado), len(resultado[0]), frac))
        self.txt_mat.setText("\n".join(lineas))

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # PESTAÁ‘A 3: COMBINACIÓN LINEAL
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _crear_tab_comb_lineal(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # --- Controles ---
        ctrl_box = QGroupBox("Configuración")
        ctrl_layout = QHBoxLayout(ctrl_box)

        ctrl_layout.addWidget(QLabel("Dimensión n (Rⁿ):"))
        self.spin_cl_n = QSpinBox(); self.spin_cl_n.setRange(1, 8); self.spin_cl_n.setValue(3)
        self.spin_cl_n.valueChanged.connect(self._actualizar_tabla_cl)
        ctrl_layout.addWidget(self.spin_cl_n)

        ctrl_layout.addWidget(QLabel("  Número de vectores k:"))
        self.spin_cl_k = QSpinBox(); self.spin_cl_k.setRange(1, 6); self.spin_cl_k.setValue(2)
        self.spin_cl_k.valueChanged.connect(self._actualizar_tabla_cl)
        ctrl_layout.addWidget(self.spin_cl_k)

        self.chk_frac_cl = QCheckBox("Fracciones")
        self.chk_frac_cl.setChecked(True)
        ctrl_layout.addWidget(self.chk_frac_cl)

        ctrl_layout.addStretch()

        btn_cl = QPushButton("▶ Verificar Combinación Lineal")
        btn_cl.setObjectName("PrimaryButton")
        btn_cl.clicked.connect(self._verificar_cl)
        ctrl_layout.addWidget(btn_cl)
        layout.addWidget(ctrl_box)

        # --- Tabla de vectores (k columnas = v1..vk, última columna = b) ---
        tabla_box = QGroupBox(
            "Matriz de vectores [v₁ | vâ‚‚ | â€¦ | vâ‚– | b]  "
            "â€” cada columna es un vector, la última columna es b"
        )
        tabla_lay = QVBoxLayout(tabla_box)
        self.tabla_cl = QTableWidget()
        tabla_lay.addWidget(self.tabla_cl)
        layout.addWidget(tabla_box)

        # --- Resultado ---
        res_box = QGroupBox("Resultado")
        res_lay = QVBoxLayout(res_box)
        self.txt_cl = QTextEdit()
        self.txt_cl.setReadOnly(True)
        res_lay.addWidget(self.txt_cl)
        layout.addWidget(res_box)

        self._actualizar_tabla_cl()
        return tab

    def _actualizar_tabla_cl(self):
        n = self.spin_cl_n.value()   # dimensión
        k = self.spin_cl_k.value()   # número de vectores generadores
        total_cols = k + 1           # k vectores + 1 columna b

        self.tabla_cl.setRowCount(n)
        self.tabla_cl.setColumnCount(total_cols)

        # Encabezados: v₁, vâ‚‚, ..., vâ‚–, b
        headers = [f"v{i+1}" for i in range(k)] + ["b"]
        self.tabla_cl.setHorizontalHeaderLabels(headers)
        self.tabla_cl.setVerticalHeaderLabels([nombre_var(i) for i in range(n)])

        for i in range(n):
            for j in range(total_cols):
                if not self.tabla_cl.item(i, j):
                    it = QTableWidgetItem("0")
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla_cl.setItem(i, j, it)
        self.tabla_cl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _verificar_cl(self):
        n = self.spin_cl_n.value()
        k = self.spin_cl_k.value()
        frac = self.chk_frac_cl.isChecked()
        errores = []

        # Leer los k vectores generadores (columnas 0..k-1)
        vectores = []
        for j in range(k):
            v = []
            for i in range(n):
                item = self.tabla_cl.item(i, j)
                val, err = parse_expresion(item.text() if item else "0")
                if err:
                    errores.append(f"â€¢ v{j+1} componente {i+1}: {err}")
                v.append(val if val is not None else Fraction(0))
            vectores.append(v)

        # Leer el vector b (última columna)
        b = []
        for i in range(n):
            item = self.tabla_cl.item(i, k)
            val, err = parse_expresion(item.text() if item else "0")
            if err:
                errores.append(f"â€¢ b componente {i+1}: {err}")
            b.append(val if val is not None else Fraction(0))

        if errores:
            QMessageBox.critical(self, "Error en los datos", "\n".join(errores))
            return

        # Llamar al motor de combinación lineal
        res = es_combinacion_lineal(b, vectores)

        if res.get("error"):
            QMessageBox.critical(self, "Error", res["error"])
            return

        # Formatear salida
        lineas = [
            "VERIFICACIÓN DE COMBINACIÓN LINEAL",
            f"¿Es  b  combinación lineal de  " +
            "{ " + ", ".join(f"v{i+1}" for i in range(k)) + " }?",
            SEP,
            "",
            "ESTRATEGIA: Se plantea el sistema  [v₁ | vâ‚‚ | â€¦ | vâ‚– | b]",
            "y se verifica si es CONSISTENTE usando Gauss-Jordan.",
            "Si tiene solución, existen escalares c₁,â€¦,câ‚– tales que b = c₁v₁+â€¦+câ‚–vâ‚–.",
            "",
        ]

        # Mostrar los vectores ingresados
        for j in range(k):
            comp_str = "  ".join(formato_numero(vectores[j][i], frac).rjust(5) for i in range(n))
            lineas.append(f"  v{j+1} = [ {comp_str} ]áµ€")
        b_str = "  ".join(formato_numero(b[i], frac).rjust(5) for i in range(n))
        lineas.append(f"   b = [ {b_str} ]áµ€")
        lineas.append("")
        lineas.append(SEP)

        if res["es_cl"]:
            lineas.append("âœ”  SÍ â€” b ES COMBINACIÓN LINEAL de los vectores dados.")
            lineas.append("")
            esc = res["escalares"]
            if esc == "infinitas":
                lineas.append(
                    "Hay INFINITAS combinaciones posibles (los vectores son linealmente dependientes)."
                )
                lineas.append(
                    "Existen múltiples conjuntos de escalares (c₁, câ‚‚, ...) que satisfacen la ecuación."
                )
            else:
                lineas.append("Escalares únicos encontrados:")
                partes_eq = []
                for j in range(k):
                    clave = nombre_var(j)
                    valor = esc.get(clave, Fraction(0))
                    lineas.append(f"   c{j+1} = {formato_numero(valor, frac)}")
                    partes_eq.append(
                        f"({formato_numero(valor, frac)})·v{j+1}"
                    )
                lineas.append("")
                lineas.append("Combinación lineal verificada:")
                lineas.append(f"   b = {' + '.join(partes_eq)}")
        else:
            lineas.append("âœ˜  NO â€” b NO es combinación lineal de los vectores dados.")
            lineas.append("")
            lineas.append(
                "El sistema [v₁|â€¦|vâ‚–|b] resultó INCONSISTENTE: la columna b "
                "es columna pivote, lo que significa que b está fuera del "
                "espacio generado por los vectores dados."
            )

        self.txt_cl.setText("\n".join(lineas))
    # ──────────────────────────────────────────────────────────────────
    # PESTAÑA 4: INDEPENDENCIA LINEAL
    # ──────────────────────────────────────────────────────────────────
    def _crear_tab_indep_lineal(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        ctrl_box = QGroupBox("Configuración de Vectores")
        ctrl_layout = QHBoxLayout(ctrl_box)
        
        ctrl_layout.addWidget(QLabel("Dimensión n (Rⁿ):"))
        self.spin_il_n = QSpinBox(); self.spin_il_n.setRange(1, 8); self.spin_il_n.setValue(3)
        self.spin_il_n.valueChanged.connect(self._actualizar_tabla_il)
        ctrl_layout.addWidget(self.spin_il_n)
        
        ctrl_layout.addWidget(QLabel("  Número de vectores k:"))
        self.spin_il_k = QSpinBox(); self.spin_il_k.setRange(1, 8); self.spin_il_k.setValue(3)
        self.spin_il_k.valueChanged.connect(self._actualizar_tabla_il)
        ctrl_layout.addWidget(self.spin_il_k)
        
        ctrl_layout.addStretch()
        btn_il = QPushButton("▶ Evaluar Independencia Lineal")
        btn_il.setObjectName("PrimaryButton")
        btn_il.clicked.connect(self._evaluar_il)
        ctrl_layout.addWidget(btn_il)
        layout.addWidget(ctrl_box)
        
        tabla_box = QGroupBox("Vectores [v₁ | v₂ | … | vₖ]")
        tabla_lay = QVBoxLayout(tabla_box)
        self.tabla_il = QTableWidget()
        tabla_lay.addWidget(self.tabla_il)
        layout.addWidget(tabla_box)
        
        res_box = QGroupBox("Resultado y Diagnóstico")
        res_lay = QVBoxLayout(res_box)
        self.txt_il = QTextEdit()
        self.txt_il.setReadOnly(True)
        res_lay.addWidget(self.txt_il)
        layout.addWidget(res_box)
        
        self._actualizar_tabla_il()
        return tab
        
    def _actualizar_tabla_il(self):
        n = self.spin_il_n.value()
        k = self.spin_il_k.value()
        self.tabla_il.setRowCount(n)
        self.tabla_il.setColumnCount(k)
        self.tabla_il.setHorizontalHeaderLabels([f"v{i+1}" for i in range(k)])
        self.tabla_il.setVerticalHeaderLabels([nombre_var(i) for i in range(n)])
        for i in range(n):
            for j in range(k):
                if not self.tabla_il.item(i, j):
                    it = QTableWidgetItem("0")
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla_il.setItem(i, j, it)
        self.tabla_il.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _evaluar_il(self):
        n = self.spin_il_n.value()
        k = self.spin_il_k.value()
        errores = []
        vectores = []
        for j in range(k):
            v = []
            for i in range(n):
                item = self.tabla_il.item(i, j)
                val, err = parse_expresion(item.text() if item else "0")
                if err: errores.append(f"• v{j+1} componente {i+1}: {err}")
                v.append(val if val is not None else Fraction(0))
            vectores.append(v)
            
        if errores:
            QMessageBox.critical(self, "Error", "\n".join(errores))
            return
            
        res = evaluar_independencia_lineal(vectores, n)
        
        lineas = [
            "EVALUACIÓN DE INDEPENDENCIA LINEAL",
            SEP,
            "Se plantea el sistema homogéneo A·x = 0, donde las columnas de A son los vectores dados.",
            "Si la única solución es la trivial (x=0), son L.I. Si hay variables libres, son L.D.",
            ""
        ]
        
        lineas.extend(res["pasos"])
        lineas.append(SEP)
        
        if res["es_li"]:
            lineas.append(f"✔ CONCLUSIÓN: Los {k} vectores son LINEALMENTE INDEPENDIENTES (L.I.).")
            lineas.append(f"   Hay un pivote en cada columna ({res['num_pivotes']} pivotes).")
            lineas.append("   La única solución a c₁v₁ + ... + cₖvₖ = 0 es c₁=0, ..., cₖ=0.")
        else:
            lineas.append(f"✘ CONCLUSIÓN: Los {k} vectores son LINEALMENTE DEPENDIENTES (L.D.).")
            lineas.append(f"   Solo hay {res['num_pivotes']} pivotes para {k} vectores.")
            lineas.append(f"   Existen {k - res['num_pivotes']} variable(s) libre(s), es decir, infinitas soluciones no triviales.")
            
        self.txt_il.setText("\n".join(lineas))

