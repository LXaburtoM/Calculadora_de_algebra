@echo off
title Configurando e Iniciando Calculadora de Algebra Lineal
cd /d "%~dp0"

echo ===================================================
echo   CONFIGURADOR AUTOMATICO PARA INTEGRANTES DEL GRUPO
echo ===================================================
echo.
 if not exist venv (
    echo [1/3] Creando entorno virtual local...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo [ERROR] No se encontro Python instalado en el sistema.
        echo Por favor instala Python desde https://www.python.org/ y marca la casilla "Add Python to PATH".
        pause
        exit /b
    )
) else (
    echo [1/3] Entorno virtual detectado.
)

echo [2/3] Instalando / Actualizando librerias necesarias...
call venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo [3/3] Iniciando la Calculadora...
echo ===================================================
call venv\Scripts\python.exe main.py

pause