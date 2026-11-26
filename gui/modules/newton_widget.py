"""Módulo de Newton-Raphson para la calculadora."""
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QSplitter, QTableWidget, QTableWidgetItem, QWidget,
)

from core.newton import COLUMNAS, CRITERIO, resolver, valor_real
from gui.componentes import PestanasSegmentadas, Tarjeta
from gui.entrada import boton_principal
from gui.styles import TEMAS


class NewtonWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resultado = None
        self.paleta = TEMAS["claro"]
        self.boton = boton_principal("Calcular", "Calcular (Ctrl+Enter)", self.accion_principal)
        datos = Tarjeta("Función y parámetros")
        formulario = QFormLayout()
        self.funcion = QLineEdit("x^2 - 2")
        self.funcion.setMaxLength(240)
        self.inicial = QLineEdit("1")
        self.tolerancia = QLineEdit("0.001")
        self.maximo = QSpinBox()
        self.maximo.setRange(1, 1000)
        self.maximo.setValue(30)
        for titulo, campo in (("f(x)", self.funcion), ("Valor inicial x₀", self.inicial),
                              ("Tolerancia", self.tolerancia), ("Máx. iteraciones", self.maximo)):
            formulario.addRow(titulo, campo)
        datos.lay.addLayout(formulario)
        criterio = QLabel(CRITERIO)
        criterio.setWordWrap(True)
        datos.lay.addWidget(criterio)
        datos.lay.addStretch()

        salida = Tarjeta()
        self.tabs = PestanasSegmentadas()
        self.tabla = QTableWidget(0, len(COLUMNAS))
        self.tabla.setHorizontalHeaderLabels(COLUMNAS)
        self.tabla.verticalHeader().hide()
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.figura = Figure(figsize=(4, 3), tight_layout=True)
        self.lienzo = FigureCanvasQTAgg(self.figura)
        self.tabs.addTab(self.tabla, "Iteraciones")
        self.tabs.addTab(self.lienzo, "Gráfica")
        salida.cabecera.addWidget(self.tabs.crear_control())
        salida.cabecera.addStretch()
        self.resumen = QLabel()
        self.resumen.setWordWrap(True)
        self.resumen.setTextFormat(Qt.TextFormat.PlainText)
        salida.lay.addWidget(self.resumen)
        salida.lay.addWidget(self.tabs, 1)

        divisor = QSplitter(Qt.Orientation.Horizontal)
        divisor.setChildrenCollapsible(False)
        divisor.setHandleWidth(12)
        divisor.addWidget(datos)
        divisor.addWidget(salida)
        divisor.setSizes([320, 720])
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(divisor)
        for campo in (self.funcion, self.inicial, self.tolerancia):
            campo.textChanged.connect(self.limpiar)
        self.maximo.valueChanged.connect(self.limpiar)
        self.limpiar()

    def barra_contexto(self):
        return None, self.boton

    def limpiar(self):
        self.resultado = None
        self.tabla.setRowCount(0)
        self.resumen.setText("Ingresá los parámetros y pulsá Calcular.")
        self.figura.clear()
        self.lienzo.draw_idle()

    def accion_principal(self):
        self.limpiar()
        try:
            inicial = float(self.inicial.text().replace(",", "."))
            tol = float(self.tolerancia.text().replace(",", "."))
        except ValueError:
            self.resumen.setText("Ingresá números válidos para x₀ y la tolerancia.")
            return
        try:
            r = resolver(self.funcion.text(), inicial, tol, self.maximo.value())
        except ValueError as exc:
            self.resumen.setText(str(exc))
            return
        self.resultado = r
        self.tabla.setRowCount(len(r.tabla))
        for fila, valores in enumerate(r.tabla.itertuples(index=False, name=None)):
            for col, valor in enumerate(valores):
                texto = f"{valor:.7g}" if isinstance(valor, float) else str(valor)
                self.tabla.setItem(fila, col, QTableWidgetItem(texto))
        self.tabla.resizeColumnsToContents()
        error = "sin paso" if r.tabla.empty else f"{r.tabla.iloc[-1]['Error']:.5g} {r.tabla.iloc[-1]['Unidad']}"
        residuo = f"{r.residuo:.5g}" if np.isfinite(r.residuo) else "indefinido"
        self.resumen.setText(
            f"{r.estado}\nf(x) = {r.funcion}     f′(x) = {r.derivada}\n"
            f"Aproximación: {r.x:.8g}    ·    Iteraciones: {len(r.tabla)}\n"
            f"Error: {error}    ·    Residuo: {residuo}"
        )
        self.dibujar()

    def aplicar_tema(self, paleta):
        self.paleta = paleta
        self.figura.set_facecolor(paleta["surface"])
        if self.resultado:
            self.dibujar()
        else:
            self.lienzo.draw_idle()

    def dibujar(self):
        r = self.resultado
        p = self.paleta
        self.figura.clear()
        eje = self.figura.add_subplot()
        eje.set_facecolor(p["surface"])
        puntos = [*r.tabla["xᵢ"], r.x]
        minimo, maximo = min(puntos), max(puntos)
        # Evita desbordar las transformaciones de escala de Matplotlib.
        if max(abs(minimo), abs(maximo)) > 1e150:
            eje.set_axis_off()
            eje.text(0.5, 0.5, "Rango demasiado grande para graficar.",
                     ha="center", color=p["text"], transform=eje.transAxes)
            self.lienzo.draw_idle()
            return
        margen = max((maximo - minimo) * 0.25, abs(r.x) * 0.05, 0.5)
        xs = np.linspace(minimo - margen, maximo + margen, 500)
        ys = np.array([valor_real(r.evaluar, x) for x in xs])
        ys[np.abs(ys) > 1e150] = np.nan
        eje.axhline(0, color=p["dim"], linewidth=1)
        eje.plot(xs, ys, color=p["text"], label="f(x)")
        for i, fila in enumerate(r.tabla.tail(8).itertuples(index=False, name=None)):
            _, x, fx, _, siguiente, _, _ = fila
            if abs(fx) <= 1e150:
                eje.plot([x, siguiente], [fx, 0], "--", color=p["muted"],
                         label="Tangentes (últimas 8)" if i == 0 else None)
        eje.scatter(puntos, np.zeros(len(puntos)), color=p["red"], s=22,
                    label="Aproximaciones", zorder=3)
        eje.set_xlabel("x", color=p["muted"])
        eje.tick_params(colors=p["muted"])
        for borde in eje.spines.values():
            borde.set_color(p["dim"])
        eje.legend(frameon=False, labelcolor=p["text"], fontsize=8)
        self.lienzo.draw_idle()
