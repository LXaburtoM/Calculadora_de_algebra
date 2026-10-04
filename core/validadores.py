"""
Módulo de Validación Centralizada para la Calculadora de Álgebra Lineal.
Tema: Lectura segura de datos desde tablas PyQt6 y formateo de matrices.
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""
from fractions import Fraction
from PyQt6.QtWidgets import QMessageBox
from core.parser import parse_expresion, formato_numero


def leer_matriz_segura(tabla, filas, columnas, etiqueta="A"):
    """Lee una matriz de una QTableWidget validando cada celda.
    Retorna (matriz, lista_de_errores).
    """
    matriz = []
    errores = []
    for i in range(filas):
        fila = []
        for j in range(columnas):
            item = tabla.item(i, j)
            texto = item.text() if item else "0"
            val, err = parse_expresion(texto)
            if err:
                errores.append(f"{etiqueta}[{i+1},{j+1}]: {err}")
            fila.append(val if val is not None else Fraction(0))
        matriz.append(fila)
    return matriz, errores


def leer_vector_seguro(tabla, n, etiqueta="v"):
    """Lee un vector de n componentes desde una tabla de 1 columna.
    Retorna (vector, lista_de_errores).
    """
    vector = []
    errores = []
    for i in range(n):
        item = tabla.item(i, 0)
        texto = item.text() if item else "0"
        val, err = parse_expresion(texto)
        if err:
            errores.append(f"{etiqueta} componente {i+1}: {err}")
        vector.append(val if val is not None else Fraction(0))
    return vector, errores


def leer_escalar_seguro(campo_texto, etiqueta="c"):
    """Lee un valor escalar desde un QLineEdit.
    Retorna (valor_Fraction, error_string_o_None).
    """
    texto = campo_texto.text().strip()
    val, err = parse_expresion(texto)
    if err:
        return None, f"{etiqueta}: {err}"
    return val, None


def mostrar_error(parent, errores):
    """Muestra un QMessageBox con la lista de errores si hay alguno.
    Retorna True si hubo errores (para cortar el flujo).
    """
    if errores:
        QMessageBox.critical(parent, "Error en los datos", "\n".join(errores))
        return True
    return False


def formatear_matriz(M, frac=True):
    """Convierte una lista de listas (matriz) a texto alineado con corchetes."""
    filas = len(M)
    cols = len(M[0])
    txts = [[formato_numero(M[i][j], frac) for j in range(cols)] for i in range(filas)]
    ancho = max(3, max(len(c) for fila in txts for c in fila) + 1)
    lineas = []
    for fila in txts:
        celdas = [c.rjust(ancho) for c in fila]
        lineas.append("   [ " + "  ".join(celdas) + " ]")
    return "\n".join(lineas)


def comparar_matrices(M1, M2):
    """Compara dos matrices elemento a elemento.
    Retorna True si son idénticas.
    """
    if len(M1) != len(M2):
        return False
    for i in range(len(M1)):
        if len(M1[i]) != len(M2[i]):
            return False
        for j in range(len(M1[i])):
            if M1[i][j] != M2[i][j]:
                return False
    return True
