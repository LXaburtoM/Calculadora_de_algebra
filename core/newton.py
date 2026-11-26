"""Aproximación de raíces reales mediante tangentes sucesivas."""
import ast
from dataclasses import dataclass

import numpy as np
import pandas as pd
import sympy as sp

from core.parser import LOCAL_MATH_DICT

X = sp.Symbol("x", real=True)
COLUMNAS = ["i", "xᵢ", "f(xᵢ)", "f′(xᵢ)", "xᵢ₊₁", "Error", "Unidad"]
CRITERIO = ("Parada por valor de función cero o por error y residuo dentro de la "
            "tolerancia. El error es porcentual, salvo al llegar a x = 0, donde es absoluto.")


def interpretar(texto):
    simbolos = dict(LOCAL_MATH_DICT, x=X)
    texto = texto.strip().replace("^", "**").replace("√", "sqrt")
    try:
        arbol = ast.parse(texto, mode="eval")
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Call):
                if not (isinstance(nodo.func, ast.Name) and callable(simbolos.get(nodo.func.id))
                        and len(nodo.args) == 1 and not nodo.keywords):
                    raise ValueError
            elif isinstance(nodo, ast.Name):
                if nodo.id not in simbolos:
                    raise ValueError
            elif isinstance(nodo, ast.Constant):
                if type(nodo.value) not in (float, int):
                    raise ValueError
            elif not isinstance(nodo, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Load,
                                       ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
                                       ast.USub, ast.UAdd)):
                raise ValueError
        funcion = sp.sympify(texto, locals=simbolos, evaluate=False)
        if not isinstance(funcion, sp.Expr):
            raise ValueError
        return funcion
    except (SyntaxError, TypeError, ValueError, AttributeError, sp.SympifyError) as exc:
        raise ValueError("Revisá f(x). Usá x, operaciones como 2*x y funciones como sen(x).") from exc


@dataclass
class Resultado:
    funcion: sp.Expr
    derivada: sp.Expr
    evaluar: object
    tabla: pd.DataFrame
    estado: str
    x: float
    residuo: float


def valor_real(evaluar, punto):
    try:
        with np.errstate(all="ignore"):
            valor = evaluar(np.float64(punto))
        if np.isrealobj(valor) and np.isfinite(valor):
            return float(valor)
    except (ArithmeticError, ValueError, TypeError):
        pass
    return np.nan


def resolver(texto, inicial, tolerancia, maximo):
    if not np.isfinite(inicial):
        raise ValueError("Ingresá un valor inicial finito.")
    if not np.isfinite(tolerancia) or tolerancia <= 0:
        raise ValueError("La tolerancia debe ser positiva y finita.")
    if not isinstance(maximo, int) or maximo < 1:
        raise ValueError("El máximo de iteraciones debe ser un entero positivo.")

    funcion = interpretar(texto)
    derivada = sp.diff(funcion, X)
    try:
        evaluar = sp.lambdify(X, funcion, "numpy")
        pendiente = sp.lambdify(X, derivada, "numpy")
    except (TypeError, ValueError, NotImplementedError, KeyError) as exc:
        raise ValueError("La función o su derivada no admite evaluación numérica real.") from exc

    x = float(inicial)
    fx = valor_real(evaluar, x)
    filas = []
    estado = "Máximo de iteraciones alcanzado sin convergencia."
    if not np.isfinite(fx):
        estado = "La función no tiene un valor real finito en x₀."
    elif fx == 0:
        estado = "Convergencia alcanzada en el valor inicial."
    else:
        for i in range(1, maximo + 1):
            df = valor_real(pendiente, x)
            if not np.isfinite(df):
                estado = "La derivada no tiene un valor real finito en la aproximación actual."
                break
            if abs(df) <= 1e-12:
                estado = "Derivada nula o cercana a cero. No se puede dar otro paso."
                break
            siguiente = x - fx / df
            if not np.isfinite(siguiente):
                estado = "La siguiente aproximación no es finita."
                break
            paso = abs(siguiente - x)
            error = abs((siguiente - x) / siguiente) * 100 if siguiente else paso
            if not np.isfinite(error):
                estado = "El error calculado no es finito."
                break
            filas.append((i, x, fx, df, siguiente, error, "%" if siguiente else "abs."))
            x = siguiente
            fx = valor_real(evaluar, x)
            if not np.isfinite(fx):
                estado = "La función salió del dominio real finito."
                break
            if fx == 0 or (error <= tolerancia and abs(fx) <= tolerancia):
                estado = "Convergencia alcanzada."
                break
    return Resultado(funcion, derivada, evaluar, pd.DataFrame(filas, columns=COLUMNAS),
                     estado, x, abs(fx))
