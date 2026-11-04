"""
Estilo visual de la Calculadora (PyQt6 QSS).
Tema: dos paletas sobrias (oscuro y claro) con un único acento rojo y la fuente del sistema.
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

# ── Paletas ──────────────────────────────────────────────────────────
# El modo claro sigue los grises de sistema de Apple: fondo agrupado gris,
# tarjetas blancas sin borde y separadores finos.
TEMAS = {
    "oscuro": {
        "bg": "#111214", "surface": "#1A1B1E", "fill": "#26272B", "fill_h": "#303136",
        "input": "#151619", "num": "#2B2C31", "sep": "#2A2B30", "thumb": "#3A3B40",
        "text": "#ECECEE", "muted": "#9A9CA4", "dim": "#6C6F77",
        "red": "#E0393E", "red_h": "#EA4F54", "red_soft": "rgba(224, 57, 62, 30)",
        "ok": "#4CC38A", "warn": "#E3A33B", "scrim": "rgba(0, 0, 0, 140)",
    },
    "claro": {
        "bg": "#F2F2F7", "surface": "#FFFFFF", "fill": "#EDEDF0", "fill_h": "#E3E3E8",
        "input": "#FFFFFF", "num": "#FFFFFF", "sep": "#E3E3E8", "thumb": "#FFFFFF",
        "text": "#1C1C1E", "muted": "#6E6E73", "dim": "#A1A1A6",
        "red": "#FF3B30", "red_h": "#E6352B", "red_soft": "rgba(255, 59, 48, 26)",
        "ok": "#34C759", "warn": "#FF9500", "scrim": "rgba(0, 0, 0, 46)",
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
    font-size: 11px; font-weight: 700;
}
QToolButton#RailItem:hover { background-color: {fill}; color: {text}; }
QToolButton#RailItem:checked { background-color: {red}; color: #FFFFFF; }

/* ── Barra superior ─────────────────────────────────────────── */
QFrame#TopBar { background-color: {surface}; border-bottom: 1px solid {sep}; }
QLabel#ModuleTitle { font-size: 15px; font-weight: 600; }

/* ── Botones ─────────────────────────────────────────────────── */
QPushButton, QToolButton {
    background-color: {fill}; color: {text};
    border: none; border-radius: 8px; padding: 7px 14px; font-weight: 600;
}
QPushButton:hover, QToolButton:hover { background-color: {fill_h}; }
QPushButton:disabled { color: {dim}; }

QToolButton#IconButton, QPushButton#IconButton {
    background: transparent; padding: 6px; border-radius: 8px;
}
QToolButton#IconButton:hover, QPushButton#IconButton:hover { background-color: {fill}; }
QToolButton#IconButton:disabled { color: {dim}; }

QPushButton#PrimaryButton, QToolButton#PrimaryButton {
    background-color: {red}; color: #FFFFFF;
}
QPushButton#PrimaryButton:hover, QToolButton#PrimaryButton:hover { background-color: {red_h}; }
QToolButton#PrimaryButton { padding: 7px 34px 7px 14px; }
QToolButton#PrimaryButton::menu-button {
    border: none; border-left: 1px solid rgba(0, 0, 0, 45);
    width: 26px; border-top-right-radius: 8px; border-bottom-right-radius: 8px;
}

/* Acciones sobre el último resultado */
QToolButton#ActionChip {
    background-color: {fill}; color: {text}; border-radius: 7px;
    padding: 4px 10px; font-size: 12px; font-weight: 500;
}
QToolButton#ActionChip:hover { background-color: {fill_h}; }

/* Control segmentado */
QFrame#Segmented { background-color: {fill}; border-radius: 9px; }
QPushButton#SegButton {
    background: transparent; border-radius: 7px; padding: 5px 12px; font-weight: 500;
}
QPushButton#SegButton:hover { background-color: {fill_h}; }
QPushButton#SegButton:checked { background-color: {thumb}; font-weight: 600; }

/* ── Menús ───────────────────────────────────────────────────── */
QMenu {
    background-color: {surface}; border: 1px solid {sep}; border-radius: 10px; padding: 5px;
}
QMenu::item { padding: 8px 28px 8px 12px; border-radius: 6px; }
QMenu::item:selected { background-color: {fill}; color: {text}; }
QMenu::separator { height: 1px; background: {sep}; margin: 4px 8px; }
QMenu::indicator { width: 0px; }
QMenu::item:checked { color: {red}; font-weight: 600; }

/* ── Tarjetas ────────────────────────────────────────────────── */
QFrame#Card { background-color: {surface}; border-radius: 12px; }
QLabel#CardTitle { font-weight: 600; }
QLabel#Muted { color: {muted}; }

QFrame#Summary { background-color: {fill}; border-radius: 10px; }
QLabel#SummaryTitle { font-weight: 600; }
QLabel#SummaryValue { font-family: "{mono}"; }
QLabel#Dot { border-radius: 4px; background-color: {ok}; }
QLabel#Dot[estado="error"] { background-color: {red}; }
QLabel#Dot[estado="aviso"] { background-color: {warn}; }

QTextBrowser#ModelInfo {
    background-color: {fill}; border: none; border-radius: 10px; padding: 6px 8px;
    font-family: "{sans}"; font-size: 13px;
}

/* ── Teclado matemático ─────────────────────────────────────── */
QPushButton#Key {
    background-color: {fill}; border-radius: 8px; padding: 0; font-size: 15px; font-weight: 500;
}
QPushButton#Key:hover { background-color: {fill_h}; }
QPushButton#Key:pressed { background-color: {sep}; }
QPushButton#Key[tipo="num"] { background-color: {num}; font-size: 17px; border: 1px solid {sep}; }
QPushButton#Key[tipo="num"]:hover { background-color: {fill_h}; }
QPushButton#Key[tipo="op"] { color: {muted}; font-size: 17px; }
QPushButton#Key[tipo="enter"] { background-color: {red}; color: #FFFFFF; font-size: 18px; }
QPushButton#Key[tipo="enter"]:hover { background-color: {red_h}; }

/* ── Menú deslizable y panel de teoremas ────────────────────── */
QWidget#Scrim { background-color: {scrim}; }
QFrame#Drawer { background-color: {surface}; border-right: 1px solid {sep}; }
QFrame#Sheet { background-color: {surface}; border-left: 1px solid {sep}; }
QLabel#Brand { font-size: 16px; font-weight: 700; }
QLabel#BrandSub { color: {dim}; font-size: 12px; }
QPushButton#NavItem {
    background: transparent; border-radius: 9px; padding: 0; text-align: left;
}
QPushButton#NavItem:hover { background-color: {fill}; }
QPushButton#NavItem:checked { background-color: {red_soft}; }
QLabel#NavIcon {
    background-color: {fill}; color: {muted}; border-radius: 8px;
    font-size: 11px; font-weight: 700;
}
QLabel#NavIcon[activo="true"] { background-color: {red}; color: #FFFFFF; }
QLabel#NavTitle { font-weight: 600; }
QLabel#NavSub { color: {muted}; font-size: 12px; }
QTextBrowser#SheetText {
    background: transparent; border: none; font-family: "{sans}"; font-size: 14px; padding: 0 6px;
}

/* ── Entradas ────────────────────────────────────────────────── */
QSpinBox, QComboBox, QLineEdit {
    background-color: {fill}; color: {text};
    border: 1px solid transparent; border-radius: 8px; padding: 6px 10px;
}
QSpinBox:focus, QComboBox:focus, QLineEdit:focus { border: 1px solid {red}; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow { image: url("{flecha}"); width: 10px; height: 10px; }
QComboBox QAbstractItemView {
    background-color: {surface}; border: 1px solid {sep};
    selection-background-color: {fill}; selection-color: {text}; outline: 0;
}
QFrame#Dims { background-color: {fill}; border-radius: 8px; }
QFrame#Dims QComboBox {
    background: transparent; border: none; border-radius: 6px;
    padding: 4px 2px 4px 8px; font-weight: 600; min-width: 18px;
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
    selection-background-color: {red_soft}; selection-color: {text};
    font-size: 16px;
}
QTableWidget::item:focus { border: 2px solid {red}; }
QTableWidget QLineEdit {
    border: none; border-radius: 0; padding: 0; background-color: {input}; font-size: 16px;
}
QHeaderView::section {
    background-color: {surface}; color: {dim}; font-weight: 500;
    border: none; border-bottom: 1px solid {sep}; border-right: 1px solid {sep}; padding: 6px;
}
/* El marco de la tabla ya cierra los bordes exteriores: sin líneas dobles */
QHeaderView::section:horizontal:last, QHeaderView::section:horizontal:only-one { border-right: none; }
QHeaderView::section:vertical:last, QHeaderView::section:vertical:only-one { border-bottom: none; }
QTableCornerButton::section { background-color: {surface}; border: none; }
QTableWidget QHeaderView { background-color: {surface}; }

/* ── Texto de resultados ────────────────────────────────────── */
QTextEdit, QPlainTextEdit {
    background-color: {surface}; color: {text}; border: none;
    font-family: "{mono}"; font-size: 13px; padding: 6px;
    selection-background-color: {red_soft}; selection-color: {text};
}

/* ── Módulos que aún usan la estructura anterior ────────────── */
QLabel#SectionHeader { font-size: 18px; font-weight: 700; margin-top: 10px; margin-bottom: 5px; }
QGroupBox {
    background-color: {surface}; border: none; border-radius: 12px;
    margin-top: 22px; padding: 12px 10px 8px 10px;
}
QGroupBox::title {
    subcontrol-origin: margin; subcontrol-position: top left;
    left: 6px; padding: 0 4px; color: {muted}; font-weight: 600;
}
QTabWidget::pane { border: none; background: {surface}; border-radius: 10px; top: -1px; }
QTabBar::tab {
    background: transparent; color: {muted}; padding: 8px 14px; margin-right: 2px;
    border: none; border-bottom: 2px solid transparent;
}
QTabBar::tab:selected { color: {text}; border-bottom: 2px solid {red}; font-weight: 600; }
QTabBar::tab:hover:!selected { color: {text}; }

QSplitter::handle { background: transparent; }
QScrollBar:vertical, QScrollBar:horizontal { background: transparent; border: none; width: 10px; height: 10px; }
QScrollBar::handle { background: {fill_h}; border-radius: 4px; min-height: 24px; min-width: 24px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: none; }
"""


def construir_estilo(tema="oscuro", mono="Menlo", sans="system-ui", flecha=""):
    """Devuelve la hoja de estilo QSS para el tema indicado."""
    valores = dict(TEMAS[tema], mono=mono, sans=sans, flecha=flecha)
    qss = _PLANTILLA
    for clave, valor in valores.items():
        qss = qss.replace("{" + clave + "}", valor)
    return qss


# Compatibilidad con código que importe la hoja directamente
STYLE_SHEET = construir_estilo("oscuro")
