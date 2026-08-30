"""
Motor de Introducción a Transformaciones Lineales T(x) = A x.
Soporta:
- Evaluación de imagen: T(u) = A · u
- Preimagen y verificación de pertenencia al rango: Resolver A · x = b
- Análisis teórico de Inyectividad (Uno a uno) y Sobreyectividad (Sobre R^m).
"""

from fractions import Fraction
from core.parser import formato_numero
from core.eliminacion_gaussiana import reducir_por_filas, nombre_var

def evaluar_transformacion(A, u, m, n):
    """
    Calcula w = T(u) = A · u
    A es matriz m x n, u es vector de dimension n.
    Retorna lista de dimension m con los resultados.
    """
    w = []
    pasos = []
    for i in range(m):
        terminos = []
        suma = Fraction(0)
        for j in range(n):
            prod = A[i][j] * u[j]
            suma += prod
            terminos.append(f"({formato_numero(A[i][j])})·({formato_numero(u[j])})")
        w.append(suma)
        pasos.append(f"Fila {i+1}: " + " + ".join(terminos) + f" = {formato_numero(suma)}")
    return w, pasos

def analizar_transformacion_completa(A, m, n, b=None, u=None, modo_fraccion=True):
    """
    Analiza rigurosamente la transformación lineal T: R^n -> R^m dada por T(x) = Ax.
    """
    # 1. Matriz aumentada para analizar A en su forma escalonada
    # Usamos columna cero ficticia para analizar solo A
    A_aug_cero = [row + [Fraction(0)] for row in A]
    res_A = reducir_por_filas(A_aug_cero, m, n, modo_fraccion=modo_fraccion)
    
    cols_pivote = [c for c in res_A["cols_pivote"] if c < n]
    pivotes_filas = [r for (r, c) in res_A["pivotes"] if c < n]
    
    num_pivotes = len(cols_pivote)
    
    # Inyectividad (Uno a uno): Pivote en CADA COLUMNA (num_pivotes == n)
    es_inyectiva = (num_pivotes == n)
    # Sobreyectiva (Sobre R^m): Pivote en CADA FILA (num_pivotes == m)
    es_sobreyectiva = (num_pivotes == m)
    
    analisis = {
        "dominio": f"R^{n}",
        "codominio": f"R^{m}",
        "num_pivotes": num_pivotes,
        "cols_pivote": cols_pivote,
        "es_inyectiva": es_inyectiva,
        "es_sobreyectiva": es_sobreyectiva,
        "ref": res_A["ref"],
        "rref": res_A["rref"],
        "detalle_inyectiva": (
            f"✔ T ES INYECTIVA (Uno a uno): La matriz A tiene {num_pivotes} columnas pivote de {n} columnas. "
            "No existen variables libres, por lo que T(x) = 0 solo tiene la solución trivial x = 0."
            if es_inyectiva else
            f"✘ T NO ES INYECTIVA: Hay solo {num_pivotes} columnas pivote para {n} variables. "
            f"Existen {n - num_pivotes} variable(s) libre(s), por lo que T(x) = 0 tiene soluciones no triviales."
        ),
        "detalle_sobreyectiva": (
            f"✔ T ES SOBREYECTIVA (Sobre R^{m}): La matriz A tiene un pivote en cada una de sus {m} filas. "
            f"Las columnas de A generan todo el codominio R^{m}, por lo que para todo b existe solución a T(x) = b."
            if es_sobreyectiva else
            f"✘ T NO ES SOBREYECTIVA: La matriz A tiene {num_pivotes} filas con pivote de un total de {m} filas. "
            f"Las columnas de A NO generan todo R^{m} (existen vectores b que no tienen preimagen)."
        )
    }
    
    # 2. Evaluación de imagen T(u) si se proporciona u
    if u is not None:
        w, pasos_u = evaluar_transformacion(A, u, m, n)
        analisis["u"] = u
        analisis["Tu"] = w
        analisis["pasos_Tu"] = pasos_u
        
    # 3. Evaluación de preimagen T(x) = b si se proporciona b
    if b is not None:
        A_aug_b = [A[i] + [b[i]] for i in range(m)]
        res_b = reducir_por_filas(A_aug_b, m, n, modo_fraccion=modo_fraccion)
        analisis["b"] = b
        analisis["res_b"] = res_b
        analisis["pertenece_rango"] = res_b["consistente"]
        
    return analisis
