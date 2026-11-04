"""
Ventana Principal de la Calculadora de Álgebra Lineal.
Tema: Área de trabajo a pantalla completa con menú deslizable de módulos (PyQt6).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

import os
import tempfile

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QFrame, QApplication, QTextBrowser, QSizePolicy, QToolButton
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QSettings
from PyQt6.QtGui import QKeySequence, QShortcut, QFontDatabase
from gui.modules.ecuaciones_widget import EcuacionesWidget
from gui.modules.transformaciones_widget import TransformacionesWidget
from gui.modules.operaciones_widget import OperacionesWidget
from gui.modules.determinantes_widget import DeterminantesWidget
from gui.modules.lu_widget import LUWidget, TEOREMAS_LU
from gui.modules.verificador_widget import VerificadorWidget
from gui.styles import construir_estilo, TEMAS
from gui.componentes import BotonIcono, ControlSegmentado, icono
from gui.entrada import TablaMatriz

ANCHO_MENU = 300
ANCHO_RIEL = 60
ANCHO_TEOREMAS = 400

# (icono, título, subtítulo) de cada módulo, en el orden del QStackedWidget
MODULOS = [
    ("Ax=b", "Sistemas de Ecuaciones", "Gauss y Gauss-Jordan"),
    ("T(x)", "Transformaciones Lineales", "T(x) = Ax"),
    ("A·B", "Operaciones Matriciales", "Combinación lineal"),
    ("|A|", "Determinantes", "Sarrus, cofactores, Cramer"),
    ("LU", "Factorización LU", "Solución de Ax = b"),
    ("∀", "Verificador", "16 propiedades"),
]

TEOREMAS = [
    (
        "Módulo 1: Sistemas de Ecuaciones Lineales\n\n"
        "• Teorema de Rouché-Frobenius: Un sistema es consistente si y solo si "
        "el rango de la matriz de coeficientes coincide con el rango de la aumentada.\n"
        "• Clasificación: Solución única (sin variables libres), Infinitas soluciones "
        "(con variables libres), Inconsistente (0 = k con k ≠ 0)."
    ),
    (
        "Módulo 2: Transformaciones Lineales [T(x) = Ax]\n\n"
        "• Definición: T es lineal si T(cu + v) = cT(u) + T(v).\n"
        "• Inyectiva (1 a 1): T(x)=0 tiene solo la solución trivial (columnas de A L.I.).\n"
        "• Sobreyectiva (Sobre R^m): Las columnas de A generan R^m (pivote en cada fila)."
    ),
    (
        "Módulo 3: Operaciones Matriciales e Independencia Lineal\n\n"
        "• Independencia Lineal: c1·v1 + ... + ck·vk = 0 implica c1 = ... = ck = 0.\n"
        "• Matriz Inversa: A es invertible si det(A) ≠ 0. Se cumple A · A⁻¹ = I."
    ),
    (
        "Módulo 4: Determinantes y Regla de Cramer\n\n"
        "• Regla de Sarrus: Válida exclusivamente para matrices 3×3.\n"
        "• Expansión por Cofactores: det(A) = sum((-1)^(i+j) · a_ij · M_ij).\n"
        "• Regla de Cramer: x_i = det(A_i) / det(A)."
    ),
    TEOREMAS_LU,
    (
        "Módulo 6: Verificador de Propiedades\n\n"
        "Evalúa ambos miembros para 16 teoremas en tres categorías:\n"
        "1. Operaciones y Transposición: (Aᵀ)ᵀ=A, (A+B)ᵀ=Aᵀ+Bᵀ, (kA)ᵀ=kAᵀ, (AB)ᵀ=BᵀAᵀ, A(B+C)=AB+AC, (AB)C=A(BC).\n"
        "2. Matriz Inversa: (A⁻¹)⁻¹=A, (AB)⁻¹=B⁻¹A⁻¹, (Aᵀ)⁻¹=(A⁻¹)ᵀ, A·A⁻¹=I.\n"
        "3. Determinantes: det(Aᵀ)=det(A), det(AB)=det(A)det(B), det(A⁻¹)=1/det(A), det(kA)=kⁿdet(A), "
        "operaciones de fila, y determinante de matriz triangular."
    ),
]


class Scrim(QWidget):
    """Capa semitransparente detrás de los paneles; un clic los cierra."""

    def __init__(self, al_cerrar, parent=None):
        super().__init__(parent)
        self.setObjectName("Scrim")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.al_cerrar = al_cerrar
        self.hide()

    def mousePressEvent(self, event):
        self.al_cerrar()


class ItemModulo(QPushButton):
    """Entrada del menú lateral: icono, título y subtítulo."""

    def __init__(self, indice, ico, titulo, sub, parent=None):
        super().__init__(parent)
        self.setObjectName("NavItem")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"Ctrl+{indice + 1}")
        self.setMinimumHeight(54)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(12)
        self.lbl_ico = QLabel(ico)
        self.lbl_ico.setObjectName("NavIcon")
        self.lbl_ico.setFixedSize(34, 34)
        self.lbl_ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        textos = QVBoxLayout()
        textos.setSpacing(1)
        t = QLabel(titulo)
        t.setObjectName("NavTitle")
        s = QLabel(sub)
        s.setObjectName("NavSub")
        textos.addWidget(t)
        textos.addWidget(s)
        lay.addWidget(self.lbl_ico)
        lay.addLayout(textos, 1)
        for w in (self.lbl_ico, t, s):
            w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def marcar(self, activo):
        self.setChecked(activo)
        self.lbl_ico.setProperty("activo", "true" if activo else "false")
        self.lbl_ico.style().unpolish(self.lbl_ico)
        self.lbl_ico.style().polish(self.lbl_ico)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Álgebra Lineal - UAM")
        self.resize(1280, 820)
        self.ajustes = QSettings("UAM", "CalculadoraAlgebraLineal")
        tema = self.ajustes.value("tema", "oscuro")
        self.tema = tema if tema in TEMAS else "oscuro"
        self._panel_abierto = None
        self.init_ui()
        self._crear_atajos()
        self.aplicar_tema(self.tema)
        self.activar_modulo(0)

    # ── Construcción ──────────────────────────────────────────────────

    def init_ui(self):
        self.central = QWidget()
        self.central.setObjectName("Central")
        self.setCentralWidget(self.central)
        main_layout = QHBoxLayout(self.central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Vistas de los módulos (mismo orden que MODULOS)
        self.ecuaciones_widget = EcuacionesWidget()
        self.transformaciones_widget = TransformacionesWidget()
        self.operaciones_widget = OperacionesWidget()
        self.determinantes_widget = DeterminantesWidget()
        self.lu_widget = LUWidget()
        self.verificador_widget = VerificadorWidget()
        self.modulos = [
            self.ecuaciones_widget, self.transformaciones_widget, self.operaciones_widget,
            self.determinantes_widget, self.lu_widget, self.verificador_widget,
        ]

        main_layout.addWidget(self._crear_riel())
        columna = QVBoxLayout()
        columna.setSpacing(0)
        columna.addWidget(self._crear_barra_superior())

        self.stack = QStackedWidget()
        for w in self.modulos:
            self.stack.addWidget(w)
        columna.addWidget(self.stack, 1)
        main_layout.addLayout(columna, 1)

        # Capas superpuestas: fondo, menú de módulos y panel de teoremas
        self.scrim = Scrim(self.cerrar_paneles, self.central)
        self.drawer = self._crear_menu()
        self.sheet = self._crear_panel_teoremas()

    def _crear_riel(self):
        """Columna fija de iconos: cambiar de módulo cuesta un solo clic."""
        riel = QFrame()
        riel.setObjectName("Rail")
        riel.setFixedWidth(ANCHO_RIEL)
        lay = QVBoxLayout(riel)
        lay.setContentsMargins(8, 10, 8, 10)
        lay.setSpacing(6)

        self.btn_menu = BotonIcono("menu", "Menú (Ctrl+M)")
        self.btn_menu.clicked.connect(self.abrir_menu)
        lay.addWidget(self.btn_menu, 0, Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(6)

        self.items_riel = []
        for i, (ico, titulo, sub) in enumerate(MODULOS):
            b = QToolButton()
            b.setObjectName("RailItem")
            b.setText(ico)
            b.setCheckable(True)
            b.setToolTip(f"{titulo}  ·  {sub}  (Ctrl+{i + 1})")
            b.setAccessibleName(titulo)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedSize(ANCHO_RIEL - 16, ANCHO_RIEL - 16)
            b.clicked.connect(lambda _, k=i: self.activar_modulo(k))
            lay.addWidget(b)
            self.items_riel.append(b)
        lay.addStretch()
        return riel

    def _crear_barra_superior(self):
        barra = QFrame()
        barra.setObjectName("TopBar")
        barra.setFixedHeight(56)
        lay = QHBoxLayout(barra)
        lay.setContentsMargins(16, 0, 12, 0)
        lay.setSpacing(10)

        self.lbl_titulo = QLabel()
        self.lbl_titulo.setObjectName("ModuleTitle")
        lay.addWidget(self.lbl_titulo)
        lay.addSpacing(4)

        # Cada módulo puede aportar controles a la izquierda y acciones a la derecha
        self.barras_izq, self.barras_der = [], []
        for w in self.modulos:
            izq, der = w.barra_contexto() if hasattr(w, "barra_contexto") else (None, None)
            self.barras_izq.append(izq)
            self.barras_der.append(der)
            if izq:
                lay.addWidget(izq)

        lay.addStretch()

        self.btn_teoremas = BotonIcono("ayuda", "Teoremas clave del módulo")
        self.btn_teoremas.clicked.connect(self.abrir_teoremas)
        lay.addWidget(self.btn_teoremas)
        for der in self.barras_der:
            if der:
                lay.addWidget(der)
        return barra

    def _crear_menu(self):
        drawer = QFrame(self.central)
        drawer.setObjectName("Drawer")
        drawer.setFixedWidth(ANCHO_MENU)
        lay = QVBoxLayout(drawer)
        lay.setContentsMargins(12, 16, 12, 16)
        lay.setSpacing(2)

        cab = QHBoxLayout()
        cab.setContentsMargins(8, 0, 0, 10)
        marca = QVBoxLayout()
        marca.setSpacing(2)
        lbl = QLabel("Álgebra Lineal")
        lbl.setObjectName("Brand")
        sub = QLabel("UAM · FIA 2026")
        sub.setObjectName("BrandSub")
        marca.addWidget(lbl)
        marca.addWidget(sub)
        cab.addLayout(marca)
        cab.addStretch()
        self.btn_cerrar_menu = BotonIcono("cerrar", "Cerrar (Esc)", 16)
        self.btn_cerrar_menu.clicked.connect(self.cerrar_paneles)
        cab.addWidget(self.btn_cerrar_menu, 0, Qt.AlignmentFlag.AlignTop)
        lay.addLayout(cab)

        self.items_menu = []
        for i, (ico, titulo, sub_t) in enumerate(MODULOS):
            item = ItemModulo(i, ico, titulo, sub_t)
            item.clicked.connect(lambda _, k=i: self._elegir_desde_menu(k))
            lay.addWidget(item)
            self.items_menu.append(item)

        lay.addStretch()

        self.selector_tema = ControlSegmentado(["Oscuro", "Claro"])
        self.selector_tema.cambiado.connect(lambda i: self.aplicar_tema(["oscuro", "claro"][i]))
        fila = QHBoxLayout()
        fila.setContentsMargins(8, 0, 8, 0)
        fila.addWidget(self.selector_tema)
        fila.addStretch()
        lay.addLayout(fila)

        drawer.hide()
        return drawer

    def _crear_panel_teoremas(self):
        sheet = QFrame(self.central)
        sheet.setObjectName("Sheet")
        sheet.setFixedWidth(ANCHO_TEOREMAS)
        lay = QVBoxLayout(sheet)
        lay.setContentsMargins(16, 16, 12, 16)
        cab = QHBoxLayout()
        lbl = QLabel("Teoremas")
        lbl.setObjectName("Brand")
        cab.addWidget(lbl)
        cab.addStretch()
        self.btn_cerrar_teoremas = BotonIcono("cerrar", "Cerrar (Esc)", 16)
        self.btn_cerrar_teoremas.clicked.connect(self.cerrar_paneles)
        cab.addWidget(self.btn_cerrar_teoremas)
        lay.addLayout(cab)
        self.txt_teoremas = QTextBrowser()
        self.txt_teoremas.setObjectName("SheetText")
        lay.addWidget(self.txt_teoremas, 1)
        sheet.hide()
        return sheet

    def _crear_atajos(self):
        for i in range(len(self.modulos)):
            QShortcut(QKeySequence(f"Ctrl+{i + 1}"), self, activated=lambda k=i: self.activar_modulo(k))
        QShortcut(QKeySequence("Ctrl+M"), self, activated=self.abrir_menu)
        QShortcut(QKeySequence("Ctrl+Return"), self, activated=self._accion_principal)
        QShortcut(QKeySequence("Ctrl+Enter"), self, activated=self._accion_principal)

    # ── Navegación ────────────────────────────────────────────────────

    def activar_modulo(self, idx):
        # Solo el módulo visible define el tamaño mínimo de la ventana
        for i, w in enumerate(self.modulos):
            politica = QSizePolicy.Policy.Preferred if i == idx else QSizePolicy.Policy.Ignored
            w.setSizePolicy(politica, politica)
        self.stack.setCurrentIndex(idx)
        self.lbl_titulo.setText(MODULOS[idx][1])
        for i, item in enumerate(self.items_menu):
            item.marcar(i == idx)
        for i, b in enumerate(self.items_riel):
            b.setChecked(i == idx)
        for i, (izq, der) in enumerate(zip(self.barras_izq, self.barras_der)):
            for w in (izq, der):
                if w:
                    w.setVisible(i == idx)
        self.txt_teoremas.setPlainText(TEOREMAS[idx])

    def _elegir_desde_menu(self, idx):
        self.activar_modulo(idx)
        self.cerrar_paneles()

    def _accion_principal(self):
        actual = self.stack.currentWidget()
        if hasattr(actual, "accion_principal"):
            actual.accion_principal()

    # ── Paneles deslizables ──────────────────────────────────────────

    def abrir_menu(self):
        self._abrir_panel(self.drawer, QPoint(-ANCHO_MENU, 0), QPoint(0, 0))

    def abrir_teoremas(self):
        ancho = self.central.width()
        self._abrir_panel(self.sheet, QPoint(ancho, 0), QPoint(ancho - ANCHO_TEOREMAS, 0))

    def _abrir_panel(self, panel, desde, hasta):
        if self._panel_abierto is panel:
            return
        self.cerrar_paneles(animar=False)
        self._panel_abierto = panel
        self.scrim.setGeometry(self.central.rect())
        self.scrim.show()
        self.scrim.raise_()
        panel.setFixedHeight(self.central.height())
        panel.move(desde)
        panel.show()
        panel.raise_()
        self._animar(panel, desde, hasta)

    def cerrar_paneles(self, animar=True):
        panel = self._panel_abierto
        if panel is None:
            return
        self._panel_abierto = None
        self.scrim.hide()
        destino = QPoint(-ANCHO_MENU, 0) if panel is self.drawer else QPoint(self.central.width(), 0)
        if animar:
            anim = self._animar(panel, panel.pos(), destino)
            anim.finished.connect(lambda p=panel: p.hide() if self._panel_abierto is not p else None)
        else:
            panel.hide()

    def _animar(self, panel, desde, hasta):
        anim = QPropertyAnimation(panel, b"pos", self)
        anim.setDuration(220)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(desde)
        anim.setEndValue(hasta)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        return anim

    def keyPressEvent(self, event):
        # Esc llega aquí solo si ningún editor lo usó (p. ej. para cancelar una celda)
        if event.key() == Qt.Key.Key_Escape and self._panel_abierto is not None:
            self.cerrar_paneles()
            return
        super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._panel_abierto is not None:
            self.scrim.setGeometry(self.central.rect())
            self._panel_abierto.setFixedHeight(self.central.height())
            if self._panel_abierto is self.sheet:
                self.sheet.move(self.central.width() - ANCHO_TEOREMAS, 0)

    # ── Tema ─────────────────────────────────────────────────────────

    def aplicar_tema(self, tema):
        self.tema = tema
        self.ajustes.setValue("tema", tema)
        paleta = TEMAS[tema]
        mono = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).family()
        sans = QApplication.font().family()
        flecha = os.path.join(tempfile.gettempdir(), f"calculadora_flecha_{tema}.png")
        icono("chevron", paleta["muted"], 12).pixmap(24, 24).save(flecha)
        self.setStyleSheet(construir_estilo(tema, mono=mono, sans=sans, flecha=flecha.replace("\\", "/")))
        self.selector_tema.seleccionar(0 if tema == "oscuro" else 1)
        for b in (self.btn_menu, self.btn_teoremas, self.btn_cerrar_menu, self.btn_cerrar_teoremas):
            b.aplicar_tema(paleta)
        for w in self.modulos:
            if hasattr(w, "aplicar_tema"):
                w.aplicar_tema(paleta)
        # Las líneas de la cuadrícula las pinta cada tabla, no la hoja de estilo
        for tabla in self.findChildren(TablaMatriz):
            tabla.aplicar_tema(paleta)
