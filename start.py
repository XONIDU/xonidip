#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XONIDIP 2026 - Lanzador Universal (v5.0)
Ahora con:
- Auto instalación de pip
- Mejor soporte Windows (python / py)
- .bat con permisos de administrador
- Manejo robusto de errores
"""

import subprocess
import sys
import os
import webbrowser
import time
import platform
import threading

# =========================
# COLORES
# =========================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def supports_color():
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                return kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                return False
        return True

if not Colors.supports_color():
    for attr in dir(Colors):
        if not attr.startswith('_') and attr != 'supports_color':
            setattr(Colors, attr, '')

# =========================
# DEPENDENCIAS
# =========================
REQUISITOS = [
    'flask==2.3.3',
    'pillow==10.0.1',
    'pandas==2.0.3',
    'qrcode==7.4.2',
    'openpyxl==3.1.2'
]

# =========================
# SISTEMA
# =========================
def get_system():
    return platform.system().lower()

def get_python_command():
    if get_system() == 'windows':
        for cmd in [['python'], ['py']]:
            try:
                subprocess.run(cmd + ['--version'], capture_output=True, check=True)
                return cmd
            except:
                continue
        return ['python']
    else:
        try:
            subprocess.run(['python3', '--version'], capture_output=True, check=True)
            return ['python3']
        except:
            return ['python']

def get_pip_command():
    return [sys.executable, '-m', 'pip']

# =========================
# ASEGURAR PIP
# =========================
def ensure_pip():
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                       capture_output=True, check=True)
        return True
    except:
        print(f"{Colors.YELLOW}pip no encontrado. Instalando...{Colors.END}")
        try:
            subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"],
                           check=True)
            print(f"{Colors.GREEN}pip instalado correctamente{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}No se pudo instalar pip{Colors.END}")
            print(e)
            return False

# =========================
# DEPENDENCIAS
# =========================
def check_dependencies():
    print(f"\n{Colors.BOLD}Verificando dependencias...{Colors.END}")
    missing = []

    for req in REQUISITOS:
        pkg = req.split('==')[0]
        try:
            __import__(pkg.replace('-', '_'))
            print(f"{Colors.GREEN}  ✔ {pkg}{Colors.END}")
        except:
            print(f"{Colors.YELLOW}  ✖ {pkg}{Colors.END}")
            missing.append(req)

    return missing

def install_dependencies(missing):
    if not missing:
        return True

    if not ensure_pip():
        return False

    print(f"\n{Colors.BOLD}Instalando dependencias...{Colors.END}")

    success = True
    for req in missing:
        try:
            subprocess.run(get_pip_command() + ['install', req], check=True)
            print(f"{Colors.GREEN}✔ {req}{Colors.END}")
        except:
            print(f"{Colors.RED}✖ Error en {req}{Colors.END}")
            success = False

    return success

# =========================
# BROWSER
# =========================
def open_browser():
    time.sleep(3)
    try:
        webbrowser.open("http://localhost:5000")
    except:
        pass

# =========================
# BAT ADMIN
# =========================
def crear_accesos_directos():
    sistema = get_system()

    if sistema == 'windows':
        with open('INICIAR_XONIDIP.bat', 'w') as f:
            f.write(r"""@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process cmd -ArgumentList '/c %~s0' -Verb runAs"
    exit /b
)

title XONIDIP 2026
color 1F

echo ================================
echo      XONIDIP 2026
echo ================================

where python >nul 2>&1
if %errorlevel%==0 (
    python start.py
) else (
    where py >nul 2>&1
    if %errorlevel%==0 (
        py start.py
    ) else (
        echo Python no encontrado
        pause
        exit /b
    )
)

pause
""")
        print(f"{Colors.GREEN}✔ BAT creado (modo admin){Colors.END}")

# =========================
# MAIN
# =========================
def main():
    os.system('cls' if get_system() == 'windows' else 'clear')

    print(f"{Colors.BLUE}{Colors.BOLD}XONIDIP 2026 INICIANDO...{Colors.END}")

    # Verificar Python
    try:
        subprocess.run(get_python_command() + ['--version'], check=True)
    except:
        print(f"{Colors.RED}Python no encontrado{Colors.END}")
        return

    # Dependencias
    missing = check_dependencies()

    if missing:
        resp = input("Instalar dependencias? (s/n): ")
        if resp.lower() == 's':
            install_dependencies(missing)

    # Verificar archivo principal
    if not os.path.exists('xonidip.py'):
        print(f"{Colors.RED}xonidip.py no encontrado{Colors.END}")
        return

    print(f"{Colors.GREEN}Iniciando servidor...{Colors.END}")

    threading.Thread(target=open_browser, daemon=True).start()

    try:
        subprocess.run(get_python_command() + ['xonidip.py'])
    except KeyboardInterrupt:
        print("\nServidor detenido")

# =========================
# RUN
# =========================
if __name__ == '__main__':
    try:
        crear_accesos_directos()
        main()
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        input("Enter para salir...")
