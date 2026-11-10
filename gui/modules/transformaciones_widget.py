"""
Módulo 2: Interfaz Gráfica para Transformaciones Lineales.
Tema: T(x) = Ax, inyectividad y sobreyectividad (Sesiones 6-8).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox, QSplitter, QApplication
)
from PyQt6.QtCore import Qt
from fractions import Fraction
from core.parser import parse_expresion, formato_numero
from core.transformaciones_lineales import analizar_transformacion_completa
from core.eliminacion_gaussiana import nombre_var
from gui.componentes import EstadoVacio, BotonIcono, PestanasSegmentadas, Tarjeta
from gui.entrada import (
    SelectorDimension, SelectorFormato, TablaMatriz, TecladoMatematico, Resumen,
    grupo_dimensiones, boton_principal, contenedor_fila
)

SEP = "-" * 60


def _vector(valores, frac):
    return "[" + ", ".join(formato_numero(x, frac) for x in valores) + "]ᵀ"


class TransformacionesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._analizado = False
        self._crear_barra()
        self.init_ui()

    # ── Barra superior del módulo (la coloca MainWindow) ─────────────

    def _crear_barra(self):
        # T: ℝⁿ → ℝᵐ  (n = columnas de A = dominio, m = filas de A = codominio)
        self.spin_n = SelectorDimension(3, "Dimensión del dominio (n columnas)")
        self.spin_m = SelectorDimension(3, "Dimensión del codominio (m filas)")
        dims = grupo_dimensiones(["  T: ℝ", self.spin_n, "→ ℝ", self.spin_m])
        dims.setToolTip("T: ℝⁿ → ℝᵐ,  T(x) = A · x")
        self.barra_izq = contenedor_fila(dims)
        self.barra_der = boton_principal("Analizar", "Analizar T (Ctrl+Enter)", self.accion_principal)

    def barra_contexto(self):
        return self.barra_izq, self.barra_der

    def accion_principal(self):
        self.analizar_transformacion()

    # ── Cuerpo ──────────────────────────────────────────────────────

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        divisor = QSplitter(Qt.Orientation.Horizontal)
        divisor.setHandleWidth(12)
        divisor.setChildrenCollapsible(False)

        izquierda = QWidget()
        izq = QVBoxLayout(izquierda)
        izq.setContentsMargins(0, 0, 0, 0)
        izq.setSpacing(12)

        tarjeta_A = Tarjeta("A")
        tarjeta_A.setToolTip("Matriz estándar de T (m × n)")
        self.btn_limpiar = BotonIcono("borrar", "Limpiar todo", 16)
        self.btn_limpiar.clicked.connect(self.limpiar_tablas)
        tarjeta_A.agregar_a_cabecera(self.btn_limpiar)
        self.tabla_A = TablaMatriz(filas_visibles=6, expandir=True, encabezado_filas=False)
        tarjeta_A.lay.addWidget(self.tabla_A)
        izq.addWidget(tarjeta_A, 1)

        # Vectores u y b como filas, lado a lado, para dejar el espacio vertical a A
        tarjeta_u = Tarjeta("u  →  T(u)")
        tarjeta_u.setToolTip("Vector u ∈ ℝⁿ para calcular su imagen T(u)")
        self.tabla_u = TablaMatriz(filas_visibles=1, encabezado_filas=False)
        tarjeta_u.lay.addWidget(self.tabla_u)
        tarjeta_b = Tarjeta("b  ∈  Im(T)?")
        tarjeta_b.setToolTip("Vector b ∈ ℝᵐ: ¿existe x tal que T(x) = b?")
        self.tabla_b = TablaMatriz(filas_visibles=1, encabezado_filas=False)
        tarjeta_b.lay.addWidget(self.tabla_b)
        fila_vectores = QHBoxLayout()
        fila_vectores.setSpacing(12)
        fila_vectores.addWidget(tarjeta_u)
        fila_vectores.addWidget(tarjeta_b)
        izq.addLayout(fila_vectores)

        self.teclado = TecladoMatematico()
        self.teclado.registrar(self.tabla_A, self.tabla_u, self.tabla_b)
        self.teclado.fin_de_entrada.connect(self.accion_principal)
        izq.addStretch(0)
        izq.addWidget(self.teclado)

        divisor.addWidget(izquierda)
        divisor.addWidget(self._crear_tarjeta_resultados())
        divisor.setSizes([600, 600])
        layout.addWidget(divisor)

        self.spin_m.valueChanged.connect(self.actualizar_tablas)
        self.spin_n.valueChanged.connect(self.actualizar_tablas)
        self.actualizar_tablas()

    def _crear_tarjeta_resultados(self):
        tarjeta = Tarjeta()
        self.tabs = PestanasSegmentadas()
        self.txt_propiedades = self._nueva_pestania("Propiedades")
        self.txt_imagen = self._nueva_pestania("T(u)")
        self.txt_rango = self._nueva_pestania("Rango")
        tarjeta.cabecera.addWidget(self.tabs.crear_control())
        tarjeta.cabecera.addStretch()

        self.chk_fracciones = SelectorFormato()
        self.chk_fracciones.cambiado.connect(self._repetir_analisis)
        tarjeta.cabecera.addWidget(self.chk_fracciones)
        self.btn_copiar = BotonIcono("copiar", "Copiar pestaña actual", 16)
        self.btn_copiar.clicked.connect(self._copiar_resultado)
        tarjeta.cabecera.addWidget(self.btn_copiar)

        self.resumen_tipo = Resumen()
        self.resumen_rango = Resumen()
        tarjeta.lay.addWidget(self.resumen_tipo)
        tarjeta.lay.addWidget(self.resumen_rango)
        tarjeta.lay.addWidget(self.tabs, 1)
        return tarjeta

    def _nueva_pestania(self, titulo):
        txt = QTextEdit()
        txt.setReadOnly(True)
        EstadoVacio(txt, "Los resultados aparecerán aquí al analizar la transformación.")
        txt.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.tabs.addTab(txt, titulo)
        return txt

    def aplicar_tema(self, paleta):
        for b in (self.btn_limpiar, self.btn_copiar):
            b.aplicar_tema(paleta)
        self.teclado.aplicar_tema(paleta)

    # ── Datos ───────────────────────────────────────────────────────

    def actualizar_tablas(self):
        m = self.spin_m.value()
        n = self.spin_n.value()
        variables = [nombre_var(j) for j in range(n)]
        self.tabla_A.redimensionar(m, n, variables, [f"R{i + 1}" for i in range(m)])
        self.tabla_u.redimensionar(1, n, variables, ["u"])
        self.tabla_b.redimensionar(1, m, [f"b{nombre_var(i)[1:]}" for i in range(m)], ["b"])
        self._limpiar_resultados()

    def limpiar_tablas(self):
        for t in (self.tabla_A, self.tabla_u, self.tabla_b):
            t.limpiar()
        self._limpiar_resultados()

    def _limpiar_resultados(self):
        """Los resultados dejan de valer cuando cambian las dimensiones o los datos."""
        self._analizado = False
        self.resumen_tipo.setVisible(False)
        self.resumen_rango.setVisible(False)
        for txt in (self.txt_propiedades, self.txt_imagen, self.txt_rango):
            txt.clear()

    def _repetir_analisis(self):
        if self._analizado:
            self.analizar_transformacion()

    def _copiar_resultado(self):
        actual = self.tabs.currentWidget()
        if actual is not None:
            QApplication.clipboard().setText(actual.toPlainText())

    def _leer(self, tabla, filas, columnas, nombre_celda, errores):
        valores = []
        for i in range(filas):
            fila = []
            for j in range(columnas):
                item = tabla.item(i, j)
                val, err = parse_expresion(item.text() if item else "0")
                if err:
                    errores.append(f"• {nombre_celda(i, j)}: {err}")
                fila.append(val if val is not None else Fraction(0))
            valores.append(fila)
        return valores

    # ── Análisis ────────────────────────────────────────────────────

    def analizar_transformacion(self):
        for t in (self.tabla_A, self.tabla_u, self.tabla_b):
            t.terminar_edicion()
        m = self.spin_m.value()
        n = self.spin_n.value()
        frac = self.chk_fracciones.isChecked()

        errores = []
        A = self._leer(self.tabla_A, m, n, lambda i, j: f"Matriz A [Fila {i+1}, Col {nombre_var(j)}]", errores)
        u = self._leer(self.tabla_u, 1, n, lambda i, j: f"Vector u [{nombre_var(j)}]", errores)[0]
        b = self._leer(self.tabla_b, 1, m, lambda i, j: f"Vector b [b{j+1}]", errores)[0]

        if errores:
            self.resumen_tipo.mostrar("error", f"Revisa {len(errores)} celda{'s' if len(errores) > 1 else ''}")
            self.resumen_rango.setVisible(False)
            QMessageBox.critical(self, "Error en los Datos", "Se encontraron errores:\n\n" + "\n".join(errores))
            return

        analisis = analizar_transformacion_completa(A, m, n, b=b, u=u, modo_fraccion=frac)
        self._analizado = True

        # 1. Propiedades
        self.txt_propiedades.setText("\n".join([
            "ANÁLISIS DE LA TRANSFORMACIÓN LINEAL  T(x) = A · x",
            SEP,
            f"• Dominio:  {analisis['dominio']}    (espacio de vectores de entrada x de dimensión {n})",
            f"• Codominio: {analisis['codominio']}    (espacio de vectores de salida w de dimensión {m})",
            f"• Número de Columnas Pivote (Rango de A): {analisis['num_pivotes']}",
            "",
            "PROPIEDADES FUNDAMENTALES (Teoremas de Inyectividad y Sobreyectividad):",
            f"  {analisis['detalle_inyectiva']}",
            "",
            f"  {analisis['detalle_sobreyectiva']}",
        ]))

        # 2. Imagen T(u)
        lineas = [
            "EVALUACIÓN DE LA IMAGEN  w = T(u) = A · u",
            SEP,
            f"   Vector ingresado u = {_vector(u, frac)}",
            f"   Resultado Imagen w = T(u) = {_vector(analisis['Tu'], frac)}",
            "   Cálculo componente a componente:",
        ]
        lineas.extend(f"     {p}" for p in analisis["pasos_Tu"])
        self.txt_imagen.setText("\n".join(lineas))

        # 3. Pertenencia al rango
        lineas = [
            "EVALUACIÓN DE PERTENENCIA AL RANGO  (¿Existe x tal que T(x) = b?)",
            SEP,
            f"   Vector objetivo b = {_vector(b, frac)}",
        ]
        if analisis["pertenece_rango"]:
            lineas.append("   ✔ EL VECTOR b SÍ PERTENECE AL RANGO / IMAGEN DE T.")
            lineas.append("   El sistema [A | b] es consistente. Existe al menos un vector x en el dominio tal que T(x) = b.")
        else:
            lineas.append("   ✘ EL VECTOR b NO PERTENECE AL RANGO / IMAGEN DE T.")
            lineas.append("   El sistema [A | b] es inconsistente (la columna b genera contradicción de pivote).")
        self.txt_rango.setText("\n".join(lineas))

        # Resumen de una línea
        iny, sob = analisis["es_inyectiva"], analisis["es_sobreyectiva"]
        if iny and sob:
            estado, titulo = "ok", "Biyectiva"
        else:
            estado = "aviso" if (iny or sob) else "error"
            titulo = f"{'Inyectiva' if iny else 'No inyectiva'} · {'sobreyectiva' if sob else 'no sobreyectiva'}"
        self.resumen_tipo.mostrar(estado, titulo, f"T(u) = {_vector(analisis['Tu'], frac)}")
        if analisis["pertenece_rango"]:
            self.resumen_rango.mostrar("ok", "b está en el rango", f"rango(A) = {analisis['num_pivotes']}")
        else:
            self.resumen_rango.mostrar("error", "b no está en el rango", f"rango(A) = {analisis['num_pivotes']}")
        self.tabs.setCurrentWidget(self.txt_propiedades)
