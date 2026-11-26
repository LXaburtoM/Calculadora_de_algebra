"""
Módulo 8: Métodos Numéricos Iterativos: Jacobi y Gauss-Seidel.
Tema: Solución aproximada de sistemas de ecuaciones lineales Ax = b,
      análisis de convergencia, dominancia diagonal, reordenamiento de filas,
      radios espectrales y contraste con soluciones de referencia.
Asignatura: Álgebra Lineal (MTM0120) - Universidad Americana (UAM).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from __future__ import annotations

import itertools
import math
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class IteracionRegistro:
    """Registro individual de una iteración k."""
    k: int
    x: np.ndarray
    error: float
    residuo: float

    def a_diccionario(self, nombres_var: list[str] | None = None) -> dict[str, Any]:
        n = len(self.x)
        if nombres_var is None:
            nombres_var = [f"x_{i+1}" for i in range(n)]
        d: dict[str, Any] = {"Iteración": self.k}
        for nombre, val in zip(nombres_var, self.x):
            d[nombre] = float(val)
        d["Error (||Δx||_∞)"] = float(self.error) if not math.isnan(self.error) else None
        d["Residuo (||Ax-b||_∞)"] = float(self.residuo)
        return d


@dataclass
class ResultadoMetodoIterativo:
    """Resultado completo de la ejecución de un método iterativo."""
    metodo: str  # "Jacobi" o "Gauss-Seidel"
    convergio: bool
    estado: str  # "CONVERGENCIA", "MAX_ITER", "DIVERGENCIA", "ERROR_DIAGONAL"
    mensaje: str
    num_iteraciones: int
    x_final: np.ndarray
    error_final: float
    residuo_final: float
    tiempo_ms: float
    historial: list[IteracionRegistro] = field(default_factory=list)
    radio_espectral: float | None = None
    matriz_iteracion: np.ndarray | None = None
    tolerancia_usada: float = 1e-4
    max_iter_usado: int = 100

    def a_dataframe(self, nombres_var: list[str] | None = None) -> pd.DataFrame:
        """Genera un DataFrame de Pandas con la tabla completa de iteraciones."""
        if not self.historial:
            return pd.DataFrame()
        filas = [reg.a_diccionario(nombres_var) for reg in self.historial]
        df = pd.DataFrame(filas)
        return df


# ─────────────────────────────────────────────────────────────────────────────
# 1. VALIDACIÓN Y ANÁLISIS DE LA MATRIZ Y DIAGONAL
# ─────────────────────────────────────────────────────────────────────────────

def validar_entradas_iterativas(
    A: Any,
    b: Any,
    x0: Any = None,
    tol: float = 1e-4,
    max_iter: int = 100
) -> tuple[np.ndarray, np.ndarray, np.ndarray, str | None]:
    """
    Valida dimensiones y tipos de entrada para los métodos iterativos.
    Retorna: (A_np, b_np, x0_np, error_str)
    """
    try:
        A_np = np.array(A, dtype=np.float64)
    except Exception as e:
        return np.empty((0, 0)), np.empty(0), np.empty(0), f"Error al convertir la matriz A a números: {e}"

    if A_np.ndim != 2:
        return np.empty((0, 0)), np.empty(0), np.empty(0), "La matriz de coeficientes A debe ser bidimensional."

    filas, cols = A_np.shape
    if filas != cols:
        return np.empty((0, 0)), np.empty(0), np.empty(0), f"La matriz A debe ser cuadrada (nxn), pero es de {filas}×{cols}."

    if filas < 1:
        return np.empty((0, 0)), np.empty(0), np.empty(0), "La matriz A no puede estar vacía."

    n = filas

    try:
        b_np = np.array(b, dtype=np.float64).flatten()
    except Exception as e:
        return np.empty((0, 0)), np.empty(0), np.empty(0), f"Error al convertir el vector b a números: {e}"

    if b_np.shape[0] != n:
        return np.empty((0, 0)), np.empty(0), np.empty(0), f"La dimensión de b ({b_np.shape[0]}) no coincide con las filas de A ({n})."

    if x0 is None:
        x0_np = np.zeros(n, dtype=np.float64)
    else:
        try:
            x0_np = np.array(x0, dtype=np.float64).flatten()
        except Exception as e:
            return np.empty((0, 0)), np.empty(0), np.empty(0), f"Error al convertir el vector inicial x0: {e}"

        if x0_np.shape[0] != n:
            return np.empty((0, 0)), np.empty(0), np.empty(0), f"La dimensión de x0 ({x0_np.shape[0]}) no coincide con n={n}."

    if tol <= 0:
        return np.empty((0, 0)), np.empty(0), np.empty(0), f"La tolerancia ε debe ser estrictamente positiva (se recibió {tol})."

    if max_iter < 1:
        return np.empty((0, 0)), np.empty(0), np.empty(0), f"El número máximo de iteraciones debe ser un entero positivo (se recibió {max_iter})."

    return A_np, b_np, x0_np, None


def analizar_diagonal_y_convergencia(A: np.ndarray) -> dict[str, Any]:
    """
    Analiza la diagonal principal de A:
    - Presencia de ceros en la diagonal.
    - Dominancia diagonal estricta por filas (|a_ii| > sum_{j!=i} |a_ij|).
    - Radios espectrales de las matrices de iteración T_J y T_GS (ρ(T) < 1).
    - Explicación matemática clara de condiciones suficientes vs. necesarias.
    """
    n = A.shape[0]
    diag = np.diag(A)
    ceros_indices = [int(i) for i in range(n) if math.isclose(diag[i], 0.0, abs_tol=1e-12)]
    tiene_ceros = len(ceros_indices) > 0

    detalles_filas = []
    filas_estrictas = []
    filas_debiles = []

    for i in range(n):
        a_ii = abs(float(diag[i]))
        suma_fuera = float(np.sum(np.abs(A[i, :])) - a_ii)
        diff = a_ii - suma_fuera
        es_estricta = diff > 1e-12
        es_debil = abs(diff) <= 1e-12 or es_estricta

        filas_estrictas.append(es_estricta)
        filas_debiles.append(es_debil)
        detalles_filas.append({
            "fila": i + 1,
            "a_ii": float(diag[i]),
            "abs_a_ii": a_ii,
            "suma_fuera": suma_fuera,
            "diferencia": diff,
            "estricta": es_estricta,
        })

    es_estrictamente_dominante = all(filas_estrictas)
    es_debilmente_dominante = all(filas_debiles) and any(filas_estrictas)

    # Cálculo de matrices de iteración y radios espectrales (si no hay ceros en diagonal)
    rho_jacobi: float | None = None
    rho_seidel: float | None = None
    T_jacobi: np.ndarray | None = None
    T_seidel: np.ndarray | None = None

    if not tiene_ceros:
        try:
            D = np.diag(diag)
            L = -np.tril(A, -1)
            U = -np.triu(A, 1)

            # Jacobi: T_J = D^(-1) (L + U)
            D_inv = np.diag(1.0 / diag)
            T_jacobi = D_inv @ (L + U)
            eig_j = np.linalg.eigvals(T_jacobi)
            rho_jacobi = float(np.max(np.abs(eig_j)))

            # Gauss-Seidel: T_GS = (D - L)^(-1) U
            D_minus_L = D - L
            T_seidel = np.linalg.inv(D_minus_L) @ U
            eig_gs = np.linalg.eigvals(T_seidel)
            rho_seidel = float(np.max(np.abs(eig_gs)))
        except Exception:
            rho_jacobi = None
            rho_seidel = None

    # Explicación de la condición suficiente y necesaria
    if es_estrictamente_dominante:
        mensaje_dominancia = (
            "✅ La matriz A presenta DIAGONAL ESTRICTAMENTE DOMINANTE por filas "
            "(|a_ii| > ∑_{j≠i} |a_ij| para toda fila i). Esta es una CONDICIÓN SUFICIENTE "
            "que garantiza matemáticamente la convergencia de los métodos de Jacobi y Gauss-Seidel "
            "para cualquier vector inicial x⁽⁰⁾."
        )
    else:
        mensaje_dominancia = (
            "ℹ️ La matriz A NO presenta diagonal estrictamente dominante por filas.\n"
            "⚠️ FUNDAMENTO MATEMÁTICO ESENCIAL: La dominancia diagonal estricta es una condición "
            "SUFICIENTE para la convergencia, pero NO es necesaria; por lo tanto, no debe afirmarse "
            "que su ausencia implique automáticamente divergencia.\n"
            "La condición NECESARIA Y SUFICIENTE para la convergencia es que el radio espectral de la "
            "matriz de iteración satisfaga ρ(T) < 1."
        )

    return {
        "n": n,
        "tiene_ceros": tiene_ceros,
        "ceros_indices": ceros_indices,
        "es_estrictamente_dominante": es_estrictamente_dominante,
        "es_debilmente_dominante": es_debilmente_dominante,
        "detalles_filas": detalles_filas,
        "mensaje_dominancia": mensaje_dominancia,
        "rho_jacobi": rho_jacobi,
        "rho_seidel": rho_seidel,
        "T_jacobi": T_jacobi,
        "T_seidel": T_seidel,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. REORDENAMIENTO DE FILAS (PIVOTAJE ESTRATÉGICO)
# ─────────────────────────────────────────────────────────────────────────────

def evaluar_reordenamiento_filas(A: np.ndarray, b: np.ndarray) -> dict[str, Any]:
    """
    Evalúa si un reordenamiento (permutación de filas) permite:
    1. Lograr diagonal estrictamente dominante por filas (prioridad 1).
    2. Eliminar ceros de la diagonal principal cuando la inicial contiene ceros (prioridad 2).
    3. Mejorar la dominancia diagonal general.

    Si no se encuentra ningún ordenamiento válido (p. ej. ceros insalvables),
    lo informa explícitamente sin forzar reordenamientos inválidos.
    """
    n = A.shape[0]
    filas = list(range(n))

    diag_inicial = np.diag(A)
    ceros_inicial = any(math.isclose(d, 0.0, abs_tol=1e-12) for d in diag_inicial)

    # Revisar si ya es estrictamente dominante
    analisis_orig = analizar_diagonal_y_convergencia(A)
    if analisis_orig["es_estrictamente_dominante"]:
        return {
            "requiere_reordenamiento": False,
            "es_posible": True,
            "tipo_resultado": "YA_DOMINANTE",
            "mensaje": "La matriz ya es estrictamente diagonal dominante. No requiere reordenamiento.",
            "permutacion": filas,
            "A_reordenada": A.copy(),
            "b_reordenado": b.copy(),
            "cambios": [],
            "analisis": analisis_orig,
        }

    # Probar permutaciones posibles
    # Para n <= 8 son hasta 40,320 permutaciones (ejecuta en milisegundos)
    # Si n > 8 se usa búsqueda voraz / heurística de pivote máximo
    mejor_perm = None
    mejor_es_estricta = False
    mejor_puntuacion = -float("inf")

    candidatos_perms: Any = itertools.permutations(filas) if n <= 8 else _permutaciones_heuristica(A)

    for perm in candidatos_perms:
        A_p = A[list(perm), :]
        diag_p = np.diag(A_p)

        # Descartar si tiene ceros en la diagonal
        if any(math.isclose(d, 0.0, abs_tol=1e-12) for d in diag_p):
            continue

        abs_diag = np.abs(diag_p)
        sumas = np.sum(np.abs(A_p), axis=1) - abs_diag
        diffs = abs_diag - sumas

        es_estricta = bool(np.all(diffs > 1e-12))
        # Puntuación basada en el margen mínimo de dominancia
        puntuacion = float(np.min(diffs))

        if es_estricta:
            mejor_perm = perm
            mejor_es_estricta = True
            mejor_puntuacion = puntuacion
            break  # Encontramos la configuración ideal (estrictamente dominante)

        if puntuacion > mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_perm = perm

    if mejor_perm is None:
        return {
            "requiere_reordenamiento": True,
            "es_posible": False,
            "tipo_resultado": "NO_POSIBLE",
            "mensaje": (
                "❌ No se encontró ningún ordenamiento de filas que elimine los ceros de la diagonal "
                "o forme una diagonal adecuada. Las ecuaciones no admiten una reestructuración válida."
            ),
            "permutacion": filas,
            "A_reordenada": A.copy(),
            "b_reordenado": b.copy(),
            "cambios": [],
            "analisis": analisis_orig,
        }

    es_misma_permutacion = list(mejor_perm) == filas
    if es_misma_permutacion:
        return {
            "requiere_reordenamiento": False,
            "es_posible": True,
            "tipo_resultado": "OPTIMO_ACTUAL",
            "mensaje": (
                "ℹ️ El orden actual de ecuaciones es el más favorable disponible, aunque no alcanza "
                "dominancia diagonal estricta. No se forzó reordenamiento."
            ),
            "permutacion": filas,
            "A_reordenada": A.copy(),
            "b_reordenado": b.copy(),
            "cambios": [],
            "analisis": analisis_orig,
        }

    # Describir los intercambios de ecuaciones realizados
    cambios = []
    for nueva_pos, vieja_pos in enumerate(mejor_perm):
        if nueva_pos != vieja_pos:
            cambios.append(f"Nueva Fila {nueva_pos + 1} ← Ecuación original {vieja_pos + 1}")

    A_reord = A[list(mejor_perm), :]
    b_reord = b[list(mejor_perm)]
    analisis_nuevo = analizar_diagonal_y_convergencia(A_reord)

    if mejor_es_estricta:
        mensaje = (
            "✅ Reordenamiento exitoso: Al permutar las filas, la matriz pasa a ser "
            "ESTRICTAMENTE DIAGONAL DOMINANTE por filas, garantizando la convergencia de Jacobi y Gauss-Seidel."
        )
        tipo_res = "CONV_ESTRICTA"
    else:
        mensaje = (
            "⚠️ Reordenamiento parcial: Se eliminaron los ceros de la diagonal y se optimizó la estructura, "
            "aunque no se alcanza la condición suficiente de dominancia estricta."
        )
        tipo_res = "SIN_CEROS"

    return {
        "requiere_reordenamiento": True,
        "es_posible": True,
        "tipo_resultado": tipo_res,
        "mensaje": mensaje,
        "permutacion": list(mejor_perm),
        "A_reordenada": A_reord,
        "b_reordenado": b_reord,
        "cambios": cambios,
        "analisis": analisis_nuevo,
    }


def _permutaciones_heuristica(A: np.ndarray) -> list[tuple[int, ...]]:
    """Genera permutaciones heurísticas ordenando cada fila por el máximo coeficiente."""
    n = A.shape[0]
    # Asignación voraz por pivote máximo
    filas_disp = set(range(n))
    perm = []
    for j in range(n):
        mejor_i = max(filas_disp, key=lambda i: abs(A[i, j]))
        perm.append(mejor_i)
        filas_disp.remove(mejor_i)
    return [tuple(perm), tuple(range(n))]


# ─────────────────────────────────────────────────────────────────────────────
# 3. ALGORITMO DE JACOBI
# ─────────────────────────────────────────────────────────────────────────────

def metodo_jacobi(
    A: np.ndarray,
    b: np.ndarray,
    x0: np.ndarray | None = None,
    tol: float = 1e-4,
    max_iter: int = 100
) -> ResultadoMetodoIterativo:
    """
    Método Iterativo de Jacobi para resolver Ax = b.

    CARACTERÍSTICA ESENCIAL (Algorítmica):
    Actualización simultánea: En cada iteración k, TODOS los componentes nuevos x_i^(k)
    se calculan utilizando EXCLUSIVAMENTE los valores de la iteración anterior x^(k-1):

        x_i^(k) = (1 / a_ii) · [ b_i - ∑_{j ≠ i} a_ij · x_j^(k-1) ]

    Criterio de parada:
        ||x^(k) - x^(k-1)||_∞ ≤ ε

    Seguimiento de residuo:
        ||Ax^(k) - b||_∞
    """
    t0 = time.perf_counter()
    A_np, b_np, x_prev, err_val = validar_entradas_iterativas(A, b, x0, tol, max_iter)
    if err_val:
        return ResultadoMetodoIterativo(
            metodo="Jacobi", convergio=False, estado="ERROR_ENTRADA",
            mensaje=err_val, num_iteraciones=0, x_final=np.empty(0),
            error_final=float("nan"), residuo_final=float("nan"), tiempo_ms=0.0
        )

    n = A_np.shape[0]
    diag = np.diag(A_np)

    # Validar que no existan ceros en la diagonal
    for i in range(n):
        if math.isclose(diag[i], 0.0, abs_tol=1e-12):
            return ResultadoMetodoIterativo(
                metodo="Jacobi", convergio=False, estado="ERROR_DIAGONAL",
                mensaje=f"Error fatal: El elemento a_{{{i+1},{i+1}}} en la diagonal principal es CERO. No es posible dividir por cero.",
                num_iteraciones=0, x_final=x_prev.copy(),
                error_final=float("nan"), residuo_final=float("nan"), tiempo_ms=0.0
            )

    # Análisis de la matriz de iteración
    analisis = analizar_diagonal_y_convergencia(A_np)
    rho_j = analisis.get("rho_jacobi")
    T_j = analisis.get("T_jacobi")

    historial: list[IteracionRegistro] = []
    # Registro de la iteración 0
    residuo_0 = float(np.max(np.abs(A_np @ x_prev - b_np)))
    historial.append(IteracionRegistro(k=0, x=x_prev.copy(), error=float("nan"), residuo=residuo_0))

    x_curr = np.zeros(n, dtype=np.float64)
    convergio = False
    estado = "MAX_ITER"
    mensaje = f"Se alcanzó el número máximo de iteraciones ({max_iter}) sin satisfacer la tolerancia ε = {tol}."

    for k in range(1, max_iter + 1):
        # ── CÁLCULO DE JACOBI: Exclusivamente x^(k-1) para todos los componentes ──
        for i in range(n):
            # Suma de a_ij * x_j^(k-1) para j != i
            suma = 0.0
            for j in range(n):
                if j != i:
                    suma += A_np[i, j] * x_prev[j]
            x_curr[i] = (b_np[i] - suma) / diag[i]

        # Verificar valores no finitos (NaN o Inf) por divergencia descontrolada
        if not np.all(np.isfinite(x_curr)):
            estado = "DIVERGENCIA"
            mensaje = f"⚠️ Divergencia detectada en la iteración {k}: los valores generaron desbordamiento numérico (Inf/NaN)."
            x_prev = x_curr.copy()
            break

        # Error entre iteraciones sucesivas: norma infinito ||x^(k) - x^(k-1)||_∞
        error_k = float(np.max(np.abs(x_curr - x_prev)))
        # Residuo: ||Ax^(k) - b||_∞
        residuo_k = float(np.max(np.abs(A_np @ x_curr - b_np)))

        historial.append(IteracionRegistro(k=k, x=x_curr.copy(), error=error_k, residuo=residuo_k))

        # Detección preventiva de divergencia si el error explota
        if error_k > 1e12 or (k > 5 and error_k > 1e6 and error_k > historial[k-1].error * 2.0):
            estado = "DIVERGENCIA"
            mensaje = f"⚠️ Divergencia evidente en la iteración {k}: el error creció exponencialmente ({error_k:.4e})."
            x_prev = x_curr.copy()
            break

        # Criterio de parada
        if error_k <= tol:
            convergio = True
            estado = "CONVERGENCIA"
            mensaje = f"✅ Convergencia alcanzada en {k} iteraciones con error {error_k:.6e} ≤ {tol}."
            x_prev = x_curr.copy()
            break

        x_prev = x_curr.copy()

    t1 = time.perf_counter()
    tiempo_ms = (t1 - t0) * 1000.0

    ultimo_reg = historial[-1]
    return ResultadoMetodoIterativo(
        metodo="Jacobi",
        convergio=convergio,
        estado=estado,
        mensaje=mensaje,
        num_iteraciones=len(historial) - 1,
        x_final=ultimo_reg.x.copy(),
        error_final=ultimo_reg.error,
        residuo_final=ultimo_reg.residuo,
        tiempo_ms=tiempo_ms,
        historial=historial,
        radio_espectral=rho_j,
        matriz_iteracion=T_j,
        tolerancia_usada=tol,
        max_iter_usado=max_iter,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4. ALGORITMO DE GAUSS-SEIDEL
# ─────────────────────────────────────────────────────────────────────────────

def metodo_gauss_seidel(
    A: np.ndarray,
    b: np.ndarray,
    x0: np.ndarray | None = None,
    tol: float = 1e-4,
    max_iter: int = 100
) -> ResultadoMetodoIterativo:
    """
    Método Iterativo de Gauss-Seidel para resolver Ax = b.

    CARACTERÍSTICA ESENCIAL (Algorítmica):
    Actualización inmediata/sucesiva: Tan pronto se calcula una nueva componente x_i^(k),
    se utiliza DE INMEDIATO para calcular las siguientes componentes x_{i+1}^(k), ..., x_n^(k)
    dentro de la misma iteración k:

        x_i^(k) = (1 / a_ii) · [ b_i - ∑_{j < i} a_ij · x_j^(k) - ∑_{j > i} a_ij · x_j^(k-1) ]

    Criterio de parada:
        ||x^(k) - x^(k-1)||_∞ ≤ ε

    Seguimiento de residuo:
        ||Ax^(k) - b||_∞
    """
    t0 = time.perf_counter()
    A_np, b_np, x_prev, err_val = validar_entradas_iterativas(A, b, x0, tol, max_iter)
    if err_val:
        return ResultadoMetodoIterativo(
            metodo="Gauss-Seidel", convergio=False, estado="ERROR_ENTRADA",
            mensaje=err_val, num_iteraciones=0, x_final=np.empty(0),
            error_final=float("nan"), residuo_final=float("nan"), tiempo_ms=0.0
        )

    n = A_np.shape[0]
    diag = np.diag(A_np)

    # Validar que no existan ceros en la diagonal
    for i in range(n):
        if math.isclose(diag[i], 0.0, abs_tol=1e-12):
            return ResultadoMetodoIterativo(
                metodo="Gauss-Seidel", convergio=False, estado="ERROR_DIAGONAL",
                mensaje=f"Error fatal: El elemento a_{{{i+1},{i+1}}} en la diagonal principal es CERO. No es posible dividir por cero.",
                num_iteraciones=0, x_final=x_prev.copy(),
                error_final=float("nan"), residuo_final=float("nan"), tiempo_ms=0.0
            )

    # Análisis de la matriz de iteración
    analisis = analizar_diagonal_y_convergencia(A_np)
    rho_gs = analisis.get("rho_seidel")
    T_gs = analisis.get("T_seidel")

    historial: list[IteracionRegistro] = []
    # Registro de la iteración 0
    residuo_0 = float(np.max(np.abs(A_np @ x_prev - b_np)))
    historial.append(IteracionRegistro(k=0, x=x_prev.copy(), error=float("nan"), residuo=residuo_0))

    # Vector de trabajo donde se actualizarán los valores en sitio
    x_curr = x_prev.copy()
    convergio = False
    estado = "MAX_ITER"
    mensaje = f"Se alcanzó el número máximo de iteraciones ({max_iter}) sin satisfacer la tolerancia ε = {tol}."

    for k in range(1, max_iter + 1):
        x_viejo = x_curr.copy()

        # ── CÁLCULO DE GAUSS-SEIDEL: Actualización inmediata componente a componente ──
        for i in range(n):
            # Suma de a_ij * x_j^(k) para j < i (valores recién calculados en esta iteración)
            suma_nuevos = 0.0
            for j in range(i):
                suma_nuevos += A_np[i, j] * x_curr[j]

            # Suma de a_ij * x_j^(k-1) para j > i (valores de la iteración anterior)
            suma_viejos = 0.0
            for j in range(i + 1, n):
                suma_viejos += A_np[i, j] * x_curr[j]

            # Actualización inmediata en sitio
            x_curr[i] = (b_np[i] - suma_nuevos - suma_viejos) / diag[i]

        # Verificar valores no finitos (NaN o Inf)
        if not np.all(np.isfinite(x_curr)):
            estado = "DIVERGENCIA"
            mensaje = f"⚠️ Divergencia detectada en la iteración {k}: los valores generaron desbordamiento numérico (Inf/NaN)."
            break

        # Error entre iteraciones: ||x^(k) - x^(k-1)||_∞
        error_k = float(np.max(np.abs(x_curr - x_viejo)))
        # Residuo: ||Ax^(k) - b||_∞
        residuo_k = float(np.max(np.abs(A_np @ x_curr - b_np)))

        historial.append(IteracionRegistro(k=k, x=x_curr.copy(), error=error_k, residuo=residuo_k))

        # Detección preventiva de divergencia si el error explota
        if error_k > 1e12 or (k > 5 and error_k > 1e6 and error_k > historial[k-1].error * 2.0):
            estado = "DIVERGENCIA"
            mensaje = f"⚠️ Divergencia evidente en la iteración {k}: el error creció exponencialmente ({error_k:.4e})."
            break

        # Criterio de parada
        if error_k <= tol:
            convergio = True
            estado = "CONVERGENCIA"
            mensaje = f"✅ Convergencia alcanzada en {k} iteraciones con error {error_k:.6e} ≤ {tol}."
            break

    t1 = time.perf_counter()
    tiempo_ms = (t1 - t0) * 1000.0

    ultimo_reg = historial[-1]
    return ResultadoMetodoIterativo(
        metodo="Gauss-Seidel",
        convergio=convergio,
        estado=estado,
        mensaje=mensaje,
        num_iteraciones=len(historial) - 1,
        x_final=ultimo_reg.x.copy(),
        error_final=ultimo_reg.error,
        residuo_final=ultimo_reg.residuo,
        tiempo_ms=tiempo_ms,
        historial=historial,
        radio_espectral=rho_gs,
        matriz_iteracion=T_gs,
        tolerancia_usada=tol,
        max_iter_usado=max_iter,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5. COMPARACIÓN Y VALIDACIÓN CON SOLUCIÓN DE REFERENCIA
# ─────────────────────────────────────────────────────────────────────────────

def comparar_jacobi_y_seidel(
    res_j: ResultadoMetodoIterativo,
    res_gs: ResultadoMetodoIterativo,
    A: np.ndarray,
    b: np.ndarray
) -> dict[str, Any]:
    """
    Compara exhaustivamente los resultados de Jacobi y Gauss-Seidel:
    - Número de iteraciones y velocidad relativa.
    - Diferencia entre ambas soluciones aproximadas: ||x_J - x_GS||_∞.
    - Validación contra solución exacta de referencia (numpy.linalg.solve).
    - Diferencia con la referencia y residuo ||Ax - b||_∞.
    """
    # Solución de referencia exacta
    x_ref: np.ndarray | None = None
    residuo_ref: float | None = None
    error_ref_j: float | None = None
    error_ref_gs: float | None = None
    cond_matriz: float | None = None

    try:
        cond_matriz = float(np.linalg.cond(A))
        x_ref = np.linalg.solve(A, b)
        residuo_ref = float(np.max(np.abs(A @ x_ref - b)))
    except Exception:
        x_ref = None
        residuo_ref = None

    # Diferencia entre soluciones aproximadas
    diff_entre_metodos: float | None = None
    vec_diff: np.ndarray | None = None
    if len(res_j.x_final) > 0 and len(res_gs.x_final) > 0 and len(res_j.x_final) == len(res_gs.x_final):
        vec_diff = np.abs(res_j.x_final - res_gs.x_final)
        diff_entre_metodos = float(np.max(vec_diff))

    if x_ref is not None:
        if len(res_j.x_final) == len(x_ref):
            error_ref_j = float(np.max(np.abs(res_j.x_final - x_ref)))
        if len(res_gs.x_final) == len(x_ref):
            error_ref_gs = float(np.max(np.abs(res_gs.x_final - x_ref)))

    # Veredicto de eficiencia
    if res_j.convergio and res_gs.convergio:
        if res_gs.num_iteraciones < res_j.num_iteraciones:
            ahorro = res_j.num_iteraciones - res_gs.num_iteraciones
            porc = (ahorro / res_j.num_iteraciones) * 100.0
            veredicto = (
                f"🏆 Gauss-Seidel fue más eficiente: requirió {res_gs.num_iteraciones} iteraciones "
                f"frente a {res_j.num_iteraciones} de Jacobi (ahorro del {porc:.1f}% de iteraciones)."
            )
        elif res_j.num_iteraciones < res_gs.num_iteraciones:
            ahorro = res_gs.num_iteraciones - res_j.num_iteraciones
            porc = (ahorro / res_gs.num_iteraciones) * 100.0
            veredicto = (
                f"🏆 Jacobi requirió menos iteraciones ({res_j.num_iteraciones} vs {res_gs.num_iteraciones}). "
                f"(Caso inusual donde Jacobi superó a Gauss-Seidel)."
            )
        else:
            veredicto = f"🤝 Ambos métodos requirieron exactamente el mismo número de iteraciones ({res_j.num_iteraciones})."
    elif res_gs.convergio and not res_j.convergio:
        veredicto = "🏆 Solo Gauss-Seidel convergió; Jacobi divergió o superó el máximo de iteraciones."
    elif res_j.convergio and not res_gs.convergio:
        veredicto = "🏆 Solo Jacobi convergió; Gauss-Seidel divergió o superó el máximo de iteraciones."
    else:
        veredicto = "⚠️ Ninguno de los dos métodos alcanzó la convergencia deseada."

    return {
        "veredicto": veredicto,
        "iter_jacobi": res_j.num_iteraciones,
        "iter_seidel": res_gs.num_iteraciones,
        "convergio_jacobi": res_j.convergio,
        "convergio_seidel": res_gs.convergio,
        "residuo_jacobi": res_j.residuo_final,
        "residuo_seidel": res_gs.residuo_final,
        "diff_entre_metodos": diff_entre_metodos,
        "vector_diferencia": vec_diff,
        "x_ref": x_ref,
        "residuo_ref": residuo_ref,
        "error_ref_j": error_ref_j,
        "error_ref_gs": error_ref_gs,
        "cond_matriz": cond_matriz,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. CASOS DE PRUEBA OFICIALES PRECONFIGURADOS
# ─────────────────────────────────────────────────────────────────────────────

CASOS_PRUEBA = [
    {
        "id": "caso_1",
        "nombre": "Caso 1: Convergencia (Estrictamente Diagonal Dominante 3×3)",
        "descripcion": (
            "Matriz con diagonal estrictamente dominante: |10|>3, |5|>2, |10|>5.\n"
            "Garantiza convergencia tanto en Jacobi como en Gauss-Seidel.\n"
            "Solución exacta entera: x = [1, -2, 1]."
        ),
        "A": [
            [10.0, 2.0, 1.0],
            [1.0, 5.0, 1.0],
            [2.0, 3.0, 10.0]
        ],
        "b": [7.0, -8.0, 6.0],
        "x0": [0.0, 0.0, 0.0],
        "tol": 1e-4,
        "max_iter": 50,
        "categoria": "Convergencia"
    },
    {
        "id": "caso_1b",
        "nombre": "Caso 1B: Convergencia de Alta Dimensión (4×4)",
        "descripcion": (
            "Sistema 4×4 estrictamente diagonal dominante.\n"
            "Permite comprobar el escalamiento y la aceleración de Gauss-Seidel.\n"
            "Solución exacta: x = [1, 2, -1, 1]."
        ),
        "A": [
            [10.0, -1.0, 2.0, 0.0],
            [-1.0, 11.0, -1.0, 3.0],
            [2.0, -1.0, 10.0, -1.0],
            [0.0, 3.0, -1.0, 8.0]
        ],
        "b": [6.0, 25.0, -11.0, 15.0],
        "x0": [0.0, 0.0, 0.0, 0.0],
        "tol": 1e-5,
        "max_iter": 60,
        "categoria": "Convergencia"
    },
    {
        "id": "caso_2",
        "nombre": "Caso 2: Reordenamiento / Cero en la Diagonal Principal (3×3)",
        "descripcion": (
            "La diagonal inicial tiene un cero en a_11 = 0 (imposible dividir por cero).\n"
            "Al reordenar filas (Fila 2→1, Fila 3→2, Fila 1→3):\n"
            "  Fila 1: [4, 1, -1] (|4| > 2)\n"
            "  Fila 2: [1, 8, 2]  (|8| > 3)\n"
            "  Fila 3: [0, 2, 5]  (|5| > 2)\n"
            "¡El reordenamiento la transforma en estrictamente dominante y converge!"
        ),
        "A": [
            [0.0, 2.0, 5.0],
            [4.0, 1.0, -1.0],
            [1.0, 8.0, 2.0]
        ],
        "b": [9.0, 3.0, 13.0],
        "x0": [0.0, 0.0, 0.0],
        "tol": 1e-4,
        "max_iter": 50,
        "categoria": "Reordenamiento"
    },
    {
        "id": "caso_2b",
        "nombre": "Caso 2B: Cero en Diagonal Insalvable (Sin Reordenamiento Válido)",
        "descripcion": (
            "Matriz con restricción estructural: las filas 1 y 2 solo tienen coeficientes\n"
            "no nulos en la columna 3. Es matemáticamente imposible permutar las filas sin que\n"
            "al menos una posición diagonal quede en cero (Teorema de Hall / Emparejamiento Bipartito).\n"
            "Demuestra que el programa detecta cuando NO existe reordenamiento matemáticamente posible "
            "y no fuerza un reordenamiento inválido."
        ),
        "A": [
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 2.0],
            [3.0, 4.0, 5.0]
        ],
        "b": [4.0, 6.0, 8.0],
        "x0": [0.0, 0.0, 0.0],
        "tol": 1e-4,
        "max_iter": 50,
        "categoria": "Reordenamiento"
    },
    {
        "id": "caso_3",
        "nombre": "Caso 3: Advertencia / Divergencia (No Dominante con ρ > 1)",
        "descripcion": (
            "Matriz sin dominancia diagonal: |1|<2, |1|<3.\n"
            "Radios espectrales: ρ(T_J) = √6 ≈ 2.45 > 1 y ρ(T_GS) = 6 > 1.\n"
            "Demuestra la divergencia matemática y activa la advertencia de no convergencia "
            "sin colapsar la calculadora."
        ),
        "A": [
            [1.0, 2.0],
            [3.0, 1.0]
        ],
        "b": [5.0, 7.0],
        "x0": [0.0, 0.0],
        "tol": 1e-4,
        "max_iter": 30,
        "categoria": "Divergencia"
    },
    {
        "id": "caso_3b",
        "nombre": "Caso 3B: No Dominante pero SÍ Converge (ρ < 1)",
        "descripcion": (
            "Matriz A = [[4, 5], [1, 2]].\n"
            "Fila 1: |4| < 5 (¡NO es diagonalmente dominante!).\n"
            "Sin embargo, el radio espectral es ρ(T_J) = √(5/8) ≈ 0.791 < 1 y ρ(T_GS) = 0.625 < 1.\n"
            "¡Demuestra que la dominancia diagonal es condición SUFICIENTE pero NO necesaria!\n"
            "Ambos métodos convergen a x = [1, 2]."
        ),
        "A": [
            [4.0, 5.0],
            [1.0, 2.0]
        ],
        "b": [14.0, 5.0],
        "x0": [0.0, 0.0],
        "tol": 1e-4,
        "max_iter": 60,
        "categoria": "Divergencia"
    }
]
