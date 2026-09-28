"""
Módulo de Álgebra Avanzada (Inversa, Determinantes, Independencia Lineal)
No usa numpy, scipy ni math.
"""
from fractions import Fraction
from core.eliminacion_gaussiana import reducir_por_filas
from core.parser import formato_numero

def copiar_matriz(A):
    return [[val for val in fila] for fila in A]

# ==========================================
# 1. MATRIZ INVERSA (vía Gauss-Jordan)
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
        A_aug.append(A[i][:] + identidad)

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
        
    return A_inv, resultado["pasos"], None

# ==========================================
# 2. INDEPENDENCIA LINEAL
# ==========================================
def evaluar_independencia_lineal(vectores, n):
    """
    Evalúa si un conjunto de vectores es L.I. o L.D.
    vectores: lista de k vectores, cada uno de dimensión n.
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
    Calcula el determinante usando expansión por cofactores (recursivo).
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
    Calcula el determinante usando operaciones elementales (triangularización).
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
