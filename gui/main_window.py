"""
Ventana Principal de la Calculadora de Álgebra Lineal.
Dashboard moderno con menú de navegación por módulos.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QFrame
from PyQt6.QtCore import Qt
from gui.modules.ecuaciones_widget import EcuacionesWidget
from gui.modules.transformaciones_widget import TransformacionesWidget
from gui.modules.operaciones_widget import OperacionesWidget
from gui.styles import STYLE_SHEET

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Álgebra Lineal - UAM (Next-Gen 2026)")
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
        
        # Botón Módulo 1: Sistemas de Ecuaciones
        self.btn_mod1 = QPushButton("1. Sistemas de Ecuaciones\n(Gauss & Gauss-Jordan)")
        self.btn_mod1.setObjectName("PrimaryButton")
        self.btn_mod1.clicked.connect(self._activar_mod1)
        sidebar_layout.addWidget(self.btn_mod1)
        
        sidebar_layout.addSpacing(10)
        
        # Botón Módulo 2: Transformaciones Lineales
        self.btn_mod2 = QPushButton("2. Transformaciones Lineales\n[ T(x) = A · x ]")
        self.btn_mod2.clicked.connect(self._activar_mod2)
        sidebar_layout.addWidget(self.btn_mod2)
        
        sidebar_layout.addSpacing(10)
        
        # Botón Módulo 3: Operaciones Matriciales
        self.btn_mod3 = QPushButton("3. Operaciones Matriciales\n& Combinación Lineal")
        self.btn_mod3.clicked.connect(self._activar_mod3)
        sidebar_layout.addWidget(self.btn_mod3)
        
        sidebar_layout.addSpacing(10)
        
        self.btn_mod4 = QPushButton("4. Determinantes & Cramer\n(Próximamente)")
        self.btn_mod4.setEnabled(False)
        sidebar_layout.addWidget(self.btn_mod4)
        
        sidebar_layout.addSpacing(10)
        
        self.btn_mod5 = QPushButton("5. Vectores & Espacios\n(Próximamente)")
        self.btn_mod5.setEnabled(False)
        sidebar_layout.addWidget(self.btn_mod5)
        
        sidebar_layout.addStretch()
        
        footer_label = QLabel("UAM - FIA 2026\nProyecto Integrador de Álgebra")
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
        
        main_layout.addWidget(self.stack)

    def _activar_mod1(self):
        self.stack.setCurrentIndex(0)
        self.btn_mod1.setObjectName("PrimaryButton")
        self.btn_mod2.setObjectName("")
        self.btn_mod3.setObjectName("")
        self._actualizar_estilos_botones()

    def _activar_mod2(self):
        self.stack.setCurrentIndex(1)
        self.btn_mod1.setObjectName("")
        self.btn_mod2.setObjectName("PrimaryButton")
        self.btn_mod3.setObjectName("")
        self._actualizar_estilos_botones()

    def _activar_mod3(self):
        self.stack.setCurrentIndex(2)
        self.btn_mod1.setObjectName("")
        self.btn_mod2.setObjectName("")
        self.btn_mod3.setObjectName("PrimaryButton")
        self._actualizar_estilos_botones()

    def _actualizar_estilos_botones(self):
        for btn in (self.btn_mod1, self.btn_mod2, self.btn_mod3):
            btn.style().unpolish(btn)
            btn.style().polish(btn)
