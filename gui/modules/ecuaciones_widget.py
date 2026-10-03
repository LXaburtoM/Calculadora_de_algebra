"""
Módulo de Interfaz Gráfica para la Solución de Sistemas de Ecuaciones Lineales.
Soporta:
- Separación explícita: Método de Gauss vs Método de Gauss-Jordan.
- Modelos Aplicados (Asignación de Recursos, Flujo de Redes de Tráfico, Inversión).
- Verificación de Forma Escalonada (5 Propiedades de Lay).
- Entrada flexible (Fracciones 1/2, decimales, constantes pi, sen, cos, etc.).
- Procedimiento paso a paso detallado y verificación automática.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QCheckBox,
    QTextEdit, QMessageBox, QGroupBox, QHeaderView, QTabWidget,
    QComboBox
)
from PyQt6.QtCore import Qt
from fractions import Fraction
from core.parser import parse_expresion, formato_numero
from core.eliminacion_gaussiana import (
   reducir_por_filas, resolver_por_gauss, analizar_forma, clasificar_sistema,
    solucion_general, forma_vectorial, verificar_solucion, verificar_homogenea,
    nombre_var, entradas_principales
)
from core.modelos_aplicados import MODELOS

ANCHO_MIN = 5
SEP = "-" * 78

class EcuacionesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- PANEL SUPERIOR: CONFIGURACIÓN Y MODELOS APLICADOS ---
        top_layout = QHBoxLayout()

        config_box = QGroupBox("1. Configuración del Sistema")
        config_layout = QHBoxLayout(config_box)

        config_layout.addWidget(QLabel("Ecuaciones (m):"))
        self.spin_m = QSpinBox()
        self.spin_m.setRange(1, 10)
        self.spin_m.setValue(3)
        self.spin_m.valueChanged.connect(self.actualizar_tabla)
        config_layout.addWidget(self.spin_m)

        config_layout.addWidget(QLabel("Variables (n):"))
        self.spin_n = QSpinBox()
        self.spin_n.setRange(1, 10)
        self.spin_n.setValue(3)
        self.spin_n.valueChanged.connect(self.actualizar_tabla)
        config_layout.addWidget(self.spin_n)

        self.chk_fracciones = QCheckBox("Mostrar como Fracciones (ej: 1/2)")
        self.chk_fracciones.setChecked(True)
        config_layout.addWidget(self.chk_fracciones)

        btn_limpiar = QPushButton("Limpiar Tabla")
        btn_limpiar.clicked.connect(self.limpiar_tabla)
        config_layout.addWidget(btn_limpiar)

        top_layout.addWidget(config_box, 2)

        # Modelos Aplicados
        modelos_box = QGroupBox("Plantillas de Modelos Aplicados")
        modelos_layout = QHBoxLayout(modelos_box)

        self.combo_modelos = QComboBox()
        self.combo_modelos.addItem("-- Seleccionar Problema Real --")
        for m in MODELOS:
            self.combo_modelos.addItem(m["nombre"])
        self.combo_modelos.currentIndexChanged.connect(self.cargar_modelo_seleccionado)
        modelos_layout.addWidget(self.combo_modelos)

        top_layout.addWidget(modelos_box, 1)
        layout.addLayout(top_layout)

        # Cuadro de descripción de modelo aplicado (oculto por defecto)
        self.lbl_modelo_info = QLabel("")
        self.lbl_modelo_info.setStyleSheet("color: #38BDF8; background-color: #0F172A; border: 1px solid #334155; border-radius: 6px; padding: 8px;")
        self.lbl_modelo_info.setWordWrap(True)
        self.lbl_modelo_info.setVisible(False)
        layout.addWidget(self.lbl_modelo_info)

        # --- TABLA MATRIZ AUMENTADA ---
        tabla_box = QGroupBox("2. Matriz Aumentada [A | b]  (Acepta enteros, decimales, fracciones 1/2 y constantes como pi, sen, cos)")
        tabla_layout = QVBoxLayout(tabla_box)

        self.tabla = QTableWidget()
        tabla_layout.addWidget(self.tabla)

        botones_layout = QHBoxLayout()

        # Botón Gauss
        btn_gauss = QPushButton("▶ Resolver por MÉTODO DE GAUSS (Escalonada + Sustitución)")
        btn_gauss.setStyleSheet("background-color: #059669; color: white; font-weight: bold; padding: 8px;")
        btn_gauss.clicked.connect(lambda: self.resolver_sistema(metodo="gauss"))
        botones_layout.addWidget(btn_gauss)

        # Botón Gauss-Jordan
        btn_gauss_jordan = QPushButton("▶ Resolver por GAUSS-JORDAN (Escalonada Reducida RREF)")
        btn_gauss_jordan.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold; padding: 8px;")
        btn_gauss_jordan.clicked.connect(lambda: self.resolver_sistema(metodo="gauss_jordan"))
        botones_layout.addWidget(btn_gauss_jordan)

        # Botón Verificar Forma
        btn_forma = QPushButton("¿Está en Forma Escalonada?")
        btn_forma.clicked.connect(self.analizar_forma_actual)
        botones_layout.addWidget(btn_forma)

        tabla_layout.addLayout(botones_layout)
        layout.addWidget(tabla_box)

        # --- RESULTADOS EN PESTAÑAS ---
        res_box = QGroupBox("3. Resultados y Análisis Teórico")
        res_layout = QVBoxLayout(res_box)

        self.tabs = QTabWidget()
        self.txt_pasos = self._nueva_pestania("Procedimiento paso a paso")
        self.txt_formas = self._nueva_pestania("Formas escalonadas y pivotes")
        self.txt_analisis = self._nueva_pestania("Existencia y unicidad")
        self.txt_verif = self._nueva_pestania("Verificación")
        res_layout.addWidget(self.tabs)

        layout.addWidget(res_box)
        layout.setStretch(0, 0)
        layout.setStretch(1, 0)
        layout.setStretch(2, 0)
        layout.setStretch(3, 1)

        self.actualizar_tabla()

    def _nueva_pestania(self, titulo):
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.tabs.addTab(txt, titulo)
        return txt

    def actualizar_tabla(self):
        m = self.spin_m.value()
        n = self.spin_n.value()

        self.tabla.setRowCount(m)
        self.tabla.setColumnCount(n + 1)

        headers = [nombre_var(j) for j in range(n)] + ["b"]
        self.tabla.setHorizontalHeaderLabels(headers)
        self.tabla.setVerticalHeaderLabels([f"R{i + 1}" for i in range(m)])

        for i in range(m):
            for j in range(n + 1):
                if not self.tabla.item(i, j):
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla.setItem(i, j, item)

        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        alto = self.tabla.horizontalHeader().height() + 6
        for i in range(m):
            alto += self.tabla.rowHeight(i)
        self.tabla.setMaximumHeight(min(alto, 200))

    def limpiar_tabla(self):
        for i in range(self.tabla.rowCount()):
            for j in range(self.tabla.columnCount()):
                self.tabla.item(i, j).setText("0")
        self.lbl_modelo_info.setVisible(False)
        self.combo_modelos.setCurrentIndex(0)

    def cargar_modelo_seleccionado(self, idx):
        if idx <= 0:
            self.lbl_modelo_info.setVisible(False)
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
        )
        self.lbl_modelo_info.setText(info_text)
        self.lbl_modelo_info.setVisible(True)

    def leer_matriz(self):
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
        msg = "Se encontraron errores en las celdas ingresadas:\n\n" + "\n".join(errores)
        QMessageBox.critical(self, "Error en los Datos", msg)

    def analizar_forma_actual(self):
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
        elif analisis["escalonada"]:
            lineas.append("DICTAMEN: La matriz está en FORMA ESCALONADA (REF), pero no reducida.")
        else:
            lineas.append("DICTAMEN: La matriz NO está en forma escalonada.")
        lineas.append(SEP)

        self.txt_formas.setText("\n".join(lineas))
        self.tabs.setCurrentWidget(self.txt_formas)

    def resolver_sistema(self, metodo="gauss_jordan"):
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
