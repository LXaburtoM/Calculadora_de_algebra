"""
Módulo 5: Interfaz Gráfica para Factorización LU y Solución Ax = b.
Tema: Descomposición LU (A = L·U) y resolución en 2 etapas (Sesión 12).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMessageBox, QComboBox
from PyQt6.QtCore import Qt
from core.parser import formato_numero
from core.eliminacion_gaussiana import nombre_var
from core.factorizacion_lu import (
    factorizacion_lu, resolver_sistema_lu, verificar_solucion_ax_b
)
from gui.componentes import BotonIcono
from gui.entrada import (
    SelectorDimension, TablaMatriz, leer_matriz_segura, TecladoMatematico, TarjetaResultado,
    grupo_dimensiones, boton_principal, contenedor_fila, pagina_seccion, tarjeta_tabla
)

SEP = "=" * 60
SUBSEP = "-" * 60

TEOREMAS_LU = """
================================================================================
                    TEOREMAS CLAVE DEL MÓDULO: FACTORIZACIÓN LU
================================================================================

1. TEOREMA DE FACTORIZACIÓN LU:
   Sea A una matriz m x n. Si A puede reducirse a una forma escalonada U usando
   ÚNICAMENTE operaciones de reemplazo de filas (Fi ← Fi - l·Fj) sin
   intercambios ni escalamiento, entonces A admite una descomposición:
                              A = L · U
   donde:
   • L es una matriz triangular inferior m x m con unos (1) en la diagonal
     principal (triangular inferior unitaria).
   • U es una matriz triangular superior / escalonada m x n.
   • Cada entrada L[i,j] (i > j) almacena el multiplicador exacto l = a_ij / pivote.

2. RESOLUCIÓN DE Ax = b EN DOS ETAPAS (DOBLE SUSTITUCIÓN):
   Dado que A = L · U, el sistema Ax = b equivale a L(Ux) = b:
   • Etapa 1: Resolver L · y = b mediante Sustitución Hacia Adelante (progresiva).
   • Etapa 2: Resolver U · x = y mediante Sustitución Hacia Atrás (regresiva).

3. EFICIENCIA COMPUTACIONAL:
   • Factorizar A = L · U requiere O(2/3 n³) operaciones (se realiza UNA sola vez).
   • Resolver para cualquier nuevo vector b toma únicamente O(2n²) operaciones.
   • Comparación: La Eliminación Gaussiana tradicional requiere O(2/3 n³) para
     CADA nuevo vector b. LU optimiza drásticamente el costo computacional.

4. CONDICIÓN DE PIVOTEO (PERMUTACIÓN):
   Si en algún paso de la diagonal de U aparece un cero que requiera intercambio
   de filas, la matriz NO admite factorización LU estándar. Requiere pivoteo
   parcial, originando la factorización P · A = L · U.
================================================================================
"""

# (nombre, A, b) de los ejemplos predefinidos
EJEMPLOS = [
    ("Ejemplo 1: Sistema 3x3 estándar",
     [["2", "1", "-1"], ["1", "3", "2"], ["1", "0", "2"]], ["8", "13", "7"]),
    ("Ejemplo 2: Matriz que requiere pivoteo (PA=LU)",
     [["0", "2", "1"], ["1", "1", "1"], ["2", "1", "0"]], ["1", "2", "3"]),
    ("Ejemplo 3: Matriz rectangular 4x3",
     [["1", "2", "1"], ["2", "5", "3"], ["3", "7", "5"], ["1", "3", "2"]], ["4", "9", "14", "5"]),
]


class LUWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ultima_matriz_L = None
        self.ultima_matriz_U = None
        self.matriz_A_factorizada = None
        self._ultima_accion = None
        self._cargando_ejemplo = False
        self._crear_barra()
        self.init_ui()

    # ── Barra superior del módulo (la coloca MainWindow) ─────────────

    def _crear_barra(self):
        self.spin_m = SelectorDimension(3, "Filas m", 6, minimo=2)
        self.spin_n = SelectorDimension(3, "Columnas n", 6, minimo=2)
        dims = grupo_dimensiones(["  A ", self.spin_m, "×", self.spin_n])

        self.combo_ejemplos = QComboBox()
        self.combo_ejemplos.addItems(["Ejemplos"] + [nombre for nombre, _, _ in EJEMPLOS])
        self.combo_ejemplos.setToolTip("Cargar un ejemplo predefinido")
        self.combo_ejemplos.setFixedHeight(32)
        self.combo_ejemplos.view().setMinimumWidth(340)
        self.combo_ejemplos.activated.connect(self._cargar_ejemplo)
        self.barra_izq = contenedor_fila(dims, self.combo_ejemplos)

        # Las dos acciones del módulo a un clic: factorizar y resolver
        self.btn_factorizar = QPushButton("Factorizar A = LU")
        self.btn_factorizar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_factorizar.clicked.connect(self._ejecutar_factorizacion)
        self.btn_resolver = boton_principal("Resolver Ax = b", "Resolver con LU (Ctrl+Enter)",
                                            self._ejecutar_resolucion)
        self.barra_der = contenedor_fila(self.btn_factorizar, self.btn_resolver)

    def barra_contexto(self):
        return self.barra_izq, self.barra_der

    def accion_principal(self):
        self._ejecutar_resolucion()

    # ── Cuerpo ──────────────────────────────────────────────────────

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabla = TablaMatriz(filas_visibles=6, expandir=True)
        tarjeta = tarjeta_tabla("[A | b]", self.tabla, "Matriz A (m × n) y términos independientes b")
        self.teclado = TecladoMatematico()
        self.teclado.registrar(self.tabla)
        self.teclado.fin_de_entrada.connect(self.accion_principal)

        self.res = TarjetaResultado(mensaje_vacio="Los resultados aparecerán aquí al factorizar o resolver.")
        self.res.formato.cambiado.connect(self._repetir_ultima_accion)
        self.chk_frac = self.res.formato
        self.txt_salida = self.res.texto
        # El procedimiento de core/ usa separadores largos: sin ajuste de línea se leen enteros
        self.txt_salida.setLineWrapMode(self.txt_salida.LineWrapMode.NoWrap)
        self.btn_limpiar = BotonIcono("borrar", "Limpiar procedimiento", 16)
        self.btn_limpiar.clicked.connect(self._limpiar_consola)
        self.res.cabecera.addWidget(self.btn_limpiar)

        layout.addWidget(pagina_seccion([], [(tarjeta, 1), (None, 0), (self.teclado, 0)], self.res))

        self.spin_m.valueChanged.connect(self._actualizar_tablas)
        self.spin_n.valueChanged.connect(self._actualizar_tablas)
        self._actualizar_tablas()
        self._cargar_ejemplo_defecto()

    def aplicar_tema(self, paleta):
        for w in (self.res, self.teclado, self.btn_limpiar):
            w.aplicar_tema(paleta)

    def _limpiar_consola(self):
        """Limpia el área de texto."""
        self.txt_salida.clear()
        self.res.resumen.setVisible(False)
        self._ultima_accion = None

    def _repetir_ultima_accion(self):
        if self._ultima_accion == "factorizar":
            self._ejecutar_factorizacion()
        elif self._ultima_accion == "resolver":
            # Si el procedimiento incluía la factorización, se rehace completo
            if "1. FACTORIZACIÓN" in self.txt_salida.toPlainText():
                self._ejecutar_factorizacion()
            self._ejecutar_resolucion()

    def _actualizar_tablas(self):
        """Redimensiona la tabla [A | b] según m y n."""
        m = self.spin_m.value()
        n = self.spin_n.value()
        self.tabla.redimensionar(m, n + 1, [nombre_var(j) for j in range(n)] + ["b"],
                                 [f"F{i+1}" for i in range(m)])
        # Si las dimensiones cambian a mano, el ejemplo mostrado ya no corresponde
        if not self._cargando_ejemplo:
            self.combo_ejemplos.setCurrentIndex(0)
        self.btn_resolver.setEnabled(m == n)
        self.btn_resolver.setToolTip("Resolver con LU (Ctrl+Enter)" if m == n
                                     else "Para resolver Ax = b la matriz debe ser cuadrada (m = n)")

    def _llenar(self, A, b):
        n = len(A[0])
        for i, fila in enumerate(A):
            for j, valor in enumerate(fila):
                self.tabla.item(i, j).setText(valor)
            self.tabla.item(i, n).setText(b[i])

    def _cargar_ejemplo_defecto(self):
        """Carga una matriz estándar por defecto."""
        _, A, b = EJEMPLOS[0]
        self._llenar(A, b)

    def _cargar_ejemplo(self, idx):
        """Carga ejemplos de prueba en la interfaz."""
        if idx <= 0:
            return
        _, A, b = EJEMPLOS[idx - 1]
        self._cargando_ejemplo = True
        self.spin_m.setValue(len(A))
        self.spin_n.setValue(len(A[0]))
        self._cargando_ejemplo = False
        self._llenar(A, b)
        self._limpiar_consola()

    def _leer(self):
        """Devuelve (A, b) desde la tabla aumentada, o None si hay errores."""
        self.tabla.terminar_edicion()
        m, n = self.spin_m.value(), self.spin_n.value()
        aumentada, errores = leer_matriz_segura(self.tabla, m, n + 1, "[A|b]")
        if errores:
            self.res.resumen.mostrar("error", "Error en los datos")
            QMessageBox.critical(self, "Error en los datos", "\n".join(errores))
            return None
        return [fila[:n] for fila in aumentada], [fila[n] for fila in aumentada]

    # ── FACTORIZAR A = LU ───────────────────────────────────────────

    def _ejecutar_factorizacion(self):
        """Calcula únicamente la factorización A = LU con evolución paso a paso."""
        datos = self._leer()
        if datos is None:
            return
        matriz_A, _ = datos
        m, n = self.spin_m.value(), self.spin_n.value()
        frac = self.chk_frac.isChecked()
        self._ultima_accion = "factorizar"

        matriz_L, matriz_U, pasos, err_lu = factorizacion_lu(matriz_A, m, n, frac)

        lineas = [
            SEP,
            "                 1. FACTORIZACIÓN DE MATRIZ: A = L · U",
            SEP,
            ""
        ]
        lineas.extend(pasos)

        if err_lu:
            lineas.append("\n" + SEP)
            lineas.append(f"ALERTA: {err_lu}")
            lineas.append(SEP)
            self.ultima_matriz_L = None
            self.ultima_matriz_U = None
            self.matriz_A_factorizada = None
            self.res.resumen.mostrar("aviso", "No admite LU sin intercambios", "requiere PA = LU")
        else:
            self.ultima_matriz_L = matriz_L
            self.ultima_matriz_U = matriz_U
            self.matriz_A_factorizada = matriz_A
            self.res.resumen.mostrar("ok", "A = L · U", f"L {m}×{m} · U {m}×{n}")

        self.txt_salida.setText("\n".join(lineas))

    # ── RESOLVER Ax = b CON LU ──────────────────────────────────────

    def _ejecutar_resolucion(self):
        """Resuelve el sistema Ax = b utilizando la factorización LU en dos etapas."""
        m, n = self.spin_m.value(), self.spin_n.value()
        frac = self.chk_frac.isChecked()

        if m != n:
            QMessageBox.warning(
                self, "Dimensiones no cuadradas",
                "Para resolver el sistema Ax = b con factorización LU, "
                "la matriz debe ser cuadrada (m = n)."
            )
            return

        datos = self._leer()
        if datos is None:
            return
        matriz_A, vector_b = datos

        # Si no se ha factorizado la matriz actual, se factoriza primero
        if (self.ultima_matriz_L is None or self.matriz_A_factorizada != matriz_A):
            matriz_L, matriz_U, _, err_lu = factorizacion_lu(matriz_A, m, n, frac)
            if err_lu:
                self.res.resumen.mostrar("aviso", "No admite LU sin intercambios", "requiere PA = LU")
                QMessageBox.critical(self, "Error en Factorización", err_lu)
                return
            self.ultima_matriz_L = matriz_L
            self.ultima_matriz_U = matriz_U
            self.matriz_A_factorizada = matriz_A

        vector_y, vector_x, pasos_sol, err_sol = resolver_sistema_lu(
            self.ultima_matriz_L, self.ultima_matriz_U, vector_b, n, frac
        )

        if err_sol:
            self.res.resumen.mostrar("error", "No se pudo resolver")
            QMessageBox.critical(self, "Error al resolver sistema", err_sol)
            return

        es_exacta, _, pasos_verif = verificar_solucion_ax_b(matriz_A, vector_x, vector_b, n, frac)
        self._ultima_accion = "resolver"

        lineas = []
        lineas.extend(pasos_sol)
        lineas.append("")
        lineas.extend(pasos_verif)

        texto_actual = self.txt_salida.toPlainText().strip()
        if texto_actual and "1. FACTORIZACIÓN" in texto_actual:
            self.txt_salida.append("\n\n" + "\n".join(lineas))
        else:
            self.txt_salida.setText("\n".join(lineas))

        self.res.resumen.mostrar("ok" if es_exacta else "aviso",
                                 "Solución" + ("  ·  A·x = b" if es_exacta else ""),
                                 "   ".join(f"{nombre_var(i)} = {formato_numero(vector_x[i], frac)}"
                                            for i in range(n)))
