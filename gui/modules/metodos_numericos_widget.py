"""
Módulo 7: Interfaz Gráfica para Métodos Numéricos.
Tema: Bisección, Graficador de Funciones, Notación Posicional y Errores Numéricos.
Asignatura: Álgebra Lineal (MTM0120) - Universidad Americana (UAM).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from __future__ import annotations

import math
from typing import Any
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QSplitter, QMessageBox, QFrame, QTextEdit,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from core.metodos_numericos import (
    metodo_biseccion, preparar_datos_grafica, analisis_posicional_completo,
    demostracion_punto_flotante, calcular_errores_absoluto_relativo,
    calcular_propagacion_error, compilar_funcion
)
from gui.componentes import ControlSegmentado, Tarjeta
from gui.entrada import TarjetaResultado, boton_principal, contenedor_fila

SEP = "=" * 78
SUBSEP = "-" * 78

SECCIONES_PRINCIPALES = [
    "Método de Bisección",
    "Graficador de Funciones",
    "Notación Posicional",
    "Errores Numéricos"
]

EJEMPLOS_BISECCION = [
    ("Ejemplos sugeridos...", "", 0, 0, 1e-4, 100),
    ("1. x³ - 2x - 5 en [2, 3] (Raíz ≈ 2.094551)", "x**3 - 2*x - 5", 2.0, 3.0, 1e-4, 100),
    ("2. cos(x) - x en [0, 1] (Raíz ≈ 0.739085)", "cos(x) - x", 0.0, 1.0, 1e-4, 100),
    ("3. x² - 2 en [1, 2] (Raíz ≈ 1.414214)", "x**2 - 2", 1.0, 2.0, 1e-4, 100),
    ("4. x³ + x - 1 en [0, 1] (Raíz ≈ 0.682328)", "x**3 + x - 1", 0.0, 1.0, 1e-4, 100),
    ("5. [Error] Sin cambio de signo: x² + 1 en [-1, 1]", "x**2 + 1", -1.0, 1.0, 1e-4, 100),
    ("6. [Extremo] Raíz en extremo: x² - 1 en [1, 2]", "x**2 - 1", 1.0, 2.0, 1e-4, 100),
    ("7. [Discontinuidad] 1/x en [-1, 1]", "1/x", -1.0, 1.0, 1e-4, 100),
    ("8. [MaxIter insuficiente] x³ - 2x - 5 (MaxIter=3)", "x**3 - 2*x - 5", 2.0, 3.0, 1e-4, 3),
]

EJEMPLOS_GRAFICAS = [
    ("Funciones de prueba...", "", -5, 5),
    ("Polinomial: x³ - 2x - 5", "x**3 - 2*x - 5", 0, 4),
    ("Trigonométrica: cos(x) - x", "cos(x) - x", -2, 4),
    ("Racional (con asíntota): 1/x", "1/x", -4, 4),
    ("Racional: (x² - 1)/(x - 2)", "(x**2 - 1)/(x - 2)", -3, 5),
    ("Logarítmica: log(x)", "log(x)", 0.01, 10),
    ("Radical: sqrt(x)", "sqrt(x)", 0, 16),
    ("Exponencial: exp(x)", "exp(x)", -4, 3),
    ("Valor Absoluto: abs(x² - 4)", "abs(x**2 - 4)", -4, 4),
]


def _crear_pagina_dividida(izq: QWidget, der: QWidget, factor_izq: int = 4, factor_der: int = 6) -> QWidget:
    """Empaqueta los paneles izquierdo y derecho dentro de un divisor horizontal elegante."""
    contenedor = QWidget()
    lay = QHBoxLayout(contenedor)
    lay.setContentsMargins(12, 12, 12, 12)
    lay.setSpacing(12)
    divisor = QSplitter(Qt.Orientation.Horizontal)
    divisor.setHandleWidth(10)
    divisor.setChildrenCollapsible(False)
    divisor.addWidget(izq)
    divisor.addWidget(der)
    divisor.setStretchFactor(0, factor_izq)
    divisor.setStretchFactor(1, factor_der)
    lay.addWidget(divisor)
    return contenedor


class MetodosNumericosWidget(QWidget):
    """
    Widget principal del Módulo 7: Métodos Numéricos.
    Incorpora Bisección desde cero, Graficador con Matplotlib,
    Notación Posicional (bases 10 y 2) y Análisis de Errores.
    """

    def __init__(self):
        super().__init__()
        self._ultima_raiz_calculada: float | None = None
        self._ultimo_intervalo: tuple[float, float] | None = None
        self._ultima_expr_biseccion: str = ""
        self._crear_barra()
        self.init_ui()

    # ── Barra superior del módulo (controlada por MainWindow) ─────────────

    def _crear_barra(self):
        self.selector_seccion = ControlSegmentado(SECCIONES_PRINCIPALES)
        self.selector_seccion.setToolTip("Sección de Métodos Numéricos")
        self.barra_izq = contenedor_fila(self.selector_seccion)

        self.btn_accion = boton_principal(
            "Calcular Bisección",
            "Ejecutar acción principal (Ctrl+Enter)",
            self.accion_principal
        )
        self.barra_der = self.btn_accion

    def barra_contexto(self):
        return self.barra_izq, self.barra_der

    def accion_principal(self):
        idx = self.paginas.currentIndex()
        if idx == 0:
            self._ejecutar_biseccion()
        elif idx == 1:
            self._ejecutar_grafica()
        elif idx == 2:
            self._ejecutar_posicional()
        elif idx == 3:
            self._ejecutar_errores()

    def _cambiar_seccion(self, idx: int):
        self.paginas.setCurrentIndex(idx)
        nombres_botones = [
            "Calcular Bisección",
            "Graficar Función",
            "Descomponer Número",
            "Analizar Errores"
        ]
        self.btn_accion.setText(nombres_botones[idx])

    def aplicar_tema(self, paleta: dict):
        """Aplica la paleta de colores del tema activo a las tarjetas de resultados."""
        for r in (self.res_biseccion, self.res_posicional, self.res_errores):
            if hasattr(r, "aplicar_tema"):
                r.aplicar_tema(paleta)

    # ── Construcción general ──────────────────────────────────────────

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        from PyQt6.QtWidgets import QStackedWidget
        self.paginas = QStackedWidget()
        self.paginas.addWidget(self._crear_tab_biseccion())
        self.paginas.addWidget(self._crear_tab_graficador())
        self.paginas.addWidget(self._crear_tab_posicional())
        self.paginas.addWidget(self._crear_tab_errores())

        self.selector_seccion.cambiado.connect(self._cambiar_seccion)
        layout.addWidget(self.paginas)

    # ──────────────────────────────────────────────────────────────────
    # 1. TAB BISECCIÓN
    # ──────────────────────────────────────────────────────────────────

    def _crear_tab_biseccion(self) -> QWidget:
        panel_izq = QWidget()
        lay_izq = QVBoxLayout(panel_izq)
        lay_izq.setContentsMargins(0, 0, 0, 0)
        lay_izq.setSpacing(10)

        tarjeta_in = Tarjeta("Parámetros del Método de Bisección")
        lay_form = QGridLayout()
        lay_form.setSpacing(8)

        # Combo de ejemplos
        lbl_ej = QLabel("Cargar ejemplo:")
        self.combo_ej_biseccion = QComboBox()
        for tit, *_ in EJEMPLOS_BISECCION:
            self.combo_ej_biseccion.addItem(tit)
        self.combo_ej_biseccion.currentIndexChanged.connect(self._cargar_ejemplo_biseccion)

        # Función f(x)
        lbl_fn = QLabel("Función f(x):")
        self.txt_fn_biseccion = QLineEdit("x**3 - 2*x - 5")
        self.txt_fn_biseccion.setPlaceholderText("Ej: x**3 - 2*x - 5, cos(x) - x, etc.")

        # Límite a
        lbl_a = QLabel("Extremo inferior (a):")
        self.txt_a = QLineEdit("2")

        # Límite b
        lbl_b = QLabel("Extremo superior (b):")
        self.txt_b = QLineEdit("3")

        # Tolerancia E
        lbl_tol = QLabel("Tolerancia absoluta (E):")
        self.txt_tol = QLineEdit("0.0001")

        # Max iteraciones
        lbl_max = QLabel("Máximo de iteraciones:")
        self.txt_max_iter = QLineEdit("100")

        lay_form.addWidget(lbl_ej, 0, 0)
        lay_form.addWidget(self.combo_ej_biseccion, 0, 1)
        lay_form.addWidget(lbl_fn, 1, 0)
        lay_form.addWidget(self.txt_fn_biseccion, 1, 1)
        lay_form.addWidget(lbl_a, 2, 0)
        lay_form.addWidget(self.txt_a, 2, 1)
        lay_form.addWidget(lbl_b, 3, 0)
        lay_form.addWidget(self.txt_b, 3, 1)
        lay_form.addWidget(lbl_tol, 4, 0)
        lay_form.addWidget(self.txt_tol, 4, 1)
        lay_form.addWidget(lbl_max, 5, 0)
        lay_form.addWidget(self.txt_max_iter, 5, 1)

        tarjeta_in.lay.addLayout(lay_form)

        # Botones de acción
        fila_btns = QHBoxLayout()
        self.btn_calc_bis = QPushButton("Calcular Bisección")
        self.btn_calc_bis.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_calc_bis.clicked.connect(self._ejecutar_biseccion)

        self.btn_ver_grafica = QPushButton("Ver en Graficador ➔")
        self.btn_ver_grafica.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ver_grafica.setToolTip("Abrir esta función con el intervalo y la raíz en el Graficador")
        self.btn_ver_grafica.clicked.connect(self._transferir_a_graficador)

        fila_btns.addWidget(self.btn_calc_bis)
        fila_btns.addWidget(self.btn_ver_grafica)
        tarjeta_in.lay.addLayout(fila_btns)

        lay_izq.addWidget(tarjeta_in)
        lay_izq.addStretch()

        # Tarjeta resultado
        self.res_biseccion = TarjetaResultado(
            formato=False,
            mensaje_vacio="Configure los parámetros y presione 'Calcular Bisección' para ver la tabla iterativa."
        )
        self.res_biseccion.texto.setFont(QFont("Consolas", 10))

        return _crear_pagina_dividida(panel_izq, self.res_biseccion, factor_izq=4, factor_der=6)

    def _cargar_ejemplo_biseccion(self, idx: int):
        if idx <= 0:
            return
        _, fn, a, b, tol, max_i = EJEMPLOS_BISECCION[idx]
        self.txt_fn_biseccion.setText(fn)
        self.txt_a.setText(str(a))
        self.txt_b.setText(str(b))
        self.txt_tol.setText(str(tol))
        self.txt_max_iter.setText(str(max_i))

    def _ejecutar_biseccion(self):
        fn_str = self.txt_fn_biseccion.text().strip()
        try:
            a_val = float(self.txt_a.text().strip().replace(",", "."))
            b_val = float(self.txt_b.text().strip().replace(",", "."))
            tol_val = float(self.txt_tol.text().strip().replace(",", "."))
            max_val = int(self.txt_max_iter.text().strip())
        except ValueError:
            self.res_biseccion.resumen.mostrar("error", "Error en los datos de entrada")
            QMessageBox.critical(self, "Error de entrada", "Asegúrese de ingresar valores numéricos válidos en a, b, E y máximo de iteraciones.")
            return

        res = metodo_biseccion(fn_str, a_val, b_val, tol_val, max_val)

        lineas: list[str] = [
            SEP,
            "               MÉTODO DE BISECCIÓN (ALGORITMO PROPIO DESDE CERO)",
            SEP,
            f"Función: f(x) = {fn_str}",
            f"Intervalo inicial: [{a_val}, {b_val}]",
            f"Tolerancia absoluta requerida: E = {tol_val}",
            f"Límite máximo de iteraciones: Nmax = {max_val}",
            SUBSEP
        ]

        if res["n_teorico"] > 0:
            lineas.append(f"Número teórico mínimo de iteraciones garantizado: n = ⌈log₂((b - a)/E)⌉ = {res['n_teorico']}")

        if res["advertencias"]:
            lineas.append("\n" + "!" * 78)
            for adv in res["advertencias"]:
                lineas.append(f"ADVERTENCIA: {adv}")
            lineas.append("!" * 78 + "\n")

        lineas.append(f"Estado: {res['mensaje']}")
        lineas.append(SUBSEP)

        if res["tabla"]:
            lineas.append("TABLA DE RESULTADOS ITERATIVOS:")
            lineas.append("(Nota: La tabla registra los valores de los extremos a y b antes de actualizar el intervalo)\n")
            encabezado = (
                f"{'k':>3} │ {'a':>10} │ {'b':>10} │ {'xr':>11} │ {'f(a)':>11} │ {'f(b)':>11} │ {'f(xr)':>11} │ {'Eb (cota)':>11} │ {'Ea':>11} │ {'εa':>11}"
            )
            lineas.append(encabezado)
            lineas.append("─" * len(encabezado))

            for fila in res["tabla"]:
                k_s = f"{fila['k']}"
                a_s = f"{fila['a']:.6f}"
                b_s = f"{fila['b']:.6f}"
                xr_s = f"{fila['xr']:.6f}"
                fa_s = f"{fila['fa']:.6g}" if not math.isnan(fila['fa']) else "indef"
                fb_s = f"{fila['fb']:.6g}" if not math.isnan(fila['fb']) else "indef"
                fr_s = f"{fila['fr']:.6g}" if not math.isnan(fila['fr']) else "indef"
                eb_s = f"{fila['Eb']:.6e}"
                ea_s = f"{fila['Ea']:.6e}" if isinstance(fila['Ea'], (int, float)) else str(fila['Ea'])
                eps_s = f"{fila['eps_a']:.6e}" if isinstance(fila['eps_a'], (int, float)) else str(fila['eps_a'])

                lineas.append(
                    f"{k_s:>3} │ {a_s:>10} │ {b_s:>10} │ {xr_s:>11} │ {fa_s:>11} │ {fb_s:>11} │ {fr_s:>11} │ {eb_s:>11} │ {ea_s:>11} │ {eps_s:>11}"
                )

            lineas.append(SUBSEP)

        if res["raiz"] is not None:
            self._ultima_raiz_calculada = res["raiz"]
            self._ultimo_intervalo = (a_val, b_val)
            self._ultima_expr_biseccion = fn_str
            lineas.append(f"\n» RAÍZ APROXIMADA HALLADA: xr = {res['raiz']:.8f}")
            lineas.append(f"» VALOR f(xr): {res['f_raiz']:.8e}")
            lineas.append(f"» ITERACIONES REALIZADAS: {res['iteraciones_realizadas']} de {res['n_teorico']} teóricas")

            if res["raiz_scipy"] is not None:
                lineas.append(f"» CONTRASTE CON SciPy (bisect): {res['raiz_scipy']:.8f}")
                lineas.append(f"» DIFERENCIA ABSOLUTA |x_propio - x_scipy|: {res['dif_scipy']:.6e}")

            if res["exito"]:
                self.res_biseccion.resumen.mostrar(
                    "ok",
                    f"Raíz hallada: xr ≈ {res['raiz']:.6f}",
                    f"{res['iteraciones_realizadas']} iters · Eb ≤ {tol_val:.1e}"
                )
            else:
                self.res_biseccion.resumen.mostrar(
                    "aviso",
                    f"Aproximación: xr ≈ {res['raiz']:.6f}",
                    "Límite alcanzado sin garantizar tolerancia"
                )
        else:
            self.res_biseccion.resumen.mostrar("error", "No se completó el cálculo", res["mensaje"][:30])

        lineas.append(SEP)
        self.res_biseccion.texto.setPlainText("\n".join(lineas))

    def _transferir_a_graficador(self):
        fn_str = self.txt_fn_biseccion.text().strip()
        try:
            a_val = float(self.txt_a.text().strip().replace(",", "."))
            b_val = float(self.txt_b.text().strip().replace(",", "."))
        except ValueError:
            a_val, b_val = -2.0, 4.0

        margen = max(1.0, (b_val - a_val) * 0.5)
        self.txt_fn_graf.setText(fn_str)
        self.txt_xmin.setText(f"{a_val - margen:.2f}")
        self.txt_xmax.setText(f"{b_val + margen:.2f}")

        if self._ultima_raiz_calculada is not None:
            self.txt_raiz_destacada.setText(f"{self._ultima_raiz_calculada:.6f}")
            self.txt_int_a.setText(f"{a_val:.4f}")
            self.txt_int_b.setText(f"{b_val:.4f}")

        self.selector_seccion.seleccionar(1)
        self._ejecutar_grafica()

    # ──────────────────────────────────────────────────────────────────
    # 2. TAB GRAFICADOR DE FUNCIONES
    # ──────────────────────────────────────────────────────────────────

    def _crear_tab_graficador(self) -> QWidget:
        panel_izq = QWidget()
        lay_izq = QVBoxLayout(panel_izq)
        lay_izq.setContentsMargins(0, 0, 0, 0)
        lay_izq.setSpacing(10)

        tarjeta_cfg = Tarjeta("Parámetros del Graficador")
        lay_form = QGridLayout()
        lay_form.setSpacing(8)

        lbl_ej = QLabel("Funciones tipo:")
        self.combo_ej_graf = QComboBox()
        for tit, *_ in EJEMPLOS_GRAFICAS:
            self.combo_ej_graf.addItem(tit)
        self.combo_ej_graf.currentIndexChanged.connect(self._cargar_ejemplo_grafica)

        lbl_fn = QLabel("Función f(x):")
        self.txt_fn_graf = QLineEdit("x**3 - 2*x - 5")

        lbl_xmin = QLabel("Límite inferior (x_min):")
        self.txt_xmin = QLineEdit("-2")

        lbl_xmax = QLabel("Límite superior (x_max):")
        self.txt_xmax = QLineEdit("4")

        lbl_raiz = QLabel("Marcar raíz (opcional):")
        self.txt_raiz_destacada = QLineEdit("")
        self.txt_raiz_destacada.setPlaceholderText("Ej: 2.094551")

        lbl_ia = QLabel("Intervalo a (opcional):")
        self.txt_int_a = QLineEdit("")
        self.txt_int_a.setPlaceholderText("Ej: 2")

        lbl_ib = QLabel("Intervalo b (opcional):")
        self.txt_int_b = QLineEdit("")
        self.txt_int_b.setPlaceholderText("Ej: 3")

        lay_form.addWidget(lbl_ej, 0, 0)
        lay_form.addWidget(self.combo_ej_graf, 0, 1)
        lay_form.addWidget(lbl_fn, 1, 0)
        lay_form.addWidget(self.txt_fn_graf, 1, 1)
        lay_form.addWidget(lbl_xmin, 2, 0)
        lay_form.addWidget(self.txt_xmin, 2, 1)
        lay_form.addWidget(lbl_xmax, 3, 0)
        lay_form.addWidget(self.txt_xmax, 3, 1)
        lay_form.addWidget(lbl_raiz, 4, 0)
        lay_form.addWidget(self.txt_raiz_destacada, 4, 1)
        lay_form.addWidget(lbl_ia, 5, 0)
        lay_form.addWidget(self.txt_int_a, 5, 1)
        lay_form.addWidget(lbl_ib, 6, 0)
        lay_form.addWidget(self.txt_int_b, 6, 1)

        tarjeta_cfg.lay.addLayout(lay_form)

        btn_graficar = QPushButton("Graficar Función")
        btn_graficar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_graficar.clicked.connect(self._ejecutar_grafica)
        tarjeta_cfg.lay.addWidget(btn_graficar)

        lay_izq.addWidget(tarjeta_cfg)
        lay_izq.addStretch()

        # Canvas Matplotlib embebido en PyQt6
        tarjeta_grafica = Tarjeta("Visualización de la Función")
        self.figura = Figure(figsize=(7, 5), dpi=100)
        self.canvas = FigureCanvas(self.figura)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setFixedHeight(34)

        tarjeta_grafica.lay.addWidget(self.toolbar)
        tarjeta_grafica.lay.addWidget(self.canvas, 1)

        # Dibujar gráfico inicial
        self._dibujar_grafica_inicial()

        return _crear_pagina_dividida(panel_izq, tarjeta_grafica, factor_izq=4, factor_der=6)

    def _cargar_ejemplo_grafica(self, idx: int):
        if idx <= 0:
            return
        _, fn, xmin, xmax = EJEMPLOS_GRAFICAS[idx]
        self.txt_fn_graf.setText(fn)
        self.txt_xmin.setText(str(xmin))
        self.txt_xmax.setText(str(xmax))
        self.txt_raiz_destacada.clear()
        self.txt_int_a.clear()
        self.txt_int_b.clear()
        self._ejecutar_grafica()

    def _dibujar_grafica_inicial(self):
        self._ejecutar_grafica()

    def _ejecutar_grafica(self):
        fn_str = self.txt_fn_graf.text().strip()
        try:
            xmin = float(self.txt_xmin.text().strip().replace(",", "."))
            xmax = float(self.txt_xmax.text().strip().replace(",", "."))
        except ValueError:
            QMessageBox.critical(self, "Error", "Ingrese valores numéricos válidos en los límites x_min y x_max.")
            return

        x_vals, y_vals, err = preparar_datos_grafica(fn_str, xmin, xmax, num_puntos=1500)
        if err or x_vals is None or y_vals is None:
            QMessageBox.warning(self, "Error al graficar", f"No se pudo graficar: {err}")
            return

        self.figura.clear()
        ax = self.figura.add_subplot(111)

        # Trazo de la función f(x)
        ax.plot(x_vals, y_vals, label=f"f(x) = {fn_str}", color="#2B82D9", linewidth=2.0)

        # Ejes coordenados
        ax.axhline(0, color="#888888", linestyle="-", linewidth=1.0, alpha=0.7)
        ax.axvline(0, color="#888888", linestyle="-", linewidth=1.0, alpha=0.7)

        # Intervalo inicial [a, b] sombreado si se indicó
        try:
            ia_str = self.txt_int_a.text().strip()
            ib_str = self.txt_int_b.text().strip()
            if ia_str and ib_str:
                ia_val = float(ia_str.replace(",", "."))
                ib_val = float(ib_str.replace(",", "."))
                ax.axvspan(ia_val, ib_val, color="#FFB800", alpha=0.18, label=f"Intervalo [{ia_val}, {ib_val}]")
                ax.axvline(ia_val, color="#D9A54A", linestyle="--", linewidth=1.2)
                ax.axvline(ib_val, color="#D9A54A", linestyle="--", linewidth=1.2)
        except Exception:
            pass

        # Raíz destacada si se indicó
        try:
            r_str = self.txt_raiz_destacada.text().strip()
            if r_str:
                r_val = float(r_str.replace(",", "."))
                _, f_callable, _ = compilar_funcion(fn_str)
                yr = f_callable(r_val) if f_callable else 0.0
                if not math.isnan(yr):
                    ax.plot(r_val, yr, marker="o", markersize=8, color="#E0393E", label=f"Raíz ≈ ({r_val:.5f}, {yr:.2g})")
                    ax.axvline(r_val, color="#E0393E", linestyle=":", linewidth=1.0, alpha=0.7)
        except Exception:
            pass

        ax.set_title(f"Gráfica de f(x) = {fn_str}", fontsize=12, fontweight="bold", pad=10)
        ax.set_xlabel("x", fontsize=10)
        ax.set_ylabel("f(x)", fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="best", framealpha=0.85)

        # Ajuste de límites verticales para no desbordar en saltos de discontinuidad
        y_valid = y_vals[~np.isnan(y_vals)]
        if len(y_valid) > 0:
            q25, q75 = np.percentile(y_valid, 10), np.percentile(y_valid, 90)
            iqr = max(1.0, q75 - q25)
            y_min_lim = max(np.min(y_valid), q25 - 1.5 * iqr)
            y_max_lim = min(np.max(y_valid), q75 + 1.5 * iqr)
            if y_min_lim < y_max_lim:
                ax.set_ylim(y_min_lim, y_max_lim)

        self.figura.tight_layout()
        self.canvas.draw()

    # ──────────────────────────────────────────────────────────────────
    # 3. TAB NOTACIÓN POSICIONAL
    # ──────────────────────────────────────────────────────────────────

    def _crear_tab_posicional(self) -> QWidget:
        panel_izq = QWidget()
        lay_izq = QVBoxLayout(panel_izq)
        lay_izq.setContentsMargins(0, 0, 0, 0)
        lay_izq.setSpacing(10)

        tarjeta_in = Tarjeta("Descomposición Posicional en Base 10 y Base 2")
        lay_form = QVBoxLayout()
        lay_form.setSpacing(10)

        lbl_desc = QLabel(
            "Ingrese un número entero para descomponerlo en sus potencias "
            "correspondientes en base 10 y base 2, demostrando su equivalencia."
        )
        lbl_desc.setWordWrap(True)
        lay_form.addWidget(lbl_desc)

        lbl_num = QLabel("Número entero:")
        self.txt_posicional = QLineEdit("84506")
        self.txt_posicional.setPlaceholderText("Ej: 84506 o 0b11110011")

        lay_form.addWidget(lbl_num)
        lay_form.addWidget(self.txt_posicional)

        fila_ejemplos = QHBoxLayout()
        btn_ej1 = QPushButton("Ejemplo Base 10: 84506")
        btn_ej1.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ej1.clicked.connect(lambda: self._set_posicional("84506"))

        btn_ej2 = QPushButton("Ejemplo Base 2: 11110011")
        btn_ej2.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ej2.clicked.connect(lambda: self._set_posicional("0b11110011"))

        fila_ejemplos.addWidget(btn_ej1)
        fila_ejemplos.addWidget(btn_ej2)
        lay_form.addLayout(fila_ejemplos)

        btn_calcular = QPushButton("Descomponer y Verificar")
        btn_calcular.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_calcular.clicked.connect(self._ejecutar_posicional)
        lay_form.addWidget(btn_calcular)

        tarjeta_in.lay.addLayout(lay_form)
        lay_izq.addWidget(tarjeta_in)
        lay_izq.addStretch()

        self.res_posicional = TarjetaResultado(
            formato=False,
            mensaje_vacio="Ingrese un número y presione 'Descomponer y Verificar' para analizar su representación posicional."
        )
        self.res_posicional.texto.setFont(QFont("Consolas", 10))

        return _crear_pagina_dividida(panel_izq, self.res_posicional, factor_izq=4, factor_der=6)

    def _set_posicional(self, valor: str):
        self.txt_posicional.setText(valor)
        self._ejecutar_posicional()

    def _ejecutar_posicional(self):
        txt = self.txt_posicional.text().strip()
        try:
            res = analisis_posicional_completo(txt)
        except Exception as e:
            self.res_posicional.resumen.mostrar("error", "Error en entrada")
            QMessageBox.critical(self, "Entrada inválida", str(e))
            return

        b10 = res["info_b10"]
        b2 = res["info_b2"]

        lineas: list[str] = [
            SEP,
            "           NOTACIÓN POSICIONAL EN BASE 10 Y BASE 2 (TEOREMA FUNDAMENTAL)",
            SEP,
            f"Número ingresado: {txt}",
            f"Valor en Base 10 (Decimal): {res['decimal']}",
            f"Valor en Base 2 (Binario):  {res['binario']}",
            SUBSEP,
            "1. DESCOMPOSICIÓN POLINÓMICA EN BASE 10:",
            f"   Fórmula: ({b10['valor_abs']})₁₀ = {b10['polinomica']}",
            f"   Evaluación de potencias: {b10['valores']}",
            f"   Resultado final: {b10['resultado_str']}",
            "",
            SUBSEP,
            "2. DESCOMPOSICIÓN POLINÓMICA EN BASE 2:",
            f"   Fórmula: ({b2['bits']})₂ = {b2['polinomica']}",
            f"   Suma de potencias: {b2['valores']}",
            f"   Equivalente en decimal: ({b2['valor_decimal']})₁₀",
            "",
            SUBSEP,
            "3. VERIFICACIÓN DE EQUIVALENCIA:",
            f"   Valor decimal de origen / calculado: ({res['decimal']})₁₀",
            f"   Valor binario interpretado:          ({res['binario']})₂",
            f"   Equivalencia matemática:             {'CORRECTA (Ambos valores coinciden) ✓' if res['equivalencia_verificada'] else 'DISCREPANCIA'}",
            "",
            SUBSEP,
            "NOTA SOBRE NÚMEROS NEGATIVOS:",
            "• El signo negativo '-' se conserva al exterior de la descomposición posicional.",
            "• La descomposición por potencias (tanto en base 10 como en base 2) se efectúa",
            "  estrictamente sobre el valor absoluto del número entero, aplicando el signo",
            "  al resultado final de la suma: N = signo · ∑ (d_i · b^i).",
            SEP
        ]

        self.res_posicional.resumen.mostrar(
            "ok" if res["equivalencia_verificada"] else "error",
            f"({res['decimal']})₁₀  ↔  ({res['binario']})₂",
            "Equivalencia verificada ✓"
        )
        self.res_posicional.texto.setPlainText("\n".join(lineas))

    # ──────────────────────────────────────────────────────────────────
    # 4. TAB ERRORES NUMÉRICOS Y PUNTO FLOTANTE
    # ──────────────────────────────────────────────────────────────────

    def _crear_tab_errores(self) -> QWidget:
        panel_izq = QWidget()
        lay_izq = QVBoxLayout(panel_izq)
        lay_izq.setContentsMargins(0, 0, 0, 0)
        lay_izq.setSpacing(10)

        tarjeta_ctrl = Tarjeta("Módulo de Errores Numéricos")
        lay_form = QVBoxLayout()
        lay_form.setSpacing(10)

        lbl_sec = QLabel("Seleccione la modalidad de análisis:")
        self.selector_sub_error = ControlSegmentado([
            "Punto Flotante",
            "Cálculo Errores",
            "Propagación",
            "Tipos de Error"
        ])
        self.selector_sub_error.cambiado.connect(self._cambiar_sub_error)
        lay_form.addWidget(lbl_sec)
        lay_form.addWidget(self.selector_sub_error)

        # Controles para Cálculo de Errores (xv, xa)
        self.frame_calc_err = QFrame()
        lay_ce = QGridLayout(self.frame_calc_err)
        lay_ce.setContentsMargins(0, 0, 0, 0)
        lay_ce.setSpacing(6)
        lay_ce.addWidget(QLabel("Valor verdadero (x_v):"), 0, 0)
        self.txt_xv = QLineEdit("10.0")
        lay_ce.addWidget(self.txt_xv, 0, 1)
        lay_ce.addWidget(QLabel("Valor aproximado (x_a):"), 1, 0)
        self.txt_xa = QLineEdit("9.85")
        lay_ce.addWidget(self.txt_xa, 1, 1)
        self.frame_calc_err.hide()
        lay_form.addWidget(self.frame_calc_err)

        # Controles para Propagación de Error (f(x), x, delta_x)
        self.frame_prop_err = QFrame()
        lay_pe = QGridLayout(self.frame_prop_err)
        lay_pe.setContentsMargins(0, 0, 0, 0)
        lay_pe.setSpacing(6)
        lay_pe.addWidget(QLabel("Función f(x):"), 0, 0)
        self.txt_fn_prop = QLineEdit("sin(x) + x**2")
        lay_pe.addWidget(self.txt_fn_prop, 0, 1)
        lay_pe.addWidget(QLabel("Punto x:"), 1, 0)
        self.txt_x_prop = QLineEdit("1.0")
        lay_pe.addWidget(self.txt_x_prop, 1, 1)
        lay_pe.addWidget(QLabel("Perturbación (Δx):"), 2, 0)
        self.txt_dx_prop = QLineEdit("0.01")
        lay_pe.addWidget(self.txt_dx_prop, 2, 1)
        self.frame_prop_err.hide()
        lay_form.addWidget(self.frame_prop_err)

        btn_ejecutar = QPushButton("Ejecutar Análisis")
        btn_ejecutar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ejecutar.clicked.connect(self._ejecutar_errores)
        lay_form.addWidget(btn_ejecutar)

        tarjeta_ctrl.lay.addLayout(lay_form)
        lay_izq.addWidget(tarjeta_ctrl)
        lay_izq.addStretch()

        self.res_errores = TarjetaResultado(
            formato=False,
            mensaje_vacio="Seleccione una opción y presione 'Ejecutar Análisis'."
        )
        self.res_errores.texto.setFont(QFont("Consolas", 10))

        # Ejecutar demostración de punto flotante por defecto
        self._analizar_punto_flotante()

        return _crear_pagina_dividida(panel_izq, self.res_errores, factor_izq=4, factor_der=6)

    def _cambiar_sub_error(self, idx: int):
        self.frame_calc_err.setVisible(idx == 1)
        self.frame_prop_err.setVisible(idx == 2)
        self._ejecutar_errores()

    def _ejecutar_errores(self):
        idx = 0
        for i, b in enumerate(self.selector_sub_error.grupo.buttons()):
            if b.isChecked():
                idx = i
                break

        if idx == 0:
            self._analizar_punto_flotante()
        elif idx == 1:
            self._analizar_calculo_errores()
        elif idx == 2:
            self._analizar_propagacion()
        elif idx == 3:
            self._analizar_tipos_error()

    def _analizar_punto_flotante(self):
        fp = demostracion_punto_flotante()
        lineas = [
            SEP,
            "         REPRESENTACIÓN EN PUNTO FLOTANTE (ESTÁNDAR IEEE 754)",
            SEP,
            "1. DEMOSTRACIÓN DE ARITMÉTICA FINITA: 0.1 + 0.2 == 0.3",
            f"   Comparación directa en Python: 0.1 + 0.2 == 0.3  ➔  {fp['resultado_comparacion']}",
            f"   Valor real de (0.1 + 0.2) en memoria: {fp['suma_repr']}",
            f"   Valor real de (0.3) en memoria:       {fp['objetivo_repr']}",
            f"   Diferencia absoluta: |(0.1 + 0.2) - 0.3| = {fp['diferencia_exacta']:.16e}",
            "",
            "   ¿Por qué ocurre esto?",
            "   En base 10, números como 0.1 (1/10) y 0.2 (1/5) tienen representación finita.",
            "   Sin embargo, en base 2 (binario), 0.1 y 0.2 son fracciones periódicas infinitas:",
            "   (0.1)₁₀ = 0.00011001100110011...₂",
            "   Dado que el formato IEEE 754 de doble precisión asigna únicamente 53 bits a",
            "   la mantisa (52 almacenados + 1 implícito), el número debe ser redondeado,",
            "   provocando que la suma difiera levemente de la representación de 0.3.",
            "",
            SUBSEP,
            "2. ÉPSILON DE MÁQUINA (np.finfo(float).eps):",
            f"   Épsilon de máquina ε_mach = {fp['epsilon_maquina']:.16e}",
            "",
            "   Significado matemático:",
            "   Representa la distancia entre 1.0 y el siguiente número en punto flotante",
            "   representable en doble precisión. Si a 1.0 se le suma un número menor que",
            "   ε_mach / 2, la máquina no detecta el cambio: 1.0 + ε_mach > 1.0, pero 1.0 + (ε/2) == 1.0.",
            "",
            SUBSEP,
            "3. EJEMPLOS CONTROLADOS DE OVERFLOW Y UNDERFLOW EN PYTHON/NUMPY:",
            f"   • OVERFLOW (Desbordamiento superior):",
            f"     Operación: np.float64(1e308) * 10.0",
            f"     Resultado devuelto: {fp['overflow_resultado']}",
            f"     Advertencia capturada: {fp['overflow_advertencia']}",
            "     Explicación: El exponente excede el límite máximo para 64 bits (~1.7976e+308),",
            "     produciendo infinito positivo (+inf).",
            "",
            f"   • UNDERFLOW (Desbordamiento inferior / Pérdida de significancia):",
            f"     Operación: np.float64(1e-308) / 1e20",
            f"     Resultado devuelto: {fp['underflow_resultado']}",
            f"     Advertencia capturada: {fp['underflow_advertencia']}",
            "     Explicación: El número es tan diminuto que queda por debajo del menor número",
            "     positivo subnormal representable (~4.94e-324), colapsando exactamente a 0.0.",
            SEP
        ]
        self.res_errores.resumen.mostrar("ok", "Punto Flotante IEEE 754", f"0.1 + 0.2 == 0.3 ➔ {fp['resultado_comparacion']}")
        self.res_errores.texto.setPlainText("\n".join(lineas))

    def _analizar_calculo_errores(self):
        try:
            xv = float(self.txt_xv.text().strip().replace(",", "."))
            xa = float(self.txt_xa.text().strip().replace(",", "."))
        except ValueError:
            QMessageBox.critical(self, "Error", "Ingrese valores numéricos válidos en xv y xa.")
            return

        res = calcular_errores_absoluto_relativo(xv, xa)
        lineas = [
            SEP,
            "                    CÁLCULO DE ERRORES NUMÉRICOS",
            SEP,
            f"Valor verdadero (xv):   {xv}",
            f"Valor aproximado (xa):  {xa}",
            SUBSEP,
            f"1. ERROR ABSOLUTO: Ea = |xv - xa|",
            f"   Ea = |{xv} - {xa}| = {res['error_absoluto']:.8f}",
            "",
            f"2. ERROR RELATIVO: Er = |xv - xa| / |xv|  (para xv ≠ 0)",
            f"   Er = {res['error_relativo_str']}",
            "",
            f"3. ERROR RELATIVO PORCENTUAL: Er(%) = Er · 100%",
            f"   Er(%) = {res['error_porcentual_str']}",
            "",
            SUBSEP,
            "NOTA IMPORTANTE:",
            "Si el valor verdadero xv es 0, el error relativo NO está definido porque",
            "implicaría una división entre cero. En tal caso solo tiene sentido evaluar el error absoluto Ea.",
            SEP
        ]
        self.res_errores.resumen.mostrar(
            "ok",
            f"Ea = {res['error_absoluto']:.6g}",
            f"Er(%) = {res['error_porcentual_str']}"
        )
        self.res_errores.texto.setPlainText("\n".join(lineas))

    def _analizar_propagacion(self):
        fn_str = self.txt_fn_prop.text().strip()
        try:
            x_val = float(self.txt_x_prop.text().strip().replace(",", "."))
            dx_val = float(self.txt_dx_prop.text().strip().replace(",", "."))
        except ValueError:
            QMessageBox.critical(self, "Error", "Ingrese valores numéricos válidos en x y Δx.")
            return

        try:
            res = calcular_propagacion_error(fn_str, x_val, dx_val)
        except Exception as e:
            QMessageBox.critical(self, "Error en propagación", str(e))
            return

        lineas = [
            SEP,
            "                     PROPAGACIÓN DEL ERROR (SERIE DE TAYLOR)",
            SEP,
            f"Función evaluada: f(x) = {res['expr_str']}",
            f"Punto base x:     {res['x']}",
            f"Perturbación Δx:  {res['delta_x']}",
            SUBSEP,
            f"1. DERIVADA ANALÍTICA (SymPy):",
            f"   f'(x) = {res['derivada_str']}",
            f"   f'({res['x']}) = {res['f_prime']:.8f}",
            "",
            f"2. CAMBIO APROXIMADO LINEAL: Δy_aprox = f'(x) · Δx",
            f"   Δy_aprox = ({res['f_prime']:.8f}) · ({res['delta_x']}) = {res['delta_y_aprox']:.8f}",
            "",
            f"3. CAMBIO REAL: Δy_real = f(x + Δx) - f(x)",
            f"   Δy_real = {res['delta_y_real']:.8f}",
            "",
            f"4. DISCREPANCIA (ERROR DE LA APROXIMACIÓN LINEAL):",
            f"   |Δy_real - Δy_aprox| = {res['diferencia_absoluta']:.8e}",
            "",
            SUBSEP,
            "INTERPRETACIÓN MATEMÁTICA:",
            "• La aproximación mediante derivada lineal corresponde al truncamiento de la",
            "  Serie de Taylor en el término de primer orden: f(x + Δx) ≈ f(x) + f'(x)Δx.",
            "• El error de la aproximación es de orden O(Δx²), lo que explica por qué la fórmula",
            "  funciona extraordinariamente bien para perturbaciones pequeñas (Δx << 1),",
            "  pero diverge cuando Δx se incrementa.",
            SEP
        ]
        self.res_errores.resumen.mostrar(
            "ok",
            f"Δy_aprox = {res['delta_y_aprox']:.6g}",
            f"Dif = {res['diferencia_absoluta']:.2e}"
        )
        self.res_errores.texto.setPlainText("\n".join(lineas))

    def _analizar_tipos_error(self):
        lineas = [
            SEP,
            "           GLOSARIO DE TIPOS DE ERRORES NUMÉRICOS (MARCO TEÓRICO)",
            SEP,
            "1. ERROR INHERENTE:",
            "   Es el error presente en los datos iniciales del problema debido a mediciones",
            "   imprecisas, incertidumbre experimental o redondeos previos antes de procesarlos.",
            "   Ejemplo: Medir una distancia con una cinta métrica con tolerancia de ±1 mm.",
            "",
            "2. ERROR DE REDONDEO:",
            "   Se genera debido a que las computadoras utilizan una cantidad finita de bits",
            "   (aritmética de punto flotante) para almacenar números reales continuos.",
            "   Ejemplo: Almacenar 1/3 como 0.3333333333333333, descartando los infinitos dígitos.",
            "",
            "3. ERROR DE TRUNCAMIENTO NUMÉRICO:",
            "   Surge al aproximar un proceso matemático infinito mediante uno finito.",
            "   Ejemplo: Evaluar la serie de Taylor de e^x usando solo los 3 primeros términos,",
            "   o detener un método iterativo como Bisección antes de alcanzar la raíz exacta.",
            "",
            "4. ERROR DEL MODELO MATEMÁTICO:",
            "   Ocurre por las simplificaciones de la física real asumidas al formular el modelo.",
            "   Ejemplo: Despreciar la resistencia del aire en la trayectoria balística de un proyectil.",
            "",
            "   » DISTINCIÓN CLAVE: Truncamiento Numérico vs Error de Modelación:",
            "     El error de truncamiento numérico reside en el MÉTODO DE CÁLCULO (algoritmo),",
            "     mientras que el error de modelación reside en las ECUACIONES FÍSICAS elegidas.",
            "",
            "5. OVERFLOW (Desbordamiento Superior):",
            "   Se produce cuando el resultado de una operación supera el mayor número positivo",
            "   representable en la memoria asignada (en doble precisión > ~1.79e+308 ➔ inf).",
            "",
            "6. UNDERFLOW (Desbordamiento Inferior):",
            "   Se produce cuando el resultado es positivo pero tan cercano a cero que no puede",
            "   distinguirse de cero en la arquitectura asignada (en doble precisión < ~4.94e-324 ➔ 0.0).",
            SEP
        ]
        self.res_errores.resumen.mostrar("ok", "Tipos de Error", "Glosario y Marco Teórico")
        self.res_errores.texto.setPlainText("\n".join(lineas))
