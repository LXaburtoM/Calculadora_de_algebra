"""
Módulo 6: Verificador Completo de Propiedades de Matrices y Determinantes.
Tema: Cobertura total de teoremas y propiedades requeridas para la Tarea 6.
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QLabel, QMessageBox, QSizePolicy
from PyQt6.QtCore import Qt
from fractions import Fraction
from core.parser import formato_numero, parse_expresion
from core.algebra_avanzada import (
    inversa_matriz, determinante_reduccion, copiar_matriz
)
from core.operaciones_matriciales import (
    sumar_matrices, multiplicar_matrices, transpuesta_matriz, escalar_por_matriz
)
from core.validadores import formatear_matriz, comparar_matrices
from core.eliminacion_gaussiana import nombre_var
from gui.componentes import Tarjeta
from gui.entrada import (
    SelectorDimension, TablaMatriz, leer_matriz_segura, TecladoMatematico, TarjetaResultado,
    grupo_dimensiones, boton_principal, contenedor_fila, pagina_seccion, tarjeta_tabla
)

SEP = "=" * 60
SUBSEP = "-" * 60
VALORES_POR_DEFECTO = {
    "A": [["1", "2"], ["3", "4"]],
    "B": [["2", "1"], ["1", "1"]],
    "C": [["1", "1"], ["0", "2"]],
}


class VerificadorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._crear_barra()
        self.init_ui()

    # ── Barra superior del módulo (la coloca MainWindow) ─────────────

    def _crear_barra(self):
        self.spin_n = SelectorDimension(2, "Dimensión n (matrices n × n)", 6, minimo=2)
        # Filas i, j para las operaciones elementales de la propiedad 15
        self.spin_fi = SelectorDimension(1, "Fila i (operaciones elementales)", 2)
        self.spin_fj = SelectorDimension(2, "Fila j (operaciones elementales)", 2)
        self.barra_izq = contenedor_fila(grupo_dimensiones(["  n =", self.spin_n]))
        self.barra_der = boton_principal("Evaluar 16 propiedades", "Evaluar (Ctrl+Enter)",
                                         self._ejecutar_verificacion)

    def barra_contexto(self):
        return self.barra_izq, self.barra_der

    def accion_principal(self):
        self._ejecutar_verificacion()

    # ── Cuerpo ──────────────────────────────────────────────────────

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Cuadrícula 2 × 2: A y B arriba; C y los parámetros abajo
        self.tabla_A = TablaMatriz(filas_visibles=3, expandir=True)
        self.tabla_B = TablaMatriz(filas_visibles=3, expandir=True)
        self.tabla_C = TablaMatriz(filas_visibles=3, expandir=True)
        cuadricula = QWidget()
        grid = QGridLayout(cuadricula)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)
        for k, (tabla, nombre) in enumerate(((self.tabla_A, "A"), (self.tabla_B, "B"), (self.tabla_C, "C"))):
            grid.addWidget(tarjeta_tabla(nombre, tabla, f"Matriz {nombre} (invertible)"),
                           k // 2, k % 2, Qt.AlignmentFlag.AlignTop)
        grid.addWidget(self._crear_parametros(), 1, 1, Qt.AlignmentFlag.AlignTop)
        # Columnas del mismo ancho sin importar el contenido de cada tarjeta
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        for tarjeta in cuadricula.findChildren(Tarjeta):
            tarjeta.setMinimumWidth(0)
            tarjeta.setSizePolicy(QSizePolicy.Policy.Ignored, tarjeta.sizePolicy().verticalPolicy())

        self.teclado = TecladoMatematico()
        self.teclado.registrar(self.tabla_A, self.tabla_B, self.tabla_C, self.tabla_k)
        self.teclado.fin_de_entrada.connect(self.accion_principal)

        self.res = TarjetaResultado(mensaje_vacio="Los resultados aparecerán aquí al evaluar las propiedades.")
        self.res.formato.cambiado.connect(self._repetir)
        self.chk_frac = self.res.formato
        self.txt_res = self.res.texto
        self.txt_res.setLineWrapMode(self.txt_res.LineWrapMode.NoWrap)

        layout.addWidget(pagina_seccion([], [(cuadricula, 1), (None, 0), (self.teclado, 0)], self.res))

        self.spin_n.valueChanged.connect(self._actualizar_tablas)
        self._actualizar_tablas()
        self._cargar_valores_por_defecto()

    def _crear_parametros(self):
        """Escalar k y filas i, j: solo los usan las propiedades 3, 14 y 15."""
        tarjeta = Tarjeta("Parámetros")
        tarjeta.setToolTip("k: propiedades 3, 14 y 15 · i, j: operaciones de fila de la propiedad 15")
        self.tabla_k = TablaMatriz(filas_visibles=1, encabezado_filas=False)
        self.tabla_k.horizontalHeader().setVisible(False)
        self.tabla_k.redimensionar(1, 1, ["k"], [""])
        self.tabla_k.item(0, 0).setText("3")
        self.tabla_k.setFixedWidth(96)
        etiqueta_k = QLabel("k =")
        etiqueta_k.setObjectName("Muted")
        filas = grupo_dimensiones(["  Filas  i =", self.spin_fi, "  j =", self.spin_fj])

        # k y las filas apiladas: la tarjeta queda tan angosta como las matrices
        fila_k = QHBoxLayout()
        fila_k.setSpacing(8)
        fila_k.addWidget(etiqueta_k)
        fila_k.addWidget(self.tabla_k)
        fila_k.addStretch()
        fila_ij = QHBoxLayout()
        fila_ij.addWidget(filas)
        fila_ij.addStretch()
        tarjeta.lay.addLayout(fila_k)
        tarjeta.lay.addLayout(fila_ij)
        return tarjeta

    def aplicar_tema(self, paleta):
        self.res.aplicar_tema(paleta)
        self.teclado.aplicar_tema(paleta)

    def _repetir(self):
        if self.res.resumen.isVisible() and self.res.resumen.punto.property("estado") != "error":
            self._ejecutar_verificacion()

    def _actualizar_tablas(self):
        """Redimensiona las 3 tablas A, B y C según n."""
        n = self.spin_n.value()
        self.spin_fi.set_maximo(n)
        self.spin_fj.set_maximo(n)
        for tabla in (self.tabla_A, self.tabla_B, self.tabla_C):
            tabla.redimensionar(n, n, [nombre_var(j) for j in range(n)], [f"F{i+1}" for i in range(n)])
        self.res.resumen.setVisible(False)
        self.txt_res.clear()

    def _cargar_valores_por_defecto(self):
        """Carga matrices invertibles predeterminadas para n=2."""
        for tabla, nombre in ((self.tabla_A, "A"), (self.tabla_B, "B"), (self.tabla_C, "C")):
            for i, fila in enumerate(VALORES_POR_DEFECTO[nombre]):
                for j, valor in enumerate(fila):
                    tabla.item(i, j).setText(valor)

    def _error(self, titulo, mensaje):
        self.res.resumen.mostrar("error", titulo)
        QMessageBox.critical(self, titulo, mensaje)

    def _veredicto(self, cumple):
        """Retorna el diagnóstico con el formato de la rúbrica."""
        return "   Diagnóstico: ✔ Se cumple" if cumple else "   Diagnóstico: ✘ No se cumple"

    # ── LÓGICA DE VERIFICACIÓN COMPLETA (16 PROPIEDADES) ─────────────

    def _ejecutar_verificacion(self):
        """Evalúa ambos miembros de cada teorema exigido en la Tarea 6."""
        for tabla in (self.tabla_A, self.tabla_B, self.tabla_C, self.tabla_k):
            tabla.terminar_edicion()
        n = self.spin_n.value()
        frac = self.chk_frac.isChecked()

        A, errA = leer_matriz_segura(self.tabla_A, n, n, "A")
        B, errB = leer_matriz_segura(self.tabla_B, n, n, "B")
        C, errC = leer_matriz_segura(self.tabla_C, n, n, "C")
        k_val, errK = parse_expresion(self.tabla_k.item(0, 0).text())

        errores = errA + errB + errC + ([f"Escalar k: {errK}"] if errK else [])
        if errores:
            return self._error("Error en los datos", "\n".join(errores))

        detA, _ = determinante_reduccion(A)
        detB, _ = determinante_reduccion(B)
        detC, _ = determinante_reduccion(C)

        if detA == 0 or detB == 0:
            return self._error(
                "Error de Invertibilidad",
                "Las matrices A y B deben ser invertibles (det != 0) para evaluar las propiedades de la inversa."
            )

        A_inv, _, _ = inversa_matriz(A, n)
        B_inv, _, _ = inversa_matriz(B, n)
        fi = self.spin_fi.value() - 1
        fj = self.spin_fj.value() - 1

        reporte = [
            SEP,
            "     REPORTE OFICIAL: EVALUACIÓN DEL CONJUNTO COMPLETO DE TEOREMAS",
            SEP,
            ""
        ]

        # ══════════════════════════════════════════════════════════════════
        # CATEGORÍA 1: OPERACIONES Y TRANSPOSICIÓN
        # ══════════════════════════════════════════════════════════════════
        reporte.append("=== CATEGORÍA 1: OPERACIONES Y TRANSPOSICIÓN ===")

        # 1. (Aᵀ)ᵀ = A
        AT, _, _ = transpuesta_matriz(A, n, n)
        AT_T, _, _ = transpuesta_matriz(AT, n, n)
        c1 = comparar_matrices(AT_T, A)
        reporte += [
            "1. Propiedad: (Aᵀ)ᵀ = A",
            self._veredicto(c1),
            "   Miembro Izquierdo (Aᵀ)ᵀ:", formatear_matriz(AT_T, frac),
            "   Miembro Derecho (A):", formatear_matriz(A, frac), SUBSEP
        ]

        # 2. (A + B)ᵀ = Aᵀ + Bᵀ
        A_mas_B, _, _ = sumar_matrices(A, B, n, n, n, n)
        izq_sum, _, _ = transpuesta_matriz(A_mas_B, n, n)
        BT, _, _ = transpuesta_matriz(B, n, n)
        der_sum, _, _ = sumar_matrices(AT, BT, n, n, n, n)
        c2 = comparar_matrices(izq_sum, der_sum)
        reporte += [
            "2. Propiedad: (A + B)ᵀ = Aᵀ + Bᵀ",
            self._veredicto(c2),
            "   Miembro Izquierdo (A + B)ᵀ:", formatear_matriz(izq_sum, frac),
            "   Miembro Derecho (Aᵀ + Bᵀ):", formatear_matriz(der_sum, frac), SUBSEP
        ]

        # 3. (k · A)ᵀ = k · Aᵀ
        kA, _, _ = escalar_por_matriz(k_val, A, n, n)
        izq_kA, _, _ = transpuesta_matriz(kA, n, n)
        der_kA, _, _ = escalar_por_matriz(k_val, AT, n, n)
        c3 = comparar_matrices(izq_kA, der_kA)
        reporte += [
            f"3. Propiedad: (k · A)ᵀ = k · Aᵀ  [k = {formato_numero(k_val, frac)}]",
            self._veredicto(c3),
            "   Miembro Izquierdo (k · A)ᵀ:", formatear_matriz(izq_kA, frac),
            "   Miembro Derecho (k · Aᵀ):", formatear_matriz(der_kA, frac), SUBSEP
        ]

        # 4. (A · B)ᵀ = Bᵀ · Aᵀ
        AB, _, _ = multiplicar_matrices(A, B, n, n, n)
        izq_AB_T, _, _ = transpuesta_matriz(AB, n, n)
        der_BT_AT, _, _ = multiplicar_matrices(BT, AT, n, n, n)
        c4 = comparar_matrices(izq_AB_T, der_BT_AT)
        reporte += [
            "4. Propiedad: (A · B)ᵀ = Bᵀ · Aᵀ",
            self._veredicto(c4),
            "   Miembro Izquierdo (A · B)ᵀ:", formatear_matriz(izq_AB_T, frac),
            "   Miembro Derecho (Bᵀ · Aᵀ):", formatear_matriz(der_BT_AT, frac), SUBSEP
        ]

        # 5. A(B + C) = A·B + A·C
        B_mas_C, _, _ = sumar_matrices(B, C, n, n, n, n)
        izq_dist, _, _ = multiplicar_matrices(A, B_mas_C, n, n, n)
        AC, _, _ = multiplicar_matrices(A, C, n, n, n)
        der_dist, _, _ = sumar_matrices(AB, AC, n, n, n, n)
        c5 = comparar_matrices(izq_dist, der_dist)
        reporte += [
            "5. Propiedad: A · (B + C) = A · B + A · C",
            self._veredicto(c5),
            "   Miembro Izquierdo A · (B + C):", formatear_matriz(izq_dist, frac),
            "   Miembro Derecho (A·B + A·C):", formatear_matriz(der_dist, frac), SUBSEP
        ]

        # 6. (A · B) · C = A · (B · C)
        izq_asoc, _, _ = multiplicar_matrices(AB, C, n, n, n)
        BC, _, _ = multiplicar_matrices(B, C, n, n, n)
        der_asoc, _, _ = multiplicar_matrices(A, BC, n, n, n)
        c6 = comparar_matrices(izq_asoc, der_asoc)
        reporte += [
            "6. Propiedad: (A · B) · C = A · (B · C)",
            self._veredicto(c6),
            "   Miembro Izquierdo (A · B) · C:", formatear_matriz(izq_asoc, frac),
            "   Miembro Derecho A · (B · C):", formatear_matriz(der_asoc, frac), SUBSEP, ""
        ]

        # ══════════════════════════════════════════════════════════════════
        # CATEGORÍA 2: MATRIZ INVERSA
        # ══════════════════════════════════════════════════════════════════
        reporte.append("=== CATEGORÍA 2: MATRIZ INVERSA ===")

        # 7. (A⁻¹)⁻¹ = A
        A_inv_inv, _, _ = inversa_matriz(A_inv, n)
        c7 = comparar_matrices(A_inv_inv, A)
        reporte += [
            "7. Propiedad: (A⁻¹)⁻¹ = A",
            self._veredicto(c7),
            "   Miembro Izquierdo (A⁻¹)⁻¹:", formatear_matriz(A_inv_inv, frac),
            "   Miembro Derecho (A):", formatear_matriz(A, frac), SUBSEP
        ]

        # 8. (A · B)⁻¹ = B⁻¹ · A⁻¹
        AB_inv, _, _ = inversa_matriz(AB, n)
        Binv_Ainv, _, _ = multiplicar_matrices(B_inv, A_inv, n, n, n)
        c8 = comparar_matrices(AB_inv, Binv_Ainv)
        reporte += [
            "8. Propiedad: (A · B)⁻¹ = B⁻¹ · A⁻¹",
            self._veredicto(c8),
            "   Miembro Izquierdo (A · B)⁻¹:", formatear_matriz(AB_inv, frac),
            "   Miembro Derecho (B⁻¹ · A⁻¹):", formatear_matriz(Binv_Ainv, frac), SUBSEP
        ]

        # 9. (Aᵀ)⁻¹ = (A⁻¹)ᵀ
        AT_inv, _, _ = inversa_matriz(AT, n)
        Ainv_T, _, _ = transpuesta_matriz(A_inv, n, n)
        c9 = comparar_matrices(AT_inv, Ainv_T)
        reporte += [
            "9. Propiedad: (Aᵀ)⁻¹ = (A⁻¹)ᵀ",
            self._veredicto(c9),
            "   Miembro Izquierdo (Aᵀ)⁻¹:", formatear_matriz(AT_inv, frac),
            "   Miembro Derecho (A⁻¹)ᵀ:", formatear_matriz(Ainv_T, frac), SUBSEP
        ]

        # 10. A · A⁻¹ = I
        A_Ainv, _, _ = multiplicar_matrices(A, A_inv, n, n, n)
        I_esp = [[Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)]
        c10 = comparar_matrices(A_Ainv, I_esp)
        reporte += [
            "10. Propiedad: A · A⁻¹ = I (Matriz Identidad)",
            self._veredicto(c10),
            "   Miembro Izquierdo (A · A⁻¹):", formatear_matriz(A_Ainv, frac),
            "   Miembro Derecho (I):", formatear_matriz(I_esp, frac), SUBSEP, ""
        ]

        # ══════════════════════════════════════════════════════════════════
        # CATEGORÍA 3: DETERMINANTES
        # ══════════════════════════════════════════════════════════════════
        reporte.append("=== CATEGORÍA 3: DETERMINANTES ===")

        # 11. det(Aᵀ) = det(A)
        det_AT, _ = determinante_reduccion(AT)
        c11 = (det_AT == detA)
        reporte += [
            "11. Propiedad: det(Aᵀ) = det(A)",
            self._veredicto(c11),
            f"   Miembro Izquierdo det(Aᵀ) = {formato_numero(det_AT, frac)}",
            f"   Miembro Derecho det(A)    = {formato_numero(detA, frac)}", SUBSEP
        ]

        # 12. det(A · B) = det(A) · det(B)
        det_AB, _ = determinante_reduccion(AB)
        der_det_prod = detA * detB
        c12 = (det_AB == der_det_prod)
        reporte += [
            "12. Propiedad: det(A · B) = det(A) · det(B)",
            self._veredicto(c12),
            f"   Miembro Izquierdo det(A · B) = {formato_numero(det_AB, frac)}",
            f"   Miembro Derecho det(A)·det(B) = ({formato_numero(detA, frac)})·({formato_numero(detB, frac)}) "
            f"= {formato_numero(der_det_prod, frac)}", SUBSEP
        ]

        # 13. det(A⁻¹) = 1 / det(A)
        det_Ainv, _ = determinante_reduccion(A_inv)
        der_inv_det = Fraction(1, detA)
        c13 = (det_Ainv == der_inv_det)
        reporte += [
            "13. Propiedad: det(A⁻¹) = 1 / det(A)",
            self._veredicto(c13),
            f"   Miembro Izquierdo det(A⁻¹) = {formato_numero(det_Ainv, frac)}",
            f"   Miembro Derecho 1 / det(A) = 1 / ({formato_numero(detA, frac)}) "
            f"= {formato_numero(der_inv_det, frac)}", SUBSEP
        ]

        # 14. det(k · A) = kⁿ · det(A)
        det_kA, _ = determinante_reduccion(kA)
        der_kn_detA = (k_val ** n) * detA
        c14 = (det_kA == der_kn_detA)
        reporte += [
            f"14. Propiedad: det(k · A) = kⁿ · det(A)  [k = {formato_numero(k_val, frac)}, n = {n}]",
            self._veredicto(c14),
            f"   Miembro Izquierdo det(k · A) = {formato_numero(det_kA, frac)}",
            f"   Miembro Derecho (kⁿ · det(A)) = ({formato_numero(k_val, frac)})^{n} · ({formato_numero(detA, frac)}) "
            f"= {formato_numero(der_kn_detA, frac)}", SUBSEP
        ]

        # 15. Efecto de Operaciones de Fila sobre det(A)
        # a) Permutación
        A_swap = copiar_matriz(A)
        A_swap[fi], A_swap[fj] = A_swap[fj], A_swap[fi]
        det_swap, _ = determinante_reduccion(A_swap)
        c15_a = (det_swap == -detA)

        # b) Multiplicación por k
        A_scale = copiar_matriz(A)
        A_scale[fi] = [A_scale[fi][c] * k_val for c in range(n)]
        det_scale, _ = determinante_reduccion(A_scale)
        c15_b = (det_scale == detA * k_val)

        # c) Reemplazo de fila
        c15_c = True
        det_rep = detA
        if fi != fj:
            A_rep = copiar_matriz(A)
            A_rep[fi] = [A_rep[fi][c] + k_val * A_rep[fj][c] for c in range(n)]
            det_rep, _ = determinante_reduccion(A_rep)
            c15_c = (det_rep == detA)

        reporte += [
            "15. Propiedad: Efecto de Operaciones de Fila sobre det(A)",
            f"   • a) Intercambio F{fi+1} ↔ F{fj+1} (Cambia signo): "
            f"det={formato_numero(det_swap, frac)} vs esperado={formato_numero(-detA, frac)}",
            self._veredicto(c15_a),
            f"   • b) Escalar F{fi+1} por k={formato_numero(k_val, frac)}: "
            f"det={formato_numero(det_scale, frac)} vs esperado={formato_numero(detA * k_val, frac)}",
            self._veredicto(c15_b),
            f"   • c) Reemplazo F{fi+1} ← F{fi+1} + ({formato_numero(k_val, frac)})·F{fj+1} (Conserva det): "
            f"det={formato_numero(det_rep, frac)} vs esperado={formato_numero(detA, frac)}",
            self._veredicto(c15_c), SUBSEP
        ]

        # 16. det(triangular) = producto de elementos diagonales
        mat_tri = copiar_matriz(A)
        intercambios = 0
        for i in range(n):
            p = i
            while p < n and mat_tri[p][i] == 0:
                p += 1
            if p == n:
                continue
            if p != i:
                mat_tri[i], mat_tri[p] = mat_tri[p], mat_tri[i]
                intercambios += 1
            for j in range(i + 1, n):
                factor = mat_tri[j][i] / mat_tri[i][i]
                for c in range(i, n):
                    mat_tri[j][c] -= factor * mat_tri[i][c]

        prod_diag = Fraction(1)
        diag_str = []
        for i in range(n):
            prod_diag *= mat_tri[i][i]
            diag_str.append(f"({formato_numero(mat_tri[i][i], frac)})")

        signo = -1 if intercambios % 2 != 0 else 1
        det_tri_calc = prod_diag * signo
        c16 = (det_tri_calc == detA)

        reporte += [
            "16. Propiedad: Determinante de Matriz Triangular = Producto de la Diagonal",
            self._veredicto(c16),
            "   Matriz Triangular Superior obtenida:", formatear_matriz(mat_tri, frac),
            f"   Producto diagonal: {' · '.join(diag_str)} = {formato_numero(prod_diag, frac)}",
            f"   Con {intercambios} intercambio(s): {formato_numero(det_tri_calc, frac)} "
            f"(det(A) original = {formato_numero(detA, frac)})", SEP
        ]

        self.txt_res.setText("\n".join(reporte))

        # Resumen: la propiedad 15 cuenta como cumplida si se cumplen sus tres casos
        resultados = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14,
                      c15_a and c15_b and c15_c, c16]
        cumplidas = sum(resultados)
        fallan = [str(i + 1) for i, ok in enumerate(resultados) if not ok]
        self.res.resumen.mostrar("ok" if not fallan else "aviso",
                                 f"{cumplidas} de 16 propiedades se cumplen",
                                 "" if not fallan else "no se cumple: " + ", ".join(fallan))
