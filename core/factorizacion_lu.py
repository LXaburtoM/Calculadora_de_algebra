"""
Módulo 5: Factorización LU y Resolución de Sistemas Ax = b.
Tema: Descomposición LU sin intercambios de fila y sustitución progresiva/regresiva (Sesión 12).
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""
from fractions import Fraction
from core.parser import formato_numero
from core.operaciones_matriciales import multiplicar_matrices
from core.validadores import comparar_matrices


def factorizacion_lu(matriz_A, m, n):
    """
    Calcula la factorización A = L · U sin intercambios de filas.
    
    Parámetros:
        matriz_A: Lista anidada con los coeficientes de la matriz m x n.
        m: Número de filas.
        n: Número de columnas.
        
    Retorna:
        (matriz_L, matriz_U, pasos, error_msg)
    """
    # U inicia como copia exacta de A para almacenar las operaciones de fila
    matriz_U = [[matriz_A[i][j] for j in range(n)] for i in range(m)]
    
    # L inicia como matriz identidad m x m (unos en la diagonal, ceros en el resto)
    matriz_L = [[Fraction(1) if i == j else Fraction(0) for j in range(m)] for i in range(m)]
    
    pasos = []
    pasos.append("INICIO DE FACTORIZACIÓN LU (A = L · U):")
    pasos.append(f"Dimensiones de A: {m}×{n}. Matriz L de orden {m}×{m}, matriz U de orden {m}×{n}.\n")
    
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
                        "(requiere pivoteo parcial PA = LU)."
                    )
            # Si toda la columna debajo es cero, no se requiere eliminación en esta columna
            continue
            
        pasos.append(f"--- Columna {k+1} (Pivote en U[{k+1},{k+1}] = {formato_numero(pivote)}) ---")
        
        for i in range(k + 1, m):
            elem = matriz_U[i][k]
            if elem != 0:
                # Se calcula el multiplicador exacto de eliminación por filas
                multiplicador_l = elem / pivote
                
                # Se registra el multiplicador en L antes de alterar la fila en U
                matriz_L[i][k] = multiplicador_l
                
                pasos.append(
                    f"   Multiplicador L[{i+1},{k+1}] = ({formato_numero(elem)}) / ({formato_numero(pivote)}) "
                    f"= {formato_numero(multiplicador_l)}"
                )
                pasos.append(
                    f"   Operación en U: F{i+1} ← F{i+1} - ({formato_numero(multiplicador_l)}) · F{k+1}"
                )
                
                # Reemplazo de fila en U para generar el cero bajo el pivote
                for j in range(k, n):
                    matriz_U[i][j] -= multiplicador_l * matriz_U[k][j]
                    
    # Verificación computacional: evaluar si L · U == A
    LU, _, _ = multiplicar_matrices(matriz_L, matriz_U, m, m, n)
    es_correcta = comparar_matrices(LU, matriz_A)
    
    if es_correcta:
        pasos.append("\n✔ Verificación de Factorización: La factorización es correcta (L · U == A).")
    else:
        pasos.append("\n✘ Error en la factorización: L · U difiere de A.")
        
    return matriz_L, matriz_U, pasos, None


def resolver_sistema_lu(matriz_L, matriz_U, vector_b, n):
    """
    Resuelve el sistema cuadrado Ax = b mediante doble sustitución:
    1) Ly = b (sustitución progresiva hacia adelante)
    2) Ux = y (sustitución regresiva hacia atrás)
    
    Parámetros:
        matriz_L: Matriz triangular inferior n x n con unos en la diagonal.
        matriz_U: Matriz triangular superior n x n.
        vector_b: Lista con los n términos independientes.
        n: Orden del sistema.
        
    Retorna:
        (vector_y, vector_x, pasos, error_msg)
    """
    pasos = []
    
    # ── ETAPA 1: Sustitución hacia adelante Ly = b ──────────────────
    pasos.append("ETAPA 1: Resolución del sistema triangular inferior L · y = b (Hacia adelante):")
    vector_y = [Fraction(0)] * n
    
    for i in range(n):
        suma = Fraction(0)
        detalle_suma = []
        for j in range(i):
            prod = matriz_L[i][j] * vector_y[j]
            suma += prod
            detalle_suma.append(f"({formato_numero(matriz_L[i][j])})·({formato_numero(vector_y[j])})")
            
        # Como L[i][i] = 1, y[i] = b[i] - suma
        vector_y[i] = vector_b[i] - suma
        
        str_detalle = " - ".join(detalle_suma) if detalle_suma else "0"
        pasos.append(
            f"   y{i+1} = {formato_numero(vector_b[i])} - [{str_detalle}] = {formato_numero(vector_y[i])}"
        )
        
    # ── ETAPA 2: Sustitución hacia atrás Ux = y ─────────────────────
    pasos.append("\nETAPA 2: Resolución del sistema triangular superior U · x = y (Hacia atrás):")
    vector_x = [Fraction(0)] * n
    
    for i in range(n - 1, -1, -1):
        pivote = matriz_U[i][i]
        if pivote == 0:
            return None, None, pasos, (
                f"Pivote U[{i+1},{i+1}] = 0. La matriz U es singular, "
                "el sistema no tiene solución única."
            )
            
        suma = Fraction(0)
        detalle_suma = []
        for j in range(i + 1, n):
            prod = matriz_U[i][j] * vector_x[j]
            suma += prod
            detalle_suma.append(f"({formato_numero(matriz_U[i][j])})·({formato_numero(vector_x[j])})")
            
        numerador = vector_y[i] - suma
        vector_x[i] = numerador / pivote
        
        str_detalle = " - ".join(detalle_suma) if detalle_suma else "0"
        pasos.append(
            f"   x{i+1} = [{formato_numero(vector_y[i])} - ({str_detalle})] / ({formato_numero(pivote)}) "
            f"= {formato_numero(vector_x[i])}"
        )
        
    return vector_y, vector_x, pasos, None


def verificar_solucion_ax_b(matriz_A, vector_x, vector_b, n):
    """
    Evalúa la exactitud de la solución verificando si A · x == b.
    
    Retorna:
        (es_exacta, vector_calculado, pasos)
    """
    pasos = []
    pasos.append("ETAPA 3: Comprobación de la solución evaluando A · x == b:")
    vector_calculado = []
    es_exacta = True
    
    for i in range(n):
        acum = Fraction(0)
        terminos = []
        for j in range(n):
            prod = matriz_A[i][j] * vector_x[j]
            acum += prod
            terminos.append(f"({formato_numero(matriz_A[i][j])})·({formato_numero(vector_x[j])})")
        vector_calculado.append(acum)
        coincide = (acum == vector_b[i])
        if not coincide:
            es_exacta = False
        estado = "✔" if coincide else "✘"
        pasos.append(
            f"   Fila {i+1}: " + " + ".join(terminos) + f" = {formato_numero(acum)} "
            f"(b{i+1} = {formato_numero(vector_b[i])}) [{estado}]"
        )
        
    if es_exacta:
        pasos.append("\n✔ Comprobación exitosa: A · x == b.")
    else:
        pasos.append("\n✘ Error en la comprobación: A · x != b.")
        
    return es_exacta, vector_calculado, pasos
