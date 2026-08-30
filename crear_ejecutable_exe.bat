@echo off
title Generando Programa Ejecutable (.EXE)
cd /d "%~dp0"

echo ===================================================
echo   GENERANDO ARCHIVO EJECUTABLE (.EXE) PARA EL GRUPO
echo ===================================================
echo.
echo Esto creara un archivo .exe independiente en tu Escritorio.
echo No requerira instalar Python ni librerias en otras computadoras.
echo Por favor espera unos segundos...
echo.

venv\Scripts\pyinstaller.exe --noconsole --onefile --name "Calculadora_Algebra_Lineal" main.py

if exist "dist\Calculadora_Algebra_Lineal.exe" (
    copy /y "dist\Calculadora_Algebra_Lineal.exe" "%USERPROFILE%\Desktop\Calculadora_Algebra_Lineal.exe"
    echo.
    echo ===================================================
    echo [EXITO] Programa .exe generado con exito en tu Escritorio:
    echo %USERPROFILE%\Desktop\Calculadora_Algebra_Lineal.exe
    echo ===================================================
) else (
    echo [ERROR] Hubo un problema al generar el ejecutable.
)

pause