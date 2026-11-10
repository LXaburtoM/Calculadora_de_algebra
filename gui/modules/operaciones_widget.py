"""
Módulo 3: Interfaz Gráfica para Operaciones Vectoriales, Matriciales e Independencia Lineal.
Tema: Operaciones con Matrices, Transpuesta, Inversa, Combinación e Independencia Lineal (Sesiones 9-10).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QStackedWidget
)
from PyQt6.QtCore import Qt
from fractions import Fraction

from core.parser import parse_expresion, formato_numero
from core.eliminacion_gaussiana import nombre_var
from core.algebra_avanzada import inversa_matriz, inversa_adjunta, evaluar_independencia_lineal
from core.validadores import formatear_matriz
from core.operaciones_matriciales import (
    sumar_vectores, restar_vectores, escalar_por_vector,
    sumar_matrices, restar_matrices, escalar_por_matriz,
    multiplicar_matrices, transpuesta_matriz, es_combinacion_lineal
)
from gui.componentes import BotonIcono, ControlSegmentado
from gui.entrada import (
    SelectorDimension, TablaMatriz, mostrar_error, TecladoMatematico, TarjetaResultado,
    grupo_dimensiones, boton_principal, contenedor_fila, pagina_seccion, tarjeta_tabla
)

SEP = "-" * 60
SECCIONES = ["Vectores", "Matrices", "Comb. lineal", "Independencia"]

OPERACIONES_VECTORES = [
    "Suma  (v₁ + v₂)",
    "Resta  (v₁ - v₂)",
    "Escalar × Vector  (c · v₁)",
]
OPERACIONES_MATRICES = [
    "Suma  (A + B)",
    "Resta  (A - B)",
    "Escalar × Matriz  (c · A)",
    "Multiplicación  (A · B)",
    "Transpuesta  (Aᵀ)",
    "Inversa  (Gauss-Jordan)",
    "Inversa  (Adjunta)",
]
EJEMPLOS_MATRICES = [
    "Ejemplos",
    "Ejemplo 1: Suma de Matrices (A + B)",
    "Ejemplo 2: Multiplicación Fila-Columna (A · B)",
    "Ejemplo 3: Matriz Transpuesta (Aᵀ)",
]


def _vector(valores, frac):
    return "[" + ", ".join(formato_numero(x, frac) for x in valores) + "]ᵀ"


def _combo(opciones, tooltip):
    c = QComboBox()
    c.addItems(opciones)
    c.setToolTip(tooltip)
    c.setFixedHeight(32)
    c.setCursor(Qt.CursorShape.PointingHandCursor)
    return c


def _texto(tabla):
    item = tabla.item(0, 0)
    return item.text().strip() if item else "0"


class OperacionesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ultimo_vector_resultado = None
        self.ultima_matriz_resultado = None
        self._crear_barra()
        self.init_ui()

    # ── Barra superior del módulo (la coloca MainWindow) ─────────────

    def _crear_barra(self):
        self.selector_seccion = ControlSegmentado(SECCIONES)
        self.selector_seccion.setToolTip("Sección del módulo")
        self.barra_izq = contenedor_fila(self.selector_seccion)
        self.btn_calcular = boton_principal("Calcular", "Calcular (Ctrl+Enter)", self.accion_principal)
        self.barra_der = self.btn_calcular

    def barra_contexto(self):
        return self.barra_izq, self.barra_der

    def accion_principal(self):
        [self._calcular_vectores, self._calcular_matrices,
         self._verificar_cl, self._evaluar_il][self.paginas.currentIndex()]()

    # ── Cuerpo ──────────────────────────────────────────────────────

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.paginas = QStackedWidget()
        self.paginas.addWidget(self._crear_tab_vectores())
        self.paginas.addWidget(self._crear_tab_matrices())
        self.paginas.addWidget(self._crear_tab_comb_lineal())
        self.paginas.addWidget(self._crear_tab_indep_lineal())
        self.selector_seccion.cambiado.connect(self._cambiar_seccion)
        layout.addWidget(self.paginas)

    def _cambiar_seccion(self, idx):
        self.paginas.setCurrentIndex(idx)
        self.btn_calcular.setText("Evaluar" if idx == 3 else ("Verificar" if idx == 2 else "Calcular"))

    def _escalar(self):
        tabla = TablaMatriz(filas_visibles=1, encabezado_filas=False)
        tabla.horizontalHeader().setVisible(False)
        tabla.redimensionar(1, 1, ["c"], [""])
        tabla.ajustar_altura()
        tabla.item(0, 0).setText("2")
        return tabla

    def _tarjeta_escalar(self, tabla):
        t = tarjeta_tabla("c", tabla, "Escalar")
        t.setFixedWidth(150)
        t.setVisible(False)
        return t

    def _fila(self, *tarjetas):
        fila = QWidget()
        fl = QHBoxLayout(fila)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(12)
        for t in tarjetas:
            fl.addWidget(t, 0 if t.maximumWidth() < 1000 else 1, Qt.AlignmentFlag.AlignTop)
        return fila

    def aplicar_tema(self, paleta):
        for t in (self.res_vec, self.res_mat, self.res_cl, self.res_il):
            t.aplicar_tema(paleta)
        for b in (self.btn_limpiar_hist,):
            b.aplicar_tema(paleta)
        for k in (self.teclado_vec, self.teclado_mat, self.teclado_cl, self.teclado_il):
            k.aplicar_tema(paleta)

    # ------------------------------------------------------------------
    # SECCIÓN 1: OPERACIONES VECTORIALES
    # ------------------------------------------------------------------
    def _crear_tab_vectores(self):
        self.combo_vec_op = _combo(OPERACIONES_VECTORES, "Operación")
        self.spin_vec_n = SelectorDimension(3, "Dimensión n")
        dims = grupo_dimensiones(["  ℝ", self.spin_vec_n])
        dims.setToolTip("Dimensión de los vectores (ℝⁿ)")

        self.tabla_v1 = TablaMatriz(filas_visibles=1, encabezado_filas=False)
        self.tabla_v2 = TablaMatriz(filas_visibles=1, encabezado_filas=False)
        self.tabla_c_vec = self._escalar()
        self.tarjeta_v1 = tarjeta_tabla("v₁", self.tabla_v1)
        self.tarjeta_v2 = tarjeta_tabla("v₂", self.tabla_v2)
        self.tarjeta_c_vec = self._tarjeta_escalar(self.tabla_c_vec)

        self.teclado_vec = TecladoMatematico()
        self.teclado_vec.registrar(self.tabla_c_vec, self.tabla_v1, self.tabla_v2)
        self.teclado_vec.fin_de_entrada.connect(self._calcular_vectores)

        self.res_vec = TarjetaResultado(mensaje_vacio="Los resultados aparecerán aquí al calcular la operación.")
        self.res_vec.formato.cambiado.connect(lambda: self._repetir(self.res_vec, self._calcular_vectores))
        self.res_vec.agregar_accion("Usar como v₁", "Copiar el resultado en v₁", self._usar_resultado_v1)
        self.res_vec.agregar_accion("Usar como v₂", "Copiar el resultado en v₂", self._usar_resultado_v2)
        self.chk_frac_vec = self.res_vec.formato
        self.txt_vec = self.res_vec.texto

        self.combo_vec_op.currentIndexChanged.connect(self._actualizar_modo_vec)
        self.spin_vec_n.valueChanged.connect(self._actualizar_tablas_vec)
        self._actualizar_tablas_vec()
        return pagina_seccion(
            [self.combo_vec_op, dims],
            [(self._fila(self.tarjeta_c_vec, self.tarjeta_v1), 0), (self.tarjeta_v2, 0), (None, 1), (self.teclado_vec, 0)],
            self.res_vec)

    def _repetir(self, tarjeta, calcular):
        if tarjeta.resumen.isVisible() and tarjeta.resumen.punto.property("estado") != "error":
            calcular()

    def _actualizar_modo_vec(self, idx):
        """Muestra v₂ o el escalar c según la operación."""
        es_escalar = (idx == 2)
        self.tarjeta_c_vec.setVisible(es_escalar)
        self.tarjeta_v2.setVisible(not es_escalar)

    def _actualizar_tablas_vec(self):
        n = self.spin_vec_n.value()
        for tabla, nombre in ((self.tabla_v1, "v₁"), (self.tabla_v2, "v₂")):
            tabla.redimensionar(1, n, [nombre_var(i) for i in range(n)], [nombre])

    def _leer_vector(self, tabla, n, etiqueta):
        """Lee un vector de n componentes desde una tabla de 1 fila."""
        v = []
        errores = []
        for i in range(n):
            item = tabla.item(0, i)
            val, err = parse_expresion(item.text() if item else "0")
            if err:
                errores.append(f"• {etiqueta} componente {i+1}: {err}")
            v.append(val if val is not None else Fraction(0))
        return v, errores

    def _error(self, tarjeta, titulo, mensaje):
        tarjeta.resumen.mostrar("error", titulo)
        QMessageBox.critical(self, titulo, mensaje)

    def _calcular_vectores(self):
        for t in (self.tabla_v1, self.tabla_v2, self.tabla_c_vec):
            t.terminar_edicion()
        n = self.spin_vec_n.value()
        frac = self.chk_frac_vec.isChecked()
        idx = self.combo_vec_op.currentIndex()

        v1, errores = self._leer_vector(self.tabla_v1, n, "v₁")

        if idx == 2:   # Escalar × vector
            esc_val, err = parse_expresion(_texto(self.tabla_c_vec))
            if err:
                errores.append(f"• Escalar c: {err}")
            if errores:
                return self._error(self.res_vec, "Error en los datos", "\n".join(errores))

            resultado, pasos, error = escalar_por_vector(esc_val, v1)
            op_str = f"{formato_numero(esc_val, frac)} · v₁"
        else:
            v2, err2 = self._leer_vector(self.tabla_v2, n, "v₂")
            errores.extend(err2)
            if errores:
                return self._error(self.res_vec, "Error en los datos", "\n".join(errores))

            if idx == 0:
                resultado, pasos, error = sumar_vectores(v1, v2)
                op_str = "v₁ + v₂"
            else:
                resultado, pasos, error = restar_vectores(v1, v2)
                op_str = "v₁ - v₂"

        if error:
            return self._error(self.res_vec, "Error", error)

        lineas = [
            f"OPERACIÓN VECTORIAL:  {op_str}",
            SEP,
            "",
            "CÁLCULO COMPONENTE A COMPONENTE:",
        ]
        lineas.extend(pasos)
        lineas.append("")
        lineas.append(SEP)
        comp_str = ",  ".join(formato_numero(x, frac) for x in resultado)
        lineas.append(f"RESULTADO:  [ {comp_str} ]ᵀ")
        self.ultimo_vector_resultado = resultado
        self.txt_vec.setText("\n".join(lineas))
        self.res_vec.resumen.mostrar("ok", op_str, _vector(resultado, frac))
        self.res_vec.acciones.setVisible(True)

    # ------------------------------------------------------------------
    # SECCIÓN 2: OPERACIONES MATRICIALES
    # ------------------------------------------------------------------
    def _crear_tab_matrices(self):
        self.combo_mat_op = _combo(OPERACIONES_MATRICES, "Operación")
        self.spin_mA = SelectorDimension(2, "Filas de A", 8)
        self.spin_nA = SelectorDimension(2, "Columnas de A", 8)
        self.spin_mB = SelectorDimension(2, "Filas de B", 8)
        self.spin_nB = SelectorDimension(2, "Columnas de B", 8)
        dims_A = grupo_dimensiones(["  A ", self.spin_mA, "×", self.spin_nA])
        self.dims_B = grupo_dimensiones(["  B ", self.spin_mB, "×", self.spin_nB])
        self.combo_ejemplos = _combo(EJEMPLOS_MATRICES, "Ejemplos de clase (Sesión 9): se cargan y resuelven")
        self.combo_ejemplos.view().setMinimumWidth(340)

        self.tabla_A = TablaMatriz(filas_visibles=5, expandir=True, encabezado_filas=False)
        self.tabla_B = TablaMatriz(filas_visibles=5, expandir=True, encabezado_filas=False)
        self.tabla_c_mat = self._escalar()
        self.tarjeta_A = tarjeta_tabla("A", self.tabla_A)
        self.tarjeta_B = tarjeta_tabla("B", self.tabla_B)
        self.tarjeta_c_mat = self._tarjeta_escalar(self.tabla_c_mat)
        fila_AB = self._fila(self.tarjeta_c_mat, self.tarjeta_A, self.tarjeta_B)

        self.teclado_mat = TecladoMatematico()
        self.teclado_mat.registrar(self.tabla_c_mat, self.tabla_A, self.tabla_B)
        self.teclado_mat.fin_de_entrada.connect(self._calcular_matrices)

        # Resultados: historial con acciones sobre el último resultado (Ans)
        self.res_mat = TarjetaResultado(mensaje_vacio="Los resultados aparecerán aquí al calcular la operación.")
        self.chk_frac_mat = self.res_mat.formato
        self.txt_mat = self.res_mat.texto

        for texto, tooltip, accion in (
            ("(Ans)ᵀ", "Transpuesta del último resultado", self._quick_transponer),
            ("(Ans)⁻¹ Gauss-Jordan", "Inversa del último resultado por Gauss-Jordan", self._quick_inv_gauss),
            ("(Ans)⁻¹ Adjunta", "Inversa del último resultado por adjunta", self._quick_inv_adj),
            ("Usar como A", "Copiar el resultado en A", self._usar_resultado_A),
            ("Usar como B", "Copiar el resultado en B", self._usar_resultado_B),
        ):
            self.res_mat.agregar_accion(texto, tooltip, accion)
        self.btn_limpiar_hist = BotonIcono("borrar", "Limpiar historial", 16)
        self.btn_limpiar_hist.clicked.connect(self._limpiar_historial)
        self.res_mat.cabecera.addWidget(self.btn_limpiar_hist)

        self.combo_mat_op.currentIndexChanged.connect(self._actualizar_modo_mat)
        for s in (self.spin_mA, self.spin_nA, self.spin_mB, self.spin_nB):
            s.valueChanged.connect(self._actualizar_tablas_mat)
        self.combo_ejemplos.activated.connect(self._cargar_ejemplo)
        self._actualizar_tablas_mat()
        return pagina_seccion(
            [self.combo_mat_op, dims_A, self.dims_B, self.combo_ejemplos],
            [(fila_AB, 1), (None, 0), (self.teclado_mat, 0)],
            self.res_mat)

    def _limpiar_historial(self):
        self.txt_mat.clear()
        self.res_mat.resumen.setVisible(False)
        self.res_mat.acciones.setVisible(False)
        self.ultima_matriz_resultado = None

    def _cargar_ejemplo(self, idx=None):
        idx = self.combo_ejemplos.currentIndex()
        if idx == 0: return

        if idx == 1: # Suma de matrices
            self.combo_mat_op.setCurrentIndex(0)
            self.spin_mA.setValue(2); self.spin_nA.setValue(2)
            self.spin_mB.setValue(2); self.spin_nB.setValue(2)
            self._llenar_matriz(self.tabla_A, [[1, 4], [2, 5]])
            self._llenar_matriz(self.tabla_B, [[-1, 3], [0, 2]])
        elif idx == 2: # Multiplicación de matrices
            self.combo_mat_op.setCurrentIndex(3)
            self.spin_mA.setValue(2); self.spin_nA.setValue(3)
            self.spin_mB.setValue(3); self.spin_nB.setValue(2)
            self._llenar_matriz(self.tabla_A, [[1, -1, 2], [0, 3, 4]])
            self._llenar_matriz(self.tabla_B, [[2, 1], [-1, 0], [3, 5]])
        elif idx == 3: # Transpuesta
            self.combo_mat_op.setCurrentIndex(4)
            self.spin_mA.setValue(2); self.spin_nA.setValue(3)
            self._llenar_matriz(self.tabla_A, [[1, 2, 3], [4, 5, 6]])

        self._calcular_matrices()

    def _llenar_matriz(self, tabla, datos):
        m = len(datos)
        n = len(datos[0])
        for i in range(m):
            for j in range(n):
                if tabla.item(i, j):
                    tabla.item(i, j).setText(str(datos[i][j]))

    def _actualizar_modo_mat(self, idx):
        """Muestra solo las entradas que usa la operación elegida."""
        es_escalar = (idx == 2)
        es_transpuesta = (idx == 4)
        es_inversa = (idx in (5, 6))
        usa_B = not es_escalar and not es_transpuesta and not es_inversa
        self.tarjeta_c_mat.setVisible(es_escalar)
        self.tarjeta_B.setVisible(usa_B)
        self.dims_B.setVisible(usa_B)

    def _actualizar_tablas_mat(self):
        mA, nA = self.spin_mA.value(), self.spin_nA.value()
        mB, nB = self.spin_mB.value(), self.spin_nB.value()
        self._resize_table(self.tabla_A, mA, nA)
        self._resize_table(self.tabla_B, mB, nB)

    def _resize_table(self, tabla, m, n):
        tabla.redimensionar(m, n, [nombre_var(j) for j in range(n)], [f"R{i+1}" for i in range(m)])

    def _leer_matriz(self, tabla, m, n, etiqueta):
        """Lee una matriz m×n desde una QTableWidget."""
        M = []
        errores = []
        for i in range(m):
            fila = []
            for j in range(n):
                item = tabla.item(i, j)
                val, err = parse_expresion(item.text() if item else "0")
                if err:
                    errores.append(f"• {etiqueta}[{i+1},{j+1}]: {err}")
                fila.append(val if val is not None else Fraction(0))
            M.append(fila)
        return M, errores

    def _formatear_matriz(self, M, m, n, frac):
        """Devuelve la matriz como texto alineado."""
        txts = [[formato_numero(M[i][j], frac) for j in range(n)] for i in range(m)]
        ancho = max(3, max(len(c) for fila in txts for c in fila) + 1)
        lineas = []
        for fila in txts:
            celdas = [c.rjust(ancho) for c in fila]
            lineas.append("   [ " + "  ".join(celdas) + " ]")
        return "\n".join(lineas)

    def _registrar_resultado_matriz(self, resultado, op_str, estado="ok"):
        self.ultima_matriz_resultado = resultado
        self.res_mat.resumen.mostrar(estado, op_str, f"{len(resultado)} × {len(resultado[0])}")
        self.res_mat.acciones.setVisible(True)
        self.txt_mat.verticalScrollBar().setValue(self.txt_mat.verticalScrollBar().maximum())

    def _calcular_matrices(self):
        for t in (self.tabla_A, self.tabla_B, self.tabla_c_mat):
            t.terminar_edicion()
        idx = self.combo_mat_op.currentIndex()
        mA, nA = self.spin_mA.value(), self.spin_nA.value()
        mB, nB = self.spin_mB.value(), self.spin_nB.value()
        frac = self.chk_frac_mat.isChecked()

        A, errA = self._leer_matriz(self.tabla_A, mA, nA, "A")
        errores = list(errA)

        if idx == 2:  # Escalar × Matriz
            esc_val, err = parse_expresion(_texto(self.tabla_c_mat))
            if err:
                errores.append(f"• Escalar c: {err}")
            if errores:
                return self._error(self.res_mat, "Error en los datos", "\n".join(errores))
            resultado, pasos, error = escalar_por_matriz(esc_val, A, mA, nA)
            op_str = f"{formato_numero(esc_val, frac)} · A"
            dim_res = f"{mA}×{nA}"
        elif idx == 4: # Transpuesta
            if errores:
                return self._error(self.res_mat, "Error en los datos", "\n".join(errores))
            resultado, pasos, error = transpuesta_matriz(A, mA, nA)
            op_str = "Aᵀ"
            dim_res = f"{nA}×{mA}"
        elif idx in (5, 6): # Inversa (Gauss-Jordan o Adjunta)
            if errores:
                return self._error(self.res_mat, "Error en los datos", "\n".join(errores))
            if mA != nA:
                return self._error(self.res_mat, "Error", "La matriz A debe ser cuadrada para calcular su inversa.")
            if idx == 5:
                resultado, pasos, error = inversa_matriz(A, mA)
                op_str = "A⁻¹ (Gauss-Jordan)"
            else:
                resultado, pasos, error = inversa_adjunta(A, mA)
                op_str = "A⁻¹ (Adjunta)"
            dim_res = f"{mA}×{nA}"

            if error:
                return self._error(self.res_mat, "Error", error)

            lineas = [
                f"OPERACIÓN MATRICIAL:  {op_str}",
                SEP,
                "",
                "PROCEDIMIENTO:",
            ]
            lineas.extend(pasos)
            lineas.append("")
            lineas.append(SEP)
            lineas.append(f"RESULTADO A⁻¹ ({dim_res}):")
            lineas.append(self._formatear_matriz(resultado, len(resultado), len(resultado[0]), frac))

            # Comprobación de la propiedad A^-1 * A = I
            prod, _, _ = multiplicar_matrices(resultado, A, mA, nA, nA)
            lineas.append("")
            lineas.append("COMPROBACIÓN DE PROPIEDAD: A⁻¹ · A = I")
            lineas.append(self._formatear_matriz(prod, len(prod), len(prod[0]), frac))
            es_I = all((prod[i][j] == 1 if i == j else prod[i][j] == 0) for i in range(mA) for j in range(mA))
            if es_I:
                lineas.append("✔ Se cumple la propiedad: A⁻¹ · A = I (Matriz Identidad).")
            else:
                lineas.append("✘ No se obtuvo la identidad.")

            self.txt_mat.append("\n".join(lineas) + "\n")
            self._registrar_resultado_matriz(resultado, op_str + ("  ·  A⁻¹A = I" if es_I else ""),
                                             "ok" if es_I else "aviso")
            return
        else:
            B, errB = self._leer_matriz(self.tabla_B, mB, nB, "B")
            errores.extend(errB)
            if errores:
                return self._error(self.res_mat, "Error en los datos", "\n".join(errores))

            if idx == 0:
                resultado, pasos, error = sumar_matrices(A, B, mA, nA, mB, nB)
                op_str = "A + B"
                dim_res = f"{mA}×{nA}"
            elif idx == 1:
                resultado, pasos, error = restar_matrices(A, B, mA, nA, mB, nB)
                op_str = "A - B"
                dim_res = f"{mA}×{nA}"
            else:   # idx == 3: Multiplicación A·B
                resultado, pasos, error = multiplicar_matrices(A, B, mA, nA, nB)
                op_str = "A × B"
                dim_res = f"{mA}×{nB}"

        if error:
            return self._error(self.res_mat, "Error de dimensiones", error)

        nombre_resultado = f"RESULTADO ({op_str})"
        lineas = [
            f"OPERACIÓN MATRICIAL:  {op_str}",
            SEP,
            "",
            "CÁLCULO ENTRADA POR ENTRADA:",
        ]
        lineas.extend(pasos)
        lineas.append("")
        lineas.append(SEP)
        lineas.append(f"{nombre_resultado} ({dim_res}):")
        lineas.append(self._formatear_matriz(resultado, len(resultado), len(resultado[0]), frac))
        self.txt_mat.append("\n".join(lineas) + "\n")
        self._registrar_resultado_matriz(resultado, op_str)

    # ------------------------------------------------------------------
    # SECCIÓN 3: COMBINACIÓN LINEAL
    # ------------------------------------------------------------------
    def _crear_tab_comb_lineal(self):
        self.spin_cl_n = SelectorDimension(3, "Dimensión n (ℝⁿ)", 8)
        self.spin_cl_k = SelectorDimension(2, "Número de vectores k", 6)
        dims = grupo_dimensiones(["  ℝ", self.spin_cl_n, "   k =", self.spin_cl_k])
        dims.setToolTip("Dimensión ℝⁿ y número de vectores k")

        self.tabla_cl = TablaMatriz(filas_visibles=6, expandir=True, encabezado_filas=False)
        tarjeta = tarjeta_tabla("[v₁ | … | vₖ | b]", self.tabla_cl,
                                      "Cada columna es un vector; la última columna es b")
        self.teclado_cl = TecladoMatematico()
        self.teclado_cl.registrar(self.tabla_cl)
        self.teclado_cl.fin_de_entrada.connect(self._verificar_cl)

        self.res_cl = TarjetaResultado(mensaje_vacio="Los resultados aparecerán aquí al verificar la combinación lineal.")
        self.res_cl.formato.cambiado.connect(lambda: self._repetir(self.res_cl, self._verificar_cl))
        self.chk_frac_cl = self.res_cl.formato
        self.txt_cl = self.res_cl.texto

        self.spin_cl_n.valueChanged.connect(self._actualizar_tabla_cl)
        self.spin_cl_k.valueChanged.connect(self._actualizar_tabla_cl)
        self._actualizar_tabla_cl()
        return pagina_seccion([dims], [(tarjeta, 1), (None, 0), (self.teclado_cl, 0)], self.res_cl)

    def _actualizar_tabla_cl(self):
        n = self.spin_cl_n.value()   # dimensión
        k = self.spin_cl_k.value()   # número de vectores generadores
        headers = [f"v{nombre_var(i)[1:]}" for i in range(k)] + ["b"]
        self.tabla_cl.redimensionar(n, k + 1, headers, [nombre_var(i) for i in range(n)])

    def _verificar_cl(self):
        self.tabla_cl.terminar_edicion()
        n = self.spin_cl_n.value()
        k = self.spin_cl_k.value()
        frac = self.chk_frac_cl.isChecked()
        errores = []

        # Leer los k vectores generadores (columnas 0..k-1)
        vectores = []
        for j in range(k):
            v = []
            for i in range(n):
                item = self.tabla_cl.item(i, j)
                val, err = parse_expresion(item.text() if item else "0")
                if err:
                    errores.append(f"• v{j+1} componente {i+1}: {err}")
                v.append(val if val is not None else Fraction(0))
            vectores.append(v)

        # Leer el vector b (última columna)
        b = []
        for i in range(n):
            item = self.tabla_cl.item(i, k)
            val, err = parse_expresion(item.text() if item else "0")
            if err:
                errores.append(f"• b componente {i+1}: {err}")
            b.append(val if val is not None else Fraction(0))

        if errores:
            return self._error(self.res_cl, "Error en los datos", "\n".join(errores))

        # Llamar al motor de combinación lineal
        res = es_combinacion_lineal(b, vectores)

        if res.get("error"):
            return self._error(self.res_cl, "Error", res["error"])

        # Formatear salida
        lineas = [
            "VERIFICACIÓN DE COMBINACIÓN LINEAL",
            f"¿Es  b  combinación lineal de  " +
            "{ " + ", ".join(f"v{i+1}" for i in range(k)) + " }?",
            SEP,
            "",
            "ESTRATEGIA: Se plantea el sistema  [v₁ | v₂ | ... | vₖ | b]",
            "y se verifica si es CONSISTENTE usando Gauss-Jordan.",
            "Si tiene solución, existen escalares c₁,...,cₖ tales que b = c₁v₁+...+cₖvₖ.",
            "",
        ]

        # Mostrar los vectores ingresados
        for j in range(k):
            comp_str = "  ".join(formato_numero(vectores[j][i], frac).rjust(5) for i in range(n))
            lineas.append(f"  v{j+1} = [ {comp_str} ]ᵀ")
        b_str = "  ".join(formato_numero(b[i], frac).rjust(5) for i in range(n))
        lineas.append(f"   b = [ {b_str} ]ᵀ")
        lineas.append("")
        lineas.append(SEP)

        if res["es_cl"]:
            lineas.append("✔  SÍ — b ES COMBINACIÓN LINEAL de los vectores dados.")
            lineas.append("")
            esc = res["escalares"]
            if esc == "infinitas":
                lineas.append(
                    "Hay INFINITAS combinaciones posibles (los vectores son linealmente dependientes)."
                )
                lineas.append(
                    "Existen múltiples conjuntos de escalares (c₁, c₂, ...) que satisfacen la ecuación."
                )
                self.res_cl.resumen.mostrar("ok", "b es combinación lineal", "infinitas combinaciones")
            else:
                lineas.append("Escalares únicos encontrados:")
                partes_eq = []
                valores = []
                for j in range(k):
                    clave = nombre_var(j)
                    valor = esc.get(clave, Fraction(0))
                    lineas.append(f"   c{j+1} = {formato_numero(valor, frac)}")
                    partes_eq.append(
                        f"({formato_numero(valor, frac)})·v{j+1}"
                    )
                    valores.append(f"c{nombre_var(j)[1:]} = {formato_numero(valor, frac)}")
                lineas.append("")
                lineas.append("Combinación lineal verificada:")
                lineas.append(f"   b = {' + '.join(partes_eq)}")
                self.res_cl.resumen.mostrar("ok", "b es combinación lineal", "   ".join(valores))
        else:
            lineas.append("✘  NO — b NO es combinación lineal de los vectores dados.")
            lineas.append("")
            lineas.append(
                "El sistema [v₁|...|vₖ|b] resultó INCONSISTENTE: la columna b "
                "es columna pivote, lo que significa que b está fuera del "
                "espacio generado por los vectores dados."
            )
            self.res_cl.resumen.mostrar("error", "b no es combinación lineal", "b ∉ Gen{v₁, …, vₖ}")

        self.txt_cl.setText("\n".join(lineas))

    # ------------------------------------------------------------------
    # SECCIÓN 4: INDEPENDENCIA LINEAL
    # ------------------------------------------------------------------
    def _crear_tab_indep_lineal(self):
        self.spin_il_n = SelectorDimension(3, "Dimensión n (ℝⁿ)", 8)
        self.spin_il_k = SelectorDimension(3, "Número de vectores k", 8)
        dims = grupo_dimensiones(["  ℝ", self.spin_il_n, "   k =", self.spin_il_k])
        dims.setToolTip("Dimensión ℝⁿ y número de vectores k")

        self.tabla_il = TablaMatriz(filas_visibles=6, expandir=True, encabezado_filas=False)
        tarjeta = tarjeta_tabla("[v₁ | v₂ | … | vₖ]", self.tabla_il, "Cada columna es un vector")
        self.teclado_il = TecladoMatematico()
        self.teclado_il.registrar(self.tabla_il)
        self.teclado_il.fin_de_entrada.connect(self._evaluar_il)

        self.res_il = TarjetaResultado(formato=False, mensaje_vacio="Los resultados aparecerán aquí al evaluar los vectores.")
        self.txt_il = self.res_il.texto

        self.spin_il_n.valueChanged.connect(self._actualizar_tabla_il)
        self.spin_il_k.valueChanged.connect(self._actualizar_tabla_il)
        self._actualizar_tabla_il()
        return pagina_seccion([dims], [(tarjeta, 1), (None, 0), (self.teclado_il, 0)], self.res_il)

    def _actualizar_tabla_il(self):
        n = self.spin_il_n.value()
        k = self.spin_il_k.value()
        self.tabla_il.redimensionar(n, k, [f"v{nombre_var(i)[1:]}" for i in range(k)],
                                    [nombre_var(i) for i in range(n)])

    def _evaluar_il(self):
        self.tabla_il.terminar_edicion()
        n = self.spin_il_n.value()
        k = self.spin_il_k.value()
        errores = []
        vectores = []
        for j in range(k):
            v = []
            for i in range(n):
                item = self.tabla_il.item(i, j)
                val, err = parse_expresion(item.text() if item else "0")
                if err: errores.append(f"• v{j+1} componente {i+1}: {err}")
                v.append(val if val is not None else Fraction(0))
            vectores.append(v)

        if errores:
            return self._error(self.res_il, "Error", "\n".join(errores))

        res = evaluar_independencia_lineal(vectores, n)

        lineas = [
            "EVALUACIÓN DE INDEPENDENCIA LINEAL",
            SEP,
            "Se plantea el sistema homogéneo A·x = 0, donde las columnas de A son los vectores dados.",
            "Si la única solución es la trivial (x=0), son L.I. Si hay variables libres, son L.D.",
            ""
        ]

        # Los pasos vienen del motor de Gauss-Jordan como diccionarios
        for num, paso in enumerate(res["pasos"], start=1):
            lineas.append(f"Paso {num}: {paso['titulo']}")
            lineas.append(f"  {paso['descripcion']}")
            lineas.append(formatear_matriz(paso["matriz"]))
            lineas.append("")
        lineas.append(SEP)

        if res["es_li"]:
            lineas.append(f"✔ CONCLUSIÓN: Los {k} vectores son LINEALMENTE INDEPENDIENTES (L.I.).")
            lineas.append(f"   Hay un pivote en cada columna ({res['num_pivotes']} pivotes).")
            lineas.append("   La única solución a c₁v₁ + ... + cₖvₖ = 0 es c₁=0, ..., cₖ=0.")
            self.res_il.resumen.mostrar("ok", "Linealmente independientes",
                                        f"{res['num_pivotes']} pivotes de {k}")
        else:
            lineas.append(f"✘ CONCLUSIÓN: Los {k} vectores son LINEALMENTE DEPENDIENTES (L.D.).")
            lineas.append(f"   Solo hay {res['num_pivotes']} pivotes para {k} vectores.")
            lineas.append(f"   Existen {k - res['num_pivotes']} variable(s) libre(s), es decir, infinitas soluciones no triviales.")
            self.res_il.resumen.mostrar("aviso", "Linealmente dependientes",
                                        f"{res['num_pivotes']} pivotes de {k}")

        self.txt_il.setText("\n".join(lineas))

    # ------------------------------------------------------------------
    # ACCIONES SOBRE EL ÚLTIMO RESULTADO (Ans)
    # ------------------------------------------------------------------
    def _quick_transponer(self):
        if not getattr(self, 'ultima_matriz_resultado', None): return
        M = self.ultima_matriz_resultado
        m, n = len(M), len(M[0])
        res, pasos, _ = transpuesta_matriz(M, m, n)

        lineas = ["--- ACCIÓN RÁPIDA: Transpuesta (Ans)ᵀ ---", SEP]
        lineas.extend(pasos)
        lineas.append(f"RESULTADO ({n}x{m}):")
        lineas.append(formatear_matriz(res, self.chk_frac_mat.isChecked()))

        self.txt_mat.append("\n".join(lineas) + "\n")
        self._registrar_resultado_matriz(res, "(Ans)ᵀ")

    def _quick_inv_gauss(self):
        self._quick_inversa(inversa_matriz, "Gauss")

    def _quick_inv_adj(self):
        self._quick_inversa(inversa_adjunta, "Adjunta")

    def _quick_inversa(self, metodo, nombre):
        if not getattr(self, 'ultima_matriz_resultado', None): return
        M = self.ultima_matriz_resultado
        m, n = len(M), len(M[0])
        if m != n: return mostrar_error(self, ["La matriz resultante no es cuadrada."])

        res, pasos, err = metodo(M, m)
        lineas = [f"--- ACCIÓN RÁPIDA: Inversa {nombre} (Ans)⁻¹ ---", SEP]
        if err:
            lineas.append(err)
            self.res_mat.resumen.mostrar("error", "(Ans)⁻¹ no existe")
        else:
            lineas.extend(pasos)
            lineas.append(f"RESULTADO ({n}x{m}):")
            lineas.append(formatear_matriz(res, self.chk_frac_mat.isChecked()))

            # Comprobación A^-1 * A = I
            prod, _, _ = multiplicar_matrices(res, M, m, m, m)
            lineas.append("")
            lineas.append("COMPROBACIÓN DE PROPIEDAD: A⁻¹ · A = I")
            lineas.append(formatear_matriz(prod, self.chk_frac_mat.isChecked()))
            es_I = all((prod[i][j] == 1 if i == j else prod[i][j] == 0) for i in range(m) for j in range(m))
            lineas.append("✔ Se cumple la propiedad: A⁻¹ · A = I (Matriz Identidad)." if es_I else "✘ No se obtuvo la identidad.")
            self._registrar_resultado_matriz(res, f"(Ans)⁻¹ ({nombre})", "ok" if es_I else "aviso")

        self.txt_mat.append("\n".join(lineas) + "\n")

    def _usar_resultado_v1(self):
        self._usar_vector(self.tabla_v1)

    def _usar_resultado_v2(self):
        self._usar_vector(self.tabla_v2)

    def _usar_vector(self, tabla):
        v = self.ultimo_vector_resultado
        if not v: return
        self.spin_vec_n.setValue(len(v))
        for i in range(len(v)):
            tabla.item(0, i).setText(str(v[i]))

    def _usar_resultado_A(self):
        self._usar_matriz(self.tabla_A, self.spin_mA, self.spin_nA)

    def _usar_resultado_B(self):
        self._usar_matriz(self.tabla_B, self.spin_mB, self.spin_nB)

    def _usar_matriz(self, tabla, spin_m, spin_n):
        M = self.ultima_matriz_resultado
        if not M: return
        m, n = len(M), len(M[0])
        spin_m.setValue(m)
        spin_n.setValue(n)
        for i in range(m):
            for j in range(n):
                tabla.item(i, j).setText(str(M[i][j]))
