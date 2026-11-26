"""
Estilo visual de la Calculadora (PyQt6 QSS).
Tema: dos paletas sobrias (oscuro y claro). El rojo se reserva a las acciones principales;
      la estructura usa negros profundos, grises suaves y blancos puros.
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from PyQt6.QtGui import QColor

# Escala tipográfica: 12 (secundario) · 13 (texto) · 15 (títulos y celdas) · 17 (cifras del teclado).
# Espaciado y radios en múltiplos de 4.

# ── Paletas ──────────────────────────────────────────────────────────
# El modo claro sigue los grises de sistema de Apple: fondo agrupado gris,
# tarjetas blancas sin borde y separadores finos.
# "fill_h" y "press" están muy cerca de "fill" a propósito: al pasar el cursor o presionar,
# el cambio es un leve cambio de tono, no un salto de color.
TEMAS = {
    "oscuro": {
        "bg": "#0B0B0C", "surface": "#141416", "fill": "#1E1E21", "fill_h": "#252528",
        "press": "#2C2C30", "input": "#101012", "num": "#222225", "sep": "#232327",
        "thumb": "#2E2E33", "text": "#F2F2F4", "muted": "#9B9BA1", "dim": "#64646A",
        "focus": "#8E8E93", "select": "rgba(255, 255, 255, 14)",
        "red": "#E0393E", "red_h": "#E64A4F", "red_p": "#CC3338",
        "ok": "#5BB98C", "warn": "#D9A54A", "scrim": "rgba(0, 0, 0, 150)",
    },
    "claro": {
        "bg": "#F5F5F7", "surface": "#FFFFFF", "fill": "#F0F0F2", "fill_h": "#EAEAED",
        "press": "#E2E2E6", "input": "#FFFFFF", "num": "#FFFFFF", "sep": "#E5E5EA",
        "thumb": "#FFFFFF", "text": "#1D1D1F", "muted": "#6E6E73", "dim": "#AEAEB2",
        "focus": "#1D1D1F", "select": "rgba(0, 0, 0, 10)",
        "red": "#FF3B30", "red_h": "#F2382E", "red_p": "#DE3329",
        "ok": "#34A853", "warn": "#E8930C", "scrim": "rgba(0, 0, 0, 40)",
    },
}

_PLANTILLA = """
QMainWindow, QWidget#Central { background-color: {bg}; }

QWidget { color: {text}; }

QToolTip {
    background-color: {surface}; color: {text};
    border: 1px solid {sep}; border-radius: 6px; padding: 4px 8px;
}

/* ── Riel de módulos ─────────────────────────────────────────── */
QFrame#Rail { background-color: {surface}; border-right: 1px solid {sep}; }
QToolButton#RailItem {
    background: transparent; color: {muted}; border-radius: 10px; padding: 0;
    font-size: 12px; font-weight: 700;
}
QToolButton#RailItem:hover { background-color: {fill}; color: {text}; }
QToolButton#RailItem:checked { background-color: {press}; color: {text}; }

/* ── Barra superior ─────────────────────────────────────────── */
QFrame#TopBar { background-color: {surface}; border-bottom: 1px solid {sep}; }
QLabel#ModuleTitle { font-size: 15px; font-weight: 600; }

/* ── Botones ─────────────────────────────────────────────────── */
QPushButton, QToolButton {
    background-color: {fill}; color: {text};
    border: none; border-radius: 8px; padding: 8px 16px; font-weight: 600;
}
QPushButton:hover, QToolButton:hover { background-color: {fill_h}; }
QPushButton:pressed, QToolButton:pressed { background-color: {press}; }
QPushButton:disabled { color: {dim}; }

QToolButton#IconButton, QPushButton#IconButton {
    background: transparent; padding: 8px; border-radius: 8px;
}
QToolButton#IconButton:hover, QPushButton#IconButton:hover { background-color: {fill}; }
QToolButton#IconButton:disabled { color: {dim}; }
QToolButton#IconButton::menu-indicator { image: none; width: 0; }

QPushButton#PrimaryButton, QToolButton#PrimaryButton {
    background-color: {red}; color: {on_red};
}
QPushButton#PrimaryButton:hover, QToolButton#PrimaryButton:hover { background-color: {red_h}; }
QPushButton#PrimaryButton:pressed { background-color: {red_p}; }
QPushButton#PrimaryButton:disabled { background-color: {fill}; color: {dim}; }
QToolButton#PrimaryButton { padding: 8px 36px 8px 16px; }
QToolButton#PrimaryButton::menu-button {
    border: none; border-left: 1px solid rgba(0, 0, 0, 45);
    width: 26px; border-top-right-radius: 8px; border-bottom-right-radius: 8px;
}

/* Acciones sobre el último resultado */
QToolButton#ActionChip {
    background-color: {fill}; color: {text}; border-radius: 7px;
    padding: 4px 12px; font-size: 12px; font-weight: 500;
}
QToolButton#ActionChip:hover { background-color: {fill_h}; }

/* Control segmentado */
QFrame#Segmented { background-color: {fill}; border-radius: 9px; }
QPushButton#SegButton {
    background: transparent; color: {muted}; border-radius: 7px; padding: 4px 12px; font-weight: 500;
}
QPushButton#SegButton:hover { color: {text}; }
QPushButton#SegButton:checked { background: transparent; color: {text}; font-weight: 600; }
QFrame#SegThumb { background-color: {thumb}; border-radius: 7px; }

/* ── Menús ───────────────────────────────────────────────────── */
QMenu {
    background-color: {surface}; border: 1px solid {sep}; border-radius: 10px; padding: 4px;
}
QMenu::item { padding: 8px 28px 8px 32px; border-radius: 6px; }
QMenu::item:selected { background-color: {fill}; color: {text}; }
QMenu::separator { height: 1px; background: {sep}; margin: 4px 8px; }
QMenu::indicator { width: 14px; height: 14px; left: 8px; }
QMenu::indicator:checked { image: url("{check}"); }
QMenu::item:checked { font-weight: 600; }
QMenu::item:disabled { color: {dim}; font-size: 12px; padding: 8px 28px 4px 12px; }

/* ── Tarjetas ────────────────────────────────────────────────── */
QFrame#Card { background-color: {surface}; border-radius: 12px; }
QLabel#CardTitle { font-weight: 600; }
QLabel#Muted { color: {muted}; }
QLabel#EmptyState { color: {dim}; font-size: 13px; }

QFrame#Summary { background-color: {fill}; border-radius: 10px; }
QLabel#SummaryTitle { font-weight: 600; }
QLabel#SummaryValue { font-family: "{mono}"; }
QLabel#Dot { border-radius: 4px; background-color: {ok}; }
QLabel#Dot[estado="error"] { background-color: {red}; }
QLabel#Dot[estado="aviso"] { background-color: {warn}; }

QTextBrowser#ModelInfo {
    background-color: {fill}; border: none; border-radius: 10px; padding: 8px;
    font-family: "{sans}"; font-size: 13px;
}

/* ── Teclado matemático ─────────────────────────────────────── */
QPushButton#Key {
    background-color: {fill}; border-radius: 8px; padding: 0; font-size: 15px; font-weight: 500;
}
QPushButton#Key:hover { background-color: {fill_h}; }
QPushButton#Key:pressed { background-color: {press}; }
QPushButton#Key[tipo="num"] { background-color: {num}; font-size: 17px; border: 1px solid {sep}; }
QPushButton#Key[tipo="num"]:hover { background-color: {fill_h}; }
QPushButton#Key[tipo="op"] { color: {muted}; font-size: 17px; }
QPushButton#Key[tipo="enter"] { background-color: {red}; color: {on_red}; font-size: 17px; }
QPushButton#Key[tipo="enter"]:hover { background-color: {red_h}; }
QPushButton#Key[tipo="enter"]:pressed { background-color: {red_p}; }

/* ── Menú deslizable y panel de teoremas ────────────────────── */
QWidget#Scrim { background-color: {scrim}; }
QFrame#Drawer { background-color: {surface}; border-right: 1px solid {sep}; }
QFrame#Sheet { background-color: {surface}; border-left: 1px solid {sep}; }
QLabel#Brand { font-size: 15px; font-weight: 700; }
QLabel#BrandSub { color: {dim}; font-size: 12px; }
QPushButton#NavItem {
    background: transparent; border-radius: 9px; padding: 0; text-align: left;
}
QPushButton#NavItem:hover { background-color: {fill}; }
QPushButton#NavItem:checked { background-color: {fill}; }
QLabel#NavIcon {
    background-color: {fill}; color: {muted}; border-radius: 8px;
    font-size: 12px; font-weight: 700;
}
QLabel#NavIcon[activo="true"] { background-color: {text}; color: {surface}; }
QLabel#NavTitle { font-weight: 600; }
QToolButton#DrawerSettings {
    background: transparent; border-radius: 8px; padding: 8px 16px; text-align: left;
    font-weight: 600; color: {text};
}
QToolButton#DrawerSettings:hover { background-color: {fill}; }
QToolButton#DrawerSettings::menu-indicator { image: none; width: 0; }
QLabel#NavSub { color: {muted}; font-size: 12px; }
QTextBrowser#SheetText {
    background: transparent; border: none; font-family: "{sans}"; font-size: 13px; padding: 0 8px;
}

/* ── Entradas ────────────────────────────────────────────────── */
QSpinBox, QComboBox, QLineEdit {
    background-color: {fill}; color: {text};
    border: 1px solid transparent; border-radius: 8px; padding: 8px 12px;
}
QSpinBox:focus, QComboBox:focus, QLineEdit:focus { border: 1px solid {focus}; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow { image: url("{flecha}"); width: 10px; height: 10px; }
QComboBox QAbstractItemView {
    background-color: {surface}; border: 1px solid {sep};
    selection-background-color: {fill}; selection-color: {text}; outline: 0;
}
QFrame#Dims { background-color: {fill}; border-radius: 8px; }
QFrame#Dims QComboBox {
    background: transparent; border: none; border-radius: 6px;
    padding: 4px 4px 4px 8px; font-weight: 600; min-width: 18px;
}
QFrame#Dims QComboBox:hover { background-color: {fill_h}; }
QFrame#Dims QComboBox::drop-down { width: 0; }
QFrame#Dims QComboBox::down-arrow { image: none; width: 0; }
QLabel#DimsX { color: {dim}; }
QCheckBox { spacing: 8px; }

/* ── Tablas ──────────────────────────────────────────────────── */
QTableWidget, QTableView {
    background-color: {input}; alternate-background-color: {input};
    gridline-color: {sep}; border: 1px solid {sep}; border-radius: 8px;
    selection-background-color: {select}; selection-color: {text};
    font-size: 15px;
}
QTableWidget::item:focus { border: 1.5px solid {focus}; border-radius: 4px; }
QTableWidget QLineEdit {
    border: none; border-radius: 0; padding: 0; background-color: {input}; font-size: 15px;
    qproperty-alignment: AlignCenter;
}
QHeaderView::section {
    background-color: {surface}; color: {dim}; font-weight: 500;
    border: none; border-bottom: 1px solid {sep}; border-right: 1px solid {sep}; padding: 8px;
}
/* El marco de la tabla ya cierra los bordes exteriores: sin líneas dobles */
QHeaderView::section:horizontal:last, QHeaderView::section:horizontal:only-one { border-right: none; }
QHeaderView::section:vertical:last, QHeaderView::section:vertical:only-one { border-bottom: none; }
QTableCornerButton::section { background-color: {surface}; border: none; }
QTableWidget QHeaderView { background-color: {surface}; }

/* ── Texto de resultados ────────────────────────────────────── */
QTextEdit, QPlainTextEdit {
    background-color: {surface}; color: {text}; border: none;
    font-family: "{mono}"; font-size: 13px; padding: 8px;
    selection-background-color: {select}; selection-color: {text};
}

QSplitter::handle { background: transparent; }
QScrollBar:vertical, QScrollBar:horizontal { background: transparent; border: none; width: 10px; height: 10px; }
QScrollBar::handle { background: {fill_h}; border-radius: 4px; min-height: 24px; min-width: 24px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: none; }
"""


# Colores de énfasis predefinidos (el rojo usa el tono propio de cada tema)
ENFASIS = {
    "rojo": None,
    "naranja": "#FF9500",   # naranja de la calculadora de iOS
}


def colores_enfasis(base):
    """Variantes del color de énfasis: normal, al pasar el cursor, presionado y texto encima."""
    color = QColor(base)
    # Texto oscuro sobre colores muy claros para mantener el contraste
    luminancia = 0.2126 * color.redF() + 0.7152 * color.greenF() + 0.0722 * color.blueF()
    return {
        "red": color.name(),
        "red_h": color.lighter(108).name(),
        "red_p": color.darker(112).name(),
        "on_red": "#1D1D1F" if luminancia > 0.72 else "#FFFFFF",
    }


def construir_estilo(tema="oscuro", mono="Menlo", sans="system-ui", flecha="", check="", enfasis=None):
    """Devuelve la hoja de estilo QSS para el tema indicado.

    `enfasis` es un color hex para botones principales; None usa el rojo del tema.
    """
    valores = dict(TEMAS[tema], mono=mono, sans=sans, flecha=flecha, check=check, on_red="#FFFFFF")
    if enfasis:
        valores.update(colores_enfasis(enfasis))
    qss = _PLANTILLA
    for clave, valor in valores.items():
        qss = qss.replace("{" + clave + "}", valor)
    return qss


# Compatibilidad con código que importe la hoja directamente
STYLE_SHEET = construir_estilo("oscuro")
