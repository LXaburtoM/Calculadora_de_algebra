# 🚀 DOCUMENTO DE CONTEXTO Y TRANSFERENCIA PARA IA (HANDOVER PROMPT)

Este documento contiene todo el contexto técnico, la arquitectura, las reglas del docente y el estado actual del proyecto para que cualquier modelo de IA (ChatGPT, Claude, Gemini, etc.) pueda continuar el desarrollo o realizar ajustes de inmediato sin tener que explicar nada desde cero.

---

## 📌 PROMPT PARA COPIAR Y PEGAR EN OTRA IA

```text
Hola! Estoy desarrollando la "Calculadora de Álgebra Lineal Next-Gen" para la asignatura de Álgebra Lineal (MTM0120) en la Universidad Americana (UAM).

Por favor lee este contexto antes de responder:

1. UBICACIÓN Y ESTRUCTURA DEL PROYECTO:
   Ruta local: C:\Users\lxman\Desktop\Clases\Algebra\Calculadora de algebra lineal
   - main.py: Punto de entrada en PyQt6.
   - core/parser.py: Parser de fracciones (1/2, -3/4), enteros, decimales y captura ultra-robusta de errores. Usa `fractions.Fraction`.
   - core/eliminacion_gaussiana.py: Motor de Eliminación por Filas (Gauss y Gauss-Jordan) en Python puro con precisión exacta de fracciones.
   - gui/main_window.py: Dashboard con menú lateral navegable para futuros módulos.
   - gui/modules/ecuaciones_widget.py: Interfaz interactiva del Módulo 1 (Sistemas de Ecuaciones Lineales).
   - gui/styles.py: Estilos visuales en modo oscuro (PyQt6 QSS).
   - ejecutar.bat / .vscode/launch.json: Archivos para iniciar la app directamente o con F5.

2. REGLAS TÉCNICAS DEL DOCENTE:
   - Prohibido el uso de NumPy, SciPy o math integrados en los motores matemáticos de core/ para las tareas entregables (debe ser Python puro: listas, bucles y fractions.Fraction).
   - Entrada flexible: Debe aceptar fracciones (ej: 1/2), decimales o enteros sin fallar.
   - Captura de errores: El programa NUNCA debe colapsar por errores de usuario (división por cero, texto inválido).

3. ESTADO ACTUAL DEL PROYECTO:
   - Módulo 1 (Sistemas de Ecuaciones Lineales / Eliminación por filas) está 100% completado, probado y funcionando.
   - Soporta paso a paso, clasificación de sistemas (Determinado, Indeterminado, Inconsistente) y comprobación automática Ax = b.

Mi solicitud actual es la siguiente: [ESCRIBE AQUÍ LO QUE NECESITAS AJUSTAR O AGREGAR]
```

---

## 📁 Estructura del Código Creado

```
Calculadora de algebra lineal/
├── main.py                          # Launcher del sistema
├── ejecutar.bat                     # Ejecutable con doble clic
├── requirements.txt                 # Dependencias (PyQt6, sympy, numpy, matplotlib, pandas)
├── CONTEXTO_PROYECTO.md             # Este documento de transferencia
├── .vscode/
│   ├── launch.json                  # F5 listo
│   └── settings.json
├── core/
│   ├── parser.py                    # Convierte '1/2' a Fraction(1, 2) y valida errores
│   └── eliminacion_gaussiana.py    # Algoritmo de Gauss-Jordan con fracciones y pasos
└── gui/
    ├── main_window.py               # Menú lateral y contenedor de pestañas
    ├── styles.py                    # Estilos CSS/QSS oscuros
    └── modules/
        └── ecuaciones_widget.py     # Widget interactivo de Sistemas de Ecuaciones (Tarea 1)
```

---

## ⚙️ Cómo Ejecutar el Proyecto

```powershell
cd "C:\Users\lxman\Desktop\Clases\Algebra\Calculadora de algebra lineal"
.\venv\Scripts\python.exe main.py
```
O presionando la tecla **F5** en VS Code / haciendo doble clic en **`ejecutar.bat`**.

---

## 💡 Próximos Módulos Planificados por Semanas

1. **Módulo 1 (COMPLETADO)**: Sistemas de Ecuaciones Lineales (Gauss / Gauss-Jordan).
2. **Módulo 2 (PENDIENTE)**: Operaciones Matriciales (Suma, Producto, Traspuesta, Inversa paso a paso).
3. **Módulo 3 (PENDIENTE)**: Determinantes y Regla de Cramer.
4. **Módulo 4 (PENDIENTE)**: Vectores y Espacios Vectoriales (Independencia Lineal, Base, Ortogonalidad).
5. **Módulo 5 (PENDIENTE)**: Aplicaciones Avanzadas (Modelo de Leontief, Valores y Vectores Propios).
