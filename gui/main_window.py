"""
Ventana Principal de la Calculadora de Ãlgebra Lineal.
Dashboard moderno con menÃº de navegaciÃ³n por mÃ³dulos.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QFrame
from PyQt6.QtCore import Qt
from gui.modules.ecuaciones_widget import EcuacionesWidget
from gui.modules.transformaciones_widget import TransformacionesWidget
from gui.modules.operaciones_widget import OperacionesWidget
from gui.modules.determinantes_widget import DeterminantesWidget
from gui.modules.verificador_widget import VerificadorWidget
from gui.styles import STYLE_SHEET

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Algebra Lineal - UAM (Next-Gen 2026)")
        self.resize(1200, 800)
        self.setStyleSheet(STYLE_SHEET)
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- PANEL LATERAL (SIDEBAR) ---
        sidebar = QFrame()
        sidebar.setObjectName("LeftPanel")
        sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(sidebar)
        
        title_label = QLabel("Calculadora\nÁlgebra Lineal")
        title_label.setObjectName("AppTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title_label)
        
        sidebar_layout.addSpacing(20)
        
        # BotÃ³n MÃ³dulo 1: Sistemas de Ecuaciones
        self.btn_mod1 = QPushButton("1. Sistemas de Ecuaciones\n(Gauss & Gauss-Jordan)")
        self.btn_mod1.setObjectName("MenuButtonActive")
        self.btn_mod1.clicked.connect(self._activar_mod1)
        sidebar_layout.addWidget(self.btn_mod1)
        
        sidebar_layout.addSpacing(10)
        
        # BotÃ³n MÃ³dulo 2: Transformaciones Lineales
        self.btn_mod2 = QPushButton("2. Transformaciones Lineales\n[ T(x) = A · x ]")
        self.btn_mod2.clicked.connect(self._activar_mod2)
        sidebar_layout.addWidget(self.btn_mod2)
        
        sidebar_layout.addSpacing(10)
        
        # BotÃ³n MÃ³dulo 3: Operaciones Matriciales
        self.btn_mod3 = QPushButton("3. Operaciones Matriciales\n& Combinación Lineal")
        self.btn_mod3.clicked.connect(self._activar_mod3)
        sidebar_layout.addWidget(self.btn_mod3)
        
        sidebar_layout.addSpacing(10)
        
        self.btn_mod4 = QPushButton("4. Determinantes & Cramer\n(Próximamente)")
        self.btn_mod4.clicked.connect(self._activar_mod4)
        sidebar_layout.addWidget(self.btn_mod4)
        
        sidebar_layout.addSpacing(10)
        
        self.btn_mod5 = QPushButton("5. Vectores & Espacios\n(Próximamente)")
        self.btn_mod5.setEnabled(False)
        sidebar_layout.addWidget(self.btn_mod5)
        
        sidebar_layout.addStretch()
        
        footer_label = QLabel("UAM - FIA 2026\nProyecto Integrador de Algebra")
        footer_label.setStyleSheet("color: #64748B; font-size: 11px;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(footer_label)
        
        main_layout.addWidget(sidebar)
        
        # --- PANEL CONTENEDOR PRINCIPAL (STACKED WIDGET) ---
        self.stack = QStackedWidget()
        
        # Vista 1: Ecuaciones
        self.ecuaciones_widget = EcuacionesWidget()
        self.stack.addWidget(self.ecuaciones_widget)
        
        # Vista 2: Transformaciones Lineales
        self.transformaciones_widget = TransformacionesWidget()
        self.stack.addWidget(self.transformaciones_widget)

        # Vista 3: Operaciones Matriciales & Combinación Lineal
        self.operaciones_widget = OperacionesWidget()
        self.stack.addWidget(self.operaciones_widget)
        
        # Vista 4: Determinantes
        self.determinantes_widget = DeterminantesWidget()
        self.stack.addWidget(self.determinantes_widget)
        
        # Vista 6: Verificador de Propiedades
        self.verificador_widget = VerificadorWidget()
        self.stack.addWidget(self.verificador_widget)
        
        main_layout.addWidget(self.stack)

    def _activar_mod1(self):
        self.stack.setCurrentIndex(0)
        self.btn_mod1.setObjectName("MenuButtonActive")
        self.btn_mod2.setObjectName("")
        self.btn_mod3.setObjectName("")
        self._actualizar_estilos_botones()

    def _activar_mod2(self):
        self.stack.setCurrentIndex(1)
        self.btn_mod1.setObjectName("")
        self.btn_mod2.setObjectName("MenuButtonActive")
        self.btn_mod3.setObjectName("")
        self._actualizar_estilos_botones()

    def _activar_mod3(self):
        self.stack.setCurrentIndex(2)
        self.btn_mod1.setObjectName("")
        self.btn_mod2.setObjectName("")
        self.btn_mod3.setObjectName("MenuButtonActive")
        self._actualizar_estilos_botones()

    def _activar_mod4(self):
        self.stack.setCurrentIndex(3)
        self.btn_mod1.setObjectName("")
        self.btn_mod2.setObjectName("")
        self.btn_mod3.setObjectName("")
        self.btn_mod4.setObjectName("MenuButtonActive")
        self._actualizar_estilos_botones()

    def _activar_mod6(self):
        self.stack.setCurrentIndex(4)
        self.btn_mod1.setObjectName("")
        self.btn_mod2.setObjectName("")
        self.btn_mod3.setObjectName("")
        self.btn_mod4.setObjectName("")
        self.btn_mod6.setObjectName("MenuButtonActive")
        self._actualizar_estilos_botones()

    def _actualizar_estilos_botones(self):
        for btn in (self.btn_mod1, self.btn_mod2, self.btn_mod3, self.btn_mod4, getattr(self, "btn_mod6", self.btn_mod4)):
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _mostrar_teoremas(self):
        from PyQt6.QtWidgets import QMessageBox
        idx = self.stack.currentIndex()
        txt = ""
        if idx == 0:
            txt = "Módulo 1: Sistemas de Ecuaciones\n\nTeorema de Rouché-Frobenius:\nUn sistema lineal es consistente si y solo si el rango de la matriz de coeficientes es igual al rango de la matriz aumentada.\n\nReglas:\n- Sin variables libres = Solución Única\n- Con variables libres = Infinitas Soluciones\n- Inconsistencia = Fila de ceros igualada a un número no nulo."
        elif idx == 1:
            txt = "Módulo 2: Transformaciones Lineales\n\nTeoremas:\n1. T es Lineal si T(cu + v) = cT(u) + T(v).\n2. Toda transformación lineal de R^n a R^m se puede representar como T(x) = Ax.\n3. T es Inyectiva (Uno a Uno) si y solo si T(x)=0 tiene solo la solución trivial (Ax=0 sin variables libres).\n4. T es Sobreyectiva (Sobre R^m) si las columnas de A generan R^m (hay un pivote en cada fila)."
        elif idx == 2:
            txt = "Módulo 3: Operaciones e Independencia Lineal\n\nIndependencia Lineal:\nUn conjunto de k vectores en R^n es L.I. si y solo si la única solución a c1v1 + ... + ckvk = 0 es la trivial (c1=...=ck=0).\n\nMatriz Inversa:\nA es invertible si y solo si su determinante es diferente de 0. [A|I] se reduce a [I|A^-1]."
        elif idx == 3:
            txt = "Módulo 4: Determinantes\n\nPropiedades:\n1. Si A tiene una fila o columna de ceros, |A| = 0.\n2. Si se intercambian dos filas, el determinante cambia de signo.\n3. Si se multiplica una fila por un escalar c, el determinante se multiplica por c.\n4. Si a una fila se le suma un múltiplo de otra (R_i = R_i + cR_j), el determinante NO cambia."
            
        QMessageBox.information(self, "Teoremas Clave del Módulo Actual", txt)

