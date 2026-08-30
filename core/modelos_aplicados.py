"""
Catálogo de Modelos Aplicados de Álgebra Lineal (Asignación de Recursos, Flujo de Redes, Inversión).
Incluye enunciados, significado de variables, ecuaciones y matrices de planteamiento.
"""

from fractions import Fraction

MODELOS = [
    {
        "id": "recursos",
        "nombre": "1. Asignación de Recursos y Mezcla de Producción",
        "descripcion": (
            "Una fábrica manufactura 3 productos (P₁, P₂, P₃) usando tres recursos: Mano de Obra, "
            "Horas de Máquina y Materia Prima.\n\n"
            "• P₁ requiere: 1h de mano de obra, 2h de máquina y 1kg de material.\n"
            "• P₂ requiere: 2h de mano de obra, 1h de máquina y 3kg de material.\n"
            "• P₃ requiere: 1h de mano de obra, 3h de máquina y 2kg de material.\n\n"
            "Se dispone semanalmente de: 100h de mano de obra, 150h de máquina y 140kg de material.\n"
            "¿Cuántas unidades de cada producto deben fabricarse para agotar exactamente los recursos?"
        ),
        "variables": [
            "x₁ = Unidades semanales de Producto 1",
            "x₂ = Unidades semanales de Producto 2",
            "x₃ = Unidades semanales de Producto 3"
        ],
        "ecuaciones": [
            "Mano de obra: 1·x₁ + 2·x₂ + 1·x₃ = 100",
            "Horas máquina: 2·x₁ + 1·x₂ + 3·x₃ = 150",
            "Materia prima: 1·x₁ + 3·x₂ + 2·x₃ = 140"
        ],
        "m": 3,
        "n": 3,
        "matriz": [
            [Fraction(1), Fraction(2), Fraction(1), Fraction(100)],
            [Fraction(2), Fraction(1), Fraction(3), Fraction(150)],
            [Fraction(1), Fraction(3), Fraction(2), Fraction(140)]
        ]
    },
    {
        "id": "trafico",
        "nombre": "2. Análisis de Flujo de Redes de Tráfico",
        "descripcion": (
            "Se analiza el flujo vehicular (vehículos/hora) en una red urbana con 4 intersecciones (A, B, C, D).\n"
            "Por el principio de conservación de flujo: En cada intersección, la suma del flujo que entra "
            "debe ser igual a la suma del flujo que sale (Entrada = Salida).\n\n"
            "• Intersección A: x₁ + x₄ = 400 + 300  ->  x₁ + x₄ = 700\n"
            "• Intersección B: x₁ + x₂ = 600 + 200  ->  x₁ + x₂ = 800\n"
            "• Intersección C: x₂ + x₃ = 500 + 100  ->  x₂ + x₃ = 600\n"
            "• Intersección D: x₃ + x₄ = 300 + 200  ->  x₃ + x₄ = 500\n\n"
            "Determina el patrón de flujo general y analiza las variables libres."
        ),
        "variables": [
            "x₁ = Flujo de calle 1 (veh/h)",
            "x₂ = Flujo de calle 2 (veh/h)",
            "x₃ = Flujo de calle 3 (veh/h)",
            "x₄ = Flujo de calle 4 (veh/h)"
        ],
        "ecuaciones": [
            "Nodo A: 1·x₁ + 0·x₂ + 0·x₃ + 1·x₄ = 700",
            "Nodo B: 1·x₁ + 1·x₂ + 0·x₃ + 0·x₄ = 800",
            "Nodo C: 0·x₁ + 1·x₂ + 1·x₃ + 0·x₄ = 600",
            "Nodo D: 0·x₁ + 0·x₂ + 1·x₃ + 1·x₄ = 500"
        ],
        "m": 4,
        "n": 4,
        "matriz": [
            [Fraction(1), Fraction(0), Fraction(0), Fraction(1), Fraction(700)],
            [Fraction(1), Fraction(1), Fraction(0), Fraction(0), Fraction(800)],
            [Fraction(0), Fraction(1), Fraction(1), Fraction(0), Fraction(600)],
            [Fraction(0), Fraction(0), Fraction(1), Fraction(1), Fraction(500)]
        ]
    },
    {
        "id": "inversion",
        "nombre": "3. Asignación Presupuestaria y Portafolio de Inversión",
        "descripcion": (
            "Un inversionista desea distribuir un capital de $100,000 entre 3 opciones: Bonos seguros (6%), "
            "Acciones de valor (8%) y Fondos inmobiliarios (10%).\n\n"
            "Condiciones del cliente:\n"
            "1. El capital total invertido debe ser exactamente $100,000.\n"
            "2. El retorno anual esperado debe ser de $8,200.\n"
            "3. La cantidad invertida en Fondos inmobiliarios debe ser igual a la suma de las otras dos opciones menos $20,000.\n\n"
            "Determina la cantidad exacta a invertir en cada instrumento."
        ),
        "variables": [
            "x₁ = Capital en Bonos (al 6%)",
            "x₂ = Capital en Acciones (al 8%)",
            "x₃ = Capital en Fondos Inmobiliarios (al 10%)"
        ],
        "ecuaciones": [
            "Capital total: 1·x₁ + 1·x₂ + 1·x₃ = 100000",
            "Rendimiento anual: (6/100)·x₁ + (8/100)·x₂ + (10/100)·x₃ = 8200",
            "Balance de inversión: 1·x₁ + 1·x₂ - 1·x₃ = 20000"
        ],
        "m": 3,
        "n": 3,
        "matriz": [
            [Fraction(1), Fraction(1), Fraction(1), Fraction(100000)],
            [Fraction(6, 100), Fraction(8, 100), Fraction(10, 100), Fraction(8200)],
            [Fraction(1), Fraction(1), Fraction(-1), Fraction(20000)]
        ]
    }
]
