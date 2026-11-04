"""
Componentes visuales reutilizables de la interfaz.
Tema: iconos dibujados, control segmentado, tarjetas y pestañas compactas (PyQt6).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

import math

from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QToolButton, QButtonGroup,
    QStackedWidget, QWidget, QLabel, QSizePolicy
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QPainterPath
from PyQt6.QtCore import Qt, QSize, QRectF, QPointF, QObject, QEvent, pyqtSignal
from gui.animaciones import animar, NORMAL


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
    elif nombre == "ajustes":
        # Engranaje de contorno continuo (estilo SF Symbols): 8 dientes y centro hueco
        puntos = []
        for k in range(8):
            a = math.radians(k * 45)
            for desfase, radio in ((-14, 4.9), (-8, 6.6), (8, 6.6), (14, 4.9)):
                ang = a + math.radians(desfase)
                puntos.append(QPointF(8 + radio * math.cos(ang), 8 + radio * math.sin(ang)))
        p.moveTo(puntos[0])
        for punto in puntos[1:]:
            p.lineTo(punto)
        p.closeSubpath()
        p.addEllipse(QPointF(8, 8), 2.1, 2.1)
    # ── Íconos de los módulos (mismo trazo que el engranaje) ──
    elif nombre == "mod_sistemas":
        # Matriz aumentada: corchetes, tres filas y la columna b
        p.moveTo(3.5, 2.5); p.lineTo(2, 2.5); p.lineTo(2, 13.5); p.lineTo(3.5, 13.5)
        p.moveTo(12.5, 2.5); p.lineTo(14, 2.5); p.lineTo(14, 13.5); p.lineTo(12.5, 13.5)
        for y in (5, 8, 11):
            p.moveTo(4.6, y); p.lineTo(7.8, y)
            p.moveTo(11.6, y); p.lineTo(11.61, y)
        p.moveTo(9.7, 3.8); p.lineTo(9.7, 12.2)
    elif nombre == "mod_transformaciones":
        # Un punto que se transforma en otro: x ↦ T(x)
        p.addEllipse(QPointF(4, 11.5), 1.8, 1.8)
        p.moveTo(5.6, 10); p.quadTo(7, 4.5, 12.5, 4)
        p.moveTo(12.5, 4); p.lineTo(10, 2.6)
        p.moveTo(12.5, 4); p.lineTo(10.8, 6.2)
    elif nombre == "mod_operaciones":
        # Dos matrices que se combinan
        p.addRoundedRect(QRectF(2, 2, 8, 8), 2, 2)
        p.addRoundedRect(QRectF(6, 6, 8, 8), 2, 2)
    elif nombre == "mod_determinantes":
        # |A|: barras verticales con entradas
        p.moveTo(3, 2.5); p.lineTo(3, 13.5)
        p.moveTo(13, 2.5); p.lineTo(13, 13.5)
        for x in (6.5, 9.5):
            for y in (6, 10):
                p.moveTo(x, y); p.lineTo(x + 0.01, y)
    elif nombre == "mod_lu":
        # Matriz partida en triangular inferior y superior
        p.addRoundedRect(QRectF(2, 2, 12, 12), 2.5, 2.5)
        p.moveTo(3.2, 3.2); p.lineTo(12.8, 12.8)
    elif nombre == "mod_verificador":
        p.addEllipse(QPointF(8, 8), 6.2, 6.2)
        p.moveTo(5.2, 8.3); p.lineTo(7.2, 10.3); p.lineTo(10.9, 6.2)
    elif nombre == "check":
        p.moveTo(3.5, 8.5); p.lineTo(6.5, 11.5); p.lineTo(12.5, 4.5)
    elif nombre == "chevron":
        p.moveTo(4.5, 6.5); p.lineTo(8, 10); p.lineTo(11.5, 6.5)
    return p


def icono_estados(nombre, color, color_activo, tam=18):
    """Ícono con dos colores: normal y marcado (para botones que se pueden seleccionar)."""
    resultado = QIcon()
    for c, estado in ((color, QIcon.State.Off), (color_activo, QIcon.State.On)):
        resultado.addPixmap(icono(nombre, c, tam).pixmap(tam, tam), QIcon.Mode.Normal, estado)
    return resultado


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
    """Grupo de opciones excluyentes con aspecto de control segmentado.

    La opción elegida se marca con una pastilla que se desliza hasta ella, como en iOS.
    """

    cambiado = pyqtSignal(int)

    def __init__(self, opciones, parent=None):
        super().__init__(parent)
        self.setObjectName("Segmented")
        # Altura propia: no se estira al alto de la barra que lo contiene
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
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
        # La pastilla va detrás de los botones; los botones no pintan fondo al estar marcados
        self.pastilla = QFrame(self)
        self.pastilla.setObjectName("SegThumb")
        self.pastilla.lower()
        self.grupo.button(0).setChecked(True)
        self.grupo.idClicked.connect(self.cambiado.emit)
        self.grupo.idToggled.connect(lambda i, marcado: marcado and self._mover_pastilla(True))

    def indice(self):
        return self.grupo.checkedId()

    def seleccionar(self, i):
        self.grupo.button(i).setChecked(True)

    def _mover_pastilla(self, animar_movimiento):
        boton = self.grupo.checkedButton()
        if boton is None or not self.isVisible():
            return
        destino = boton.geometry()
        if animar_movimiento and self.pastilla.width() > 0:
            animar(self.pastilla, b"geometry", self.pastilla.geometry(), destino, NORMAL)
        else:
            self.pastilla.setGeometry(destino)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        self._mover_pastilla(False)

    def showEvent(self, evento):
        super().showEvent(evento)
        self._mover_pastilla(False)


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
        self.lay.setContentsMargins(16, 8, 16, 16)
        self.lay.setSpacing(8)
        self.cabecera = QHBoxLayout()
        self.cabecera.setContentsMargins(0, 0, 0, 0)
        self.cabecera.setSpacing(8)
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


# ── Estado vacío ────────────────────────────────────────────────────

class EstadoVacio(QObject):
    """Mensaje centrado sobre un QTextEdit mientras no tenga contenido."""

    def __init__(self, texto_edit, mensaje):
        super().__init__(texto_edit)
        self.texto_edit = texto_edit
        self.etiqueta = QLabel(mensaje, texto_edit.viewport())
        self.etiqueta.setObjectName("EmptyState")
        self.etiqueta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.etiqueta.setWordWrap(True)
        self.etiqueta.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        texto_edit.viewport().installEventFilter(self)
        texto_edit.textChanged.connect(self._actualizar)
        self._actualizar()

    def eventFilter(self, objeto, evento):
        if evento.type() == QEvent.Type.Resize:
            self.etiqueta.setGeometry(objeto.rect().adjusted(24, 0, -24, 0))
        return False

    def _actualizar(self):
        self.etiqueta.setVisible(self.texto_edit.document().isEmpty())
