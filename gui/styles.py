"""
Estilos visuales modernos para la interfaz PyQt6 (Tema Oscuro Elegante).
"""

STYLE_SHEET = """
QMainWindow {
    background-color: #121824;
}

QWidget {
    color: #E2E8F0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

QFrame#LeftPanel {
    background-color: #1E293B;
    border-right: 1px solid #334155;
}

QLabel#AppTitle {
    color: #38BDF8;
    font-size: 20px;
    font-weight: bold;
    padding: 10px 0;
}

QLabel#SectionHeader {
    color: #F8FAFC;
    font-size: 16px;
    font-weight: 600;
    margin-top: 10px;
}

QPushButton {
    background-color: #0F172A;
    color: #E2E8F0;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #1E293B;
    border-color: #38BDF8;
}

QPushButton#PrimaryButton {
    background-color: #0284C7;
    color: #FFFFFF;
    border: none;
    font-weight: bold;
}

QPushButton#PrimaryButton:hover {
    background-color: #0369A1;
}

QTableWidget {
    background-color: #1E293B;
    gridline-color: #334155;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #F8FAFC;
}

QHeaderView::section {
    background-color: #0F172A;
    color: #38BDF8;
    font-weight: bold;
    border: 1px solid #334155;
    padding: 4px;
}

QSpinBox, QComboBox, QLineEdit {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 5px;
}

QSpinBox:focus, QLineEdit:focus {
    border-color: #38BDF8;
}

QTextEdit, QPlainTextEdit {
    background-color: #0F172A;
    color: #E2E8F0;
    border: 1px solid #334155;
    border-radius: 6px;
    font-family: 'Consolas', 'Courier New', monospace;
}

QGroupBox {
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 14px;
    font-weight: bold;
    color: #38BDF8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
}
"""
