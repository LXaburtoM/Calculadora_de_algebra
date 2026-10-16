"""
Ventana Principal de la Calculadora de Álgebra Lineal.
Tema: Dashboard moderno con navegación por módulos (PyQt6).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from gui.modules.ecuaciones_widget import EcuacionesWidget
from gui.modules.transformaciones_widget import TransformacionesWidget
from gui.modules.operaciones_widget import OperacionesWidget
from gui.modules.determinantes_widget import DeterminantesWidget
from gui.modules.lu_widget import LUWidget, TEOREMAS_LU
from gui.modules.verificador_widget import VerificadorWidget
from gui.styles import STYLE_SHEET


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Álgebra Lineal - UAM (Next-Gen 2026)")
        self.resize(1280, 850)
        self.setStyleSheet(STYLE_SHEET)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── PANEL LATERAL (SIDEBAR) ──────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName("LeftPanel")
        sidebar.setFixedWidth(290)
        sidebar_layout = QVBoxLayout(sidebar)

        title_label = QLabel("Calculadora\nÁlgebra Lineal")
        title_label.setObjectName("AppTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title_label)

        sidebar_layout.addSpacing(15)

        # Botón 0: Teoremas Clave Global (Accesible desde menú principal)
        self.btn_teoremas_global = QPushButton("0. Ver Teoremas Clave\n(Módulo Actual)")
        self.btn_teoremas_global.setStyleSheet(
            "background-color: #1E293B; color: #38BDF8; font-weight: bold; border: 1px solid #38BDF8;"
        )
        self.btn_teoremas_global.clicked.connect(self._mostrar_teoremas)
        sidebar_layout.addWidget(self.btn_teoremas_global)

        sidebar_layout.addSpacing(15)

        # Botón Módulo 1: Sistemas de Ecuaciones
        self.btn_mod1 = QPushButton("1. Sistemas de Ecuaciones\n(Gauss & Gauss-Jordan)")
        self.btn_mod1.setObjectName("MenuButtonActive")
        self.btn_mod1.clicked.connect(self._activar_mod1)
        sidebar_layout.addWidget(self.btn_mod1)

        sidebar_layout.addSpacing(8)

        # Botón Módulo 2: Transformaciones Lineales
        self.btn_mod2 = QPushButton("2. Transformaciones Lineales\n[ T(x) = A · x ]")
        self.btn_mod2.clicked.connect(self._activar_mod2)
        sidebar_layout.addWidget(self.btn_mod2)

        sidebar_layout.addSpacing(8)

        # Botón Módulo 3: Operaciones Matriciales
        self.btn_mod3 = QPushButton("3. Operaciones Matriciales\n& Combinación Lineal")
        self.btn_mod3.clicked.connect(self._activar_mod3)
        sidebar_layout.addWidget(self.btn_mod3)

        sidebar_layout.addSpacing(8)

        # Botón Módulo 4: Determinantes & Cramer
        self.btn_mod4 = QPushButton("4. Determinantes & Cramer\n(Sarrus & Cofactores)")
        self.btn_mod4.clicked.connect(self._activar_mod4)
        sidebar_layout.addWidget(self.btn_mod4)

        sidebar_layout.addSpacing(8)

        # Botón Módulo 5: Factorización LU (NUEVO TAREA 6)
        self.btn_mod5 = QPushButton("5. Factorización LU\n& Solución Ax = b")
        self.btn_mod5.clicked.connect(self._activar_mod5)
        sidebar_layout.addWidget(self.btn_mod5)

        sidebar_layout.addSpacing(8)

        # Botón Módulo 6: Verificador de Propiedades
        self.btn_mod6 = QPushButton("6. Verificador de Propiedades\n(16 Teoremas Clave)")
        self.btn_mod6.clicked.connect(self._activar_mod6)
        sidebar_layout.addWidget(self.btn_mod6)

        sidebar_layout.addStretch()

        footer_label = QLabel("UAM - FIA 2026\nProyecto Integrador de Álgebra")
        footer_label.setStyleSheet("color: #64748B; font-size: 11px;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(footer_label)

        main_layout.addWidget(sidebar)

        # ── PANEL CONTENEDOR PRINCIPAL (STACKED WIDGET) ───────────────
        self.stack = QStackedWidget()

        # Vista 1: Ecuaciones (Index 0)
        self.ecuaciones_widget = EcuacionesWidget()
        self.stack.addWidget(self.ecuaciones_widget)

        # Vista 2: Transformaciones Lineales (Index 1)
        self.transformaciones_widget = TransformacionesWidget()
        self.stack.addWidget(self.transformaciones_widget)

        # Vista 3: Operaciones Matriciales (Index 2)
        self.operaciones_widget = OperacionesWidget()
        self.stack.addWidget(self.operaciones_widget)

        # Vista 4: Determinantes (Index 3)
        self.determinantes_widget = DeterminantesWidget()
        self.stack.addWidget(self.determinantes_widget)

        # Vista 5: Factorización LU (Index 4)
        self.lu_widget = LUWidget()
        self.stack.addWidget(self.lu_widget)

        # Vista 6: Verificador de Propiedades (Index 5)
        self.verificador_widget = VerificadorWidget()
        self.stack.addWidget(self.verificador_widget)

        main_layout.addWidget(self.stack)

    # ── Control de Navegación ─────────────────────────────────────────

    def _desactivar_todos_botones(self):
        for btn in (self.btn_mod1, self.btn_mod2, self.btn_mod3,
                    self.btn_mod4, self.btn_mod5, self.btn_mod6):
            btn.setObjectName("")

    def _actualizar_estilos_botones(self):
        for btn in (self.btn_mod1, self.btn_mod2, self.btn_mod3,
                    self.btn_mod4, self.btn_mod5, self.btn_mod6):
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _activar_mod1(self):
        self.stack.setCurrentIndex(0)
        self._desactivar_todos_botones()
        self.btn_mod1.setObjectName("MenuButtonActive")
        self._actualizar_estilos_botones()

    def _activar_mod2(self):
        self.stack.setCurrentIndex(1)
        self._desactivar_todos_botones()
        self.btn_mod2.setObjectName("MenuButtonActive")
        self._actualizar_estilos_botones()

    def _activar_mod3(self):
        self.stack.setCurrentIndex(2)
        self._desactivar_todos_botones()
        self.btn_mod3.setObjectName("MenuButtonActive")
        self._actualizar_estilos_botones()

    def _activar_mod4(self):
        self.stack.setCurrentIndex(3)
        self._desactivar_todos_botones()
        self.btn_mod4.setObjectName("MenuButtonActive")
        self._actualizar_estilos_botones()

    def _activar_mod5(self):
        self.stack.setCurrentIndex(4)
        self._desactivar_todos_botones()
        self.btn_mod5.setObjectName("MenuButtonActive")
        self._actualizar_estilos_botones()

    def _activar_mod6(self):
        self.stack.setCurrentIndex(5)
        self._desactivar_todos_botones()
        self.btn_mod6.setObjectName("MenuButtonActive")
        self._actualizar_estilos_botones()

    def _mostrar_teoremas(self):
        """Muestra los teoremas clave según el módulo actualmente activo."""
        idx = self.stack.currentIndex()
        if idx == 0:
            txt = (
                "Módulo 1: Sistemas de Ecuaciones Lineales\n\n"
                "• Teorema de Rouché-Frobenius: Un sistema es consistente si y solo si "
                "el rango de la matriz de coeficientes coincide con el rango de la aumentada.\n"
                "• Clasificación: Solución única (sin variables libres), Infinitas soluciones "
                "(con variables libres), Inconsistente (0 = k con k ≠ 0)."
            )
        elif idx == 1:
            txt = (
                "Módulo 2: Transformaciones Lineales [T(x) = Ax]\n\n"
                "• Definición: T es lineal si T(cu + v) = cT(u) + T(v).\n"
                "• Inyectiva (1 a 1): T(x)=0 tiene solo la solución trivial (columnas de A L.I.).\n"
                "• Sobreyectiva (Sobre R^m): Las columnas de A generan R^m (pivote en cada fila)."
            )
        elif idx == 2:
            txt = (
                "Módulo 3: Operaciones Matriciales e Independencia Lineal\n\n"
                "• Independencia Lineal: c1·v1 + ... + ck·vk = 0 implica c1 = ... = ck = 0.\n"
                "• Matriz Inversa: A es invertible si det(A) ≠ 0. Se cumple A · A⁻¹ = I."
            )
        elif idx == 3:
            txt = (
                "Módulo 4: Determinantes y Regla de Cramer\n\n"
                "• Regla de Sarrus: Válida exclusivamente para matrices 3×3.\n"
                "• Expansión por Cofactores: det(A) = sum((-1)^(i+j) · a_ij · M_ij).\n"
                "• Regla de Cramer: x_i = det(A_i) / det(A)."
            )
        elif idx == 4:
            txt = TEOREMAS_LU
        elif idx == 5:
            txt = (
                "Módulo 6: Verificador de Propiedades\n\n"
                "Evalúa ambos miembros para 16 teoremas en tres categorías:\n"
                "1. Operaciones y Transposición: (Aᵀ)ᵀ=A, (A+B)ᵀ=Aᵀ+Bᵀ, (kA)ᵀ=kAᵀ, (AB)ᵀ=BᵀAᵀ, A(B+C)=AB+AC, (AB)C=A(BC).\n"
                "2. Matriz Inversa: (A⁻¹)⁻¹=A, (AB)⁻¹=B⁻¹A⁻¹, (Aᵀ)⁻¹=(A⁻¹)ᵀ, A·A⁻¹=I.\n"
                "3. Determinantes: det(Aᵀ)=det(A), det(AB)=det(A)det(B), det(A⁻¹)=1/det(A), det(kA)=kⁿdet(A), "
                "operaciones de fila, y determinante de matriz triangular."
            )
        else:
            txt = "Seleccione un módulo para consultar sus teoremas."

        QMessageBox.information(self, "0. Teoremas Clave del Módulo Actual", txt)
