"""
Módulo de Interfaz Gráfica para Cálculo de Determinantes.
Soporta:
- Expansión por cofactores (para matrices pequeñas)
- Reducción de filas / Operaciones elementales (para matrices grandes)
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QCheckBox,
    QTextEdit, QMessageBox, QGroupBox, QHeaderView
)
from PyQt6.QtCore import Qt
from fractions import Fraction
from core.parser import parse_expresion, formato_numero
from core.eliminacion_gaussiana import nombre_var
from core.algebra_avanzada import determinante_cofactores, determinante_reduccion

SEP = "-" * 78

class DeterminantesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        encabezado = QLabel("Cálculo de Determinantes")
        encabezado.setObjectName("SectionHeader")
        encabezado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(encabezado)

        # --- Controles ---
        ctrl_box = QGroupBox("Configuración de la Matriz Cuadrada (n × n)")
        ctrl_layout = QHBoxLayout(ctrl_box)
        
        ctrl_layout.addWidget(QLabel("Dimensión n:"))
        self.spin_n = QSpinBox()
        self.spin_n.setRange(1, 8)
        self.spin_n.setValue(3)
        self.spin_n.valueChanged.connect(self.actualizar_tabla)
        ctrl_layout.addWidget(self.spin_n)
        
        self.chk_fracciones = QCheckBox("Mostrar Fracciones")
        self.chk_fracciones.setChecked(True)
        ctrl_layout.addWidget(self.chk_fracciones)
        
        ctrl_layout.addStretch()
        
        btn_cof = QPushButton("▶ Cofactores (Laplace)")
        btn_cof.clicked.connect(lambda: self.calcular(metodo="cofactores"))
        ctrl_layout.addWidget(btn_cof)
        
        btn_red = QPushButton("▶ Reducción (Operaciones de Fila)")
        btn_red.setObjectName("PrimaryButton")
        btn_red.clicked.connect(lambda: self.calcular(metodo="reduccion"))
        ctrl_layout.addWidget(btn_red)
        
        layout.addWidget(ctrl_box)

        # --- Tabla ---
        mat_box = QGroupBox("Matriz A")
        mat_lay = QVBoxLayout(mat_box)
        self.tabla = QTableWidget()
        mat_lay.addWidget(self.tabla)
        layout.addWidget(mat_box)

        # --- Resultado ---
        res_box = QGroupBox("Procedimiento y Resultado")
        res_lay = QVBoxLayout(res_box)
        self.txt_res = QTextEdit()
        self.txt_res.setReadOnly(True)
        res_lay.addWidget(self.txt_res)
        layout.addWidget(res_box)

        self.actualizar_tabla()

    def actualizar_tabla(self):
        n = self.spin_n.value()
        self.tabla.setRowCount(n)
        self.tabla.setColumnCount(n)
        for i in range(n):
            for j in range(n):
                if not self.tabla.item(i, j):
                    it = QTableWidgetItem("0")
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla.setItem(i, j, it)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def calcular(self, metodo):
        n = self.spin_n.value()
        errores = []
        A = []
        for i in range(n):
            fila = []
            for j in range(n):
                item = self.tabla.item(i, j)
                val, err = parse_expresion(item.text() if item else "0")
                if err: errores.append(f"• A[{i+1},{j+1}]: {err}")
                fila.append(val if val is not None else Fraction(0))
            A.append(fila)
            
        if errores:
            QMessageBox.critical(self, "Error", "\n".join(errores))
            return
            
        lineas = [f"CÁLCULO DEL DETERMINANTE POR {metodo.upper()}", SEP, ""]
        
        if metodo == "cofactores":
            det, pasos = determinante_cofactores(A)
            lineas.append(pasos)
        else:
            det, pasos = determinante_reduccion(A)
            lineas.extend(pasos)
            
        lineas.append(SEP)
        lineas.append(f"|A| = {formato_numero(det, self.chk_fracciones.isChecked())}")
        
        self.txt_res.setText("\n".join(lineas))
