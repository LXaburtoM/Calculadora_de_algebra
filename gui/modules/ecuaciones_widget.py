"""
Módulo 1: Interfaz Gráfica para Sistemas de Ecuaciones.
Tema: Resolución de SEL por Gauss y Gauss-Jordan con paso a paso (Sesiones 1-5).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QToolButton, QTextEdit, QTextBrowser,
    QMessageBox, QComboBox, QSplitter, QMenu, QApplication
)
from PyQt6.QtGui import QActionGroup
from PyQt6.QtCore import Qt, QSize
from fractions import Fraction
from core.parser import parse_expresion, formato_numero
from core.eliminacion_gaussiana import (
   reducir_por_filas, resolver_por_gauss, analizar_forma, clasificar_sistema,
    solucion_general, forma_vectorial, verificar_solucion, verificar_homogenea,
    nombre_var, entradas_principales
)
from core.modelos_aplicados import MODELOS
from gui.componentes import BotonIcono, PestanasSegmentadas, Tarjeta, icono
from gui.entrada import (
    SelectorDimension, SelectorFormato, TablaMatriz, TecladoMatematico, Resumen, grupo_dimensiones
)

ANCHO_MIN = 5
SEP = "-" * 78

METODOS = {"gauss": "Gauss", "gauss_jordan": "Gauss-Jordan"}


class EcuacionesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.metodo = "gauss_jordan"
        self._ultima_accion = None
        self._crear_barra()
        self.init_ui()

    # ── Barra superior del módulo (la coloca MainWindow) ─────────────

    def _crear_barra(self):
        self.barra_izq = QWidget()
        lay = QHBoxLayout(self.barra_izq)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        self.spin_m = SelectorDimension(3, "Ecuaciones (filas)")
        self.spin_n = SelectorDimension(3, "Variables (columnas)")
        lay.addWidget(grupo_dimensiones([self.spin_m, "×", self.spin_n]))

        self.combo_modelos = QComboBox()
        self.combo_modelos.setToolTip("Plantillas de modelos aplicados")
        self.combo_modelos.addItem("Ejemplos")
        for m in MODELOS:
            self.combo_modelos.addItem(m["nombre"])
        self.combo_modelos.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_modelos.setMinimumContentsLength(12)
        self.combo_modelos.view().setMinimumWidth(380)
        self.combo_modelos.setFixedHeight(32)
        lay.addWidget(self.combo_modelos)

        # Acción principal con menú de métodos
        self.barra_der = QWidget()
        rl = QHBoxLayout(self.barra_der)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)
        self.btn_resolver = QPushButton(METODOS[self.metodo])
        self.btn_resolver.setObjectName("SplitMain")
        self.btn_resolver.setToolTip("Resolver (Ctrl+Enter)")
        self.btn_resolver.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_resolver.clicked.connect(self.accion_principal)
        self.btn_metodos = QToolButton()
        self.btn_metodos.setObjectName("SplitMenu")
        self.btn_metodos.setToolTip("Elegir método")
        self.btn_metodos.setIconSize(QSize(12, 12))
        self.btn_metodos.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_metodos.setCursor(Qt.CursorShape.PointingHandCursor)

        menu = QMenu(self.btn_metodos)
        grupo = QActionGroup(menu)
        self.acciones_metodo = {}
        for clave, nombre in METODOS.items():
            acc = menu.addAction(f"Resolver por {nombre}")
            acc.setCheckable(True)
            acc.setChecked(clave == self.metodo)
            acc.triggered.connect(lambda _, k=clave: self._elegir_metodo(k))
            grupo.addAction(acc)
            self.acciones_metodo[clave] = acc
        menu.addSeparator()
        menu.addAction("¿Está en forma escalonada?", self.analizar_forma_actual)
        self.btn_metodos.setMenu(menu)

        rl.addWidget(self.btn_resolver)
        rl.addWidget(self.btn_metodos)

    def barra_contexto(self):
        return self.barra_izq, self.barra_der

    def accion_principal(self):
        self.resolver_sistema(metodo=self.metodo)

    def _elegir_metodo(self, clave):
        self.metodo = clave
        self.btn_resolver.setText(METODOS[clave])
        self.resolver_sistema(metodo=clave)

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
        izq.addWidget(self._crear_tarjeta_matriz(), 1)
        self.teclado = TecladoMatematico()
        self.teclado.registrar(self.tabla)
        self.teclado.fin_de_entrada.connect(self.accion_principal)
        izq.addStretch(0)
        izq.addWidget(self.teclado, 1)

        divisor.addWidget(izquierda)
        divisor.addWidget(self._crear_tarjeta_resultados())
        divisor.setSizes([600, 600])
        layout.addWidget(divisor)

        self.spin_m.valueChanged.connect(self.actualizar_tabla)
        self.spin_n.valueChanged.connect(self.actualizar_tabla)
        self.combo_modelos.currentIndexChanged.connect(self.cargar_modelo_seleccionado)
        self.actualizar_tabla()

    def _crear_tarjeta_matriz(self):
        tarjeta = Tarjeta("[A | b]")
        tarjeta.setToolTip("Acepta enteros, decimales, fracciones (1/2) y funciones (pi, sen, cos…)")
        self.btn_limpiar = BotonIcono("borrar", "Limpiar tabla", 16)
        self.btn_limpiar.clicked.connect(self.limpiar_tabla)
        tarjeta.agregar_a_cabecera(self.btn_limpiar)

        self.tabla = TablaMatriz(expandir=True)
        tarjeta.lay.addWidget(self.tabla)

        # Enunciado del modelo aplicado (visible al elegir un ejemplo)
        self.lbl_modelo_info = QTextBrowser()
        self.lbl_modelo_info.setObjectName("ModelInfo")
        self.lbl_modelo_info.setMaximumHeight(150)
        self.lbl_modelo_info.setVisible(False)
        tarjeta.lay.addWidget(self.lbl_modelo_info)
        return tarjeta

    def _crear_tarjeta_resultados(self):
        tarjeta = Tarjeta()
        self.tabs = PestanasSegmentadas()
        self.txt_pasos = self._nueva_pestania("Pasos")
        self.txt_formas = self._nueva_pestania("Pivotes")
        self.txt_analisis = self._nueva_pestania("Existencia")
        self.txt_verif = self._nueva_pestania("Verificación")
        tarjeta.cabecera.addWidget(self.tabs.crear_control())
        tarjeta.cabecera.addStretch()

        self.chk_fracciones = SelectorFormato()
        self.chk_fracciones.cambiado.connect(self._repetir_ultima_accion)
        tarjeta.cabecera.addWidget(self.chk_fracciones)

        self.btn_copiar = BotonIcono("copiar", "Copiar pestaña actual", 16)
        self.btn_copiar.clicked.connect(self._copiar_resultado)
        tarjeta.cabecera.addWidget(self.btn_copiar)

        self.resumen = Resumen()
        tarjeta.lay.addWidget(self.resumen)

        tarjeta.lay.addWidget(self.tabs, 1)
        return tarjeta

    def _nueva_pestania(self, titulo):
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.tabs.addTab(txt, titulo)
        return txt

    def aplicar_tema(self, paleta):
        for b in (self.btn_limpiar, self.btn_copiar):
            b.aplicar_tema(paleta)
        self.btn_metodos.setIcon(icono("chevron", "#FFFFFF", 12))
        self.teclado.aplicar_tema(paleta)

    # ── Resultados ──────────────────────────────────────────────────

    def _mostrar_resumen(self, estado, titulo, valor=""):
        self.resumen.mostrar(estado, titulo, valor)

    def _limpiar_resultados(self):
        """Los resultados dejan de valer cuando cambia la matriz de entrada."""
        self._ultima_accion = None
        self.resumen.setVisible(False)
        for txt in (self.txt_pasos, self.txt_formas, self.txt_analisis, self.txt_verif):
            txt.clear()

    def _repetir_ultima_accion(self):
        if self._ultima_accion == "forma":
            self.analizar_forma_actual()
        elif self._ultima_accion:
            self.resolver_sistema(metodo=self._ultima_accion)

    def _copiar_resultado(self):
        actual = self.tabs.currentWidget()
        if actual is not None:
            QApplication.clipboard().setText(actual.toPlainText())

    # ── Datos de la tabla ───────────────────────────────────────────

    def actualizar_tabla(self):
        m = self.spin_m.value()
        n = self.spin_n.value()
        self.tabla.redimensionar(m, n + 1, [nombre_var(j) for j in range(n)] + ["b"],
                                 [f"R{i + 1}" for i in range(m)])
        self._limpiar_resultados()

    def limpiar_tabla(self):
        self.tabla.limpiar()
        self._mostrar_info(False)
        self.combo_modelos.setCurrentIndex(0)
        self._limpiar_resultados()

    def _mostrar_info(self, visible):
        self.lbl_modelo_info.setVisible(visible)
        self.tabla.parentWidget().ajustar_a_contenido()

    def cargar_modelo_seleccionado(self, idx):
        if idx <= 0:
            self._mostrar_info(False)
            return

        modelo = MODELOS[idx - 1]
        self.spin_m.setValue(modelo["m"])
        self.spin_n.setValue(modelo["n"])

        for i in range(modelo["m"]):
            for j in range(modelo["n"] + 1):
                val = modelo["matriz"][i][j]
                self.tabla.item(i, j).setText(formato_numero(val, True))

        info_text = (
            f"<b>{modelo['nombre']}</b><br>"
            f"{modelo['descripcion']}<br><br>"
            f"<b>Variables:</b> {', '.join(modelo['variables'])}<br>"
            f"<b>Ecuaciones del modelo:</b><br>• " + "<br>• ".join(modelo["ecuaciones"])
        ).replace("\n", "<br>")
        self.lbl_modelo_info.setHtml(info_text)
        self._mostrar_info(True)
        self._limpiar_resultados()

    def leer_matriz(self):
        self.tabla.terminar_edicion()
        m = self.spin_m.value()
        n = self.spin_n.value()
        matriz = []
        errores = []

        for i in range(m):
            fila = []
            for j in range(n + 1):
                item = self.tabla.item(i, j)
                texto = item.text() if item else "0"
                valor, err = parse_expresion(texto)
                if err:
                    col_nombre = nombre_var(j) if j < n else "b"
                    errores.append(f"• Fila {i + 1}, columna '{col_nombre}': {err}")
                    fila.append(Fraction(0))
                else:
                    fila.append(valor)
            matriz.append(fila)

        if errores:
            return None, errores
        return matriz, None

    def _mostrar_errores(self, errores):
        plural = "s" if len(errores) > 1 else ""
        self._mostrar_resumen("error", f"Revisa {len(errores)} celda{plural}")
        msg = "Se encontraron errores en las celdas ingresadas:\n\n" + "\n".join(errores)
        QMessageBox.critical(self, "Error en los Datos", msg)

    # ── Análisis ────────────────────────────────────────────────────

    def analizar_forma_actual(self):
        self._ultima_accion = "forma"
        matriz, errores = self.leer_matriz()
        if errores:
            self._mostrar_errores(errores)
            return

        m = self.spin_m.value()
        n = self.spin_n.value()
        frac = self.chk_fracciones.isChecked()

        analisis = analizar_forma(matriz, m, n + 1)
        principales = analisis["principales"]

        lineas = [
            "ANÁLISIS DE FORMA ESCALONADA DE LA MATRIZ INGRESADA",
            SEP,
            "Matriz evaluada:",
            self._render_matriz(matriz, m, n + 1, principales, frac),
            "",
            "Entradas principales (el primer elemento no nulo de cada fila):",
        ]

        if principales:
            for fila in sorted(principales.keys()):
                col = principales[fila]
                val = formato_numero(matriz[fila][col], frac)
                col_nom = nombre_var(col) if col < n else "b (columna aumentada)"
                lineas.append(f"  • Fila {fila + 1}: valor {val} en columna {col_nom}")
        else:
            lineas.append("  (la matriz es completamente nula)")

        lineas.append("")
        lineas.append("Evaluación de las 5 propiedades formales (Lay, §1.2):")
        for num, desc, cumple, detalle in analisis["propiedades"]:
            simb = "✔" if cumple else "✘"
            lineas.append(f"  [{simb}] Propiedad {num}: {desc}")
            lineas.append(f"      -> {detalle}")

        lineas.append("")
        lineas.append(SEP)
        if analisis["reducida"]:
            lineas.append("DICTAMEN: La matriz está en FORMA ESCALONADA REDUCIDA (RREF).")
            self._mostrar_resumen("ok", "Forma escalonada reducida", "RREF")
        elif analisis["escalonada"]:
            lineas.append("DICTAMEN: La matriz está en FORMA ESCALONADA (REF), pero no reducida.")
            self._mostrar_resumen("aviso", "Forma escalonada, no reducida", "REF")
        else:
            lineas.append("DICTAMEN: La matriz NO está en forma escalonada.")
            self._mostrar_resumen("error", "No está en forma escalonada")
        lineas.append(SEP)

        self.txt_formas.setText("\n".join(lineas))
        self.tabs.setCurrentWidget(self.txt_formas)

    def resolver_sistema(self, metodo="gauss_jordan"):
        self._ultima_accion = metodo
        matriz, errores = self.leer_matriz()
        if errores:
            self._mostrar_errores(errores)
            return

        m = self.spin_m.value()
        n = self.spin_n.value()
        frac = self.chk_fracciones.isChecked()

        # 1. PESTAÑA 1: PROCEDIMIENTO PASO A PASO
        if metodo == "gauss":
            res_gauss = resolver_por_gauss(matriz, m, n, modo_fraccion=frac)
            resultado = res_gauss["resultado_base"]
            pasos_a_mostrar = res_gauss["pasos_gauss"]
            titulo_metodo = "MÉTODO DE ELIMINACIÓN DE GAUSS (Escalonamiento + Sustitución Hacia Atrás)"
        else:
            resultado = reducir_por_filas(matriz, m, n, modo_fraccion=frac, detener_si_inconsistente=True)
            pasos_a_mostrar = resultado["pasos"]
            titulo_metodo = "MÉTODO DE GAUSS-JORDAN (Fase Progresiva + Fase Regresiva a RREF)"

        pivotes_dict = {f: c for (f, c) in resultado["pivotes"]}

        lineas_pasos = [
            titulo_metodo,
            SEP,
            "Aritmética exacta con fracciones — sin redondeo.",
            "",
        ]

        for k, p in enumerate(pasos_a_mostrar, start=1):
            lineas_pasos.append(f"Paso {k}: {p['titulo']}")
            lineas_pasos.append(f"  {p['descripcion']}")
            pivs_hasta_ahora = pivotes_dict if p["fase"] in ("HITO_REF", "REGRESIVA", "HITO_RREF") else None
            lineas_pasos.append(self._render_matriz(p["matriz"], m, n + 1, pivs_hasta_ahora, frac))
            lineas_pasos.append("")

        if metodo == "gauss" and res_gauss["pasos_sustitucion"]:
            lineas_pasos.extend(res_gauss["pasos_sustitucion"])

        self.txt_pasos.setText("\n".join(lineas_pasos))

        # 2. PESTAÑA 2: FORMAS ESCALONADAS Y PIVOTES
        lineas_formas = [
            "IDENTIFICACIÓN DE PIVOTES Y FORMAS ESCALONADAS",
            SEP,
            "1. FORMA ESCALONADA (REF) — resultado de la fase progresiva:",
            self._render_matriz(resultado["ref"], m, n + 1, pivotes_dict, frac),
            "",
        ]

        if resultado["rref"] is not None:
            rref_principales = entradas_principales(resultado["rref"], m, n + 1)
            lineas_formas.extend([
                "2. FORMA ESCALONADA REDUCIDA (RREF) — resultado de la fase regresiva:",
                self._render_matriz(resultado["rref"], m, n + 1, rref_principales, frac),
                "",
            ])

        cols_piv = [c for c in resultado["cols_pivote"] if c < n]
        libres = [j for j in range(n) if j not in cols_piv]

        lineas_formas.extend([
            "3. POSICIONES Y COLUMNAS PIVOTE:",
            f"  • Posiciones pivote (fila, columna): " + (", ".join(f"(R{f+1}, {nombre_var(c) if c < n else 'b'})" for (f, c) in resultado["pivotes"]) if resultado["pivotes"] else "ninguna"),
            f"  • Columnas pivote de A: " + (", ".join(nombre_var(c) for c in cols_piv) if cols_piv else "ninguna"),
            f"  • Columnas libres (variables libres): " + (", ".join(nombre_var(j) for j in libres) if libres else "ninguna (todas son básicas)"),
            f"  • Rango de A: {len(cols_piv)}  (número de pivotes en la matriz de coeficientes)",
        ])
        self.txt_formas.setText("\n".join(lineas_formas))

        # 3. PESTAÑA 3: EXISTENCIA Y UNICIDAD
        clasif = clasificar_sistema(resultado, m, n)
        lineas_analisis = [
            "ANÁLISIS DE EXISTENCIA Y UNICIDAD (Lay, §1.2, Teorema 2)",
            SEP,
            f"Clasificación: {clasif['tipo']} — {clasif['mensaje']}",
            "",
            "Fundamentación teórica:",
            f"  {clasif['detalle']}",
            "",
        ]

        if resultado["consistente"] and resultado["rref"] is not None:
            despejes = solucion_general(resultado["rref"], m, n, resultado["pivotes"])
            lineas_analisis.append("Solución general (variables básicas despejadas):")
            for d in despejes:
                v = nombre_var(d["var"])
                if d["libre"]:
                    lineas_analisis.append(f"  • {v} es libre  ({v} ∈ ℝ)")
                else:
                    c_str = formato_numero(d["const"], frac)
                    parts = []
                    if d["const"] != 0 or not d["coefs"]:
                        parts.append(c_str)
                    for k_col, coef in d["coefs"].items():
                        c_k = formato_numero(coef, frac)
                        vk = nombre_var(k_col)
                        if coef == 1:
                            parts.append(f"+ {vk}")
                        elif coef == -1:
                            parts.append(f"− {vk}")
                        elif coef > 0:
                            parts.append(f"+ ({c_k})·{vk}")
                        else:
                            parts.append(f"− ({formato_numero(abs(coef), frac)})·{vk}")
                    lineas_analisis.append(f"  • {v} = " + " ".join(parts).lstrip("+ "))

            lineas_analisis.append("")
            p_vec, dirs = forma_vectorial(despejes, n, libres)
            lineas_analisis.append("Forma vectorial paramétrica:  x = p + Σ t_k · v_k")
            lineas_analisis.append(self._render_forma_vectorial(p_vec, dirs, n, frac))

        self.txt_analisis.setText("\n".join(lineas_analisis))

        # Resumen de una línea
        if clasif["tipo"] == "INCONSISTENTE":
            self._mostrar_resumen("error", "Sin solución", f"0 = {formato_numero(resultado['ref'][resultado['fila_contradiccion']][n], frac)}")
        elif clasif["tipo"] == "INDETERMINADO":
            self._mostrar_resumen("aviso", "Infinitas soluciones",
                                  "libres: " + ", ".join(nombre_var(j) for j in clasif["libres"]))
        else:
            despejes = solucion_general(resultado["rref"], m, n, resultado["pivotes"])
            self._mostrar_resumen("ok", "Solución única",
                                  "   ".join(f"{nombre_var(d['var'])} = {formato_numero(d['const'], frac)}" for d in despejes))

        # 4. PESTAÑA 4: VERIFICACIÓN
        lineas_verif = [
            "VERIFICACIÓN DE LA SOLUCIÓN POR SUSTITUCIÓN",
            SEP,
        ]

        if not resultado["consistente"]:
            lineas_verif.append("El sistema es INCONSISTENTE. No existe solución que sustituir.")
        elif resultado["rref"] is not None:
            despejes = solucion_general(resultado["rref"], m, n, resultado["pivotes"])
            sol_particular = [d["const"] for d in despejes]
            res_part = verificar_solucion(matriz, sol_particular, m, n)

            lineas_verif.append("1. Comprobación de la solución particular p (con todas las variables libres = 0):")
            lineas_verif.append("   Vector probado p = [" + ", ".join(formato_numero(x, frac) for x in sol_particular) + "]ᵀ")
            lineas_verif.append("")
            for r in res_part:
                simb = "✔ OK" if r["correcto"] else "✘ FALLA"
                lineas_verif.append(f"  [{simb}] {r['ecuacion']}: {r['expresion']} (esperado: {r['esperado']})")

            p_vec, dirs = forma_vectorial(despejes, n, libres)
            if dirs:
                lineas_verif.append("")
                lineas_verif.append("2. Comprobación de los vectores dirección v_k (deben cumplir A · v_k = 0):")
                for k_col, v in dirs:
                    lineas_verif.append(f"  Vector asociado a variable libre {nombre_var(k_col)}:")
                    res_h = verificar_homogenea(matriz, v, m, n)
                    for r in res_h:
                        simb = "✔ OK" if r["correcto"] else "✘ FALLA"
                        lineas_verif.append(f"    [{simb}] {r['ecuacion']}: valor = {r['valor']} (esperado: 0)")

        self.txt_verif.setText("\n".join(lineas_verif))
        self.tabs.setCurrentWidget(self.txt_pasos)

    def _render_matriz(self, matriz, m, n_cols, pivotes=None, modo_fraccion=True):
        ancho = 0
        celdas = []
        for i in range(m):
            fila_strs = []
            for j in range(n_cols):
                s = formato_numero(matriz[i][j], modo_fraccion)
                if pivotes and i in pivotes and pivotes[i] == j:
                    s = f"[{s}]"
                fila_strs.append(s)
                ancho = max(ancho, len(s))
            celdas.append(fila_strs)

        ancho = max(ancho, ANCHO_MIN)
        lineas = []
        for i in range(m):
            coefs = "  ".join(celdas[i][j].rjust(ancho) for j in range(n_cols - 1))
            b_str = celdas[i][-1].rjust(ancho)
            lineas.append(f"  │  {coefs}  │  {b_str}  │")
        return "\n".join(lineas)

    def _render_forma_vectorial(self, p, dirs, n, modo_fraccion):
        p_strs = [formato_numero(x, modo_fraccion) for x in p]
        dir_strs = [[formato_numero(v[i], modo_fraccion) for i in range(n)] for (_, v) in dirs]

        ancho_p = max(len(s) for s in p_strs)
        anchos_d = [max(len(d[i]) for i in range(n)) for d in dir_strs] if dirs else []

        lineas = []
        for i in range(n):
            var_nom = nombre_var(i).rjust(3)
            p_val = p_strs[i].rjust(ancho_p)
            fila = f"  │ {var_nom} │   =   │ {p_val} │"
            for k, (col_libre, _) in enumerate(dirs):
                d_val = dir_strs[k][i].rjust(anchos_d[k])
                vk_nom = nombre_var(col_libre)
                fila += f"   +   {vk_nom} · │ {d_val} │"
            lineas.append(fila)
        return "\n".join(lineas)
