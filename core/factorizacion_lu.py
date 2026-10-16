"""
Módulo 5: Factorización LU y Resolución de Sistemas Ax = b.
Tema: Descomposición LU sin intercambios de fila y sustitución progresiva/regresiva (Sesión 12).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""
from fractions import Fraction
from core.parser import formato_numero
from core.operaciones_matriciales import multiplicar_matrices
from core.validadores import comparar_matrices, formatear_matriz


def factorizacion_lu(matriz_A, m, n, frac=True):
    """
    Calcula la factorización A = L · U sin intercambios de filas.
    Registra paso a paso la evolución de las matrices L y U en cada eliminación.
    
    Parámetros:
        matriz_A: Lista anidada con los coeficientes de la matriz m x n.
        m: Número de filas.
        n: Número de columnas.
        frac: Si True muestra fracciones exactas, si False decimales.
        
    Retorna:
        (matriz_L, matriz_U, pasos, error_msg)
    """
    # U inicia como copia exacta de A para almacenar las operaciones de fila
    matriz_U = [[matriz_A[i][j] for j in range(n)] for i in range(m)]
    
    # L inicia como matriz identidad m x m (unos en la diagonal, ceros en el resto)
    matriz_L = [[Fraction(1) if i == j else Fraction(0) for j in range(m)] for i in range(m)]
    
    pasos = []
    pasos.append("PASO 1 · Obtención de matrices L y U (Operaciones elementales de reemplazo):")
    pasos.append("Matriz inicial U = A:")
    pasos.append(formatear_matriz(matriz_U, frac))
    pasos.append("Matriz inicial L = I:")
    pasos.append(formatear_matriz(matriz_L, frac))
    pasos.append("")
    
    paso_num = 1
    limite = min(m, n)
    for k in range(limite):
        pivote = matriz_U[k][k]
        
        # Si el pivote en la diagonal es cero, se verifica si requiere intercambio
        if pivote == 0:
            for r in range(k + 1, m):
                if matriz_U[r][k] != 0:
                    # El algoritmo LU estándar no admite permutación de filas
                    return None, None, pasos, (
                        "La matriz no admite Factorización LU sin permutación "
                        "(requiere pivoteo parcial PA = LU ya que el pivote en la diagonal es 0)."
                    )
            # Si toda la columna debajo es cero, no se requiere eliminación en esta columna
            continue
        
        for i in range(k + 1, m):
            elem = matriz_U[i][k]
            if elem != 0:
                paso_num += 1
                # Se calcula el multiplicador exacto de eliminación por filas
                multiplicador_l = elem / pivote
                
                # Se registra el multiplicador en L antes de alterar la fila en U
                matriz_L[i][k] = multiplicador_l
                
                # Reemplazo de fila en U para generar el cero bajo el pivote
                for j in range(k, n):
                    matriz_U[i][j] -= multiplicador_l * matriz_U[k][j]
                    
                pasos.append(
                    f"{paso_num}. F{i+1} ← F{i+1} - ({formato_numero(multiplicador_l, frac)})·F{k+1}; "
                    f"L[{i+1},{k+1}] = {formato_numero(multiplicador_l, frac)}."
                )
                pasos.append("L =")
                pasos.append(formatear_matriz(matriz_L, frac))
                pasos.append("U =")
                pasos.append(formatear_matriz(matriz_U, frac))
                pasos.append("")

    # ── PASO 2: Comprobación A = L · U ──────────────────────────────
    LU, _, _ = multiplicar_matrices(matriz_L, matriz_U, m, m, n)
    es_correcta = comparar_matrices(LU, matriz_A)
    
    pasos.append("PASO 2 · Comprobación A = L · U")
    pasos.append("L · U =")
    pasos.append(formatear_matriz(LU, frac))
    if es_correcta:
        pasos.append("✓ Se cumple: A = L · U.")
    else:
        pasos.append("✘ Error: L · U != A.")
        
    return matriz_L, matriz_U, pasos, None


def resolver_sistema_lu(matriz_L, matriz_U, vector_b, n, frac=True):
    """
    Resuelve el sistema cuadrado Ax = b mediante doble sustitución:
    1) Ly = b (sustitución progresiva hacia adelante)
    2) Ux = y (sustitución regresiva hacia atrás)
    
    Parámetros:
        matriz_L: Matriz triangular inferior n x n con unos en la diagonal.
        matriz_U: Matriz triangular superior n x n.
        vector_b: Lista con los n términos independientes.
        n: Orden del sistema.
        frac: Si True muestra fracciones exactas, si False decimales.
        
    Retorna:
        (vector_y, vector_x, pasos, error_msg)
    """
    pasos = []
    pasos.append("================================================================================")
    pasos.append("RESOLUCIÓN DEL SISTEMA Ax = b CON FACTORIZACIÓN LU (DOBLE SUSTITUCIÓN)")
    pasos.append("================================================================================\n")
    
    # ── ETAPA 1: Sustitución hacia adelante Ly = b ──────────────────
    pasos.append("PASO 1 · Resolver L · y = b (Sustitución hacia adelante):")
    pasos.append("Matriz L:")
    pasos.append(formatear_matriz(matriz_L, frac))
    b_str = ", ".join(formato_numero(bi, frac) for bi in vector_b)
    pasos.append(f"Vector b = [ {b_str} ]ᵀ\n")
    
    vector_y = [Fraction(0)] * n
    for i in range(n):
        suma = Fraction(0)
        detalle_suma = []
        for j in range(i):
            prod = matriz_L[i][j] * vector_y[j]
            suma += prod
            detalle_suma.append(f"({formato_numero(matriz_L[i][j], frac)})·({formato_numero(vector_y[j], frac)})")
            
        vector_y[i] = vector_b[i] - suma
        str_detalle = " + ".join(detalle_suma) if detalle_suma else "0"
        pasos.append(
            f"   y{i+1} = {formato_numero(vector_b[i], frac)} - [{str_detalle}] = {formato_numero(vector_y[i], frac)}"
        )
        
    y_str = ", ".join(formato_numero(yi, frac) for yi in vector_y)
    pasos.append(f"\nVector intermedio obtenido: y = [ {y_str} ]ᵀ\n")
    pasos.append("-" * 78)
    
    # ── ETAPA 2: Sustitución hacia atrás Ux = y ─────────────────────
    pasos.append("PASO 2 · Resolver U · x = y (Sustitución hacia atrás):")
    pasos.append("Matriz U:")
    pasos.append(formatear_matriz(matriz_U, frac))
    pasos.append(f"Vector y = [ {y_str} ]ᵀ\n")
    
    vector_x = [Fraction(0)] * n
    for i in range(n - 1, -1, -1):
        pivote = matriz_U[i][i]
        if pivote == 0:
            return None, None, pasos, (
                f"Pivote U[{i+1},{i+1}] = 0. La matriz U es singular, "
                "el sistema no admite solución única."
            )
            
        suma = Fraction(0)
        detalle_suma = []
        for j in range(i + 1, n):
            prod = matriz_U[i][j] * vector_x[j]
            suma += prod
            detalle_suma.append(f"({formato_numero(matriz_U[i][j], frac)})·({formato_numero(vector_x[j], frac)})")
            
        numerador = vector_y[i] - suma
        vector_x[i] = numerador / pivote
        
        str_detalle = " + ".join(detalle_suma) if detalle_suma else "0"
        pasos.append(
            f"   x{i+1} = [{formato_numero(vector_y[i], frac)} - ({str_detalle})] / ({formato_numero(pivote, frac)}) "
            f"= {formato_numero(vector_x[i], frac)}"
        )
        
    x_str = ", ".join(formato_numero(xi, frac) for xi in vector_x)
    pasos.append(f"\nVector solución final: x = [ {x_str} ]ᵀ\n")
    pasos.append("-" * 78)
    
    return vector_y, vector_x, pasos, None


def verificar_solucion_ax_b(matriz_A, vector_x, vector_b, n, frac=True):
    """
    Evalúa la exactitud de la solución verificando si A · x == b.
    
    Retorna:
        (es_exacta, vector_calculado, pasos)
    """
    pasos = []
    pasos.append("PASO 3 · Comprobación A · x == b:")
    vector_calculado = []
    es_exacta = True
    
    for i in range(n):
        acum = Fraction(0)
        terminos = []
        for j in range(n):
            prod = matriz_A[i][j] * vector_x[j]
            acum += prod
            terminos.append(f"({formato_numero(matriz_A[i][j], frac)})·({formato_numero(vector_x[j], frac)})")
        vector_calculado.append(acum)
        coincide = (acum == vector_b[i])
        if not coincide:
            es_exacta = False
        estado = "✔" if coincide else "✘"
        pasos.append(
            f"   Fila {i+1}: " + " + ".join(terminos) + f" = {formato_numero(acum, frac)} "
            f"(b{i+1} = {formato_numero(vector_b[i], frac)}) [{estado}]"
        )
        
    if es_exacta:
        pasos.append("\n✓ Comprobación exitosa: A · x == b.")
    else:
        pasos.append("\n✘ Error en la comprobación: A · x != b.")
        
    return es_exacta, vector_calculado, pasos
