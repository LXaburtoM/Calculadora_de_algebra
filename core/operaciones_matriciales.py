"""
Módulo de Operaciones Algebraicas en Rn y Operaciones Matriciales Básicas.

Implementa (sin usar numpy, scipy ni math):
  SECCIÓN 1 - Operaciones Vectoriales:
    - suma_vectores        : v1 + v2  componente a componente
    - resta_vectores       : v1 - v2  componente a componente
    - escalar_por_vector   : c * v    cada componente multiplicada por c
  SECCIÓN 2 - Operaciones Matriciales:
    - sumar_matrices       : A + B    (valida que tengan mismas dimensiones m x n)
    - restar_matrices      : A - B    (valida que tengan mismas dimensiones m x n)
    - escalar_por_matriz   : c * A    cada entrada multiplicada por c
    - multiplicar_matrices : A * B    (Regla Fila-Columna, valida cols A == filas B)
    - transpuesta_matriz   : A^T      intercambia filas por columnas (Sesión 9)
  SECCIÓN 3 - Combinación Lineal:
    - es_combinacion_lineal: verifica si b pertenece a span{v1, v2, ..., vk}
                             planteando el sistema [v1|v2|...|vk|b] y revisando
                             si es consistente con Gauss-Jordan.
"""

from fractions import Fraction
from core.eliminacion_gaussiana import (
    reducir_por_filas, solucion_general, forma_vectorial, nombre_var
)
from core.parser import formato_numero


# ══════════════════════════════════════════════════════════════════════
# SECCIÓN 1: OPERACIONES VECTORIALES EN Rn
# ══════════════════════════════════════════════════════════════════════

def sumar_vectores(v1, v2):
    """
    Suma dos vectores componente a componente: resultado[i] = v1[i] + v2[i]
    Ambos vectores deben tener la misma dimensión n.
    Retorna (resultado, pasos, error_msg).
    """
    n = len(v1)
    if len(v2) != n:
        return None, [], (
            f"Dimensiones incompatibles: v\u2081 tiene {n} componentes "
            f"y v\u2082 tiene {len(v2)} componentes."
        )

    resultado = []
    pasos = []
    for i in range(n):
        # Operación elemental: suma de las i-ésimas componentes
        r = v1[i] + v2[i]
        resultado.append(r)
        pasos.append(
            f"  Componente {i+1}: "
            f"{formato_numero(v1[i])} + ({formato_numero(v2[i])}) = {formato_numero(r)}"
        )
    return resultado, pasos, None


def restar_vectores(v1, v2):
    """
    Resta dos vectores componente a componente: resultado[i] = v1[i] - v2[i]
    Ambos vectores deben tener la misma dimensión n.
    Retorna (resultado, pasos, error_msg).
    """
    n = len(v1)
    if len(v2) != n:
        return None, [], (
            f"Dimensiones incompatibles: v\u2081 tiene {n} componentes "
            f"y v\u2082 tiene {len(v2)} componentes."
        )

    resultado = []
    pasos = []
    for i in range(n):
        # Operación elemental: resta de las i-ésimas componentes
        r = v1[i] - v2[i]
        resultado.append(r)
        pasos.append(
            f"  Componente {i+1}: "
            f"{formato_numero(v1[i])} \u2212 ({formato_numero(v2[i])}) = {formato_numero(r)}"
        )
    return resultado, pasos, None


def escalar_por_vector(escalar, v):
    """
    Multiplica un escalar c por un vector v: resultado[i] = c * v[i]
    Cada componente del vector se multiplica por el mismo escalar.
    Retorna (resultado, pasos, error_msg).
    """
    resultado = []
    pasos = []
    for i in range(len(v)):
        # Multiplicación escalar: propiedad de los espacios vectoriales
        r = escalar * v[i]
        resultado.append(r)
        pasos.append(
            f"  Componente {i+1}: "
            f"{formato_numero(escalar)} \u00d7 {formato_numero(v[i])} = {formato_numero(r)}"
        )
    return resultado, pasos, None


# ══════════════════════════════════════════════════════════════════════
# SECCIÓN 2: OPERACIONES MATRICIALES BÁSICAS
# ══════════════════════════════════════════════════════════════════════

def sumar_matrices(A, B, mA, nA, mB, nB):
    """
    Suma dos matrices A (mA x nA) + B (mB x nB).
    Requiere mA == mB y nA == nB (mismas dimensiones).
    Resultado C[i][j] = A[i][j] + B[i][j].
    Retorna (C, pasos, error_msg).
    """
    if mA != mB or nA != nB:
        return None, [], (
            f"Dimensiones incompatibles: A es {mA}\u00d7{nA} pero B es {mB}\u00d7{nB}. "
            "Para sumar matrices deben tener exactamente las mismas dimensiones."
        )

    # Inicializar resultado con ceros (mismo tamaño que A y B)
    C = [[Fraction(0)] * nA for _ in range(mA)]
    pasos = []
    for i in range(mA):
        for j in range(nA):
            # Suma entrada a entrada
            C[i][j] = A[i][j] + B[i][j]
            pasos.append(
                f"  C[{i+1},{j+1}] = "
                f"{formato_numero(A[i][j])} + ({formato_numero(B[i][j])}) = {formato_numero(C[i][j])}"
            )
    return C, pasos, None


def restar_matrices(A, B, mA, nA, mB, nB):
    """
    Resta dos matrices A (mA x nA) - B (mB x nB).
    Requiere mA == mB y nA == nB.
    Resultado C[i][j] = A[i][j] - B[i][j].
    Retorna (C, pasos, error_msg).
    """
    if mA != mB or nA != nB:
        return None, [], (
            f"Dimensiones incompatibles: A es {mA}\u00d7{nA} pero B es {mB}\u00d7{nB}. "
            "Para restar matrices deben tener exactamente las mismas dimensiones."
        )

    C = [[Fraction(0)] * nA for _ in range(mA)]
    pasos = []
    for i in range(mA):
        for j in range(nA):
            # Resta entrada a entrada
            C[i][j] = A[i][j] - B[i][j]
            pasos.append(
                f"  C[{i+1},{j+1}] = "
                f"{formato_numero(A[i][j])} \u2212 ({formato_numero(B[i][j])}) = {formato_numero(C[i][j])}"
            )
    return C, pasos, None


def escalar_por_matriz(escalar, A, m, n):
    """
    Multiplica un escalar c por una matriz A (m x n): C[i][j] = c * A[i][j]
    Se aplica el escalar a cada una de las m*n entradas de la matriz.
    Retorna (C, pasos, error_msg).
    """
    C = [[Fraction(0)] * n for _ in range(m)]
    pasos = []
    for i in range(m):
        for j in range(n):
            # Multiplicación por escalar: propiedad de matrices
            C[i][j] = escalar * A[i][j]
            pasos.append(
                f"  C[{i+1},{j+1}] = "
                f"{formato_numero(escalar)} \u00d7 {formato_numero(A[i][j])} = {formato_numero(C[i][j])}"
            )
    return C, pasos, None


def multiplicar_matrices(A, B, mA, nA, nB):
    """
    Multiplica A (mA x nA) por B (nA x nB) -> resultado C (mA x nB).

    VALIDACIÓN: columnas de A (nA) deben ser iguales a filas de B (nA).
    FÓRMULA:    C[i][j] = sum_{k=0}^{nA-1}  A[i][k] * B[k][j]

    Este triple bucle (i, j, k) es el núcleo del algoritmo de multiplicación
    de matrices y corre en O(mA * nA * nB).
    Retorna (C, pasos, error_msg).
    """
    filas_B = len(B)
    if nA != filas_B:
        return None, [], (
            f"Dimensiones incompatibles para multiplicar: "
            f"A es {mA}\u00d7{nA} y B es {filas_B}\u00d7{nB}. "
            f"Las columnas de A ({nA}) deben ser iguales a las filas de B ({filas_B})."
        )

    # Resultado tiene dimensión mA x nB, inicializado en cero
    C = [[Fraction(0)] * nB for _ in range(mA)]
    pasos = []

    for i in range(mA):          # Recorre cada fila de A
        for j in range(nB):      # Recorre cada columna de B
            suma = Fraction(0)
            terminos = []
            for k in range(nA):  # Producto punto: fila i de A · columna j de B
                prod = A[i][k] * B[k][j]
                suma += prod
                terminos.append(
                    f"({formato_numero(A[i][k])})·({formato_numero(B[k][j])})"
                )
            C[i][j] = suma
            pasos.append(
                f"  C[{i+1},{j+1}] = " + " + ".join(terminos) +
                f" = {formato_numero(suma)}"
            )
    return C, pasos, None


def transpuesta_matriz(A, m, n):
    """
    Calcula la transpuesta de una matriz A (m x n) -> A^T (n x m).
    Las filas de A se convierten en las columnas de A^T.
    Retorna (C, pasos, error_msg).
    """
    C = [[Fraction(0)] * m for _ in range(n)]
    pasos = []
    for i in range(m):
        for j in range(n):
            C[j][i] = A[i][j]
            pasos.append(f"  C[{j+1},{i+1}] = A[{i+1},{j+1}] = {formato_numero(A[i][j])}")
    return C, pasos, None


# ══════════════════════════════════════════════════════════════════════
# SECCIÓN 3: COMBINACIÓN LINEAL
# ══════════════════════════════════════════════════════════════════════

def es_combinacion_lineal(b, vectores):
    """
    Verifica si el vector b es combinación lineal del conjunto {v1, v2, ..., vk}.

    ESTRATEGIA ALGEBRAICA:
      b es CL de {v1,...,vk}  <=>  el sistema  c1*v1 + c2*v2 + ... + ck*vk = b
      tiene solución para los escalares c1, c2, ..., ck.
      Esto equivale a que el sistema [v1 | v2 | ... | vk | b] sea CONSISTENTE.

    Se construye la matriz aumentada poniendo cada vector vᵢ como una columna,
    y b como la última columna. Luego se resuelve con Gauss-Jordan.

    Retorna un dict con:
      'es_cl'           : True/False
      'escalares'       : dict {nombre: valor} si es único, 'infinitas' si hay libres, None si no
      'resultado_gauss' : el resultado completo de reducir_por_filas
      'k'               : número de vectores del conjunto
      'm'               : dimensión de cada vector
    """
    k = len(vectores)   # Número de vectores generadores
    m = len(b)          # Dimensión del espacio Rm

    # Validar que todos los vectores tengan la misma dimensión que b
    for idx, v in enumerate(vectores):
        if len(v) != m:
            return {
                "es_cl": False,
                "escalares": None,
                "resultado_gauss": None,
                "k": k, "m": m,
                "error": (
                    f"El vector v{idx+1} tiene dimensión {len(v)}, "
                    f"pero b tiene dimensión {m}. Deben coincidir."
                )
            }

    # Construir la matriz aumentada [v1 | v2 | ... | vk | b]
    # Cada columna j (0..k-1) es el vector vj, la columna k es b
    A_aug = []
    for i in range(m):
        fila = [vectores[j][i] for j in range(k)] + [b[i]]
        A_aug.append(fila)

    # Aplicar Gauss-Jordan para determinar consistencia
    resultado = reducir_por_filas(A_aug, m, k)

    escalares = None
    if resultado["consistente"]:
        despejes = solucion_general(resultado["rref"], m, k, resultado["pivotes"])
        tiene_libres = any(d["libre"] for d in despejes)

        if not tiene_libres:
            # Escalares únicos: c1, c2, ..., ck determinados
            escalares = {nombre_var(d["var"]): d["const"] for d in despejes}
        else:
            # Infinitas combinaciones posibles (dependencia lineal en los vᵢ)
            escalares = "infinitas"

    return {
        "es_cl": resultado["consistente"],
        "escalares": escalares,
        "resultado_gauss": resultado,
        "k": k,
        "m": m,
        "error": None,
    }
