"""
Componentes visuales reutilizables de la interfaz.
Tema: iconos dibujados, control segmentado, tarjetas y pestañas compactas (PyQt6).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QToolButton, QButtonGroup,
    QStackedWidget, QWidget, QLabel
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QPainterPath
from PyQt6.QtCore import Qt, QSize, QRectF, QPointF, pyqtSignal


# ── Iconos ───────────────────────────────────────────────────────────
# Trazos simples sobre una cuadrícula de 16×16 para que se vean nítidos
# en cualquier tema sin depender de archivos de imagen.

def _trazos(nombre):
    p = QPainterPath()
    if nombre == "menu":
        for y in (4, 8, 12):
            p.moveTo(2.5, y); p.lineTo(13.5, y)
    elif nombre == "ayuda":
        p.addEllipse(QPointF(8, 8), 6.2, 6.2)
        p.moveTo(6.3, 6.3)
        p.cubicTo(6.3, 4.2, 9.9, 4.2, 9.9, 6.3)
        p.cubicTo(9.9, 7.6, 8.0, 7.7, 8.0, 9.2)
        p.moveTo(8.0, 11.2); p.lineTo(8.0, 11.4)
    elif nombre == "borrar":
        p.moveTo(3, 4.5); p.lineTo(13, 4.5)
        p.moveTo(6.5, 4.5); p.lineTo(6.5, 3); p.lineTo(9.5, 3); p.lineTo(9.5, 4.5)
        p.moveTo(4.5, 4.5); p.lineTo(5.1, 13); p.lineTo(10.9, 13); p.lineTo(11.5, 4.5)
    elif nombre == "copiar":
        p.addRoundedRect(QRectF(5, 5, 8, 8.5), 1.8, 1.8)
        p.moveTo(3, 10.5); p.lineTo(3, 4); p.quadTo(3, 2.5, 4.5, 2.5); p.lineTo(10, 2.5)
    elif nombre == "cerrar":
        p.moveTo(4, 4); p.lineTo(12, 12)
        p.moveTo(12, 4); p.lineTo(4, 12)
    elif nombre == "retroceso":
        p.moveTo(5.5, 3); p.lineTo(14, 3); p.lineTo(14, 13); p.lineTo(5.5, 13); p.lineTo(1.5, 8); p.closeSubpath()
        p.moveTo(8, 6); p.lineTo(11.5, 10)
        p.moveTo(11.5, 6); p.lineTo(8, 10)
    elif nombre == "enter":
        p.moveTo(13, 3.5); p.lineTo(13, 9); p.lineTo(3.5, 9)
        p.moveTo(6.5, 6); p.lineTo(3.5, 9); p.lineTo(6.5, 12)
    elif nombre == "chevron":
        p.moveTo(4.5, 6.5); p.lineTo(8, 10); p.lineTo(11.5, 6.5)
    return p


def icono(nombre, color, tam=18):
    """Dibuja el icono `nombre` en el color indicado y lo devuelve como QIcon."""
    escala = 2
    pix = QPixmap(tam * escala, tam * escala)
    pix.fill(Qt.GlobalColor.transparent)
    pintor = QPainter(pix)
    pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
    pintor.scale(tam * escala / 16, tam * escala / 16)
    lapiz = QPen(QColor(color), 1.5)
    lapiz.setCapStyle(Qt.PenCapStyle.RoundCap)
    lapiz.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pintor.setPen(lapiz)
    pintor.drawPath(_trazos(nombre))
    pintor.end()
    pix.setDevicePixelRatio(escala)
    return QIcon(pix)


class BotonIcono(QToolButton):
    """Botón sin fondo que solo muestra un icono; el tema define su color."""

    def __init__(self, nombre, tooltip="", tam=18, parent=None):
        super().__init__(parent)
        self.nombre_icono = nombre
        self.tam = tam
        self.setObjectName("IconButton")
        self.setToolTip(tooltip)
        self.setAccessibleName(tooltip)
        self.setIconSize(QSize(tam, tam))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def aplicar_tema(self, paleta):
        self.setIcon(icono(self.nombre_icono, paleta["muted"], self.tam))


# ── Control segmentado ──────────────────────────────────────────────

class ControlSegmentado(QFrame):
    """Grupo de opciones excluyentes con aspecto de control segmentado."""

    cambiado = pyqtSignal(int)

    def __init__(self, opciones, parent=None):
        super().__init__(parent)
        self.setObjectName("Segmented")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(2)
        self.grupo = QButtonGroup(self)
        self.grupo.setExclusive(True)
        for i, texto in enumerate(opciones):
            b = QPushButton(texto)
            b.setObjectName("SegButton")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.grupo.addButton(b, i)
            lay.addWidget(b)
        self.grupo.button(0).setChecked(True)
        self.grupo.idClicked.connect(self.cambiado.emit)

    def indice(self):
        return self.grupo.checkedId()

    def seleccionar(self, i):
        self.grupo.button(i).setChecked(True)


class PestanasSegmentadas(QStackedWidget):
    """Pila de páginas controlada por un ControlSegmentado externo.

    Ofrece setCurrentWidget()/addTab() igual que QTabWidget, para que el
    código de los módulos no tenga que cambiar.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._titulos = []
        self.control = None

    def addTab(self, widget, titulo):
        self._titulos.append(titulo)
        self.addWidget(widget)

    def crear_control(self):
        self.control = ControlSegmentado(self._titulos)
        self.control.cambiado.connect(self.setCurrentIndex)
        return self.control

    def setCurrentWidget(self, widget):
        super().setCurrentWidget(widget)
        if self.control:
            self.control.seleccionar(self.indexOf(widget))


# ── Tarjeta ─────────────────────────────────────────────────────────

class Tarjeta(QFrame):
    """Superficie con esquinas redondeadas y una cabecera opcional."""

    def __init__(self, titulo=None, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(14, 8, 14, 14)
        self.lay.setSpacing(10)
        self.cabecera = QHBoxLayout()
        self.cabecera.setContentsMargins(2, 0, 0, 0)
        self.cabecera.setSpacing(6)
        if titulo:
            lbl = QLabel(titulo)
            lbl.setObjectName("CardTitle")
            self.cabecera.addWidget(lbl)
        self.lay.addLayout(self.cabecera)

    def ajustar_a_contenido(self):
        """Limita la altura de la tarjeta a lo que su contenido puede usar.

        Así el espacio que sobra en la ventana no queda como un hueco dentro de la tarjeta.
        """
        m = self.lay.contentsMargins()
        alto = m.top() + m.bottom()
        visibles = 0
        for i in range(self.lay.count()):
            item = self.lay.itemAt(i)
            w = item.widget()
            if w is not None and w.isHidden():
                continue
            maximo = item.maximumSize().height()
            alto += maximo if maximo < 10000 else item.sizeHint().height()
            visibles += 1
        alto += self.lay.spacing() * max(0, visibles - 1)
        self.setMaximumHeight(alto)

    def agregar_a_cabecera(self, widget, al_final=True):
        if al_final:
            if not getattr(self, "_estirado", False):
                self.cabecera.addStretch()
                self._estirado = True
        self.cabecera.addWidget(widget)
