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


class TestMetodosNumericos(unittest.TestCase):
    def test_biseccion_casos_guia(self):
        from core.metodos_numericos import metodo_biseccion
        # Caso 1: x^3 - 2x - 5 en [2, 3]
        r1 = metodo_biseccion("x**3 - 2*x - 5", 2, 3, tol=1e-4)
        self.assertTrue(r1["exito"])
        self.assertAlmostEqual(r1["raiz"], 2.09455148, places=3)
        self.assertEqual(r1["n_teorico"], 14)

        # Caso 2: cos(x) - x en [0, 1]
        r2 = metodo_biseccion("cos(x) - x", 0, 1, tol=1e-4)
        self.assertTrue(r2["exito"])
        self.assertAlmostEqual(r2["raiz"], 0.73908513, places=3)
        self.assertEqual(r2["n_teorico"], 14)

        # Caso 3: x^2 - 2 en [1, 2]
        r3 = metodo_biseccion("x**2 - 2", 1, 2, tol=1e-4)
        self.assertTrue(r3["exito"])
        self.assertAlmostEqual(r3["raiz"], 1.41421356, places=3)

        # Caso 4: x^3 + x - 1 en [0, 1]
        r4 = metodo_biseccion("x**3 + x - 1", 0, 1, tol=1e-4)
        self.assertTrue(r4["exito"])
        self.assertAlmostEqual(r4["raiz"], 0.68232780, places=3)

    def test_biseccion_pruebas_obligatorias(self):
        from core.metodos_numericos import metodo_biseccion
        # 1. Sin cambio de signo
        r1 = metodo_biseccion("x**2 + 1", -1, 1)
        self.assertFalse(r1["exito"])

        # 2. Raíz en extremo
        r2 = metodo_biseccion("x**2 - 1", 1, 2)
        self.assertTrue(r2["exito"])
        self.assertEqual(r2["raiz"], 1.0)

        # 3. Discontinuidad 1/x
        r3 = metodo_biseccion("1/x", -1, 1)
        self.assertTrue(len(r3["advertencias"]) > 0)

        # 4. Iteraciones insuficientes
        r4 = metodo_biseccion("x**3 - 2*x - 5", 2, 3, tol=1e-4, max_iter=3)
        self.assertFalse(r4["exito"])

    def test_notacion_posicional(self):
        from core.metodos_numericos import analisis_posicional_completo
        p10 = analisis_posicional_completo("84506")
        self.assertEqual(p10["decimal"], 84506)
        p2 = analisis_posicional_completo("0b11110011")
        self.assertEqual(p2["decimal"], 243)

    def test_errores_y_flotante(self):
        from core.metodos_numericos import demostracion_punto_flotante, calcular_errores_absoluto_relativo
        fp = demostracion_punto_flotante()
        self.assertFalse(fp["resultado_comparacion"])
        err = calcular_errores_absoluto_relativo(10.0, 9.8)
        self.assertAlmostEqual(err["error_absoluto"], 0.2)
        self.assertAlmostEqual(err["error_porcentual"], 2.0)
        err_zero = calcular_errores_absoluto_relativo(0.0, 1.0)
        self.assertIsNone(err_zero["error_relativo"])


class TestMetodosIterativos(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np = np

    def test_validaciones_entradas(self):
        from core.metodos_iterativos import validar_entradas_iterativas
        # Matriz no cuadrada
        _, _, _, err1 = validar_entradas_iterativas([[1, 2, 3], [4, 5, 6]], [1, 2])
        self.assertIsNotNone(err1)
        self.assertIn("cuadrada", err1)

        # Tolerancia negativa
        _, _, _, err2 = validar_entradas_iterativas([[2, 1], [1, 3]], [1, 2], tol=-0.01)
        self.assertIsNotNone(err2)
        self.assertIn("positiva", err2)

        # Máximo de iteraciones <= 0
        _, _, _, err3 = validar_entradas_iterativas([[2, 1], [1, 3]], [1, 2], max_iter=0)
        self.assertIsNotNone(err3)

    def test_caso_1_convergencia_y_dominancia(self):
        from core.metodos_iterativos import (
            metodo_jacobi, metodo_gauss_seidel, CASOS_PRUEBA,
            analizar_diagonal_y_convergencia, comparar_jacobi_y_seidel
        )
        c1 = CASOS_PRUEBA[0]
        analisis = analizar_diagonal_y_convergencia(self.np.array(c1["A"]))
        self.assertTrue(analisis["es_estrictamente_dominante"])
        self.assertFalse(analisis["tiene_ceros"])
        self.assertLess(analisis["rho_jacobi"], 1.0)
        self.assertLess(analisis["rho_seidel"], 1.0)

        res_j = metodo_jacobi(c1["A"], c1["b"], c1["x0"], tol=c1["tol"], max_iter=c1["max_iter"])
        res_gs = metodo_gauss_seidel(c1["A"], c1["b"], c1["x0"], tol=c1["tol"], max_iter=c1["max_iter"])

        self.assertTrue(res_j.convergio)
        self.assertTrue(res_gs.convergio)
        self.assertLess(res_gs.num_iteraciones, res_j.num_iteraciones)  # GS suele ser más rápido
        self.assertTrue(self.np.allclose(res_j.x_final, [1.0, -2.0, 1.0], atol=1e-3))
        self.assertTrue(self.np.allclose(res_gs.x_final, [1.0, -2.0, 1.0], atol=1e-3))

        comp = comparar_jacobi_y_seidel(res_j, res_gs, self.np.array(c1["A"]), self.np.array(c1["b"]))
        self.assertLess(comp["diff_entre_metodos"], 1e-3)
        self.assertLess(comp["error_ref_j"], 1e-3)
        self.assertLess(comp["error_ref_gs"], 1e-3)

    def test_caso_2_cero_diagonal_y_reordenamiento(self):
        from core.metodos_iterativos import (
            metodo_jacobi, metodo_gauss_seidel, CASOS_PRUEBA,
            analizar_diagonal_y_convergencia, evaluar_reordenamiento_filas
        )
        c2 = CASOS_PRUEBA[2]
        A2 = self.np.array(c2["A"])
        b2 = self.np.array(c2["b"])

        # Sin reordenar, tiene ceros en la diagonal y falla inmediatamente
        analisis_orig = analizar_diagonal_y_convergencia(A2)
        self.assertTrue(analisis_orig["tiene_ceros"])
        res_fail = metodo_jacobi(A2, b2)
        self.assertFalse(res_fail.convergio)
        self.assertEqual(res_fail.estado, "ERROR_DIAGONAL")

        # Al reordenar filas, encuentra una permutación estrictamente dominante
        reord = evaluar_reordenamiento_filas(A2, b2)
        self.assertTrue(reord["es_posible"])
        self.assertEqual(reord["tipo_resultado"], "CONV_ESTRICTA")

        res_j = metodo_jacobi(reord["A_reordenada"], reord["b_reordenado"])
        res_gs = metodo_gauss_seidel(reord["A_reordenada"], reord["b_reordenado"])
        self.assertTrue(res_j.convergio)
        self.assertTrue(res_gs.convergio)

    def test_caso_2b_cero_insalvable(self):
        from core.metodos_iterativos import CASOS_PRUEBA, evaluar_reordenamiento_filas
        c2b = CASOS_PRUEBA[3]
        A2b = self.np.array(c2b["A"])
        b2b = self.np.array(c2b["b"])

        reord = evaluar_reordenamiento_filas(A2b, b2b)
        self.assertFalse(reord["es_posible"])
        self.assertEqual(reord["tipo_resultado"], "NO_POSIBLE")

    def test_caso_3_divergencia_controlada(self):
        from core.metodos_iterativos import (
            metodo_jacobi, metodo_gauss_seidel, CASOS_PRUEBA,
            analizar_diagonal_y_convergencia
        )
        c3 = CASOS_PRUEBA[4]
        analisis = analizar_diagonal_y_convergencia(self.np.array(c3["A"]))
        self.assertFalse(analisis["es_estrictamente_dominante"])
        self.assertGreater(analisis["rho_jacobi"], 1.0)
        self.assertGreater(analisis["rho_seidel"], 1.0)

        # Debe detectar la divergencia sin crashear ni lanzar excepciones no controladas
        res_j = metodo_jacobi(c3["A"], c3["b"], max_iter=30)
        res_gs = metodo_gauss_seidel(c3["A"], c3["b"], max_iter=30)
        self.assertFalse(res_j.convergio)
        self.assertFalse(res_gs.convergio)

    def test_caso_3b_no_dominante_pero_convergente(self):
        from core.metodos_iterativos import (
            metodo_jacobi, metodo_gauss_seidel, CASOS_PRUEBA,
            analizar_diagonal_y_convergencia
        )
        c3b = CASOS_PRUEBA[5]
        analisis = analizar_diagonal_y_convergencia(self.np.array(c3b["A"]))
        # No es estrictamente dominante
        self.assertFalse(analisis["es_estrictamente_dominante"])
        # Pero ambos radios espectrales son menores que 1
        self.assertLess(analisis["rho_jacobi"], 1.0)
        self.assertLess(analisis["rho_seidel"], 1.0)

        res_j = metodo_jacobi(c3b["A"], c3b["b"], tol=1e-4, max_iter=60)
        res_gs = metodo_gauss_seidel(c3b["A"], c3b["b"], tol=1e-4, max_iter=60)
        self.assertTrue(res_j.convergio)
        self.assertTrue(res_gs.convergio)
        self.assertTrue(self.np.allclose(res_j.x_final, [1.0, 2.0], atol=1e-3))
        self.assertTrue(self.np.allclose(res_gs.x_final, [1.0, 2.0], atol=1e-3))

    def test_dataframe_iteraciones(self):
        from core.metodos_iterativos import metodo_jacobi, CASOS_PRUEBA
        c1 = CASOS_PRUEBA[0]
        res = metodo_jacobi(c1["A"], c1["b"], tol=1e-4, max_iter=20)
        df = res.a_dataframe()
        self.assertGreater(len(df), 0)
        self.assertIn("Iteración", df.columns)
        self.assertIn("Error (||Δx||_∞)", df.columns)
        self.assertIn("Residuo (||Ax-b||_∞)", df.columns)



if __name__ == "__main__":
    unittest.main()
