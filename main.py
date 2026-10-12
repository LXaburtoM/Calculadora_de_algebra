"""
Punto de Entrada Principal de la Calculadora de Ãlgebra Lineal.
Tema: Proyecto Integrador de Ãlgebra Lineal (MTM0120).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas RamÃ­rez, Luis Xavier Aburto Mantilla.
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

