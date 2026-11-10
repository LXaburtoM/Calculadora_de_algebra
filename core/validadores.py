"""
Módulo de Validación Centralizada para la Calculadora de Álgebra Lineal.
Tema: Formateo y comparación de matrices (Python puro, sin dependencias de la interfaz).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""
from core.parser import formato_numero


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
