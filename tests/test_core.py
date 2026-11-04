"""
Pruebas de los motores matemáticos de core/ (Python puro, sin interfaz).
Ejecutar desde la raíz del proyecto:  python -m unittest discover -s tests -t .
"""
import unittest
from fractions import Fraction as F

from core.parser import parse_expresion
from core.eliminacion_gaussiana import (
    reducir_por_filas, resolver_por_gauss, clasificar_sistema, solucion_general
)
from core.algebra_avanzada import (
    determinante_cofactores, determinante_reduccion, determinante_sarrus, regla_de_cramer,
    inversa_matriz, inversa_adjunta, evaluar_independencia_lineal
)
from core.factorizacion_lu import factorizacion_lu, resolver_sistema_lu
from core.operaciones_matriciales import multiplicar_matrices, es_combinacion_lineal
from core.transformaciones_lineales import analizar_transformacion_completa


def fr(matriz):
    return [[F(x) for x in fila] for fila in matriz]


SISTEMA_3x3 = fr([[2, 1, -1, 8], [-3, -1, 2, -11], [-2, 1, 2, -3]])   # x = (2, 3, -1)
MATRIZ_DET = fr([[2, 1, 3], [0, -1, 4], [1, 2, 0]])                   # det = -9


class TestParser(unittest.TestCase):
    def test_fraccion_y_decimal(self):
        self.assertEqual(parse_expresion("1/2"), (F(1, 2), None))
        self.assertEqual(parse_expresion("2.5")[0], F(5, 2))
        self.assertEqual(parse_expresion("raiz(4)")[0], F(2))

    def test_texto_invalido_devuelve_error(self):
        valor, error = parse_expresion("abc")
        self.assertIsNone(valor)
        self.assertTrue(error)


class TestSistemas(unittest.TestCase):
    def _solucion(self, resultado, m=3, n=3):
        return [d["const"] for d in solucion_general(resultado["rref"], m, n, resultado["pivotes"])]

    def test_gauss_jordan_solucion_unica(self):
        resultado = reducir_por_filas(SISTEMA_3x3, 3, 3)
        self.assertEqual(clasificar_sistema(resultado, 3, 3)["tipo"], "DETERMINADO")
        self.assertEqual(self._solucion(resultado), [F(2), F(3), F(-1)])

    def test_gauss_da_lo_mismo(self):
        resultado = resolver_por_gauss(SISTEMA_3x3, 3, 3)["resultado_base"]
        self.assertEqual(self._solucion(resultado), [F(2), F(3), F(-1)])

    def test_inconsistente(self):
        resultado = reducir_por_filas(fr([[1, 1, 2], [1, 1, 3]]), 2, 2)
        self.assertEqual(clasificar_sistema(resultado, 2, 2)["tipo"], "INCONSISTENTE")

    def test_infinitas_soluciones(self):
        resultado = reducir_por_filas(fr([[1, 1, 2], [2, 2, 4]]), 2, 2)
        clasif = clasificar_sistema(resultado, 2, 2)
        self.assertEqual(clasif["tipo"], "INDETERMINADO")
        self.assertEqual(clasif["libres"], [1])


class TestDeterminantes(unittest.TestCase):
    def test_tres_metodos_coinciden(self):
        self.assertEqual(determinante_cofactores(MATRIZ_DET)[0], F(-9))
        self.assertEqual(determinante_reduccion(MATRIZ_DET)[0], F(-9))
        self.assertEqual(determinante_sarrus(MATRIZ_DET)[0], F(-9))

    def test_cramer(self):
        A = [fila[:3] for fila in SISTEMA_3x3]
        b = [fila[3] for fila in SISTEMA_3x3]
        soluciones, _, error = regla_de_cramer(A, b, 3)
        self.assertIsNone(error)
        self.assertEqual(soluciones, [F(2), F(3), F(-1)])

    def test_cramer_singular_da_error(self):
        _, _, error = regla_de_cramer(fr([[1, 2], [2, 4]]), fr([[1, 2]])[0], 2)
        self.assertTrue(error)


class TestOperaciones(unittest.TestCase):
    def test_inversa_por_dos_metodos(self):
        A = fr([[2, 1], [1, 1]])
        esperado = fr([[1, -1], [-1, 2]])
        self.assertEqual(inversa_matriz(A, 2)[0], esperado)
        self.assertEqual(inversa_adjunta(A, 2)[0], esperado)

    def test_multiplicacion_ejemplo_de_clase(self):
        A = fr([[1, -1, 2], [0, 3, 4]])
        B = fr([[2, 1], [-1, 0], [3, 5]])
        self.assertEqual(multiplicar_matrices(A, B, 2, 3, 2)[0], fr([[9, 11], [9, 20]]))

    def test_combinacion_lineal(self):
        res = es_combinacion_lineal(fr([[2, 3, 5]])[0], fr([[1, 0, 1], [0, 1, 1]]))
        self.assertTrue(res["es_cl"])
        self.assertEqual(list(res["escalares"].values()), [F(2), F(3)])

    def test_independencia_lineal(self):
        self.assertTrue(evaluar_independencia_lineal(fr([[1, 0, 0], [0, 1, 0], [0, 0, 1]]), 3)["es_li"])
        self.assertFalse(evaluar_independencia_lineal(fr([[1, 0, 0], [0, 1, 0], [1, 0, 0]]), 3)["es_li"])


class TestFactorizacionLU(unittest.TestCase):
    def test_l_por_u_es_a_y_resuelve(self):
        A = fr([[2, 1, -1], [1, 3, 2], [1, 0, 2]])
        L, U, _, error = factorizacion_lu(A, 3, 3)
        self.assertIsNone(error)
        self.assertEqual(multiplicar_matrices(L, U, 3, 3, 3)[0], A)
        _, x, _, error = resolver_sistema_lu(L, U, fr([[8, 13, 7]])[0], 3)
        self.assertIsNone(error)
        self.assertEqual(x, [F(19, 5), F(2), F(8, 5)])

    def test_requiere_pivoteo(self):
        *_, error = factorizacion_lu(fr([[0, 2, 1], [1, 1, 1], [2, 1, 0]]), 3, 3)
        self.assertTrue(error)


class TestTransformaciones(unittest.TestCase):
    def test_identidad_es_biyectiva(self):
        I = fr([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        analisis = analizar_transformacion_completa(I, 3, 3, b=fr([[4, 5, 6]])[0], u=fr([[1, 2, 3]])[0])
        self.assertTrue(analisis["es_inyectiva"] and analisis["es_sobreyectiva"])
        self.assertEqual(analisis["Tu"], [F(1), F(2), F(3)])
        self.assertTrue(analisis["pertenece_rango"])


if __name__ == "__main__":
    unittest.main()
