"""
Animaciones de la interfaz.
Tema: transiciones cortas con curvas naturales (sin movimiento lineal) para paneles y avisos.
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QAbstractAnimation
from PyQt6.QtWidgets import QGraphicsOpacityEffect

# Duraciones en ms: rápidas para que la app se sienta inmediata
RAPIDA = 120
NORMAL = 180
PANEL = 280


def curva_resorte():
    """Salida con un leve rebote, como un resorte amortiguado."""
    curva = QEasingCurve(QEasingCurve.Type.OutBack)
    curva.setOvershoot(0.7)
    return curva


def curva_suave():
    return QEasingCurve(QEasingCurve.Type.OutCubic)


def curva_entrada_salida():
    return QEasingCurve(QEasingCurve.Type.InOutCubic)


def animar(objeto, propiedad, desde, hasta, duracion=NORMAL, curva=None, padre=None):
    """Crea y arranca una QPropertyAnimation que se libera sola al terminar."""
    anim = QPropertyAnimation(objeto, propiedad, padre or objeto)
    anim.setDuration(duracion)
    anim.setEasingCurve(curva or curva_suave())
    anim.setStartValue(desde)
    anim.setEndValue(hasta)
    anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    return anim


def aparecer(widget, duracion=NORMAL):
    """Fundido de entrada para elementos pequeños que aparecen (no para páginas enteras).

    El efecto se reutiliza y queda en opacidad 1: quitarlo al final provoca un
    redibujado que se ve como un parpadeo.
    """
    efecto = widget.graphicsEffect()
    if not isinstance(efecto, QGraphicsOpacityEffect):
        efecto = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(efecto)
    efecto.setOpacity(0.0)
    return animar(efecto, b"opacity", 0.0, 1.0, duracion, curva_entrada_salida(), padre=widget)
