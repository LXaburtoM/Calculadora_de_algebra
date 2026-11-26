"""
Tipografía de la interfaz.
Tema: carga la fuente incluida en gui/fuentes/ para que la app se vea igual en Windows, macOS y Linux.
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

import os
import sys

from PyQt6.QtGui import QFont, QFontDatabase

# Familia preferida; si sus archivos no están en gui/fuentes/ se usa la fuente del sistema
FAMILIA = "Inter"
TAMANO_PUNTOS = 13


def _carpeta_fuentes():
    # En el .exe de PyInstaller los datos se extraen en sys._MEIPASS
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, "gui", "fuentes")


def aplicar_fuente(app):
    """Registra las fuentes incluidas y la usa en toda la app. Devuelve la familia aplicada."""
    carpeta = _carpeta_fuentes()
    familias = set()
    if os.path.isdir(carpeta):
        for nombre in sorted(os.listdir(carpeta)):
            if nombre.lower().endswith((".ttf", ".otf", ".ttc")):
                indice = QFontDatabase.addApplicationFont(os.path.join(carpeta, nombre))
                if indice != -1:
                    familias.update(QFontDatabase.applicationFontFamilies(indice))
    if FAMILIA not in familias:
        return app.font().family()
    fuente = QFont(FAMILIA, TAMANO_PUNTOS)
    fuente.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    app.setFont(fuente)
    return FAMILIA
