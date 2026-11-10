"""
Módulo 7: Métodos Numéricos.
Tema: Bisección, Graficador de Funciones, Notación Posicional y Errores Numéricos.
Asignatura: Álgebra Lineal (MTM0120) - Universidad Americana (UAM).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

from __future__ import annotations

import math
import warnings
from typing import Callable, Any
import numpy as np
import sympy as sp

# Diccionario seguro de funciones y constantes permitidas para evaluación de funciones
FUNCIONES_PERMITIDAS = {
    'x': sp.Symbol('x'),
    'pi': sp.pi, 'PI': sp.pi, 'Pi': sp.pi, 'π': sp.pi,
    'e': sp.E, 'E': sp.E, 'euler': sp.E,
    'sin': sp.sin, 'sen': sp.sin, 'seno': sp.sin,
    'cos': sp.cos, 'coseno': sp.cos,
    'tan': sp.tan, 'tangente': sp.tan, 'tg': sp.tan,
    'asin': sp.asin, 'arcsen': sp.asin, 'arcsin': sp.asin,
    'acos': sp.acos, 'arccos': sp.acos,
    'atan': sp.atan, 'arctan': sp.atan, 'arctg': sp.atan,
    'exp': sp.exp,
    'log': sp.log, 'ln': sp.log,
    'sqrt': sp.sqrt, 'raiz': sp.sqrt, 'raíz': sp.sqrt,
    'abs': sp.Abs, 'absoluto': sp.Abs,
    'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh
}


def sanitizar_expresion(texto: str) -> str:
    """
    Normaliza caracteres comunes en expresiones matemáticas escritas por el usuario:
    - Reemplaza potencias con caret '^' por '**'
    - Convierte comas decimales ',' en puntos '.'
    - Normaliza símbolos de raíz '√' y pi 'π'
    """
    if not texto:
        return ""
    t = str(texto).strip()
    t = t.replace("^", "**").replace(",", ".").replace("√", "sqrt").replace("π", "pi")
    return t


def compilar_funcion(texto: str) -> tuple[sp.Expr | None, Callable[[float], float] | None, str | None]:
    """
    Compila de manera segura una expresión matemática f(x) ingresada como texto.
    Utiliza SymPy con una lista blanca estricta de funciones y símbolos permitidos
    para evitar el uso peligroso de eval().

    Retorna: (expr_sympy, funcion_nativa, mensaje_error)
    """
    limpio = sanitizar_expresion(texto)
    if not limpio:
        return None, None, "La expresión de la función no puede estar vacía."

    try:
        expr = sp.sympify(limpio, locals=FUNCIONES_PERMITIDAS)
    except Exception as e:
        return None, None, f"Error de sintaxis en la expresión '{texto}': {e}"

    # Validar que los símbolos presentes sean únicamente 'x' (o constantes permitidas)
    simbolos = expr.free_symbols
    simbolo_x = sp.Symbol('x')
    for s in simbolos:
        if s != simbolo_x:
            return None, None, f"Variable o símbolo no autorizado detectado: '{s}'. Use 'x' como variable independiente."

    # Función evaluable de forma segura
    def f_eval(x_val: float) -> float:
        try:
            # Sustitución directa y conversión a float
            res = expr.subs(simbolo_x, x_val).evalf()
            if not res.is_real or str(res) in ('zoo', 'nan', 'oo', '-oo'):
                return float('nan')
            val = float(res)
            return val
        except (ZeroDivisionError, ValueError, OverflowError):
            return float('nan')
        except Exception:
            return float('nan')

    return expr, f_eval, None


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO A: MÉTODO DE BISECCIÓN
# ─────────────────────────────────────────────────────────────────────────────

def metodo_biseccion(
    expr_str: str,
    a: float,
    b: float,
    tol: float = 1e-4,
    max_iter: int = 100
) -> dict[str, Any]:
    """
    Implementación desde cero del Método de Bisección para hallar raíces de f(x) = 0
    en el intervalo [a, b], conforme a los requisitos de la Universidad Americana (UAM).

    Parámetros:
    - expr_str: Cadena con la función f(x) (ej: 'x**3 - 2*x - 5')
    - a: Extremo inferior del intervalo inicial
    - b: Extremo superior del intervalo inicial
    - tol: Tolerancia absoluta de error E > 0 (por defecto 10^-4)
    - max_iter: Límite máximo de iteraciones Nmax >= 1 (por defecto 100)

    Retorna un diccionario con:
    - exito: bool
    - mensaje: str explicativo
    - raiz: float | None
    - f_raiz: float | None
    - iteraciones_realizadas: int
    - n_teorico: int
    - advertencias: list[str]
    - tabla: list[dict] con columnas k, a, b, xr, fa, fb, fr, Eb, Ea, eps_a
    - raiz_scipy: float | None
    - dif_scipy: float | None
    """
    resultado: dict[str, Any] = {
        "exito": False,
        "mensaje": "",
        "raiz": None,
        "f_raiz": None,
        "iteraciones_realizadas": 0,
        "n_teorico": 0,
        "advertencias": [],
        "tabla": [],
        "raiz_scipy": None,
        "dif_scipy": None,
        "a_inicial": a,
        "b_inicial": b,
        "tol": tol,
        "max_iter": max_iter,
        "expr_str": expr_str
    }

    # 1. Validación de entradas básicas
    if a >= b:
        resultado["mensaje"] = f"Límites incorrectos: El extremo inferior a ({a}) debe ser estrictamente menor que b ({b})."
        return resultado

    if tol <= 0:
        resultado["mensaje"] = f"Tolerancia no positiva: La tolerancia absoluta E ({tol}) debe ser mayor que cero."
        return resultado

    if max_iter < 1:
        resultado["mensaje"] = f"Iteraciones inválidas: El número máximo de iteraciones ({max_iter}) debe ser al menos 1."
        return resultado

    # 2. Compilar la función ingresada
    expr, f, err = compilar_funcion(expr_str)
    if err or f is None:
        resultado["mensaje"] = err or "Error al compilar la función."
        return resultado

    # 3. Evaluar extremos del intervalo f(a) y f(b)
    fa = f(a)
    fb = f(b)

    if math.isnan(fa) or math.isinf(fa):
        resultado["mensaje"] = f"La función f(x) no está definida o produce un valor no finito en a = {a}."
        return resultado

    if math.isnan(fb) or math.isinf(fb):
        resultado["mensaje"] = f"La función f(x) no está definida o produce un valor no finito en b = {b}."
        return resultado

    # 4. Caso especial: Raíz exacta en un extremo
    if abs(fa) < 1e-15:
        resultado["exito"] = True
        resultado["raiz"] = a
        resultado["f_raiz"] = 0.0
        resultado["mensaje"] = f"Se encontró una raíz exacta directamente en el extremo inferior: x = {a}."
        return resultado

    if abs(fb) < 1e-15:
        resultado["exito"] = True
        resultado["raiz"] = b
        resultado["f_raiz"] = 0.0
        resultado["mensaje"] = f"Se encontró una raíz exacta directamente en el extremo superior: x = {b}."
        return resultado

    # 5. Condición de cambio de signo (Teorema de Bolzano)
    if fa * fb > 0:
        resultado["mensaje"] = (
            f"El intervalo [{a}, {b}] no cumple la condición de cambio de signo: "
            f"f(a) = {fa:.6g} y f(b) = {fb:.6g} tienen el mismo signo (f(a) · f(b) > 0). "
            f"El Teorema de Bolzano requiere f(a) · f(b) < 0. "
            f"(Nota: Esto no afirma que la función no tenga raíces en otros intervalos)."
        )
        return resultado

    # 6. Verificación de continuidad en el intervalo
    # Muestreo de 120 puntos para detectar asíntotas o discontinuidades tipo 1/x
    puntos_test = np.linspace(a, b, 120)
    hay_discontinuidad = False
    for pt in puntos_test:
        val = f(float(pt))
        if math.isnan(val) or math.isinf(val) or abs(val) > 1e12:
            hay_discontinuidad = True
            break

    if hay_discontinuidad:
        resultado["advertencias"].append(
            "¡ADVERTENCIA DE DISCONTINUIDAD! Se detectó una aparente indeterminación o asíntota en el intervalo. "
            "Aunque los signos en los extremos sean opuestos, el Teorema de Bolzano exige que la función sea CONTINUA "
            "en [a, b]. El método de bisección puede converger a la asíntota en lugar de a una raíz real."
        )

    # 7. Cálculo del número teórico mínimo de iteraciones
    # n_minimo = ceil(log2((b - a) / E))
    ancho_inicial = b - a
    try:
        n_teorico = math.ceil(math.log2(ancho_inicial / tol))
        resultado["n_teorico"] = n_teorico
    except Exception:
        resultado["n_teorico"] = 0

    if max_iter < resultado["n_teorico"]:
        resultado["advertencias"].append(
            f"El máximo de iteraciones fijado ({max_iter}) es menor que el número teórico requerido "
            f"({resultado['n_teorico']}) para garantizar la cota de error E = {tol:.2e}."
        )

    # 8. Proceso iterativo propio (Bisección desde cero)
    a_k = a
    b_k = b
    fa_k = fa
    fb_k = fb
    xr_prev = None
    tolerancia_alcanzada = False
    raiz_exacta = False

    for k in range(1, max_iter + 1):
        xr = (a_k + b_k) / 2.0
        Eb = (b_k - a_k) / 2.0  # Cota del error por semiancho ANTES de actualizar
        fr = f(xr)

        # Cálculo de errores de aproximación entre iteraciones sucesivas
        if k == 1 or xr_prev is None:
            Ea: float | str = "—"
            eps_a: float | str = "—"
        else:
            Ea = abs(xr - xr_prev)
            if abs(xr) > 1e-15:
                eps_a = Ea / abs(xr)
            else:
                eps_a = "No definido"

        # Si se detecta indefinición matemática en xr
        if math.isnan(fr) or math.isinf(fr):
            resultado["advertencias"].append(
                f"Indefinición matemática detectada al evaluar f(xr) en xr = {xr:.8f} (división por cero o asíntota vertical). "
                f"El método no puede continuar porque la función no es continua en el intervalo."
            )
            # Aún registramos la iteración para que la tabla muestre el punto del colapso
            resultado["tabla"].append({
                "k": k, "a": a_k, "b": b_k, "xr": xr,
                "fa": fa_k, "fb": fb_k, "fr": fr,
                "Eb": Eb, "Ea": Ea, "eps_a": eps_a
            })
            resultado["iteraciones_realizadas"] = k
            resultado["raiz"] = xr
            resultado["f_raiz"] = fr
            break

        # Registrar fila en la tabla ANTES de actualizar extremos
        resultado["tabla"].append({
            "k": k,
            "a": a_k,
            "b": b_k,
            "xr": xr,
            "fa": fa_k,
            "fb": fb_k,
            "fr": fr,
            "Eb": Eb,
            "Ea": Ea,
            "eps_a": eps_a
        })

        resultado["iteraciones_realizadas"] = k
        resultado["raiz"] = xr
        resultado["f_raiz"] = fr

        # Parada por raíz exacta en aritmética de máquina
        if abs(fr) == 0.0 or abs(fr) < 1e-15:
            raiz_exacta = True
            break

        # Parada por tolerancia de semiancho
        if Eb <= tol:
            tolerancia_alcanzada = True
            break

        # Actualizar intervalo conservando la mitad con cambio de signo
        if fa_k * fr < 0:
            b_k = xr
            fb_k = fr
        else:
            a_k = xr
            fa_k = fr

        xr_prev = xr

    # 9. Conclusión del estado
    if raiz_exacta:
        resultado["exito"] = True
        resultado["mensaje"] = (
            f"Se encontró una raíz exacta (f(xr) ≈ 0) en la iteración {resultado['iteraciones_realizadas']}: "
            f"x = {resultado['raiz']:.8f}."
        )
    elif tolerancia_alcanzada:
        resultado["exito"] = True
        resultado["mensaje"] = (
            f"Tolerancia alcanzada exitosamente en {resultado['iteraciones_realizadas']} iteraciones. "
            f"Cota de error Eb = {resultado['tabla'][-1]['Eb']:.6e} ≤ E = {tol:.2e}."
        )
    else:
        resultado["exito"] = False
        if resultado["tabla"]:
            ultima_cota = resultado["tabla"][-1]["Eb"]
            resultado["mensaje"] = (
                f"Se detuvo en la iteración {resultado['iteraciones_realizadas']} sin garantizar la tolerancia solicitada. "
                f"Última cota calculada Eb = {ultima_cota:.6e} > E = {tol:.2e}."
            )
        else:
            resultado["mensaje"] = (
                "El método no pudo realizar iteraciones debido a condiciones matemáticas no satisfechas en el intervalo."
            )

    # 10. Validación externa con SciPy (únicamente para contrastar)
    if not hay_discontinuidad:
        try:
            import scipy.optimize as opt
            # Utilizar bisect de SciPy
            raiz_sp = opt.bisect(f, a, b, xtol=tol, maxiter=max_iter)
            resultado["raiz_scipy"] = float(raiz_sp)
            if resultado["raiz"] is not None:
                resultado["dif_scipy"] = abs(float(resultado["raiz"]) - float(raiz_sp))
        except Exception:
            pass

    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO B: GRAFICADOR DE FUNCIONES
# ─────────────────────────────────────────────────────────────────────────────

def preparar_datos_grafica(
    expr_str: str,
    x_min: float,
    x_max: float,
    num_puntos: int = 1500
) -> tuple[np.ndarray | None, np.ndarray | None, str | None]:
    """
    Genera puntos x e y para graficar f(x) en [x_min, x_max].
    Evita unir puntos a través de asíntotas verticales / discontinuidades
    insertando np.nan en los saltos abruptos.
    Controla funciones con dominio restringido (log, sqrt, divisiones).

    Retorna: (x_vals, y_vals, mensaje_error)
    """
    if x_min >= x_max:
        return None, None, f"Límites incorrectos: x_min ({x_min}) debe ser menor que x_max ({x_max})."

    expr, f, err = compilar_funcion(expr_str)
    if err or f is None:
        return None, None, err

    x_raw = np.linspace(x_min, x_max, num_puntos)
    y_list: list[float] = []

    for x_val in x_raw:
        val = f(float(x_val))
        if math.isnan(val) or math.isinf(val) or abs(val) > 1e6:
            y_list.append(np.nan)
        else:
            y_list.append(val)

    y_arr = np.array(y_list, dtype=float)

    # Detección de discontinuidades / asíntotas para no cruzar líneas verticales
    # Si hay un cambio de signo y un salto numérico muy grande en el valor de y:
    for i in range(1, len(y_arr)):
        y_prev = y_arr[i - 1]
        y_curr = y_arr[i]
        if not np.isnan(y_prev) and not np.isnan(y_curr):
            delta_y = abs(y_curr - y_prev)
            # Salto gigantesco con cambio de signo en puntos contiguos
            if delta_y > 50 and (y_prev * y_curr < 0):
                y_arr[i] = np.nan

    return x_raw, y_arr, None


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO C: NOTACIÓN POSICIONAL
# ─────────────────────────────────────────────────────────────────────────────

def descomponer_base10(numero: int) -> dict[str, Any]:
    """
    Descompone un número entero en base 10 mostrando cada dígito multiplicado
    por su potencia de 10 correspondiente y la suma final.
    Ejemplo: (84506)10 = 8·10^4 + 4·10^3 + 5·10^2 + 0·10^1 + 6·10^0
    """
    es_negativo = numero < 0
    valor_abs = abs(numero)
    s_digits = str(valor_abs)
    n = len(s_digits)

    terminos_polinomicos: list[str] = []
    terminos_valores: list[int] = []

    for i, d in enumerate(s_digits):
        potencia = n - 1 - i
        digito = int(d)
        terminos_polinomicos.append(f"{digito} · 10^{potencia}")
        terminos_valores.append(digito * (10 ** potencia))

    expresion_polinomica = " + ".join(terminos_polinomicos)
    expresion_valores = " + ".join(str(v) for v in terminos_valores)

    if es_negativo:
        polinomica_final = f"-({expresion_polinomica})"
        valores_final = f"-({expresion_valores})"
        res_str = f"-({valor_abs})₁₀ = {numero}"
    else:
        polinomica_final = expresion_polinomica
        valores_final = expresion_valores
        res_str = f"({valor_abs})₁₀ = {numero}"

    return {
        "numero_original": numero,
        "es_negativo": es_negativo,
        "valor_abs": valor_abs,
        "polinomica": polinomica_final,
        "valores": valores_final,
        "resultado_str": res_str,
        "terminos": terminos_polinomicos
    }


def descomponer_base2(binario_str: str) -> dict[str, Any]:
    """
    Descompone un número binario en base 2 mostrando cada bit multiplicado
    por su potencia de 2 correspondiente y la suma final en base 10.
    Ejemplo: (11110011)2 = 1·2^7 + 1·2^6 + 1·2^5 + 1·2^4 + 0·2^3 + 0·2^2 + 1·2^1 + 1·2^0
             = 128 + 64 + 32 + 16 + 2 + 1 = (243)10
    """
    limpio = binario_str.strip()
    es_negativo = limpio.startswith("-")
    if es_negativo:
        limpio = limpio[1:].strip()

    # Validar que contenga únicamente caracteres '0' y '1'
    if not limpio or not all(c in '01' for c in limpio):
        raise ValueError(f"Cadena binaria inválida: '{binario_str}'. Debe contener solo dígitos 0 y 1.")

    n = len(limpio)
    terminos_polinomicos: list[str] = []
    terminos_valores: list[int] = []
    suma_total = 0

    for i, b in enumerate(limpio):
        potencia = n - 1 - i
        bit = int(b)
        terminos_polinomicos.append(f"{bit} · 2^{potencia}")
        val = bit * (2 ** potencia)
        terminos_valores.append(val)
        suma_total += val

    expresion_polinomica = " + ".join(terminos_polinomicos)
    # En la suma mostramos los términos activos (o todos los sumandos)
    expresion_valores = " + ".join(str(v) for v in terminos_valores if v > 0) or "0"

    total_final = -suma_total if es_negativo else suma_total

    if es_negativo:
        polinomica_final = f"-({expresion_polinomica})"
        valores_final = f"-({expresion_valores}) = ({total_final})₁₀"
    else:
        polinomica_final = expresion_polinomica
        valores_final = f"{expresion_valores} = ({total_final})₁₀"

    return {
        "binario_original": binario_str,
        "es_negativo": es_negativo,
        "bits": limpio,
        "polinomica": polinomica_final,
        "valores": valores_final,
        "valor_decimal": total_final,
        "terminos": terminos_polinomicos
    }


def analisis_posicional_completo(numero_input: str) -> dict[str, Any]:
    """
    Realiza el análisis integral de notación posicional:
    Si se ingresa un entero decimal, genera su descomposición en base 10,
    lo convierte a binario y muestra su descomposición en base 2 con verificación
    de equivalencia.
    Si se ingresa un binario (con prefijo '0b' o mediante bandera), realiza la inversa.
    """
    texto = numero_input.strip()
    resultado: dict[str, Any] = {}

    # Caso binario explícito
    if texto.lower().startswith("0b") or (all(c in '01-' for c in texto) and len(texto) >= 4 and not texto.lstrip("-").isdigit()):
        b_clean = texto.lower().replace("0b", "")
        res_b2 = descomponer_base2(b_clean)
        val_dec = res_b2["valor_decimal"]
        res_b10 = descomponer_base10(val_dec)
        resultado = {
            "tipo_origen": "base2",
            "decimal": val_dec,
            "binario": b_clean,
            "info_b10": res_b10,
            "info_b2": res_b2,
            "equivalencia_verificada": True
        }
    else:
        try:
            num_int = int(texto)
        except ValueError:
            raise ValueError(f"Entrada no válida: '{numero_input}'. Ingrese un número entero.")

        res_b10 = descomponer_base10(num_int)
        val_abs = abs(num_int)
        bin_str = bin(val_abs)[2:]
        if num_int < 0:
            bin_str = "-" + bin_str
        res_b2 = descomponer_base2(bin_str)

        resultado = {
            "tipo_origen": "base10",
            "decimal": num_int,
            "binario": bin_str,
            "info_b10": res_b10,
            "info_b2": res_b2,
            "equivalencia_verificada": (num_int == res_b2["valor_decimal"])
        }

    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO D: ERRORES NUMÉRICOS Y PUNTO FLOTANTE
# ─────────────────────────────────────────────────────────────────────────────

def demostracion_punto_flotante() -> dict[str, Any]:
    """
    Ejecuta y explica por qué la comparación '0.1 + 0.2 == 0.3' devuelve False.
    Calcula el épsilon de máquina de NumPy y genera ejemplos controlados de
    overflow y underflow capturando advertencias.
    """
    # 1. Comparación 0.1 + 0.2 == 0.3
    suma = 0.1 + 0.2
    objetivo = 0.3
    resultado_comparacion = (suma == objetivo)
    diferencia = abs(suma - objetivo)

    # 2. Épsilon de máquina (doble precisión float64)
    eps_float = float(np.finfo(float).eps)

    # 3. Ejemplo controlado de Overflow
    advertencia_overflow = ""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # En NumPy, float64(1e308) * 10 produce overflow a inf
        val_overflow = np.float64(1e308) * 10.0
        if w:
            advertencia_overflow = str(w[-1].message)

    # 4. Ejemplo controlado de Underflow
    advertencia_underflow = ""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Número más allá del rango normal de precisión doble (1e-308 / 1e20)
        val_underflow = np.float64(1e-308) / 1e20
        if w:
            advertencia_underflow = str(w[-1].message)

    return {
        "suma_calculada": suma,
        "suma_repr": f"{suma:.17f}",
        "objetivo_repr": f"{objetivo:.17f}",
        "resultado_comparacion": resultado_comparacion,
        "diferencia_exacta": diferencia,
        "epsilon_maquina": eps_float,
        "overflow_resultado": str(val_overflow),
        "overflow_advertencia": advertencia_overflow or "RuntimeWarning: overflow encountered in scalar multiply",
        "underflow_resultado": str(val_underflow),
        "underflow_advertencia": advertencia_underflow or "Pérdida de significancia / número cae a 0.0"
    }


def calcular_errores_absoluto_relativo(xv: float, xa: float) -> dict[str, Any]:
    """
    Calcula el error absoluto, relativo y relativo porcentual entre el valor
    verdadero xv y el valor aproximado xa.
    Si xv == 0, el error relativo no está definido y se indica claramente.
    """
    ea = abs(xv - xa)

    if xv == 0:
        er_str = "No definido (división entre cero: el valor verdadero xv es 0)"
        erp_str = "No definido"
        er_val = None
        erp_val = None
    else:
        er_val = ea / abs(xv)
        erp_val = er_val * 100.0
        er_str = f"{er_val:.6e}"
        erp_str = f"{erp_val:.6f}%"

    return {
        "xv": xv,
        "xa": xa,
        "error_absoluto": ea,
        "error_relativo": er_val,
        "error_relativo_str": er_str,
        "error_porcentual": erp_val,
        "error_porcentual_str": erp_str
    }


def calcular_propagacion_error(
    expr_str: str,
    x_val: float,
    delta_x: float
) -> dict[str, Any]:
    """
    Analiza la propagación del error utilizando aproximación lineal por derivada:
    f'(x) calculada simbólicamente mediante SymPy.
    Δy aproximado = f'(x) · Δx
    Δy real = f(x + Δx) - f(x)
    Diferencia absoluta = |Δy real - Δy aproximado|
    """
    expr, f, err = compilar_funcion(expr_str)
    if err or expr is None or f is None:
        raise ValueError(err or "Error al compilar la función.")

    x_sym = sp.Symbol('x')
    derivada_sym = sp.diff(expr, x_sym)

    # Evaluar derivada en x_val
    try:
        f_prime_val = float(derivada_sym.subs(x_sym, x_val).evalf())
    except Exception as e:
        raise ValueError(f"No se pudo evaluar la derivada en x={x_val}: {e}")

    # Evaluar f(x) y f(x + delta_x)
    fx = f(x_val)
    fx_plus_delta = f(x_val + delta_x)

    if math.isnan(fx) or math.isnan(fx_plus_delta):
        raise ValueError("La función no está definida en x o en x + Δx.")

    delta_y_aprox = f_prime_val * delta_x
    delta_y_real = fx_plus_delta - fx
    dif_absoluta = abs(delta_y_real - delta_y_aprox)

    return {
        "expr_str": expr_str,
        "derivada_str": str(derivada_sym),
        "x": x_val,
        "delta_x": delta_x,
        "f_prime": f_prime_val,
        "delta_y_aprox": delta_y_aprox,
        "delta_y_real": delta_y_real,
        "diferencia_absoluta": dif_absoluta
    }
