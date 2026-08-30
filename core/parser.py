"""
Módulo de Lectura, Evaluación y Conversión de Expresiones Matemáticas y Fracciones.
Soporta:
- Constantes: pi, PI, Pi, π, e, E
- Fracciones y decimales: 1/2, -3/4, 2.5
- Funciones trigonométricas en español e inglés:
  * tangente, tan, tg
  * cotangente, cot, ctg
  * seno, sen, sin
  * coseno, cos
  * secante, sec
  * cosecante, csc
- Raíces y potencias: raiz(16), raíz(25), sqrt(9), 2^3
- Logaritmos y exponenciales: ln(e), exp(0), abs(-5)
- Manejo de Errores: Captura divisiones por cero, asíntotas e indeterminaciones.
"""

from fractions import Fraction
import re
import sympy as sp

# Diccionario de funciones y constantes en español e inglés
LOCAL_MATH_DICT = {
    'pi': sp.pi, 'PI': sp.pi, 'Pi': sp.pi, 'π': sp.pi,
    'e': sp.E, 'E': sp.E, 'euler': sp.E, 'Euler': sp.E,
    'sen': sp.sin, 'seno': sp.sin, 'sin': sp.sin,
    'cos': sp.cos, 'coseno': sp.cos,
    'tan': sp.tan, 'tangente': sp.tan, 'tg': sp.tan,
    'cot': sp.cot, 'cotangente': sp.cot, 'ctg': sp.cot, 'cotg': sp.cot,
    'sec': sp.sec, 'secante': sp.sec,
    'csc': sp.csc, 'cosecante': sp.csc, 'cosec': sp.csc,
    'arcsen': sp.asin, 'arcsin': sp.asin, 'arcoseno': sp.asin, 'asen': sp.asin,
    'arccos': sp.acos, 'arcocoseno': sp.acos, 'acos': sp.acos,
    'arctan': sp.atan, 'arcotangente': sp.atan, 'atan': sp.atan, 'arctg': sp.atan,
    'arccot': sp.acot, 'arcocotangente': sp.acot, 'acot': sp.acot,
    'raiz': sp.sqrt, 'raíz': sp.sqrt, 'sqrt': sp.sqrt,
    'ln': sp.log, 'log': sp.log,
    'abs': sp.Abs, 'absoluto': sp.Abs,
    'exp': sp.exp
}

def parse_expresion(texto: str) -> tuple[Fraction | None, str | None]:
    """
    Parsea una cadena de texto y devuelve una tupla (Fraction_obj, error_msg).
    Si es correcto, error_msg es None.
    Si falla, Fraction_obj es None y error_msg contiene la explicación clara del error.
    """
    if not texto or not str(texto).strip():
        return Fraction(0), None

    limpio = str(texto).strip().replace(",", ".")
    # Normalización de caracteres comunes
    limpio = limpio.replace("^", "**").replace("π", "pi").replace("√", "sqrt")

    # 1. Intento directo como Fracción "a/b" simple
    if re.match(r"^\s*[-+]?\s*\d+\s*/\s*[-+]?\s*\d+\s*$", limpio):
        partes = limpio.split("/")
        try:
            num = int(partes[0].strip())
            den = int(partes[1].strip())
            if den == 0:
                return None, "División por cero no permitida (denominador cero)."
            return Fraction(num, den), None
        except Exception as e:
            return None, f"Fracción no válida: {e}"

    # 2. Intento directo como float / entero
    try:
        val_f = float(limpio)
        frac = Fraction(limpio).limit_denominator(1000000)
        return frac, None
    except Exception:
        pass

    # 3. Evaluación simbólica y trigonométrica avanzada
    try:
        expr = sp.sympify(limpio, locals=LOCAL_MATH_DICT)
        
        # Verificar si quedaron variables no reconocidas (ej: x, y, abc)
        if expr.free_symbols:
            vars_desconocidas = ", ".join(str(s) for s in expr.free_symbols)
            return None, f"Símbolo o variable no reconocida: '{vars_desconocidas}'."

        val_evaluated = expr.evalf()
        
        # Verificar indeterminaciones (infinito, división por cero, números complejos)
        if str(val_evaluated) in ('zoo', 'nan', 'oo', '-oo') or not val_evaluated.is_real:
            return None, "Indefinición matemática (resultado infinito, asíntota o no definido)."

        val_num = float(val_evaluated)
        frac = Fraction.from_float(val_num).limit_denominator(1000000)
        return frac, None
    except ZeroDivisionError:
        return None, "División por cero en la expresión."
    except Exception:
        return None, f"Expresión matemática '{texto}' no válida."

def formato_numero(valor: Fraction | float | int, modo_fraccion: bool = True) -> str:
    """
    Formatea una Fracción o número para mostrar en tablas o resultados.
    Si modo_fraccion=True, muestra '1/2' o '-3'.
    Si modo_fraccion=False, muestra decimal '0.5000'.
    """
    if valor is None:
        return "0"

    if isinstance(valor, (int, float)):
        valor = Fraction(str(valor)).limit_denominator(1000000)

    if modo_fraccion:
        if valor.denominator == 1:
            return str(valor.numerator)
        return f"{valor.numerator}/{valor.denominator}"
    else:
        val_float = float(valor)
        if val_float.is_integer():
            return str(int(val_float))
        return f"{val_float:.4f}"
