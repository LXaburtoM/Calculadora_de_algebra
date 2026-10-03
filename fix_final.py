import os
import glob

directory = r'C:\Users\lxman\Desktop\Clases\Algebra\Calculadora_Algebra_Lineal_Grupo\gui'
py_files = glob.glob(directory + '/**/*.py', recursive=True)

for filepath in py_files:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Arreglar la linea gigantesca
    content = content.replace('â”€', '-')
    content = content.replace('─', '-')
    
    # Arreglar las tildes y símbolos raros en la interfaz
    content = content.replace('CombinaciÃ³n', 'Combinación')
    content = content.replace('PrÃ³ximamente', 'Próximamente')
    content = content.replace('Ã lgebra', 'Álgebra')
    content = content.replace('â„ ⁿ', 'Rⁿ')
    content = content.replace('Aáµ€', 'Aᵀ')
    content = content.replace('vâ‚‚', 'v₂')
    content = content.replace('vâ‚–', 'vₖ')
    content = content.replace('câ‚–', 'cₖ')
    content = content.replace('â€¦', '...')
    content = content.replace('âˆ’', '-')
    content = content.replace('Á—', '×')
    content = content.replace('â€¢', '•')
    content = content.replace('âœ”', '✔')
    content = content.replace('âœ˜', '✘')
    content = content.replace('áµ€', 'ᵀ')
    content = content.replace('Â·', '·')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Limpiado {filepath}")
