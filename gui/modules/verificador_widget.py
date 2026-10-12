"""
Módulo 6: Verificador de Propiedades de Matrices.
Tema: Propiedades de la Matriz Inversa y Determinantes (Sesiones 10-11).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QCheckBox,
    QTextEdit, QMessageBox, QGroupBox, QHeaderView, QLineEdit
)
from PyQt6.QtCore import Qt
from fractions import Fraction
from core.parser import formato_numero
from core.algebra_avanzada import (
    inversa_matriz, determinante_reduccion, copiar_matriz
)
from core.operaciones_matriciales import multiplicar_matrices, transpuesta_matriz
from core.validadores import (
    leer_matriz_segura, leer_escalar_seguro, mostrar_error,
    formatear_matriz, comparar_matrices
)

SEP = "-" * 78


class VerificadorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        encabezado = QLabel("Verificador de Propiedades")
        encabezado.setObjectName("SectionHeader")
        encabezado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(encabezado)

        layout.addWidget(self._crear_controles())
        layout.addLayout(self._crear_tablas())
        layout.addWidget(self._crear_prop5_controles())
        layout.addWidget(self._crear_resultado())
        self._actualizar_tablas()

    # ── Construcción de la Interfaz ──────────────────────────────────

    def _crear_controles(self):
        """Crea la caja de configuración superior."""
        box = QGroupBox("Configuración (Matrices Cuadradas de orden n)")
        lay = QHBoxLayout(box)
        lay.addWidget(QLabel("Dimensión n:"))
        self.spin_n = QSpinBox()
        self.spin_n.setRange(2, 8)
        self.spin_n.setValue(2)
        self.spin_n.valueChanged.connect(self._actualizar_tablas)
        lay.addWidget(self.spin_n)
        self.chk_frac = QCheckBox("Fracciones")
        self.chk_frac.setChecked(True)
        lay.addWidget(self.chk_frac)
        lay.addStretch()
        btn = QPushButton("▶ Ejecutar Verificación Completa")
        btn.setObjectName("PrimaryButton")
        btn.clicked.connect(self._ejecutar_verificacion)
        lay.addWidget(btn)
        return box

    def _crear_tablas(self):
        """Crea las tablas para las matrices A y B."""
        tablas = QHBoxLayout()
        boxA = QGroupBox("Matriz A (Invertible)")
        layA = QVBoxLayout(boxA)
        self.tabla_A = QTableWidget()
        layA.addWidget(self.tabla_A)
        tablas.addWidget(boxA)
        boxB = QGroupBox("Matriz B (Invertible)")
        layB = QVBoxLayout(boxB)
        self.tabla_B = QTableWidget()
        layB.addWidget(self.tabla_B)
        tablas.addWidget(boxB)
        return tablas

    def _crear_prop5_controles(self):
        """Crea los controles de Fila i, Fila j y escalar k para la Propiedad 5."""
        box = QGroupBox("Variables para Propiedad 5 (Operaciones de Fila sobre A)")
        lay = QHBoxLayout(box)
        lay.addWidget(QLabel("Fila i:"))
        self.spin_fi = QSpinBox()
        self.spin_fi.setRange(1, 8)
        self.spin_fi.setValue(1)
        lay.addWidget(self.spin_fi)
        lay.addWidget(QLabel("Fila j:"))
        self.spin_fj = QSpinBox()
        self.spin_fj.setRange(1, 8)
        self.spin_fj.setValue(2)
        lay.addWidget(self.spin_fj)
        lay.addWidget(QLabel("Escalar k:"))
        self.le_k = QLineEdit("3")
        self.le_k.setFixedWidth(60)
        lay.addWidget(self.le_k)
        lay.addStretch()
        return box

    def _crear_resultado(self):
        """Crea la caja del reporte de resultados."""
        box = QGroupBox("Reporte de Propiedades")
        lay = QVBoxLayout(box)
        self.txt_res = QTextEdit()
        self.txt_res.setReadOnly(True)
        lay.addWidget(self.txt_res)
        return box

    def _actualizar_tablas(self):
        """Redimensiona las tablas A y B al orden n seleccionado."""
        n = self.spin_n.value()
        self.spin_fi.setRange(1, n)
        self.spin_fj.setRange(1, n)
        for tabla in (self.tabla_A, self.tabla_B):
            tabla.setRowCount(n)
            tabla.setColumnCount(n)
            tabla.setHorizontalHeaderLabels([f"C{j+1}" for j in range(n)])
            tabla.setVerticalHeaderLabels([f"F{i+1}" for i in range(n)])
            for i in range(n):
                for j in range(n):
                    if not tabla.item(i, j):
                        it = QTableWidgetItem("0")
                        it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        tabla.setItem(i, j, it)
            tabla.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )

    # ── Lógica del Verificador ───────────────────────────────────────

    def _ejecutar_verificacion(self):
        """Lee las matrices, valida y genera el reporte de las 6 propiedades."""
        n = self.spin_n.value()
        A, errA = leer_matriz_segura(self.tabla_A, n, n, "A")
        B, errB = leer_matriz_segura(self.tabla_B, n, n, "B")
        k_val, errK = leer_escalar_seguro(self.le_k, "Escalar k")
        errores = errA + errB + ([errK] if errK else [])
        if mostrar_error(self, errores):
            return

        detA, _ = determinante_reduccion(A)
        detB, _ = determinante_reduccion(B)
        if detA == 0 or detB == 0:
            QMessageBox.critical(
                self, "Error",
                "Ambas matrices deben ser invertibles (det != 0)."
            )
            return

        A_inv, _, _ = inversa_matriz(A, n)
        B_inv, _, _ = inversa_matriz(B, n)
        fi = self.spin_fi.value() - 1
        fj = self.spin_fj.value() - 1
        frac = self.chk_frac.isChecked()

        reporte = ["REPORTE DE VERIFICACIÓN DE PROPIEDADES", SEP, ""]
        reporte += self._prop_identidad(A, A_inv, n, frac)
        reporte += self._prop1(A, A_inv, n, frac)
        reporte += self._prop2(A, B, A_inv, B_inv, n, frac)
        reporte += self._prop3(A, A_inv, n, frac)
        reporte += self._prop4(A_inv, detA, frac)
        reporte += self._prop5(A, detA, fi, fj, k_val, n, frac)
        reporte += self._prop6(A, detA, n, frac)
        self.txt_res.setText("\n".join(reporte))

    # ── Cada propiedad en su propia función corta ────────────────────

    def _veredicto(self, cumple):
        """Retorna la línea de texto con el checkmark correspondiente."""
        return "   ✔ Se cumple." if cumple else "   ✘ No se cumple."

    def _prop_identidad(self, A, A_inv, n, frac):
        """Propiedad fundamental: A⁻¹ · A = I."""
        Ainv_A, _, _ = multiplicar_matrices(A_inv, A, n, n, n)
        I_esp = [[Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)]
        cumple = comparar_matrices(Ainv_A, I_esp)
        return [
            "▶ Propiedad Fundamental: A⁻¹ · A = I (Matriz Identidad)",
            self._veredicto(cumple),
            "   Lado izquierdo (A⁻¹ · A):",
            formatear_matriz(Ainv_A, frac),
            "   Lado derecho (I):",
            formatear_matriz(I_esp, frac), SEP
        ]

    def _prop1(self, A, A_inv, n, frac):
        """Propiedad 1: (A⁻¹)⁻¹ = A."""
        A_inv_inv, _, _ = inversa_matriz(A_inv, n)
        cumple = comparar_matrices(A_inv_inv, A)
        return [
            "▶ Propiedad 1: (A⁻¹)⁻¹ = A",
            self._veredicto(cumple),
            "   Lado izquierdo (A⁻¹)⁻¹:",
            formatear_matriz(A_inv_inv, frac),
            "   Lado derecho (A):",
            formatear_matriz(A, frac), SEP
        ]

    def _prop2(self, A, B, A_inv, B_inv, n, frac):
        """Propiedad 2: (AB)⁻¹ = B⁻¹ A⁻¹."""
        AB, _, _ = multiplicar_matrices(A, B, n, n, n)
        AB_inv, _, _ = inversa_matriz(AB, n)
        Binv_Ainv, _, _ = multiplicar_matrices(B_inv, A_inv, n, n, n)
        cumple = comparar_matrices(AB_inv, Binv_Ainv)
        return [
            "▶ Propiedad 2: (AB)⁻¹ = B⁻¹ A⁻¹",
            self._veredicto(cumple),
            "   Lado izquierdo (AB)⁻¹:",
            formatear_matriz(AB_inv, frac),
            "   Lado derecho (B⁻¹ A⁻¹):",
            formatear_matriz(Binv_Ainv, frac), SEP
        ]

    def _prop3(self, A, A_inv, n, frac):
        """Propiedad 3: (Aᵀ)⁻¹ = (A⁻¹)ᵀ."""
        AT, _, _ = transpuesta_matriz(A, n, n)
        AT_inv, _, _ = inversa_matriz(AT, n)
        Ainv_T, _, _ = transpuesta_matriz(A_inv, n, n)
        cumple = comparar_matrices(AT_inv, Ainv_T)
        return [
            "▶ Propiedad 3: (Aᵀ)⁻¹ = (A⁻¹)ᵀ",
            self._veredicto(cumple),
            "   Lado izquierdo (Aᵀ)⁻¹:",
            formatear_matriz(AT_inv, frac),
            "   Lado derecho (A⁻¹)ᵀ:",
            formatear_matriz(Ainv_T, frac), SEP
        ]

    def _prop4(self, A_inv, detA, frac):
        """Propiedad 4: det(A⁻¹) = 1/det(A)."""
        det_Ainv, _ = determinante_reduccion(A_inv)
        inverso = Fraction(1, detA)
        cumple = (det_Ainv == inverso)
        return [
            "▶ Propiedad 4: det(A⁻¹) = 1 / det(A)",
            self._veredicto(cumple),
            f"   det(A⁻¹) = {formato_numero(det_Ainv, frac)}",
            f"   1/det(A) = 1/({formato_numero(detA, frac)}) = "
            f"{formato_numero(inverso, frac)}", SEP
        ]

    def _prop5(self, A, detA, fi, fj, k_val, n, frac):
        """Propiedad 5: Efecto de operaciones de fila sobre det(A)."""
        lineas = [
            "▶ Propiedad 5: Operaciones de fila sobre det(A)",
            f"   det(A) original = {formato_numero(detA, frac)}"
        ]
        # a) Intercambio de filas: det cambia de signo
        A_swap = copiar_matriz(A)
        A_swap[fi], A_swap[fj] = A_swap[fj], A_swap[fi]
        det_swap, _ = determinante_reduccion(A_swap)
        lineas.append(f"   a) Intercambio F{fi+1} <-> F{fj+1}:")
        lineas.append(f"      Nuevo det = {formato_numero(det_swap, frac)}"
                       f".  Esperado = {formato_numero(-detA, frac)}")
        lineas.append(self._veredicto(det_swap == -detA))

        # b) Multiplicar fila por escalar: det se multiplica por k
        A_scale = copiar_matriz(A)
        A_scale[fi] = [A_scale[fi][c] * k_val for c in range(n)]
        det_scale, _ = determinante_reduccion(A_scale)
        lineas.append(f"   b) Multiplicar F{fi+1} por k={formato_numero(k_val, frac)}:")
        lineas.append(f"      Nuevo det = {formato_numero(det_scale, frac)}"
                       f".  Esperado = {formato_numero(detA * k_val, frac)}")
        lineas.append(self._veredicto(det_scale == detA * k_val))

        # c) Reemplazo Fi -> Fi + k*Fj: det no cambia
        if fi != fj:
            A_rep = copiar_matriz(A)
            A_rep[fi] = [A_rep[fi][c] + k_val * A_rep[fj][c] for c in range(n)]
            det_rep, _ = determinante_reduccion(A_rep)
            lineas.append(f"   c) F{fi+1} -> F{fi+1} + ({formato_numero(k_val, frac)})*F{fj+1}:")
            lineas.append(f"      Nuevo det = {formato_numero(det_rep, frac)}"
                           f".  Esperado = {formato_numero(detA, frac)}")
            lineas.append(self._veredicto(det_rep == detA))

        lineas.append(SEP)
        return lineas

    def _prop6(self, A, detA, n, frac):
        """Propiedad 6: Determinante de triangular = producto de la diagonal."""
        mat_tri = copiar_matriz(A)
        intercambios = 0
        for i in range(n):
            # Buscar pivote no nulo para evitar división entre cero
            p = i
            while p < n and mat_tri[p][i] == 0:
                p += 1
            if p == n:
                continue
            if p != i:
                mat_tri[i], mat_tri[p] = mat_tri[p], mat_tri[i]
                intercambios += 1
            for j in range(i + 1, n):
                factor = mat_tri[j][i] / mat_tri[i][i]
                for c in range(i, n):
                    mat_tri[j][c] -= factor * mat_tri[i][c]

        prod_diag = Fraction(1)
        diag_str = []
        for i in range(n):
            prod_diag *= mat_tri[i][i]
            diag_str.append(f"({formato_numero(mat_tri[i][i], frac)})")

        signo = -1 if intercambios % 2 != 0 else 1
        det_calc = prod_diag * signo
        cumple = (det_calc == detA)

        return [
            "▶ Propiedad 6: det(triangular) = producto de la diagonal",
            "   Matriz triangular superior:",
            formatear_matriz(mat_tri, frac),
            f"   Producto diagonal: {' * '.join(diag_str)} = "
            f"{formato_numero(prod_diag, frac)}",
            f"   Con {intercambios} intercambio(s): "
            f"{formato_numero(det_calc, frac)}",
            f"   det(A) real: {formato_numero(detA, frac)}",
            self._veredicto(cumple)
        ]
