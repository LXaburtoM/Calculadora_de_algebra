"""
MÃ³dulo de Ãlgebra Avanzada: Inversa, Determinantes e Independencia Lineal.
Tema: Matriz Inversa (SesiÃ³n 10), Determinantes por cofactores y reducciÃ³n (SesiÃ³n 11).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas RamÃ­rez, Luis Xavier Aburto Mantilla.
"""
from fractions import Fraction
from core.eliminacion_gaussiana import reducir_por_filas
from core.parser import formato_numero

def copiar_matriz(A):
    return [[val for val in fila] for fila in A]

# ==========================================
# 1. MATRIZ INVERSA (vÃ­a Gauss-Jordan)
# ==========================================
def inversa_matriz(A, n):
    """
    Calcula la matriz inversa de A (n x n) resolviendo [A | I].
    Retorna (A_inv, pasos, error_msg).
    """
    A_aug = []
    for i in range(n):
        # Concatena A[i] con la fila de la identidad
        identidad = [Fraction(1) if i == j else Fraction(0) for j in range(n)]
        A_aug.append(A[i][:] + identidad + [Fraction(0)])

    # Reducimos la matriz aumentada de n x 2n
    resultado = reducir_por_filas(A_aug, n, 2*n, modo_fraccion=True)
    
    # Para que sea invertible, los pivotes deben estar todos en las primeras n columnas
    # y debe haber exactamente n pivotes.
    pivotes = resultado["pivotes"]
    pivotes_en_A = [c for r, c in pivotes if c < n]
    
    if len(pivotes_en_A) < n:
        return None, resultado["pasos"], "La matriz NO es invertible (es singular, determinante = 0)."
    
    A_inv = []
    for i in range(n):
        A_inv.append(resultado["rref"][i][n:2*n])
        
    pasos_str = []
    for p in resultado["pasos"]:
        titulo = p.get("titulo", p.get("operacion", "Paso"))
        desc = p.get("descripcion", "")
        pasos_str.append(f"-> {titulo}: {desc}")
        M = p["matriz"]
        txts = [[formato_numero(M[i][j], True) for j in range(len(M[0]))] for i in range(len(M))]
        ancho = max(3, max(len(c) for fila in txts for c in fila) + 1)
        for fila in txts:
            celdas = [c.rjust(ancho) for c in fila]
            pasos_str.append("   [ " + "  ".join(celdas) + " ]")
        pasos_str.append("")
        
    return A_inv, pasos_str, None

# ==========================================
# 2. INDEPENDENCIA LINEAL
# ==========================================
def evaluar_independencia_lineal(vectores, n):
    """
    EvalÃºa si un conjunto de vectores es L.I. o L.D.
    vectores: lista de k vectores, cada uno de dimensiÃ³n n.
    Arma [v1 | v2 | ... | vk | 0] y reduce.
    """
    k = len(vectores)
    A_aug = []
    for i in range(n):
        fila = [vectores[j][i] for j in range(k)] + [Fraction(0)]
        A_aug.append(fila)
        
    resultado = reducir_por_filas(A_aug, n, k)
    num_pivotes = len([c for r, c in resultado["pivotes"] if c < k])
    
    es_li = (num_pivotes == k)
    
    return {
        "es_li": es_li,
        "num_pivotes": num_pivotes,
        "k": k,
        "n": n,
        "matriz_reducida": resultado["rref"],
        "pasos": resultado["pasos"]
    }

# ==========================================
# 3. DETERMINANTES
# ==========================================
def menor_complementario(A, i, j):
    """Obtiene la submatriz eliminando la fila i y columna j."""
    return [fila[:j] + fila[j+1:] for idx, fila in enumerate(A) if idx != i]

def determinante_cofactores(A):
    """
    Calcula el determinante usando expansiÃ³n por cofactores (recursivo).
    Retorna (valor, pasos textuales).
    """
    n = len(A)
    if n == 1:
        return A[0][0], f"Det = {formato_numero(A[0][0])}"
    if n == 2:
        val = A[0][0]*A[1][1] - A[0][1]*A[1][0]
        paso = f"({formato_numero(A[0][0])})({formato_numero(A[1][1])}) - ({formato_numero(A[0][1])})({formato_numero(A[1][0])}) = {formato_numero(val)}"
        return val, paso
        
    det = Fraction(0)
    pasos = []
    for j in range(n):
        if A[0][j] == 0:
            continue
        signo = 1 if j % 2 == 0 else -1
        sub_A = menor_complementario(A, 0, j)
        sub_det, _ = determinante_cofactores(sub_A)
        termino = signo * A[0][j] * sub_det
        det += termino
        sg_str = "+" if signo > 0 else "-"
        pasos.append(f"{sg_str} {formato_numero(A[0][j])} * ({formato_numero(sub_det)})")
        
    if not pasos:
        return Fraction(0), "Fila completa de ceros."
        
    return det, " ".join(pasos) + f" = {formato_numero(det)}"

def determinante_reduccion(A):
    """
    Calcula el determinante usando operaciones elementales (triangularizaciÃ³n).
    Retorna (valor, pasos).
    """
    n = len(A)
    mat = copiar_matriz(A)
    pasos = []
    intercambios = 0
    
    for i in range(n):
        # Buscar pivote
        pivote_fila = i
        while pivote_fila < n and mat[pivote_fila][i] == 0:
            pivote_fila += 1
            
        if pivote_fila == n:
            pasos.append(f"Columna {i+1} sin pivote. El determinante es 0.")
            return Fraction(0), pasos
            
        if pivote_fila != i:
            mat[i], mat[pivote_fila] = mat[pivote_fila], mat[i]
            intercambios += 1
            pasos.append(f"Intercambio F{i+1} <-> F{pivote_fila+1} (Cambia signo del Det)")
            
        # Hacer ceros abajo
        for j in range(i+1, n):
            factor = mat[j][i] / mat[i][i]
            if factor != 0:
                pasos.append(f"F{j+1} = F{j+1} - ({formato_numero(factor)})*F{i+1}")
                for k in range(i, n):
                    mat[j][k] -= factor * mat[i][k]
                    
    # Multiplicar diagonal
    det = Fraction(1)
    diag_str = []
    for i in range(n):
        det *= mat[i][i]
        diag_str.append(f"({formato_numero(mat[i][i])})")
        
    if intercambios % 2 != 0:
        det *= Fraction(-1)
        pasos.append(f"Det = -1 * (" + " * ".join(diag_str) + f") = {formato_numero(det)}")
    else:
        pasos.append(f"Det = " + " * ".join(diag_str) + f" = {formato_numero(det)}")
        
    return det, pasos


# ==========================================
# 4. REGLA DE CRAMER
# ==========================================
def reemplazar_columna(A, b, col):
    """Crea una copia de A con la columna 'col' sustituida por el vector b."""
    copia = copiar_matriz(A)
    for i in range(len(A)):
        copia[i][col] = b[i]
    return copia


def regla_de_cramer(A, b, n):
    """Resuelve Ax = b usando la Regla de Cramer.
    Retorna (soluciones, pasos, error_msg).
    """
    detA, paso_detA = determinante_cofactores(A)
    pasos = [f"det(A) = {paso_detA}"]

    if detA == 0:
        return None, pasos, "det(A) = 0. El sistema no tiene solucion unica (Cramer no aplica)."

    soluciones = []
    for i in range(n):
        Ai = reemplazar_columna(A, b, i)
        detAi, paso_detAi = determinante_cofactores(Ai)
        xi = detAi / detA
        pasos.append(f"det(A{i+1}) = {paso_detAi}")
        pasos.append(f"x{i+1} = det(A{i+1}) / det(A) = "
                     f"{formato_numero(detAi)} / {formato_numero(detA)} = "
                     f"{formato_numero(xi)}")
        soluciones.append(xi)

    return soluciones, pasos, None

# ==========================================
# 5. INVERSA POR ADJUNTA
# ==========================================
def inversa_adjunta(A, n):
    """
    Calcula la matriz inversa usando A^-1 = 1/det(A) * Adj(A).
    Retorna (A_inv, pasos, error_msg).
    """
    detA, paso_detA = determinante_cofactores(A)
    if detA == 0:
        return None, [f"det(A) = {paso_detA}"], "La matriz NO es invertible (determinante = 0)."
        
    pasos = [f"1) det(A) = {paso_detA}", "2) Matriz de Cofactores (C):"]
    
    # Calcular matriz de cofactores
    C = []
    for i in range(n):
        fila = []
        for j in range(n):
            signo = 1 if (i + j) % 2 == 0 else -1
            sub = menor_complementario(A, i, j)
            sub_det, _ = determinante_cofactores(sub)
            fila.append(signo * sub_det)
        C.append(fila)
        pasos.append(f"   Fila {i+1}: " + "  ".join(formato_numero(x) for x in fila))
        
    # Calcular adjunta (Transpuesta de cofactores)
    Adj = []
    pasos.append("3) Matriz Adjunta (C^T):")
    for j in range(n):
        fila = [C[i][j] for i in range(n)]
        Adj.append(fila)
        pasos.append(f"   Fila {j+1}: " + "  ".join(formato_numero(x) for x in fila))
        
    # Multiplicar por 1/detA
    A_inv = []
    pasos.append(f"4) A^-1 = 1/det(A) * Adj(A):")
    for i in range(n):
        fila = [Adj[i][j] / detA for j in range(n)]
        A_inv.append(fila)
        pasos.append(f"   Fila {i+1}: " + "  ".join(formato_numero(x) for x in fila))
        
    return A_inv, pasos, None


# ==========================================
# 6. REGLA DE SARRUS (3x3)
# ==========================================
def determinante_sarrus(A):
    """
    Calcula el determinante de una matriz 3x3 usando la Regla de Sarrus.
    Retorna (det, pasos, error_msg).
    """
    if len(A) != 3 or len(A[0]) != 3:
        return None, [], "La Regla de Sarrus solo es aplicable a matrices cuadradas de 3x3."
        
    d1 = A[0][0] * A[1][1] * A[2][2]
    d2 = A[0][1] * A[1][2] * A[2][0]
    d3 = A[0][2] * A[1][0] * A[2][1]
    suma_desc = d1 + d2 + d3
    
    u1 = A[2][0] * A[1][1] * A[0][2]
    u2 = A[2][1] * A[1][2] * A[0][0]
    u3 = A[2][2] * A[1][0] * A[0][1]
    suma_asc = u1 + u2 + u3
    
    det = suma_desc - suma_asc
    
    pasos = [
        "1) Extensión de las dos primeras columnas a la derecha:",
        f"   | {formato_numero(A[0][0])}  {formato_numero(A[0][1])}  {formato_numero(A[0][2])} | {formato_numero(A[0][0])}  {formato_numero(A[0][1])}",
        f"   | {formato_numero(A[1][0])}  {formato_numero(A[1][1])}  {formato_numero(A[1][2])} | {formato_numero(A[1][0])}  {formato_numero(A[1][1])}",
        f"   | {formato_numero(A[2][0])}  {formato_numero(A[2][1])}  {formato_numero(A[2][2])} | {formato_numero(A[2][0])}  {formato_numero(A[2][1])}",
        "",
        "2) Diagonales descendentes (↘ suman):",
        f"   d1 = ({formato_numero(A[0][0])})*({formato_numero(A[1][1])})*({formato_numero(A[2][2])}) = {formato_numero(d1)}",
        f"   d2 = ({formato_numero(A[0][1])})*({formato_numero(A[1][2])})*({formato_numero(A[2][0])}) = {formato_numero(d2)}",
        f"   d3 = ({formato_numero(A[0][2])})*({formato_numero(A[1][0])})*({formato_numero(A[2][1])}) = {formato_numero(d3)}",
        f"   Suma (↘) = {formato_numero(d1)} + {formato_numero(d2)} + {formato_numero(d3)} = {formato_numero(suma_desc)}",
        "",
        "3) Diagonales ascendentes (↗ restan):",
        f"   u1 = ({formato_numero(A[2][0])})*({formato_numero(A[1][1])})*({formato_numero(A[0][2])}) = {formato_numero(u1)}",
        f"   u2 = ({formato_numero(A[2][1])})*({formato_numero(A[1][2])})*({formato_numero(A[0][0])}) = {formato_numero(u2)}",
        f"   u3 = ({formato_numero(A[2][2])})*({formato_numero(A[1][0])})*({formato_numero(A[0][1])}) = {formato_numero(u3)}",
        f"   Suma (↗) = {formato_numero(u1)} + {formato_numero(u2)} + {formato_numero(u3)} = {formato_numero(suma_asc)}",
        "",
        "4) det(A) = (Suma ↘) - (Suma ↗):",
        f"   det(A) = ({formato_numero(suma_desc)}) - ({formato_numero(suma_asc)}) = {formato_numero(det)}"
    ]
    return det, pasos, None
