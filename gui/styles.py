"""
Estilo visual ultra moderno (Dark Theme) para PyQt6.
"""

STYLE_SHEET = """
QMainWindow {
    background-color: #0E1117;
}

QWidget {
    color: #C9D1D9;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    font-size: 14px;
}

QFrame#LeftPanel {
    background-color: #161B22;
    border-right: 1px solid #30363D;
}

QLabel#AppTitle {
    color: #58A6FF;
    font-size: 22px;
    font-weight: 800;
    padding: 15px 0;
}

QLabel#SectionHeader {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 5px;
}

QPushButton {
    background-color: #21262D;
    color: #C9D1D9;
    border: 1px solid #363B42;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #30363D;
    border-color: #8B949E;
}

QPushButton:pressed {
    background-color: #282E33;
}

QPushButton#PrimaryButton {
    background-color: #238636;
    color: #FFFFFF;
    border: 1px solid #2EA043;
    font-weight: 700;
}

QPushButton#PrimaryButton:hover {
    background-color: #2EA043;
    border-color: #3FB950;
}

QPushButton#PrimaryButton:pressed {
    background-color: #238636;
}

/* El botón azul claro activo del menú lateral */
QPushButton#MenuButtonActive {
    background-color: #1F6FEB;
    color: #FFFFFF;
    border: none;
}

QTableWidget {
    background-color: #0D1117;
    gridline-color: #30363D;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #C9D1D9;
    alternate-background-color: #161B22;
    selection-background-color: #1F6FEB;
    selection-color: #FFFFFF;
}

QHeaderView::section {
    background-color: #161B22;
    color: #8B949E;
    font-weight: 700;
    border: none;
    border-right: 1px solid #30363D;
    border-bottom: 1px solid #30363D;
    padding: 6px;
}

QSpinBox, QComboBox, QLineEdit {
    background-color: #0D1117;
    color: #C9D1D9;
    border: 1px solid #30363D;
    border-radius: 6px;
    padding: 6px 10px;
}

QSpinBox:focus, QComboBox:focus, QLineEdit:focus {
    border: 1px solid #58A6FF;
    background-color: #161B22;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QTextEdit, QPlainTextEdit {
    background-color: #0D1117;
    color: #C9D1D9;
    border: 1px solid #30363D;
    border-radius: 6px;
    font-family: 'Consolas', 'Fira Code', 'Courier New', monospace;
    font-size: 14px;
    padding: 10px;
    line-height: 1.5;
}

QGroupBox {
    border: 1px solid #30363D;
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 15px;
    padding-bottom: 5px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    left: 10px;
    color: #58A6FF;
    font-weight: 700;
}

QTabWidget::pane {
    border: 1px solid #30363D;
    border-radius: 6px;
    background: #0E1117;
    top: -1px;
}

QTabBar::tab {
    background: #161B22;
    border: 1px solid #30363D;
    border-bottom: none;
    color: #8B949E;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background: #0E1117;
    color: #58A6FF;
    border-top: 2px solid #58A6FF;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background: #21262D;
    color: #C9D1D9;
}

"""
