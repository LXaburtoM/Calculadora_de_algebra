@echo off
title Exportar ZIP Limpio para el Grupo
cd /d "%~dp0"

echo ===================================================
echo   EXPORTANDO PROYECTO LIMPIO PARA COMPARTIR
echo ===================================================
echo.

venv\Scripts\python.exe -c "import os, zipfile; proj=r'.'+os.sep; desktop=os.path.join(os.path.expanduser('~'), 'Desktop'); zip_path=os.path.join(desktop, 'Calculadora_Algebra_Lineal_Grupo.zip'); ignore={'venv','_Pycache__','.git','.vscode'}; zipf=zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED); [zipf.write(os.path.join(r,f), os.path.relpath(os.path.join(r,f), proj)) for rd,files in os.walk(proj) if not any(ig in r.split(os.sep) for ig in ignore) for f in files if not f.endswith(('.pyc','.pyo'))]; zipf.close(); print('[EXITO] ZIP creado en tu Escritorio:', zip_path)"

echo.
echo Presiona cualquier tecla para cerrar...
pause > nul