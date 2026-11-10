"""
Pruebas de humo de la interfaz: abre la ventana sin mostrarla en pantalla y
resuelve un caso por módulo, como lo haría un usuario.
Ejecutar desde la raíz del proyecto:  python -m unittest discover -s tests -t .
"""
import os
import tempfile
import unittest
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication

app = QApplication.instance() or QApplication([])

# Ajustes en un archivo temporal para no tocar las preferencias reales del usuario
_AJUSTES = os.path.join(tempfile.mkdtemp(), "ajustes.ini")


def _ajustes_de_prueba(*_):
    return QSettings(_AJUSTES, QSettings.Format.IniFormat)


def llenar(tabla, datos):
    for i, fila in enumerate(datos):
        for j, valor in enumerate(fila):
            tabla.item(i, j).setText(str(valor))


def resumen(tarjeta_o_resumen):
    r = getattr(tarjeta_o_resumen, "resumen", tarjeta_o_resumen)
    return r.titulo.text(), r.valor.text()


class TestInterfaz(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with mock.patch("gui.main_window.QSettings", _ajustes_de_prueba):
            from gui.main_window import MainWindow
            cls.w = MainWindow()
        cls.w.resize(1280, 780)
        cls.w.show()
        app.processEvents()

    def test_navegacion_con_el_riel(self):
        for i in range(len(self.w.modulos)):
            self.w.items_riel[i].click()
            self.assertEqual(self.w.stack.currentIndex(), i)

    def test_ecuaciones_con_teclado_y_enter(self):
        e = self.w.ecuaciones_widget
        self.w.activar_modulo(0)
        e.tabla.setFocus()
        e.tabla.setCurrentCell(0, 0)
        for valor in ["2", "1", "-1", "8", "-3", "-1", "2", "-11", "-2", "1", "2", "-3"]:
            for caracter in valor:
                e.teclado.insertar(caracter)
            e.teclado.enter()          # en la última celda, Enter resuelve
        self.assertEqual(resumen(e.resumen)[0], "Solución única")
        self.assertIn("x₁ = 2", resumen(e.resumen)[1])
        e.selector_metodo.grupo.button(0).click()      # Gauss a un clic
        self.assertEqual(e.metodo, "gauss")
        self.assertEqual(resumen(e.resumen)[0], "Solución única")

    def test_transformaciones(self):
        t = self.w.transformaciones_widget
        llenar(t.tabla_A, [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        llenar(t.tabla_u, [[1, 2, 3]])
        t.accion_principal()
        self.assertEqual(resumen(t.resumen_tipo)[0], "Biyectiva")

    def test_operaciones_inversa_y_ans(self):
        o = self.w.operaciones_widget
        o.selector_seccion.grupo.button(1).click()
        o.spin_mA.setValue(2)
        o.spin_nA.setValue(2)
        llenar(o.tabla_A, [[2, 1], [1, 1]])
        o.combo_mat_op.setCurrentIndex(5)              # Inversa (Gauss-Jordan)
        o.accion_principal()
        self.assertEqual(o.ultima_matriz_resultado[1][1], 2)
        o._usar_resultado_B()
        self.assertEqual(o.tabla_B.item(0, 1).text(), "-1")

    def test_determinantes_y_cramer(self):
        d = self.w.determinantes_widget
        llenar(d.tabla_det, [[2, 1, 3], [0, -1, 4], [1, 2, 0]])
        d.selector_metodo.grupo.button(1).click()      # Sarrus
        self.assertEqual(resumen(d.res_det)[0], "|A| = -9")
        d.spin_det_n.setValue(2)
        self.assertFalse(d.btn_sarrus.isEnabled())

        d.selector_seccion.grupo.button(1).click()
        llenar(d.tabla_cr, [[2, 1, -1, 8], [-3, -1, 2, -11], [-2, 1, 2, -3]])
        d.accion_principal()
        self.assertEqual(resumen(d.res_cr)[0], "Solución única")

    def test_lu(self):
        l = self.w.lu_widget
        l._cargar_ejemplo(1)
        l.btn_resolver.click()
        self.assertIn("x₁ = 19/5", resumen(l.res)[1])
        l.spin_m.setValue(4)
        self.assertFalse(l.btn_resolver.isEnabled())
        self.assertEqual(l.combo_ejemplos.currentIndex(), 0)

    def test_verificador(self):
        v = self.w.verificador_widget
        v.spin_n.setValue(2)
        v._cargar_valores_por_defecto()
        v.accion_principal()
        self.assertEqual(resumen(v.res)[0], "16 de 16 propiedades se cumplen")

    def test_cambio_de_tema(self):
        for tema in ("claro", "oscuro"):
            self.w.elegir_tema(tema)
            self.assertEqual(self.w.tema, tema)
            self.assertTrue(self.w.acciones_tema[tema].isChecked())

    def test_color_de_enfasis(self):
        self.w.elegir_enfasis("naranja")
        self.assertIn("#ff9500", self.w.styleSheet())
        self.assertTrue(self.w.acciones_enfasis["naranja"].isChecked())
        self.w.elegir_enfasis("personalizado", "#0A84FF")
        self.assertIn("#0a84ff", self.w.styleSheet())
        self.assertTrue(self.w.acciones_enfasis["personalizado"].isChecked())
        self.w.elegir_enfasis("rojo")
        self.assertTrue(self.w.acciones_enfasis["rojo"].isChecked())

    def test_tema_del_sistema(self):
        from PyQt6.QtCore import Qt
        self.w.elegir_tema("sistema")
        esperado = "oscuro" if app.styleHints().colorScheme() == Qt.ColorScheme.Dark else "claro"
        self.assertEqual(self.w.tema, esperado)
        self.assertTrue(self.w.acciones_tema["sistema"].isChecked())


    def test_metodos_numericos_gui(self):
        m = self.w.metodos_numericos_widget
        self.w.activar_modulo(6)
        m.txt_fn_biseccion.setText("x**3 - 2*x - 5")
        m.txt_a.setText("2")
        m.txt_b.setText("3")
        m.accion_principal()
        self.assertIn("Raíz hallada", resumen(m.res_biseccion)[0])

        m.selector_seccion.grupo.button(2).click()
        m.txt_posicional.setText("84506")
        m.accion_principal()
        self.assertIn("84506", resumen(m.res_posicional)[0])
        self.assertIn("Equivalencia", resumen(m.res_posicional)[1])

        m.selector_seccion.grupo.button(3).click()
        m.accion_principal()
        self.assertIn("Punto Flotante", resumen(m.res_errores)[0])


if __name__ == "__main__":
    unittest.main()
