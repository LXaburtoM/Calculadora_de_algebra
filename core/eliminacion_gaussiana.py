"""
MÃ³dulo 1: Motor de EliminaciÃ³n Gaussiana y Gauss-Jordan.
Tema: Sistemas de Ecuaciones Lineales, Forma Escalonada Reducida (RREF).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas RamÃ­rez, Luis Xavier Aburto Mantilla.
"""

from fractions import Fraction
from core.parser import formato_numero

_SUBINDICES = "â‚€â‚â‚‚â‚ƒâ‚„â‚…â‚†â‚‡â‚ˆâ‚‰"

def copiar_matriz(matriz):
    return [[cell for cell in row] for row in matriz]

def nombre_var(j):
    return "x" + "".join(_SUBINDICES[int(d)] for d in str(j + 1))

def _paso(titulo, descripcion, matriz, fase):
    return {
        "titulo": titulo,
        "descripcion": descripcion,
        "matriz": copiar_matriz(matriz),
        "fase": fase,
    }

def entradas_principales(matriz, m, n_cols):
    principales = {}
    for i in range(m):
        for j in range(n_cols):
            if matriz[i][j] != 0:
                principales[i] = j
                break
    return principales

# --------------------------------------------------------------------------
# ReducciÃ³n por Filas en Dos Fases
# --------------------------------------------------------------------------
def reducir_por_filas(A_aug, m, n, modo_fraccion=True, detener_si_inconsistente=True):
    matriz = copiar_matriz(A_aug)
    pasos = [_paso(
        "Matriz aumentada inicial [A | b]",
        "Se escribe el sistema de ecuaciones como matriz aumentada [A | b].",
        matriz,
        "INICIAL",
    )]

    # ================= FASE PROGRESIVA -> FORMA ESCALONADA (REF) =================
    pivotes = []
    fila_piv = 0

    for col in range(n + 1):
        if fila_piv >= m:
            break

        # 1. Pivoteo parcial
        max_fila = fila_piv
        max_val = abs(matriz[fila_piv][col])
        for k in range(fila_piv + 1, m):
            if abs(matriz[k][col]) > max_val:
                max_val = abs(matriz[k][col])
                max_fila = k

        if max_val == 0:
            nombre = nombre_var(col) if col < n else "b (columna aumentada)"
            pasos.append(_paso(
                f"Columna {nombre}: sin posiciÃ³n pivote",
                f"Todas las entradas de la columna {nombre}, desde la fila {fila_piv + 1} hacia abajo, son cero.",
                matriz,
                "PROGRESIVA",
            ))
            continue

        if max_fila != fila_piv:
            matriz[fila_piv], matriz[max_fila] = matriz[max_fila], matriz[fila_piv]
            pasos.append(_paso(
                f"Intercambio de filas  R{fila_piv + 1} â†” R{max_fila + 1}",
                f"Se intercambia la fila {fila_piv + 1} con la fila {max_fila + 1} (Pivoteo Parcial).",
                matriz,
                "PROGRESIVA",
            ))

        pivote = matriz[fila_piv][col]
        pivotes.append((fila_piv, col))

        # 2. Ceros debajo del pivote
        for i in range(fila_piv + 1, m):
            if matriz[i][col] != 0:
                factor = matriz[i][col] / pivote
                for j in range(col, n + 1):
                    matriz[i][j] -= factor * matriz[fila_piv][j]
                pasos.append(_paso(
                    f"Ceros debajo del pivote  (fila {i + 1})",
                    f"R{i + 1} = R{i + 1} âˆ’ ({formato_numero(factor, modo_fraccion)}) Â· R{fila_piv + 1}",
                    matriz,
                    "PROGRESIVA",
                ))

        fila_piv += 1

    ref = copiar_matriz(matriz)
    cols_pivote = [c for (_, c) in pivotes]

    pasos.append(_paso(
        "âœ” FORMA ESCALONADA (REF) alcanzada",
        "Fin de la fase progresiva. Se han generado ceros debajo de cada posiciÃ³n pivote.",
        ref,
        "HITO_REF",
    ))

    # Teorema de Existencia
    consistente = n not in cols_pivote
    fila_contradiccion = None
    if not consistente:
        for (i, c) in pivotes:
            if c == n:
                fila_contradiccion = i
                break

    if not consistente and detener_si_inconsistente:
        pasos.append(_paso(
            "âœ˜ Sistema INCONSISTENTE â€” sin soluciÃ³n",
            f"La columna aumentada b es columna pivote (Fila {fila_contradiccion + 1}: 0 = {formato_numero(ref[fila_contradiccion][n], modo_fraccion)}).",
            ref,
            "HITO_FIN",
        ))
        return {
            "ref": ref,
            "rref": None,
            "pasos": pasos,
            "pivotes": pivotes,
            "cols_pivote": cols_pivote,
            "consistente": False,
            "fila_contradiccion": fila_contradiccion,
        }

    # ================= FASE REGRESIVA -> FORMA ESCALONADA REDUCIDA (RREF) =================
    for (fila_p, col_p) in reversed(pivotes):
        pivote = matriz[fila_p][col_p]

        if pivote != 1:
            for j in range(col_p, n + 1):
                matriz[fila_p][j] = matriz[fila_p][j] / pivote
            pasos.append(_paso(
                f"Escalamiento del pivote a 1  (fila {fila_p + 1})",
                f"R{fila_p + 1} = R{fila_p + 1} Ã· ({formato_numero(pivote, modo_fraccion)})",
                matriz,
                "REGRESIVA",
            ))

        for i in range(fila_p - 1, -1, -1):
            if matriz[i][col_p] != 0:
                factor = matriz[i][col_p]
                for j in range(col_p, n + 1):
                    matriz[i][j] -= factor * matriz[fila_p][j]
                pasos.append(_paso(
                    f"Ceros arriba del pivote  (fila {i + 1})",
                    f"R{i + 1} = R{i + 1} âˆ’ ({formato_numero(factor, modo_fraccion)}) Â· R{fila_p + 1}",
                    matriz,
                    "REGRESIVA",
                ))

    rref = copiar_matriz(matriz)
    pasos.append(_paso(
        "âœ” FORMA ESCALONADA REDUCIDA (RREF) alcanzada",
        "Cada entrada principal es 1 y es la Ãºnica entrada no nula en su columna.",
        rref,
        "HITO_RREF",
    ))

    return {
        "ref": ref,
        "rref": rref,
        "pasos": pasos,
        "pivotes": pivotes,
        "cols_pivote": cols_pivote,
        "consistente": consistente,
        "fila_contradiccion": fila_contradiccion,
    }

# --------------------------------------------------------------------------
# MÃ©todo de Gauss: Fase Progresiva (REF) + SustituciÃ³n Hacia AtrÃ¡s
# --------------------------------------------------------------------------
def resolver_por_gauss(A_aug, m, n, modo_fraccion=True):
    """
    Ejecuta el MÃ©todo de Gauss tradicional:
    1. ReducciÃ³n a Forma Escalonada (REF).
    2. SustituciÃ³n Hacia AtrÃ¡s explÃ­cita con ecuaciones y despejes paso a paso.
    """
    res = reducir_por_filas(A_aug, m, n, modo_fraccion=modo_fraccion, detener_si_inconsistente=True)
    
    # Filtrar solo los pasos de la fase progresiva (hasta la REF)
    pasos_gauss = [p for p in res["pasos"] if p["fase"] in ("INICIAL", "PROGRESIVA", "HITO_REF", "HITO_FIN")]
    
    pasos_sustitucion = []
    solucion = None
    
    if res["consistente"]:
        cols_piv = [c for c in res["cols_pivote"] if c < n]
        libres = [j for j in range(n) if j not in cols_piv]
        
        if not libres:
            # SoluciÃ³n Ãšnica por SustituciÃ³n Hacia AtrÃ¡s
            sol = [Fraction(0)] * n
            pivs = [(i, c) for (i, c) in res["pivotes"] if c < n]
            
            pasos_sustitucion.append("================================================================================")
            pasos_sustitucion.append("             FASE DE SUSTITUCIÃ“N HACIA ATRÃS (BACK-SUBSTITUTION)")
            pasos_sustitucion.append("================================================================================\n")
            
            for (fila, col) in reversed(pivs):
                coef_piv = res["ref"][fila][col]
                b_val = res["ref"][fila][n]
                
                # EcuaciÃ³n correspondiente en la REF
                terms_str = []
                suma_conocidos = Fraction(0)
                despeje_terms = []
                
                for j in range(col, n):
                    c_val = res["ref"][fila][j]
                    if c_val != 0:
                        terms_str.append(f"({formato_numero(c_val, modo_fraccion)})Â·{nombre_var(j)}")
                        if j > col:
                            suma_conocidos += c_val * sol[j]
                            despeje_terms.append(f"({formato_numero(c_val, modo_fraccion)})Â·({formato_numero(sol[j], modo_fraccion)})")
                            
                eq_str = " + ".join(terms_str) + f" = {formato_numero(b_val, modo_fraccion)}"
                pasos_sustitucion.append(f"â€¢ De la Fila {fila + 1}: {eq_str}")
                
                # Despeje de la variable
                numerador = b_val - suma_conocidos
                sol[col] = numerador / coef_piv
                
                if despeje_terms:
                    desp_str = f"  {nombre_var(col)} = [{formato_numero(b_val, modo_fraccion)} âˆ’ (" + " + ".join(despeje_terms) + f")] Ã· ({formato_numero(coef_piv, modo_fraccion)})"
                else:
                    desp_str = f"  {nombre_var(col)} = {formato_numero(b_val, modo_fraccion)} Ã· {formato_numero(coef_piv, modo_fraccion)}"
                    
                pasos_sustitucion.append(desp_str)
                pasos_sustitucion.append(f"  ðŸ‘‰ {nombre_var(col)} = {formato_numero(sol[col], modo_fraccion)}  (Decimal: {float(sol[col]):.4f})\n")
                
            solucion = sol
            
    return {
        "resultado_base": res,
        "pasos_gauss": pasos_gauss,
        "pasos_sustitucion": pasos_sustitucion,
        "solucion": solucion
    }

# --------------------------------------------------------------------------
# VerificaciÃ³n de Formas Escalonadas (5 Propiedades de Lay)
# --------------------------------------------------------------------------
def analizar_forma(matriz, m, n_cols):
    filas_nulas = [i for i in range(m) if all(matriz[i][j] == 0 for j in range(n_cols))]
    principales = entradas_principales(matriz, m, n_cols)
    no_nulas = sorted(principales.keys())

    p1 = all(i < min(filas_nulas) for i in no_nulas) if filas_nulas else True
    p1_msg = "Todas las filas nulas estÃ¡n al final." if p1 else "Hay una fila nula arriba de una no nula."

    p2 = True
    previa = -1
    for i in no_nulas:
        if principales[i] <= previa:
            p2 = False
            break
        previa = principales[i]
    p2_msg = "Las entradas principales avanzan en patrÃ³n de escalera." if p2 else "Una entrada principal no estÃ¡ a la derecha de la anterior."

    p3 = True
    for i in no_nulas:
        col = principales[i]
        for k in range(i + 1, m):
            if matriz[k][col] != 0:
                p3 = False
                break
        if not p3:
            break
    p3_msg = "Debajo de cada entrada principal todo es cero." if p3 else "Hay elementos no nulos debajo de un pivote."

    p4 = all(matriz[i][principales[i]] == 1 for i in no_nulas)
    p4_msg = "Cada entrada principal vale 1." if p4 else "Alguna entrada principal no vale 1."

    p5 = True
    for i in no_nulas:
        col = principales[i]
        for k in range(m):
            if k != i and matriz[k][col] != 0:
                p5 = False
                break
        if not p5:
            break
    p5_msg = "Cada 1 principal es el Ãºnico no nulo en su columna." if p5 else "Hay elementos no nulos arriba de un 1 principal."

    escalonada = p1 and p2 and p3
    reducida = escalonada and p4 and p5

    return {
        "propiedades": [
            (1, "Las filas nulas estÃ¡n debajo de las no nulas.", p1, p1_msg),
            (2, "Cada entrada principal estÃ¡ a la derecha de la fila superior.", p2, p2_msg),
            (3, "Debajo de cada entrada principal solo hay ceros.", p3, p3_msg),
            (4, "[RREF] Cada entrada principal es 1.", p4, p4_msg),
            (5, "[RREF] Cada 1 principal es la Ãºnica entrada no nula en su columna.", p5, p5_msg),
        ],
        "escalonada": escalonada,
        "reducida": reducida,
        "principales": principales,
    }

# --------------------------------------------------------------------------
# ClasificaciÃ³n, SoluciÃ³n General y VerificaciÃ³n
# --------------------------------------------------------------------------
def clasificar_sistema(resultado, m, n):
    cols_pivote = [c for c in resultado["cols_pivote"] if c < n]
    libres = [j for j in range(n) if j not in cols_pivote]
    rango = len(cols_pivote)

    if not resultado["consistente"]:
        i = resultado["fila_contradiccion"]
        val = resultado["ref"][i][n]
        return {
            "tipo": "INCONSISTENTE",
            "mensaje": "Sistema Inconsistente (sin soluciÃ³n).",
            "detalle": (
                f"La columna aumentada b ES columna pivote. La fila {i + 1} quedÃ³ como "
                f"[0 â€¦ 0 | {formato_numero(val)}], correspondiente a 0 = {formato_numero(val)}."
            ),
            "basicas": [],
            "libres": [],
            "rango": rango,
        }

    if libres:
        return {
            "tipo": "INDETERMINADO",
            "mensaje": "Sistema Consistente Indeterminado (infinidad de soluciones).",
            "detalle": (
                f"La columna aumentada b NO es pivote. Rango(A) = {rango} < n = {n}. "
                f"Existen {len(libres)} variable(s) libre(s): {', '.join(nombre_var(j) for j in libres)}."
            ),
            "basicas": cols_pivote,
            "libres": libres,
            "rango": rango,
        }

    return {
        "tipo": "DETERMINADO",
        "mensaje": "Sistema Consistente Determinado (soluciÃ³n Ãºnica).",
        "detalle": f"Rango(A) = {rango} = n = {n}. No hay variables libres, la soluciÃ³n es Ãºnica.",
        "basicas": cols_pivote,
        "libres": [],
        "rango": rango,
    }

def solucion_general(rref, m, n, pivotes):
    cols_pivote = [c for (_, c) in pivotes if c < n]
    libres = [j for j in range(n) if j not in cols_pivote]

    despejes = []
    for j in range(n):
        if j in libres:
            despejes.append({"var": j, "libre": True, "const": Fraction(0), "coefs": {}})
            continue

        fila = next(i for (i, c) in pivotes if c == j)
        coefs = {}
        for k in libres:
            if rref[fila][k] != 0:
                coefs[k] = -rref[fila][k]
        despejes.append({
            "var": j,
            "libre": False,
            "const": rref[fila][n],
            "coefs": coefs,
        })
    return despejes

def forma_vectorial(despejes, n, libres):
    p = [d["const"] for d in despejes]
    direcciones = []
    for k in libres:
        v = [Fraction(0)] * n
        v[k] = Fraction(1)
        for d in despejes:
            if not d["libre"] and k in d["coefs"]:
                v[d["var"]] = d["coefs"][k]
        direcciones.append((k, v))
    return p, direcciones

def verificar_solucion(A_aug_original, solucion, m, n):
    if solucion is None:
        return []
    resultados = []
    for i in range(m):
        suma_lhs = Fraction(0)
        terminos = []
        for j in range(n):
            coef = A_aug_original[i][j]
            val_x = solucion[j]
            suma_lhs += coef * val_x
            terminos.append(f"({formato_numero(coef)})Â·({formato_numero(val_x)})")
        b_esperado = A_aug_original[i][n]
        resultados.append({
            "ecuacion": f"EcuaciÃ³n {i + 1}",
            "expresion": " + ".join(terminos) + f" = {formato_numero(suma_lhs)}",
            "esperado": formato_numero(b_esperado),
            "correcto": suma_lhs == b_esperado,
        })
    return resultados

def verificar_homogenea(A_aug_original, vector, m, n):
    resultados = []
    for i in range(m):
        suma = Fraction(0)
        for j in range(n):
            suma += A_aug_original[i][j] * vector[j]
        resultados.append({
            "ecuacion": f"EcuaciÃ³n {i + 1}",
            "valor": formato_numero(suma),
            "correcto": suma == 0,
        })
    return resultados


