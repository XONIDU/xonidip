#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XONIDIP 2026 - Lanzador Universal (Mejorado + .bat para admin en Windows)
Detecta el sistema, instala dependencias, genera .bat y ejecuta xonidip.py

Desarrollado por: Darian Alberto Camacho Salas
Organización: XONIDU
"""

import subprocess
import sys
import os
import time
import platform
import shutil
import webbrowser
import threading

# ============================================================================
# Colores para terminal
# ============================================================================
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
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

# ============================================================================
# Detección del sistema
# ============================================================================
def get_system():
    return platform.system().lower()

def get_linux_distro():
    """Detecta el tipo de distribución Linux"""
    if get_system() != 'linux':
        return None
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if any(x in content for x in ['ubuntu', 'debian', 'mint', 'antix', 'kali']):
                    return 'debian-based'
                elif any(x in content for x in ['arch', 'manjaro']):
                    return 'arch-based'
                elif 'fedora' in content:
                    return 'fedora'
                elif 'centos' in content or 'rhel' in content:
                    return 'centos'
                elif 'opensuse' in content:
                    return 'opensuse'
        if shutil.which('apt'):
            return 'debian-based'
        elif shutil.which('pacman'):
            return 'arch-based'
        elif shutil.which('dnf'):
            return 'fedora'
        elif shutil.which('yum'):
            return 'centos'
        elif shutil.which('zypper'):
            return 'opensuse'
        return 'linux-generico'
    except:
        return 'linux-generico'

def get_python_command():
    if get_system() == 'windows':
        return ['python']
    else:
        try:
            subprocess.run(['python3', '--version'], capture_output=True, check=True)
            return ['python3']
        except:
            return ['python']

def get_pip_command():
    return [sys.executable, '-m', 'pip']

def get_install_flags():
    flags = []
    sistema = get_system()
    distro = get_linux_distro()
    if sistema == 'linux':
        if distro in ['arch-based', 'fedora']:
            flags.append('--break-system-packages')
        else:
            flags.append('--user')
    elif sistema == 'darwin':
        flags.append('--user')
    return flags

def print_banner():
    sistema = get_system()
    distro = get_linux_distro()
    sistema_texto = {
        'windows': 'WINDOWS',
        'linux': f'LINUX ({distro.upper()})' if distro else 'LINUX',
        'darwin': 'MACOS'
    }.get(sistema, 'DESCONOCIDO')
    
    banner = f"""
{Colors.PURPLE}{Colors.BOLD}╔══════════════════════════════════════════════════════════╗
║                    XONIDIP 2026 v4.2.0                      ║
║              Generador Profesional de Diplomas               ║
║                                                            ║
║               Sistema detectado: {sistema_texto:<27} ║
║                                                            ║
║               Desarrollado por: Darian Alberto             ║
║                      Camacho Salas                         ║
║                      Organización: XONIDU                  ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
    """
    print(banner)

# ============================================================================
# Verificación e instalación de pip
# ============================================================================
def check_python():
    try:
        cmd = get_python_command() + ['--version']
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except:
        return False

def check_pip():
    try:
        cmd = get_pip_command() + ['--version']
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except:
        return False

def install_pip_linux():
    distro = get_linux_distro()
    print(f"{Colors.YELLOW}Instalando pip en Linux ({distro})...{Colors.END}")
    if distro == 'debian-based':
        try:
            subprocess.run(['sudo', 'apt', 'update'], check=False)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'python3-pip'], check=True)
            return True
        except:
            return False
    elif distro == 'arch-based':
        try:
            subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'python-pip'], check=True)
            return True
        except:
            return False
    elif distro == 'fedora':
        try:
            subprocess.run(['sudo', 'dnf', 'install', '-y', 'python3-pip'], check=True)
            return True
        except:
            return False
    elif distro == 'centos':
        try:
            subprocess.run(['sudo', 'yum', 'install', '-y', 'python3-pip'], check=True)
            return True
        except:
            return False
    elif distro == 'opensuse':
        try:
            subprocess.run(['sudo', 'zypper', 'install', '-y', 'python3-pip'], check=True)
            return True
        except:
            return False
    return False

def install_pip_windows():
    print(f"{Colors.YELLOW}Instalando pip en Windows...{Colors.END}")
    try:
        subprocess.run([sys.executable, '-m', 'ensurepip', '--upgrade'], check=True)
        return True
    except:
        try:
            import urllib.request
            urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')
            subprocess.run([sys.executable, 'get-pip.py'], check=True)
            os.remove('get-pip.py')
            return True
        except:
            return False

# ============================================================================
# Dependencias desde requisitos.txt o lista por defecto
# ============================================================================
def get_requirements():
    if os.path.exists('requisitos.txt'):
        with open('requisitos.txt', 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        'flask==2.3.3',
        'pillow==10.0.1',
        'pandas==2.0.3',
        'qrcode==7.4.2',
        'openpyxl==3.1.2'
    ]

def check_dependencies():
    print(f"\n{Colors.BOLD}Verificando dependencias...{Colors.END}")
    reqs = get_requirements()
    missing = []
    for req in reqs:
        pkg = req.split('[')[0].split('==')[0].split('>=')[0].strip()
        try:
            __import__(pkg.replace('-', '_'))
            print(f"{Colors.GREEN}  - {pkg} OK{Colors.END}")
        except ImportError:
            print(f"{Colors.YELLOW}  - {pkg} (faltante){Colors.END}")
            missing.append(req)
    return missing

def install_dependencies(missing):
    if not missing:
        return True
    print(f"\n{Colors.BOLD}Instalando dependencias faltantes...{Colors.END}")
    pip_cmd = get_pip_command()
    flags = get_install_flags()
    success = True
    for req in missing:
        try:
            cmd = pip_cmd + ['install', req] + flags
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"{Colors.GREEN}    - {req} instalado{Colors.END}")
        except:
            try:
                cmd2 = pip_cmd + ['install', req]
                subprocess.run(cmd2, check=True)
                print(f"{Colors.GREEN}    - {req} instalado (sin flags){Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}    - Error instalando {req}: {e}{Colors.END}")
                success = False
    return success

# ============================================================================
# Verificar archivos necesarios
# ============================================================================
def check_files():
    if not os.path.exists('xonidip.py'):
        print(f"\n{Colors.RED}Error: No se encuentra xonidip.py{Colors.END}")
        return False
    for folder in ['templates', 'uploads', 'diplomas_generados', 'fonts']:
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
                print(f"{Colors.GREEN}Carpeta {folder} creada{Colors.END}")
            except:
                print(f"{Colors.YELLOW}No se pudo crear {folder}/{Colors.END}")
    return True

# ============================================================================
# Crear archivos .bat para Windows (con y sin admin)
# ============================================================================
def create_windows_bat():
    if get_system() != 'windows':
        return
    
    # .bat normal (solo ejecuta start.py)
    simple_bat = '''@echo off
title XONIDIP 2026
color 1F
echo ========================================
echo      XONIDIP 2026 - Generador de Diplomas
echo      Desarrollado por Darian Alberto
echo ========================================
echo.
python start.py
pause
'''
    with open('XONIDIP.bat', 'w', encoding='utf-8') as f:
        f.write(simple_bat)
    print(f"{Colors.GREEN}Creado XONIDIP.bat (ejecucion normal){Colors.END}")
    
    # .bat con administrador (solicita elevacion e instala dependencias)
    admin_bat = '''@echo off
title XONIDIP 2026 - Modo Administrador
color 1F
cls

echo ========================================
echo      XONIDIP 2026 - Generador de Diplomas
echo      (Modo Administrador)
echo ========================================
echo.

:: Verificar si se ejecuta como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Se requieren permisos de administrador.
    echo Solicitando elevacion...
    echo.
    :: Crear script VBS para solicitar elevacion
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\\getadmin.vbs"
    "%temp%\\getadmin.vbs"
    del "%temp%\\getadmin.vbs"
    exit /B
)

echo [OK] Permisos de administrador obtenidos
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado
    echo Descarga desde: https://www.python.org/downloads/
    echo IMPORTANTE: Marca "Add Python to PATH" durante la instalacion
    pause
    start https://www.python.org/downloads/
    exit
)

echo [OK] Python instalado
python --version
echo.

:: Instalar dependencias (con permisos de admin)
echo Instalando dependencias...
python -m pip install flask==2.3.3
python -m pip install pillow==10.0.1
python -m pip install pandas==2.0.3
python -m pip install qrcode==7.4.2
python -m pip install openpyxl==3.1.2
echo.
echo [OK] Dependencias instaladas
echo.

:: Iniciar XONIDIP
echo ========================================
echo Iniciando XONIDIP...
echo ========================================
echo.
start http://localhost:5000
python xonidip.py

pause
'''
    with open('XONIDIP_ADMIN.bat', 'w', encoding='utf-8') as f:
        f.write(admin_bat)
    print(f"{Colors.GREEN}Creado XONIDIP_ADMIN.bat (ejecutar como administrador){Colors.END}")

# ============================================================================
# Abrir navegador automaticamente
# ============================================================================
def open_browser_later():
    time.sleep(2)
    url = 'http://localhost:5000'
    try:
        webbrowser.open(url)
        print(f"{Colors.GREEN}Navegador abierto en {url}{Colors.END}")
    except:
        print(f"{Colors.YELLOW}No se pudo abrir el navegador automaticamente. Abre manualmente: {url}{Colors.END}")

# ============================================================================
# Ejecutar servidor (xonidip.py)
# ============================================================================
def run_server():
    print(f"\n{Colors.BOLD}Iniciando XONIDIP...{Colors.END}")
    print(f"{Colors.CYAN}Presiona Ctrl+C para detener el servidor{Colors.END}")
    print("-" * 60)
    
    browser_thread = threading.Thread(target=open_browser_later)
    browser_thread.daemon = True
    browser_thread.start()
    
    python_cmd = get_python_command()
    cmd = python_cmd + ['xonidip.py']
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Servidor detenido por el usuario{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Error ejecutando xonidip.py: {e}{Colors.END}")
        sys.exit(1)

# ============================================================================
# Menu principal
# ============================================================================
def main():
    os.system('clear' if get_system() != 'windows' else 'cls')
    print_banner()
    
    sistema = get_system()
    distro = get_linux_distro()
    print(f"{Colors.BOLD}Sistema operativo:{Colors.END} {sistema}")
    if distro:
        print(f"{Colors.BOLD}Distribucion:{Colors.END} {distro}")
    print(f"{Colors.BOLD}Python:{Colors.END} {sys.version.split()[0]}")
    print(f"{Colors.BOLD}Directorio:{Colors.END} {os.getcwd()}")
    
    # Crear archivos .bat si estamos en Windows
    if sistema == 'windows':
        create_windows_bat()
        print()
    
    if not check_files():
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    
    if not check_python():
        print(f"\n{Colors.RED}Error: Python no esta instalado o no esta en el PATH{Colors.END}")
        if sistema == 'windows':
            print("   Descarga Python desde: https://www.python.org/downloads/")
            print("   IMPORTANTE: Marca 'Add Python to PATH' durante la instalacion.")
        elif sistema == 'linux':
            print("   Instala Python con el gestor de paquetes de tu distribucion.")
        elif sistema == 'darwin':
            print("   Instala Python con: brew install python3")
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    
    if not check_pip():
        print(f"\n{Colors.YELLOW}Pip no encontrado. Intentando instalar...{Colors.END}")
        instalado = False
        if sistema == 'linux':
            instalado = install_pip_linux()
        elif sistema == 'windows':
            instalado = install_pip_windows()
        else:
            print(f"{Colors.YELLOW}Instala pip manualmente (python -m ensurepip) y vuelve a ejecutar.{Colors.END}")
        
        if not instalado:
            print(f"{Colors.RED}No se pudo instalar pip automaticamente. Instalalo manualmente y vuelve a ejecutar.{Colors.END}")
            input("\nPresiona Enter para salir...")
            sys.exit(1)
        else:
            print(f"{Colors.GREEN}Pip instalado correctamente{Colors.END}")
    
    missing = check_dependencies()
    if missing:
        print(f"\n{Colors.YELLOW}Faltan {len(missing)} dependencias.{Colors.END}")
        respuesta = input("Instalar automaticamente? (s/n): ")
        if respuesta.lower() == 's':
            if not install_dependencies(missing):
                print(f"{Colors.RED}Algunas dependencias no se instalaron. El servidor podria fallar.{Colors.END}")
                time.sleep(2)
        else:
            print(f"{Colors.YELLOW}No se instalaran. Continuando de todas formas...{Colors.END}")
    
    run_server()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Saliendo...{Colors.END}")
        sys.exit(0)
