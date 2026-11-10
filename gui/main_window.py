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
    QLabel, QStackedWidget, QFrame, QApplication, QTextBrowser, QSizePolicy, QToolButton,
    QGraphicsOpacityEffect, QMenu, QColorDialog
)
from PyQt6.QtCore import Qt, QEasingCurve, QPoint, QSettings, QSize
from PyQt6.QtGui import QKeySequence, QShortcut, QFontDatabase, QActionGroup, QColor
from gui.modules.ecuaciones_widget import EcuacionesWidget
from gui.modules.transformaciones_widget import TransformacionesWidget
from gui.modules.operaciones_widget import OperacionesWidget
from gui.modules.determinantes_widget import DeterminantesWidget
from gui.modules.lu_widget import LUWidget, TEOREMAS_LU
from gui.modules.verificador_widget import VerificadorWidget
from gui.modules.metodos_numericos_widget import MetodosNumericosWidget
from gui.styles import construir_estilo, colores_enfasis, TEMAS, ENFASIS
from gui.componentes import BotonIcono, icono, icono_estados
from gui.entrada import TablaMatriz
from gui import sonido
from gui.animaciones import (
    animar as animar_propiedad, curva_resorte, curva_entrada_salida, RAPIDA, NORMAL, PANEL
)

ANCHO_MENU = 300
ANCHO_RIEL = 60
ANCHO_TEOREMAS = 400

# (icono, título, subtítulo) de cada módulo, en el orden del QStackedWidget
MODULOS = [
    ("mod_sistemas", "Sistemas de Ecuaciones", "Gauss y Gauss-Jordan"),
    ("mod_transformaciones", "Transformaciones Lineales", "T(x) = Ax"),
    ("mod_operaciones", "Operaciones Matriciales", "Combinación lineal"),
    ("mod_determinantes", "Determinantes", "Sarrus, cofactores, Cramer"),
    ("mod_lu", "Factorización LU", "Solución de Ax = b"),
    ("mod_verificador", "Verificador", "16 propiedades"),
    ("mod_metodos_numericos", "Métodos Numéricos", "Bisección, Gráfica, Errores"),
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
    (
        "Módulo 7: Métodos Numéricos\n\n"
        "1. Teorema de Bolzano (Existencia de Raíces):\n"
        "   Si f(x) es continua en [a, b] y f(a)·f(b) < 0, existe al menos un r ∈ (a, b) tal que f(r) = 0.\n\n"
        "2. Método de Bisección:\n"
        "   • Punto medio: xr = (a + b) / 2.\n"
        "   • Cota del error por semiancho: Eb = (b - a) / 2.\n"
        "   • Cota en el paso n: |r - xr,n| ≤ (b - a) / 2ⁿ.\n"
        "   • Número teórico de iteraciones: n = ⌈log₂((b - a) / E)⌉.\n"
        "   • Error relativo aproximado: εa = |(xr,k - xr,k-1) / xr,k| (si xr,k ≠ 0).\n\n"
        "3. Representación en Punto Flotante (IEEE 754):\n"
        "   • 0.1 + 0.2 ≠ 0.3 por el redondeo de fracciones binarias periódicas.\n"
        "   • Épsilon de máquina (eps ≈ 2.22e-16): distancia entre 1.0 y el siguiente representable.\n\n"
        "4. Propagación de Errores:\n"
        "   • Aproximación lineal por derivada: Δy_aprox = f'(x) · Δx.\n"
        "   • Cambio real: Δy_real = f(x + Δx) - f(x)."
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
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(12)
        self.nombre_icono = ico
        self.lbl_ico = QLabel()
        self.lbl_ico.setObjectName("NavIcon")
        self.lbl_ico.setFixedSize(34, 34)
        self.lbl_ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        textos = QVBoxLayout()
        textos.setSpacing(0)
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
        self._pintar_icono()

    def aplicar_tema(self, paleta):
        self.paleta = paleta
        self._pintar_icono()

    def _pintar_icono(self):
        paleta = getattr(self, "paleta", None)
        if paleta:
            color = paleta["surface"] if self.isChecked() else paleta["muted"]
            self.lbl_ico.setPixmap(icono(self.nombre_icono, color, 18).pixmap(18, 18))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Álgebra Lineal - UAM")
        self.resize(1280, 820)
        self.ajustes = QSettings("UAM", "CalculadoraAlgebraLineal")
        # "sistema" (predeterminado) sigue el modo claro/oscuro del sistema operativo
        preferencia = self.ajustes.value("tema", "sistema")
        self.preferencia_tema = preferencia if preferencia in ("sistema", *TEMAS) else "sistema"
        self.tema = self._tema_efectivo()
        sonido.activar(self.ajustes.value("sonido", "true") == "true")
        # Color de los botones principales: vacío = rojo del tema
        self.enfasis = self.ajustes.value("enfasis", "") or ""
        self._panel_abierto = None
        self.init_ui()
        self._crear_atajos()
        self.aplicar_tema(self.tema)
        # Si el usuario cambia el modo del sistema con la app abierta, se actualiza sola
        QApplication.styleHints().colorSchemeChanged.connect(self._al_cambiar_esquema_sistema)
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
        self.metodos_numericos_widget = MetodosNumericosWidget()
        self.modulos = [
            self.ecuaciones_widget, self.transformaciones_widget, self.operaciones_widget,
            self.determinantes_widget, self.lu_widget, self.verificador_widget,
            self.metodos_numericos_widget,
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
        self.opacidad_scrim = QGraphicsOpacityEffect(self.scrim)
        self.opacidad_scrim.setOpacity(0.0)
        self.scrim.setGraphicsEffect(self.opacidad_scrim)
        self.drawer = self._crear_menu()
        self.sheet = self._crear_panel_teoremas()

    def _crear_riel(self):
        """Columna fija de iconos: cambiar de módulo cuesta un solo clic."""
        riel = QFrame()
        riel.setObjectName("Rail")
        riel.setFixedWidth(ANCHO_RIEL)
        lay = QVBoxLayout(riel)
        lay.setContentsMargins(8, 12, 8, 12)
        lay.setSpacing(8)

        self.btn_menu = BotonIcono("menu", "Menú (Ctrl+M)")
        self.btn_menu.clicked.connect(self.abrir_menu)
        lay.addWidget(self.btn_menu, 0, Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(6)

        self.items_riel = []
        for i, (ico, titulo, sub) in enumerate(MODULOS):
            b = QToolButton()
            b.setObjectName("RailItem")
            b.setProperty("nombre_icono", ico)
            b.setIconSize(QSize(22, 22))
            b.setCheckable(True)
            b.setToolTip(f"{titulo}  ·  {sub}  (Ctrl+{i + 1})")
            b.setAccessibleName(titulo)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedSize(ANCHO_RIEL - 16, ANCHO_RIEL - 16)
            b.clicked.connect(lambda _, k=i: self.activar_modulo(k))
            lay.addWidget(b)
            self.items_riel.append(b)
        lay.addStretch()

        self.btn_ajustes = BotonIcono("ajustes", "Ajustes: tema, color de énfasis y sonido")
        self.btn_ajustes.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_ajustes.setMenu(self._crear_menu_ajustes())
        lay.addWidget(self.btn_ajustes, 0, Qt.AlignmentFlag.AlignHCenter)
        return riel

    def _crear_menu_ajustes(self):
        """Menú del engranaje: tema, color de énfasis y sonido, cada uno con opciones excluyentes."""
        menu = QMenu(self)
        self.acciones_tema = {}
        self.acciones_enfasis = {}
        self.acciones_sonido = {}
        for titulo, opciones, destino, al_elegir in (
            ("Tema", (("sistema", "Igual que el sistema"), ("oscuro", "Oscuro"), ("claro", "Claro")),
             self.acciones_tema, self.elegir_tema),
            ("Color de énfasis", (("rojo", "Rojo"), ("naranja", "Naranja"), ("personalizado", "Elegir color…")),
             self.acciones_enfasis, self.elegir_enfasis),
            ("Sonido", ((True, "Clic suave"), (False, "Silencio")), self.acciones_sonido, self._cambiar_sonido),
        ):
            # Encabezado visible en todos los sistemas (addSection no muestra el texto en macOS)
            if menu.actions():
                menu.addSeparator()
            encabezado = menu.addAction(titulo)
            encabezado.setEnabled(False)
            grupo = QActionGroup(menu)
            for clave, texto in opciones:
                accion = menu.addAction(texto)
                accion.setCheckable(True)
                accion.triggered.connect(lambda _, k=clave, f=al_elegir: f(k))
                grupo.addAction(accion)
                destino[clave] = accion
        self.acciones_sonido[sonido.esta_activo()].setChecked(True)
        return menu

    def _clave_enfasis(self):
        if not self.enfasis:
            return "rojo"
        for clave, color in ENFASIS.items():
            if color and color.lower() == self.enfasis.lower():
                return clave
        return "personalizado"

    def elegir_enfasis(self, clave, color=None):
        """Rojo (predeterminado), naranja o un color elegido con el selector del sistema."""
        if clave == "personalizado" and color is None:
            inicial = QColor(self.enfasis or TEMAS[self.tema]["red"])
            elegido = QColorDialog.getColor(inicial, self, "Color de énfasis")
            if not elegido.isValid():
                # Cancelado: se mantiene la marca en la opción anterior
                self.acciones_enfasis[self._clave_enfasis()].setChecked(True)
                return
            color = elegido.name()
        self.enfasis = color if clave == "personalizado" else (ENFASIS[clave] or "")
        self.ajustes.setValue("enfasis", self.enfasis)
        self.aplicar_tema(self.tema)

    def _crear_barra_superior(self):
        barra = QFrame()
        barra.setObjectName("TopBar")
        barra.setFixedHeight(56)
        lay = QHBoxLayout(barra)
        lay.setContentsMargins(16, 0, 12, 0)
        lay.setSpacing(8)

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
        cab.setContentsMargins(8, 0, 0, 12)
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

        # Ajustes también desde el menú: comparte el mismo menú que el engranaje del riel
        self.btn_ajustes_menu = QToolButton()
        self.btn_ajustes_menu.setObjectName("DrawerSettings")
        self.btn_ajustes_menu.setText("Ajustes")
        self.btn_ajustes_menu.setToolTip("Tema, color de énfasis y sonido")
        self.btn_ajustes_menu.setIconSize(QSize(18, 18))
        self.btn_ajustes_menu.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btn_ajustes_menu.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_ajustes_menu.setMenu(self.btn_ajustes.menu())
        self.btn_ajustes_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ajustes_menu.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_ajustes_menu.setMinimumHeight(48)
        lay.addWidget(self.btn_ajustes_menu)
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

    def _cambiar_sonido(self, activo):
        sonido.activar(activo)
        self.ajustes.setValue("sonido", "true" if activo else "false")
        sonido.reproducir()

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
        animar_propiedad(self.opacidad_scrim, b"opacity", self.opacidad_scrim.opacity(), 1.0, NORMAL, padre=self)
        panel.setFixedHeight(self.central.height())
        panel.move(desde)
        panel.show()
        panel.raise_()
        # Entrada con un leve rebote de resorte; la salida es más corta y sin rebote
        animar_propiedad(panel, b"pos", desde, hasta, PANEL, curva_resorte(), padre=self)

    def cerrar_paneles(self, animar=True):
        panel = self._panel_abierto
        if panel is None:
            return
        self._panel_abierto = None
        destino = QPoint(-ANCHO_MENU, 0) if panel is self.drawer else QPoint(self.central.width(), 0)
        if not animar:
            self.scrim.hide()
            self.opacidad_scrim.setOpacity(0.0)
            panel.hide()
            return
        fondo = animar_propiedad(self.opacidad_scrim, b"opacity", self.opacidad_scrim.opacity(), 0.0,
                                 RAPIDA + 40, curva_entrada_salida(), padre=self)
        fondo.finished.connect(lambda: self.scrim.hide() if self._panel_abierto is None else None)
        anim = animar_propiedad(panel, b"pos", panel.pos(), destino, NORMAL,
                                QEasingCurve(QEasingCurve.Type.InCubic), padre=self)
        anim.finished.connect(lambda p=panel: p.hide() if self._panel_abierto is not p else None)

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

    def _tema_efectivo(self):
        if self.preferencia_tema != "sistema":
            return self.preferencia_tema
        # Windows, macOS y los escritorios Linux modernos informan su esquema;
        # si el sistema no lo informa se usa el claro
        esquema = QApplication.styleHints().colorScheme()
        return "oscuro" if esquema == Qt.ColorScheme.Dark else "claro"

    def elegir_tema(self, preferencia):
        """Opción del menú de ajustes: 'sistema', 'oscuro' o 'claro'. Se recuerda entre sesiones."""
        self.preferencia_tema = preferencia
        self.ajustes.setValue("tema", preferencia)
        self.aplicar_tema(self._tema_efectivo())

    def _al_cambiar_esquema_sistema(self, _esquema):
        if self.preferencia_tema == "sistema":
            self.aplicar_tema(self._tema_efectivo())

    def aplicar_tema(self, tema):
        """Aplica la paleta 'oscuro' o 'claro' a toda la ventana."""
        self.tema = tema
        paleta = dict(TEMAS[tema], on_red="#FFFFFF")
        if self.enfasis:
            paleta.update(colores_enfasis(self.enfasis))
        mono = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).family()
        sans = QApplication.font().family()
        # Las imágenes que usa la hoja de estilo se dibujan en el color del tema
        rutas = {}
        for nombre, color in (("chevron", paleta["muted"]), ("check", paleta["text"])):
            ruta = os.path.join(tempfile.gettempdir(), f"calculadora_{nombre}_{tema}.png")
            icono(nombre, color, 12).pixmap(24, 24).save(ruta)
            rutas[nombre] = ruta.replace("\\", "/")
        self.setStyleSheet(construir_estilo(tema, mono=mono, sans=sans, flecha=rutas["chevron"],
                                            check=rutas["check"], enfasis=self.enfasis or None))
        self.acciones_tema[self.preferencia_tema].setChecked(True)
        self.acciones_enfasis[self._clave_enfasis()].setChecked(True)
        for b in (self.btn_menu, self.btn_ajustes, self.btn_teoremas, self.btn_cerrar_menu, self.btn_cerrar_teoremas):
            b.aplicar_tema(paleta)
        self.btn_ajustes_menu.setIcon(icono("ajustes", paleta["muted"], 18))
        for b in self.items_riel:
            b.setIcon(icono_estados(b.property("nombre_icono"), paleta["muted"], paleta["text"], 22))
        for item in self.items_menu:
            item.aplicar_tema(paleta)
        for w in self.modulos:
            if hasattr(w, "aplicar_tema"):
                w.aplicar_tema(paleta)
        # Las líneas de la cuadrícula las pinta cada tabla, no la hoja de estilo
        for tabla in self.findChildren(TablaMatriz):
            tabla.aplicar_tema(paleta)
