"""
Módulo de Interfaz Gráfica para Introducción a Transformaciones Lineales T(x) = Ax.
Soporta:
- Configuración de T: R^n -> R^m mediante matriz estándar A.
- Cálculo de Imagen: w = T(u) = A · u
- Preimagen / Verificación de pertenencia al rango: ¿Existe x tal que T(x) = b?
- Análisis teórico formal de Inyectividad (Uno a uno) y Sobreyectividad (Sobre R^m).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QCheckBox,
    QTextEdit, QMessageBox, QGroupBox, QHeaderView
)
from PyQt6.QtCore import Qt
from fractions import Fraction
from core.parser import parse_expresion, formato_numero
from core.transformaciones_lineales import analizar_transformacion_completa, evaluar_transformacion
from core.eliminacion_gaussiana import nombre_var

SEP = "-" * 78

class TransformacionesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- 1. CONFIGURACIÓN DE DIMENSIONES ---
        config_box = QGroupBox("1. Definición de la Transformación Lineal  T: ℝⁿ → ℝᵐ   [ T(x) = A · x ]")
        config_layout = QHBoxLayout(config_box)

        config_layout.addWidget(QLabel("Dimensión Codominio (m filas):"))
        self.spin_m = QSpinBox()
        self.spin_m.setRange(1, 10)
        self.spin_m.setValue(3)
        self.spin_m.valueChanged.connect(self.actualizar_tablas)
        config_layout.addWidget(self.spin_m)

        config_layout.addWidget(QLabel("Dimensión Dominio (n columnas):"))
        self.spin_n = QSpinBox()
        self.spin_n.setRange(1, 10)
        self.spin_n.setValue(3)
        self.spin_n.valueChanged.connect(self.actualizar_tablas)
        config_layout.addWidget(self.spin_n)

        self.chk_fracciones = QCheckBox("Mostrar como Fracciones (ej: 1/2)")
        self.chk_fracciones.setChecked(True)
        config_layout.addWidget(self.chk_fracciones)

        btn_limpiar = QPushButton("Limpiar Todo")
        btn_limpiar.clicked.connect(self.limpiar_tablas)
        config_layout.addWidget(btn_limpiar)

        layout.addWidget(config_box)

        # --- 2. MATRIZ ESTÁNDAR A Y VECTORES u, b ---
        paneles_layout = QHBoxLayout()

        # Matriz A
        mat_box = QGroupBox("Matriz Estándar A (m × n)")
        mat_layout = QVBoxLayout(mat_box)
        self.tabla_A = QTableWidget()
        mat_layout.addWidget(self.tabla_A)
        paneles_layout.addWidget(mat_box, 3)

        # Vector u para T(u)
        u_box = QGroupBox("Vector u ∈ ℝⁿ  [Para calcular T(u)]")
        u_layout = QVBoxLayout(u_box)
        self.tabla_u = QTableWidget()
        u_layout.addWidget(self.tabla_u)
        paneles_layout.addWidget(u_box, 1)

        # Vector b para preimagen
        b_box = QGroupBox("Vector b ∈ ℝᵐ  [¿Pertenece al Rango?]")
        b_layout = QVBoxLayout(b_box)
        self.tabla_b = QTableWidget()
        b_layout.addWidget(self.tabla_b)
        paneles_layout.addWidget(b_box, 1)

        layout.addLayout(paneles_layout)

        # Botón de Análisis
        btn_analizar = QPushButton("▶ Analizar Transformación Lineal Completa (Imagen, Rango, Inyectividad y Sobreyectividad)")
        btn_analizar.setObjectName("PrimaryButton")
        btn_analizar.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold; padding: 10px; font-size: 14px;")
        btn_analizar.clicked.connect(self.analizar_transformacion)
        layout.addWidget(btn_analizar)

        # --- 3. RESULTADOS DEL ANÁLISIS ---
        res_box = QGroupBox("Resultados y Diagnóstico de la Transformación Lineal")
        res_layout = QVBoxLayout(res_box)
        self.txt_salida = QTextEdit()
        self.txt_salida.setReadOnly(True)
        res_layout.addWidget(self.txt_salida)
        layout.addWidget(res_box)

        layout.setStretch(0, 0)
        layout.setStretch(1, 0)
        layout.setStretch(2, 0)
        layout.setStretch(3, 1)

        self.actualizar_tablas()

    def actualizar_tablas(self):
        m = self.spin_m.value()
        n = self.spin_n.value()

        # Matriz A
        self.tabla_A.setRowCount(m)
        self.tabla_A.setColumnCount(n)
        self.tabla_A.setHorizontalHeaderLabels([nombre_var(j) for j in range(n)])
        self.tabla_A.setVerticalHeaderLabels([f"R{i+1}" for i in range(m)])
        self._inicializar_celdas(self.tabla_A, m, n)
        self.tabla_A.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Vector u (n filas x 1 columna)
        self.tabla_u.setRowCount(n)
        self.tabla_u.setColumnCount(1)
        self.tabla_u.setHorizontalHeaderLabels(["u"])
        self.tabla_u.setVerticalHeaderLabels([nombre_var(j) for j in range(n)])
        self._inicializar_celdas(self.tabla_u, n, 1)
        self.tabla_u.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Vector b (m filas x 1 columna)
        self.tabla_b.setRowCount(m)
        self.tabla_b.setColumnCount(1)
        self.tabla_b.setHorizontalHeaderLabels(["b"])
        self.tabla_b.setVerticalHeaderLabels([f"b{i+1}" for i in range(m)])
        self._inicializar_celdas(self.tabla_b, m, 1)
        self.tabla_b.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _inicializar_celdas(self, tabla, filas, columnas):
        for i in range(filas):
            for j in range(columnas):
                if not tabla.item(i, j):
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    tabla.setItem(i, j, item)

    def limpiar_tablas(self):
        for t in (self.tabla_A, self.tabla_u, self.tabla_b):
            for i in range(t.rowCount()):
                for j in range(t.columnCount()):
                    t.item(i, j).setText("0")
        self.txt_salida.clear()

    def analizar_transformacion(self):
        m = self.spin_m.value()
        n = self.spin_n.value()
        frac = self.chk_fracciones.isChecked()

        # 1. Leer Matriz A
        A = []
        errores = []
        for i in range(m):
            fila = []
            for j in range(n):
                item = self.tabla_A.item(i, j)
                val, err = parse_expresion(item.text() if item else "0")
                if err:
                    errores.append(f"• Matriz A [Fila {i+1}, Col {nombre_var(j)}]: {err}")
                fila.append(val if val is not None else Fraction(0))
            A.append(fila)

        # 2. Leer Vector u
        u = []
        for j in range(n):
            item = self.tabla_u.item(j, 0)
            val, err = parse_expresion(item.text() if item else "0")
            if err:
                errores.append(f"• Vector u [{nombre_var(j)}]: {err}")
            u.append(val if val is not None else Fraction(0))

        # 3. Leer Vector b
        b = []
        for i in range(m):
            item = self.tabla_b.item(i, 0)
            val, err = parse_expresion(item.text() if item else "0")
            if err:
                errores.append(f"• Vector b [b{i+1}]: {err}")
            b.append(val if val is not None else Fraction(0))

        if errores:
            QMessageBox.critical(self, "Error en los Datos", "Se encontraron errores:\n\n" + "\n".join(errores))
            return

        # 4. Ejecutar análisis completo
        analisis = analizar_transformacion_completa(A, m, n, b=b, u=u, modo_fraccion=frac)

        lineas = [
            "ANÁLISIS DE LA TRANSFORMACIÓN LINEAL  T(x) = A · x",
            SEP,
            f"• Dominio:  {analisis['dominio']}    (espacio de vectores de entrada x de dimensión {n})",
            f"• Codominio: {analisis['codominio']}    (espacio de vectores de salida w de dimensión {m})",
            f"• Número de Columnas Pivote (Rango de A): {analisis['num_pivotes']}",
            "",
            "1. PROPIEDADES FUNDAMENTALES (Teoremas de Inyectividad y Sobreyectividad):",
            f"  {analisis['detalle_inyectiva']}",
            "",
            f"  {analisis['detalle_sobreyectiva']}",
            "",
            SEP,
            "2. EVALUACIÓN DE LA IMAGEN  w = T(u) = A · u :",
            f"   Vector ingresado u = [" + ", ".join(formato_numero(x, frac) for x in u) + "]ᵀ",
            f"   Resultado Imagen w = T(u) = [" + ", ".join(formato_numero(x, frac) for x in analisis['Tu']) + "]ᵀ",
            "   Cálculo componente a componente:",
        ]

        for p in analisis["pasos_Tu"]:
            lineas.append(f"     {p}")

        lineas.extend([
            "",
            SEP,
            "3. EVALUACIÓN DE PERTENENCIA AL RANGO  (¿Existe x tal que T(x) = b?):",
            f"   Vector objetivo b = [" + ", ".join(formato_numero(x, frac) for x in b) + "]ᵀ",
        ])

        if analisis["pertenece_rango"]:
            lineas.append(f"   ✔ EL VECTOR b SÍ PERTENECE AL RANGO / IMAGEN DE T.")
            lineas.append("   El sistema [A | b] es consistente. Existe al menos un vector x en el dominio tal que T(x) = b.")
        else:
            lineas.append(f"   ✘ EL VECTOR b NO PERTENECE AL RANGO / IMAGEN DE T.")
            lineas.append("   El sistema [A | b] es inconsistente (la columna b genera contradicción de pivote).")

        self.txt_salida.setText("\n".join(lineas))
