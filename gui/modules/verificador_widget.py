"""
Módulo 6: Verificador de Propiedades (Tarea 5)
Comprueba las propiedades de la matriz inversa y los determinantes.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QCheckBox,
    QTextEdit, QMessageBox, QGroupBox, QHeaderView, QLineEdit
)
from PyQt6.QtCore import Qt
from fractions import Fraction
from core.parser import parse_expresion, formato_numero
from core.algebra_avanzada import inversa_matriz, determinante_reduccion, copiar_matriz
from core.operaciones_matriciales import multiplicar_matrices, transpuesta_matriz

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

        # --- Controles Superiores ---
        ctrl_box = QGroupBox("Configuración (Matrices Cuadradas de orden n)")
        ctrl_layout = QHBoxLayout(ctrl_box)
        
        ctrl_layout.addWidget(QLabel("Dimensión n:"))
        self.spin_n = QSpinBox()
        self.spin_n.setRange(2, 8)
        self.spin_n.setValue(2)
        self.spin_n.valueChanged.connect(self._actualizar_tablas)
        ctrl_layout.addWidget(self.spin_n)
        
        self.chk_frac = QCheckBox("Fracciones")
        self.chk_frac.setChecked(True)
        ctrl_layout.addWidget(self.chk_frac)

        ctrl_layout.addStretch()
        
        btn_verificar = QPushButton("▶ Ejecutar Verificación Completa")
        btn_verificar.setObjectName("PrimaryButton")
        btn_verificar.clicked.connect(self._ejecutar_verificacion)
        ctrl_layout.addWidget(btn_verificar)
        
        layout.addWidget(ctrl_box)

        # --- Tablas A y B ---
        tablas_layout = QHBoxLayout()
        
        boxA = QGroupBox("Matriz A (Invertible)")
        layA = QVBoxLayout(boxA)
        self.tabla_A = QTableWidget()
        layA.addWidget(self.tabla_A)
        tablas_layout.addWidget(boxA)
        
        boxB = QGroupBox("Matriz B (Invertible)")
        layB = QVBoxLayout(boxB)
        self.tabla_B = QTableWidget()
        layB.addWidget(self.tabla_B)
        tablas_layout.addWidget(boxB)
        
        layout.addLayout(tablas_layout)

        # --- Operaciones de Fila (Propiedad 5) ---
        prop5_box = QGroupBox("Variables para Propiedad 5 (Operaciones de Fila sobre A)")
        prop5_lay = QHBoxLayout(prop5_box)
        
        prop5_lay.addWidget(QLabel("Fila i:"))
        self.spin_fi = QSpinBox()
        self.spin_fi.setRange(1, 8)
        self.spin_fi.setValue(1)
        prop5_lay.addWidget(self.spin_fi)
        
        prop5_lay.addWidget(QLabel("Fila j:"))
        self.spin_fj = QSpinBox()
        self.spin_fj.setRange(1, 8)
        self.spin_fj.setValue(2)
        prop5_lay.addWidget(self.spin_fj)
        
        prop5_lay.addWidget(QLabel("Escalar k:"))
        self.le_k = QLineEdit("3")
        self.le_k.setFixedWidth(60)
        prop5_lay.addWidget(self.le_k)
        
        prop5_lay.addStretch()
        layout.addWidget(prop5_box)

        # --- Resultado ---
        res_box = QGroupBox("Reporte de Propiedades")
        res_lay = QVBoxLayout(res_box)
        self.txt_res = QTextEdit()
        self.txt_res.setReadOnly(True)
        res_lay.addWidget(self.txt_res)
        layout.addWidget(res_box)

        self._actualizar_tablas()

    def _actualizar_tablas(self):
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
            tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _leer_matriz(self, tabla, n):
        M = []
        errores = []
        for i in range(n):
            fila = []
            for j in range(n):
                item = tabla.item(i, j)
                val, err = parse_expresion(item.text() if item else "0")
                if err:
                    errores.append(f"F{i+1}C{j+1}: {err}")
                fila.append(val if val is not None else Fraction(0))
            M.append(fila)
        return M, errores

    def _formatear_matriz(self, M, n):
        frac = self.chk_frac.isChecked()
        txts = [[formato_numero(M[i][j], frac) for j in range(n)] for i in range(n)]
        ancho = max(3, max(len(c) for fila in txts for c in fila) + 1)
        lineas = []
        for fila in txts:
            celdas = [c.rjust(ancho) for c in fila]
            lineas.append("   [ " + "  ".join(celdas) + " ]")
        return "\n".join(lineas)

    def _comparar_matrices(self, M1, M2, n):
        for i in range(n):
            for j in range(n):
                if M1[i][j] != M2[i][j]: return False
        return True

    def _ejecutar_verificacion(self):
        n = self.spin_n.value()
        frac = self.chk_frac.isChecked()
        A, errA = self._leer_matriz(self.tabla_A, n)
        B, errB = self._leer_matriz(self.tabla_B, n)
        
        errores = errA + errB
        k_val, errK = parse_expresion(self.le_k.text().strip())
        if errK: errores.append(f"Escalar k: {errK}")
        
        if errores:
            QMessageBox.critical(self, "Error en los datos", "\n".join(errores))
            return
            
        fi = self.spin_fi.value() - 1
        fj = self.spin_fj.value() - 1
            
        reporte = ["REPORTE DE VERIFICACIÓN DE PROPIEDADES (TAREA 5)", SEP, ""]
        
        # Calcular Inversas y Determinantes iniciales
        detA, _ = determinante_reduccion(A)
        detB, _ = determinante_reduccion(B)
        
        if detA == 0 or detB == 0:
            QMessageBox.critical(self, "Error", "Ambas matrices deben ser invertibles (det != 0) para estas propiedades.")
            return
            
        A_inv, _, _ = inversa_matriz(A, n)
        B_inv, _, _ = inversa_matriz(B, n)
        
        # --- Propiedad 1: (A^-1)^-1 = A ---
        reporte.append("▶ Propiedad 1: (A⁻¹)⁻¹ = A")
        A_inv_inv, _, _ = inversa_matriz(A_inv, n)
        if self._comparar_matrices(A_inv_inv, A, n):
            reporte.append("   ✔ Se cumple: Ambas matrices son idénticas.")
        else:
            reporte.append("   ✘ No se cumple.")
        reporte.append("   Lado izquierdo (A⁻¹)⁻¹:")
        reporte.append(self._formatear_matriz(A_inv_inv, n))
        reporte.append("   Lado derecho (A):")
        reporte.append(self._formatear_matriz(A, n))
        reporte.append(SEP)
        
        # --- Propiedad 2: (AB)^-1 = B^-1 * A^-1 ---
        reporte.append("▶ Propiedad 2: (AB)⁻¹ = B⁻¹ A⁻¹")
        AB, _, _ = multiplicar_matrices(A, B, n, n, n)
        AB_inv, _, _ = inversa_matriz(AB, n)
        Binv_Ainv, _, _ = multiplicar_matrices(B_inv, A_inv, n, n, n)
        
        if self._comparar_matrices(AB_inv, Binv_Ainv, n):
            reporte.append("   ✔ Se cumple: El resultado es el mismo.")
        else:
            reporte.append("   ✘ No se cumple.")
        reporte.append("   Lado izquierdo (AB)⁻¹:")
        reporte.append(self._formatear_matriz(AB_inv, n))
        reporte.append("   Lado derecho (B⁻¹ A⁻¹):")
        reporte.append(self._formatear_matriz(Binv_Ainv, n))
        reporte.append(SEP)
        
        # --- Propiedad 3: (A^T)^-1 = (A^-1)^T ---
        reporte.append("▶ Propiedad 3: (Aᵀ)⁻¹ = (A⁻¹)ᵀ")
        AT, _, _ = transpuesta_matriz(A, n, n)
        AT_inv, _, _ = inversa_matriz(AT, n)
        Ainv_T, _, _ = transpuesta_matriz(A_inv, n, n)
        
        if self._comparar_matrices(AT_inv, Ainv_T, n):
            reporte.append("   ✔ Se cumple.")
        else:
            reporte.append("   ✘ No se cumple.")
        reporte.append("   Lado izquierdo (Aᵀ)⁻¹:")
        reporte.append(self._formatear_matriz(AT_inv, n))
        reporte.append("   Lado derecho (A⁻¹)ᵀ:")
        reporte.append(self._formatear_matriz(Ainv_T, n))
        reporte.append(SEP)
        
        # --- Propiedad 4: det(A^-1) = 1/det(A) ---
        reporte.append("▶ Propiedad 4: det(A⁻¹) = 1 / det(A)")
        det_Ainv, _ = determinante_reduccion(A_inv)
        inverso_detA = Fraction(1, detA)
        if det_Ainv == inverso_detA:
            reporte.append("   ✔ Se cumple.")
        else:
            reporte.append("   ✘ No se cumple.")
        reporte.append(f"   det(A⁻¹) = {formato_numero(det_Ainv, frac)}")
        reporte.append(f"   1 / det(A) = 1 / ({formato_numero(detA, frac)}) = {formato_numero(inverso_detA, frac)}")
        reporte.append(SEP)
        
        # --- Propiedad 5: Operaciones de Fila ---
        reporte.append("▶ Propiedad 5: Efecto de las operaciones de fila sobre el determinante de A")
        reporte.append(f"   Determinante original det(A) = {formato_numero(detA, frac)}")
        
        # 5a. Intercambio
        A_swap = copiar_matriz(A)
        A_swap[fi], A_swap[fj] = A_swap[fj], A_swap[fi]
        det_swap, _ = determinante_reduccion(A_swap)
        cumple_swap = (det_swap == -detA)
        reporte.append(f"   a) Intercambio F{fi+1} <-> F{fj+1}:")
        reporte.append(f"      Nuevo det = {formato_numero(det_swap, frac)}. Esperado = -det(A) = {formato_numero(-detA, frac)}")
        reporte.append("      ✔ Se cumple." if cumple_swap else "      ✘ No se cumple.")
        
        # 5b. Escalar
        A_scale = copiar_matriz(A)
        A_scale[fi] = [A_scale[fi][c] * k_val for c in range(n)]
        det_scale, _ = determinante_reduccion(A_scale)
        cumple_scale = (det_scale == detA * k_val)
        reporte.append(f"   b) Multiplicar F{fi+1} por k={formato_numero(k_val, frac)}:")
        reporte.append(f"      Nuevo det = {formato_numero(det_scale, frac)}. Esperado = k*det(A) = {formato_numero(detA * k_val, frac)}")
        reporte.append("      ✔ Se cumple." if cumple_scale else "      ✘ No se cumple.")
        
        # 5c. Reemplazo
        A_rep = copiar_matriz(A)
        if fi != fj:
            A_rep[fi] = [A_rep[fi][c] + k_val * A_rep[fj][c] for c in range(n)]
            det_rep, _ = determinante_reduccion(A_rep)
            cumple_rep = (det_rep == detA)
            reporte.append(f"   c) Reemplazo F{fi+1} -> F{fi+1} + ({formato_numero(k_val, frac)})*F{fj+1}:")
            reporte.append(f"      Nuevo det = {formato_numero(det_rep, frac)}. Esperado = det(A) = {formato_numero(detA, frac)}")
            reporte.append("      ✔ Se cumple." if cumple_rep else "      ✘ No se cumple.")
        reporte.append(SEP)
        
        # --- Propiedad 6: Matriz Triangular ---
        reporte.append("▶ Propiedad 6: Determinante de matriz triangular (Producto de la diagonal)")
        
        mat_tri = copiar_matriz(A)
        intercambios = 0
        factores = []
        for i in range(n):
            p = i
            while p < n and mat_tri[p][i] == 0: p += 1
            if p == n: continue
            if p != i:
                mat_tri[i], mat_tri[p] = mat_tri[p], mat_tri[i]
                intercambios += 1
            for j in range(i+1, n):
                f = mat_tri[j][i] / mat_tri[i][i]
                for c in range(i, n):
                    mat_tri[j][c] -= f * mat_tri[i][c]
                    
        prod_diag = Fraction(1)
        diag_str = []
        for i in range(n):
            prod_diag *= mat_tri[i][i]
            diag_str.append(f"({formato_numero(mat_tri[i][i], frac)})")
            
        signo = -1 if intercambios % 2 != 0 else 1
        det_calculado = prod_diag * signo
        cumple_tri = (det_calculado == detA)
        
        reporte.append(f"   Matriz reducida a triangular superior:")
        reporte.append(self._formatear_matriz(mat_tri, n))
        reporte.append(f"   Producto diagonal: " + " * ".join(diag_str) + f" = {formato_numero(prod_diag, frac)}")
        reporte.append(f"   Con ajuste por {intercambios} intercambios de fila: {formato_numero(det_calculado, frac)}")
        reporte.append(f"   Determinante real: {formato_numero(detA, frac)}")
        reporte.append("   ✔ Se cumple." if cumple_tri else "   ✘ No se cumple.")
        
        self.txt_res.setText("\n".join(reporte))
