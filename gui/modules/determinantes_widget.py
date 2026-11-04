"""
Módulo 4: Interfaz Gráfica para Determinantes y Regla de Cramer.
Tema: Expansión por cofactores, reducción por fila y Regla de Cramer (Sesión 11).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QMessageBox
from core.parser import formato_numero
from core.algebra_avanzada import (
    determinante_cofactores, determinante_reduccion, regla_de_cramer, determinante_sarrus
)
from core.eliminacion_gaussiana import nombre_var
from core.validadores import leer_matriz_segura, formatear_matriz
from gui.componentes import ControlSegmentado
from gui.entrada import (
    SelectorDimension, TablaMatriz, TecladoMatematico, TarjetaResultado,
    grupo_dimensiones, boton_principal, contenedor_fila, pagina_seccion, tarjeta_tabla
)

SEP = "-" * 60
SECCIONES = ["Determinante", "Cramer"]
METODOS = {"cofactores": "Cofactores", "sarrus": "Sarrus", "reduccion": "Reducción"}


class DeterminantesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.metodo = "reduccion"
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
        if self.paginas.currentIndex() == 0:
            self._calcular_det(self.metodo)
        else:
            self._resolver_cramer()

    def _cambiar_seccion(self, idx):
        self.paginas.setCurrentIndex(idx)
        self.btn_calcular.setText("Calcular" if idx == 0 else "Resolver")

    # ── Cuerpo ──────────────────────────────────────────────────────

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.paginas = QStackedWidget()
        self.paginas.addWidget(self._crear_tab_determinantes())
        self.paginas.addWidget(self._crear_tab_cramer())
        self.selector_seccion.cambiado.connect(self._cambiar_seccion)
        layout.addWidget(self.paginas)

    def aplicar_tema(self, paleta):
        for t in (self.res_det, self.res_cr, self.teclado_det, self.teclado_cr):
            t.aplicar_tema(paleta)

    @staticmethod
    def _repetir(tarjeta, calcular):
        if tarjeta.resumen.isVisible() and tarjeta.resumen.punto.property("estado") != "error":
            calcular()

    def _error(self, tarjeta, errores):
        tarjeta.resumen.mostrar("error", "Error en los datos")
        QMessageBox.critical(self, "Error en los datos", "\n".join(errores))

    # ── Sección 1: Determinantes ─────────────────────────────────────

    def _crear_tab_determinantes(self):
        """Construye la sección de cálculo de determinantes."""
        self.spin_det_n = SelectorDimension(3, "Dimensión n (matriz n × n)", 8)
        dims = grupo_dimensiones(["  n =", self.spin_det_n])

        # Cada método está a un clic: elegirlo calcula el determinante
        self.selector_metodo = ControlSegmentado(list(METODOS.values()))
        self.selector_metodo.setToolTip("Método de cálculo")
        self.selector_metodo.seleccionar(list(METODOS).index(self.metodo))
        self.selector_metodo.cambiado.connect(lambda i: self._elegir_metodo(list(METODOS)[i]))
        self.btn_sarrus = self.selector_metodo.grupo.button(list(METODOS).index("sarrus"))

        self.tabla_det = TablaMatriz(filas_visibles=6, expandir=True)
        tarjeta = tarjeta_tabla("A", self.tabla_det, "Matriz cuadrada n × n")
        self.teclado_det = TecladoMatematico()
        self.teclado_det.registrar(self.tabla_det)
        self.teclado_det.fin_de_entrada.connect(self.accion_principal)

        self.res_det = TarjetaResultado()
        self.res_det.formato.cambiado.connect(lambda: self._repetir(self.res_det, self.accion_principal))
        self.chk_frac_det = self.res_det.formato
        self.txt_det = self.res_det.texto

        self.spin_det_n.valueChanged.connect(self._actualizar_tabla_det)
        self._actualizar_tabla_det()
        return pagina_seccion([dims, self.selector_metodo],
                              [(tarjeta, 1), (None, 0), (self.teclado_det, 0)], self.res_det)

    def _elegir_metodo(self, metodo):
        self.metodo = metodo
        self._calcular_det(metodo)

    def _actualizar_tabla_det(self):
        """Redimensiona la tabla de determinantes."""
        n = self.spin_det_n.value()
        self.tabla_det.redimensionar(n, n, [nombre_var(j) for j in range(n)], [f"R{i+1}" for i in range(n)])
        # Sarrus solo existe para 3 × 3
        self.btn_sarrus.setEnabled(n == 3)
        self.btn_sarrus.setToolTip("" if n == 3 else "Sarrus solo aplica a matrices 3 × 3")
        if n != 3 and self.metodo == "sarrus":
            self.metodo = "reduccion"
            self.selector_metodo.seleccionar(list(METODOS).index("reduccion"))
        self.res_det.resumen.setVisible(False)
        self.txt_det.clear()

    def _calcular_det(self, metodo):
        """Calcula el determinante por el método elegido."""
        self.tabla_det.terminar_edicion()
        n = self.spin_det_n.value()
        frac = self.chk_frac_det.isChecked()

        if metodo == "sarrus" and n != 3:
            return self._error(self.res_det, ["La Regla de Sarrus solo es aplicable a matrices cuadradas de orden 3x3.\nAjuste la dimensión 'n' a 3 para usar este método."])

        A, errores = leer_matriz_segura(self.tabla_det, n, n, "A")
        if errores:
            return self._error(self.res_det, errores)

        lineas = [f"CÁLCULO DEL DETERMINANTE POR {METODOS[metodo].upper()}", SEP, ""]
        if metodo == "cofactores":
            det, pasos = determinante_cofactores(A)
            lineas.append(pasos)
        elif metodo == "sarrus":
            det, pasos, err = determinante_sarrus(A)
            if err:
                return self._error(self.res_det, [err])
            lineas.extend(pasos)
        else:
            det, pasos = determinante_reduccion(A)
            lineas.extend(pasos)

        lineas.append(SEP)
        lineas.append(f"|A| = {formato_numero(det, frac)}")
        self.txt_det.setText("\n".join(lineas))
        if det != 0:
            self.res_det.resumen.mostrar("ok", f"|A| = {formato_numero(det, frac)}", "A es invertible")
        else:
            self.res_det.resumen.mostrar("aviso", "|A| = 0", "A es singular (no invertible)")

    # ── Sección 2: Regla de Cramer ───────────────────────────────────

    def _crear_tab_cramer(self):
        """Construye la sección de la Regla de Cramer con la matriz aumentada [A | b]."""
        self.spin_cr_n = SelectorDimension(3, "Número de ecuaciones e incógnitas n", 8, minimo=2)
        dims = grupo_dimensiones(["  n =", self.spin_cr_n])

        self.tabla_cr = TablaMatriz(filas_visibles=6, expandir=True)
        tarjeta = tarjeta_tabla("[A | b]", self.tabla_cr, "Coeficientes A y términos independientes b")
        self.teclado_cr = TecladoMatematico()
        self.teclado_cr.registrar(self.tabla_cr)
        self.teclado_cr.fin_de_entrada.connect(self.accion_principal)

        self.res_cr = TarjetaResultado()
        self.res_cr.formato.cambiado.connect(lambda: self._repetir(self.res_cr, self._resolver_cramer))
        self.chk_frac_cr = self.res_cr.formato
        self.txt_cramer = self.res_cr.texto

        self.spin_cr_n.valueChanged.connect(self._actualizar_tablas_cramer)
        self._actualizar_tablas_cramer()
        return pagina_seccion([dims], [(tarjeta, 1), (None, 0), (self.teclado_cr, 0)], self.res_cr)

    def _actualizar_tablas_cramer(self):
        """Redimensiona la tabla [A | b] de Cramer."""
        n = self.spin_cr_n.value()
        self.tabla_cr.redimensionar(n, n + 1, [nombre_var(j) for j in range(n)] + ["b"],
                                    [f"Ec{i+1}" for i in range(n)])
        self.res_cr.resumen.setVisible(False)
        self.txt_cramer.clear()

    def _resolver_cramer(self):
        """Lee [A | b], aplica Cramer y muestra el procedimiento."""
        self.tabla_cr.terminar_edicion()
        n = self.spin_cr_n.value()
        frac = self.chk_frac_cr.isChecked()
        aumentada, errores = leer_matriz_segura(self.tabla_cr, n, n + 1, "[A|b]")
        if errores:
            return self._error(self.res_cr, errores)
        A = [fila[:n] for fila in aumentada]
        b = [fila[n] for fila in aumentada]

        soluciones, pasos, error = regla_de_cramer(A, b, n)

        lineas = ["SOLUCIÓN DEL SISTEMA POR REGLA DE CRAMER", SEP, ""]
        lineas.append("Matriz A:")
        lineas.append(formatear_matriz(A, frac))
        lineas.append("")
        b_str = ", ".join(formato_numero(bi, frac) for bi in b)
        lineas.append(f"Vector b = [ {b_str} ]")
        lineas.append(SEP)
        lineas.extend(pasos)
        lineas.append(SEP)

        if error:
            lineas.append(f"ERROR: {error}")
            self.res_cr.resumen.mostrar("error", "Cramer no aplica", "det(A) = 0")
        else:
            lineas.append("SOLUCIÓN FINAL:")
            for i in range(n):
                lineas.append(
                    f"   x{i+1} = {formato_numero(soluciones[i], frac)}"
                )
            self.res_cr.resumen.mostrar("ok", "Solución única", "   ".join(
                f"{nombre_var(i)} = {formato_numero(soluciones[i], frac)}" for i in range(n)))

        self.txt_cramer.setText("\n".join(lineas))
