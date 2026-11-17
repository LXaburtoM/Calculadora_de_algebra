# 🚀 DOCUMENTO DE CONTEXTO Y TRANSFERENCIA PARA IA (HANDOVER PROMPT)

Este documento contiene todo el contexto técnico, la arquitectura, las reglas del docente y el estado actual del proyecto para que cualquier modelo de IA (ChatGPT, Claude, Gemini, etc.) pueda continuar el desarrollo o realizar ajustes de inmediato sin tener que explicar nada desde cero.

---

## 📌 PROMPT PARA COPIAR Y PEGAR EN OTRA IA

```text
Hola! Estoy desarrollando la "Calculadora de Álgebra Lineal Next-Gen" para la asignatura de Álgebra Lineal (MTM0120) en la Universidad Americana (UAM).

Por favor lee este contexto antes de responder:

1. UBICACIÓN Y ESTRUCTURA DEL PROYECTO:
   Ruta local: C:\Users\lxman\Desktop\Clases\Algebra\Calculadora_Algebra_Lineal_Grupo
   - main.py: Punto de entrada en PyQt6.
   - core/parser.py: Parser de expresiones numéricas y fracciones.
   - core/eliminacion_gaussiana.py: Motor de Eliminación por Filas (Gauss y Gauss-Jordan).
   - core/algebra_avanzada.py: Determinantes, Cramer, Inversas y Espacios Vectoriales.
   - core/factorizacion_lu.py: Descomposición LU (A = LU) y resolución en 2 etapas.
   - core/metodos_numericos.py: Módulo 7 (Bisección desde cero, graficador de funciones, notación posicional bases 10 y 2, punto flotante y errores).
   - core/metodos_iterativos.py: Módulo 8 (Métodos iterativos de Jacobi y Gauss-Seidel, dominancia diagonal, reordenamiento de ecuaciones, radios espectrales y validación).
   - gui/main_window.py: Dashboard con menú deslizable lateral, riel rápido y 8 módulos integrados.
   - gui/modules/metodos_numericos_widget.py: Interfaz interactiva de Métodos Numéricos (Programa 7).
   - gui/modules/iterativos_widget.py: Interfaz interactiva de Métodos Iterativos Jacobi y Gauss-Seidel (Programa 8).
   - gui/styles.py: Estilos visuales en modo oscuro y claro (PyQt6 QSS).
   - tests/: Suite de pruebas unitarias (test_core.py) y de interfaz (test_interfaz.py).

2. REGLAS TÉCNICAS DEL DOCENTE (PROGRAMA 8):
   - Librerías autorizadas: NumPy para operaciones numéricas y validación; Pandas para tablas; Matplotlib para gráficas; SymPy cuando se requiera manejo simbólico.
   - Algoritmos propios implementados desde cero: Jacobi (actualización simultánea usando x^(k-1)) y Gauss-Seidel (actualización inmediata sucesiva en sitio).
   - Función de referencia: numpy.linalg.solve(A, b) usada únicamente para contrastar resultados y calcular discrepancias/residuos, no para sustituir la implementación iterativa.
   - Criterio de parada consistente: ||x^(k) - x^(k-1)||_∞ ≤ ε y registro de residuo ||Ax - b||_∞.
   - Manejo de diagonal: Comprobación de ceros en la diagonal, análisis de dominancia estricta por filas (condición suficiente pero NO necesaria, ρ(T) < 1 necesaria y suficiente), y asistente de reordenamiento/permutación de filas.
   - Robustez: Detección preventiva de divergencia y desbordamientos (Inf/NaN) sin cerrar inesperadamente la calculadora.

3. ESTADO ACTUAL DEL PROYECTO:
   - 8 módulos completamente integrados y operativos:
     1. Sistemas de Ecuaciones Lineales (Gauss / Gauss-Jordan)
     2. Transformaciones Lineales [T(x) = Ax]
     3. Operaciones Matriciales e Independencia Lineal
     4. Determinantes y Regla de Cramer
     5. Factorización LU y resolución Ax = b
     6. Verificador de 16 propiedades y teoremas
     7. Métodos Numéricos: Bisección, Graficador, Notación Posicional y Errores Numéricos.
     8. Métodos Numéricos Iterativos: Jacobi y Gauss-Seidel (Programa 8).
```

---

## 📁 Estructura del Código

```
Calculadora_Algebra_Lineal_Grupo/
├── main.py                                  # Launcher del sistema
├── ejecutar.bat                             # Ejecutable con doble clic
├── requirements.txt                         # Dependencias (PyQt6, sympy, numpy, matplotlib, scipy, pandas)
├── CONTEXTO_PROYECTO.md                     # Documento de transferencia
├── core/
│   ├── parser.py                            # Expresiones numéricas y fracciones
│   ├── eliminacion_gaussiana.py            # Gauss y Gauss-Jordan
│   ├── factorizacion_lu.py                 # Descomposición A = LU
│   ├── algebra_avanzada.py                 # Determinantes, inversas, espacios vectoriales
│   ├── transformaciones_lineales.py         # Análisis T(x) = Ax
│   ├── operaciones_matriciales.py          # Suma, producto, transpuesta, combinación lineal
│   ├── validadores.py                       # Validaciones matriciales
│   ├── metodos_numericos.py                 # Motor matemático del Módulo 7 (Programa 7)
│   └── metodos_iterativos.py                # Motor matemático del Módulo 8: Jacobi y Gauss-Seidel (Programa 8)
├── gui/
│   ├── main_window.py                       # Menú lateral y orquestador de módulos
│   ├── componentes.py                       # Iconos vectoriales y controles interactivos
│   ├── entrada.py                           # Componentes de entrada y presentación de resultados
│   ├── styles.py                            # Estilos QSS oscuros y claros
│   └── modules/
│       ├── ecuaciones_widget.py             # Módulo 1: Sistemas de Ecuaciones
│       ├── transformaciones_widget.py       # Módulo 2: Transformaciones Lineales
│       ├── operaciones_widget.py            # Módulo 3: Operaciones Matriciales
│       ├── determinantes_widget.py          # Módulo 4: Determinantes y Cramer
│       ├── lu_widget.py                     # Módulo 5: Factorización LU
│       ├── verificador_widget.py            # Módulo 6: Verificador de Propiedades
│       ├── metodos_numericos_widget.py      # Módulo 7: Métodos Numéricos (Programa 7)
│       └── iterativos_widget.py             # Módulo 8: Métodos Iterativos (Programa 8)
└── tests/
    ├── test_core.py                         # Pruebas unitarias de algoritmos
    └── test_interfaz.py                     # Pruebas de integración de la GUI
```

---

## ⚙️ Cómo Ejecutar el Proyecto

```powershell
cd "c:\Users\lxman\Desktop\Clases\Algebra\Calculadora_Algebra_Lineal_Grupo"
.\.venv\Scripts\python.exe main.py
```
O presionando la tecla **F5** en VS Code / haciendo doble clic en **`ejecutar.bat`**.
