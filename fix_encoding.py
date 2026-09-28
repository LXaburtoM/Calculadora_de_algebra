import os
import glob

directory = r'C:\Users\lxman\Desktop\Clases\Algebra\Calculadora_Algebra_Lineal_Grupo\gui'
py_files = glob.glob(directory + '/**/*.py', recursive=True)

# Lista manual de arreglos
arreglos = [
    ("Ã³", "ó"), ("Ã¡", "á"), ("Ã©", "é"), ("Ã\xad", "í"), ("Ãº", "ú"), ("Ã±", "ñ"),
    ("Ã\x81", "Á"), ("Ã‰", "É"), ("Ã\x8d", "Í"), ("Ã“", "Ó"), ("Ãš", "Ú"),
    ("Â°", "°"), ("â\x81»", "⁻"), ("â\x81¹", "¹"), ("â\x81¿", "ⁿ"),
    ("â‚\x81", "₁"), ("â‚\x82", "₂"), ("â‚\x83", "₃"), ("â‚\x84", "₄"), ("â‚\x85", "₅"),
    ("â‚\x86", "₆"), ("â‚\x87", "₇"), ("â‚\x88", "₈"), ("â‚\x89", "₉"), ("â‚\x80", "₀"),
    ("â\x94\x80", "─"), ("â–¶", "▶"), ("Â²", "²"), ("Â³", "³"),
    ("â\x80\x9c", '"'), ("â\x80\x9d", '"'), ("â\x80\x98", "'"), ("â\x80\x99", "'"),
    ("â\x80\x94", "—"), ("â\x80\x93", "–"), ("â\x80\xa6", "…"), ("â€\x8e", ""), ("â\x80\x8b", ""),
    ("Â", ""), ("Ã", "Á"), ("Á³", "ó"), ("Á³", "ó") # Fallbacks
]

for filepath in py_files:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    if content.startswith('\ufeff'):
        content = content[1:]
        
    for bad, good in arreglos:
        content = content.replace(bad, good)
        
    # Correcciones manuales extra por si acaso
    content = content.replace("CombinaciÁn", "Combinación")
    content = content.replace("OperaciÁn", "Operación")
    content = content.replace("Matriciales BÁ¡sicas", "Matriciales Básicas")
    content = content.replace("PrÁ³ximamente", "Próximamente")
    content = content.replace("MÁ³dulo", "Módulo")
    content = content.replace("NÁºmero", "Número")
    content = content.replace("DimensiÁn", "Dimensión")
    content = content.replace("ConfiguraciÁn", "Configuración")
    content = content.replace("Álgebra", "Álgebra")
    content = content.replace("Á lgebra", "Álgebra")
    content = content.replace("Á¡", "á")
    content = content.replace("Á©", "é")
    content = content.replace("Á\xad", "í")
    content = content.replace("Áº", "ú")
    content = content.replace("Á±", "ñ")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Procesado: {filepath}')
