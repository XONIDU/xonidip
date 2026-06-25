#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XONIDIP 2026 - Lanzador Universal (Ultra Robust)
Detecta el sistema, instala pip si falta, instala dependencias con multiples estrategias
Genera .bat en Windows y ejecuta xonidip.py

Desarrollado por: Darian Alberto Camacho Salas
Organizacion: XONIDU
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
# Deteccion del sistema
# ============================================================================
def get_system():
    return platform.system().lower()

def get_linux_distro():
    """Detecta el tipo de distribucion Linux"""
    if get_system() != 'linux':
        return None
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if any(x in content for x in ['ubuntu', 'debian', 'mint', 'antix', 'kali']):
                    return 'debian-based'
                elif any(x in content for x in ['arch', 'manjaro', 'endeavouros']):
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
║                    XONIDIP 2026 v4.3.0                      ║
║              Generador Profesional de Diplomas               ║
║                   (Instalacion Ultra Robust)                 ║
║                                                            ║
║               Sistema detectado: {sistema_texto:<27} ║
║                                                            ║
║               Desarrollado por: Darian Alberto             ║
║                      Camacho Salas                         ║
║                      Organizacion: XONIDU                  ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
    """
    print(banner)

# ============================================================================
# Verificacion de Python
# ============================================================================
def check_python():
    try:
        cmd = get_python_command() + ['--version']
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except:
        return False

# ============================================================================
# INSTALACION DE PIP - MULTIPLES ESTRATEGIAS
# ============================================================================
def check_pip():
    try:
        cmd = get_pip_command() + ['--version']
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except:
        return False

def install_pip_windows():
    """Instala pip en Windows usando multiples metodos"""
    print(f"{Colors.YELLOW}Instalando pip en Windows...{Colors.END}")
    
    # Metodo 1: ensurepip
    try:
        print("  Intentando con ensurepip...")
        subprocess.run([sys.executable, '-m', 'ensurepip', '--upgrade'], check=True)
        print(f"{Colors.GREEN}  Pip instalado con ensurepip{Colors.END}")
        return True
    except:
        pass
    
    # Metodo 2: get-pip.py
    try:
        print("  Descargando get-pip.py...")
        import urllib.request
        urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')
        subprocess.run([sys.executable, 'get-pip.py'], check=True)
        os.remove('get-pip.py')
        print(f"{Colors.GREEN}  Pip instalado con get-pip.py{Colors.END}")
        return True
    except:
        pass
    
    print(f"{Colors.RED}  No se pudo instalar pip en Windows{Colors.END}")
    return False

def install_pip_linux():
    """Instala pip en Linux usando el gestor de paquetes de la distro"""
    distro = get_linux_distro()
    print(f"{Colors.YELLOW}Instalando pip en Linux ({distro})...{Colors.END}")
    
    if distro == 'debian-based':
        try:
            print("  Usando apt (Debian/Ubuntu/Mint)...")
            subprocess.run(['sudo', 'apt', 'update'], check=False)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'python3-pip'], check=True)
            print(f"{Colors.GREEN}  Pip instalado con apt{Colors.END}")
            return True
        except:
            pass
    elif distro == 'arch-based':
        try:
            print("  Usando pacman (Arch/Manjaro)...")
            subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'python-pip'], check=True)
            print(f"{Colors.GREEN}  Pip instalado con pacman{Colors.END}")
            return True
        except:
            pass
    elif distro == 'fedora':
        try:
            print("  Usando dnf (Fedora)...")
            subprocess.run(['sudo', 'dnf', 'install', '-y', 'python3-pip'], check=True)
            print(f"{Colors.GREEN}  Pip instalado con dnf{Colors.END}")
            return True
        except:
            pass
    elif distro == 'centos':
        try:
            print("  Usando yum (CentOS)...")
            subprocess.run(['sudo', 'yum', 'install', '-y', 'python3-pip'], check=True)
            print(f"{Colors.GREEN}  Pip instalado con yum{Colors.END}")
            return True
        except:
            pass
    elif distro == 'opensuse':
        try:
            print("  Usando zypper (openSUSE)...")
            subprocess.run(['sudo', 'zypper', 'install', '-y', 'python3-pip'], check=True)
            print(f"{Colors.GREEN}  Pip instalado con zypper{Colors.END}")
            return True
        except:
            pass
    
    # Metodo alternativo: ensurepip
    try:
        print("  Intentando con ensurepip...")
        subprocess.run([sys.executable, '-m', 'ensurepip', '--upgrade'], check=True)
        print(f"{Colors.GREEN}  Pip instalado con ensurepip{Colors.END}")
        return True
    except:
        pass
    
    # Metodo alternativo: get-pip.py
    try:
        print("  Intentando con get-pip.py...")
        import urllib.request
        urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')
        subprocess.run([sys.executable, 'get-pip.py', '--user'], check=True)
        os.remove('get-pip.py')
        print(f"{Colors.GREEN}  Pip instalado con get-pip.py (--user){Colors.END}")
        return True
    except:
        pass
    
    print(f"{Colors.RED}  No se pudo instalar pip en Linux{Colors.END}")
    return False

def install_pip_mac():
    """Instala pip en macOS"""
    print(f"{Colors.YELLOW}Instalando pip en macOS...{Colors.END}")
    
    # Metodo 1: brew
    try:
        print("  Intentando con brew...")
        subprocess.run(['brew', 'install', 'python3'], check=True)
        print(f"{Colors.GREEN}  Pip instalado con brew{Colors.END}")
        return True
    except:
        pass
    
    # Metodo 2: ensurepip
    try:
        print("  Intentando con ensurepip...")
        subprocess.run([sys.executable, '-m', 'ensurepip', '--upgrade'], check=True)
        print(f"{Colors.GREEN}  Pip instalado con ensurepip{Colors.END}")
        return True
    except:
        pass
    
    # Metodo 3: get-pip.py
    try:
        print("  Intentando con get-pip.py...")
        import urllib.request
        urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')
        subprocess.run([sys.executable, 'get-pip.py', '--user'], check=True)
        os.remove('get-pip.py')
        print(f"{Colors.GREEN}  Pip instalado con get-pip.py{Colors.END}")
        return True
    except:
        pass
    
    print(f"{Colors.RED}  No se pudo instalar pip en macOS{Colors.END}")
    return False

def ensure_pip():
    """Asegura que pip este instalado en cualquier sistema"""
    if check_pip():
        print(f"{Colors.GREEN}Pip ya instalado{Colors.END}")
        return True
    
    print(f"\n{Colors.YELLOW}Pip no encontrado. Instalando...{Colors.END}")
    sistema = get_system()
    
    if sistema == 'windows':
        return install_pip_windows()
    elif sistema == 'linux':
        return install_pip_linux()
    elif sistema == 'darwin':
        return install_pip_mac()
    else:
        print(f"{Colors.RED}Sistema no soportado para instalacion automatica de pip{Colors.END}")
        return False

# ============================================================================
# DEPENDENCIAS - MULTIPLES ESTRATEGIAS DE INSTALACION
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

def install_with_pip(package, flags):
    """Intenta instalar con pip y flags especificos"""
    try:
        cmd = [sys.executable, '-m', 'pip', 'install', package] + flags
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except:
        return False

def install_dependency(package):
    """Instala una dependencia con multiples estrategias"""
    print(f"  Instalando {package}...")
    
    sistema = get_system()
    distro = get_linux_distro()
    
    # ===== ESTRATEGIA 1: Con flags especificos segun sistema =====
    flags = []
    if sistema == 'linux':
        if distro in ['arch-based', 'fedora']:
            flags = ['--break-system-packages']
        else:
            flags = ['--user']
    elif sistema == 'darwin':
        flags = ['--user']
    
    if flags and install_with_pip(package, flags):
        print(f"{Colors.GREEN}    - {package} instalado (con flags){Colors.END}")
        return True
    
    # ===== ESTRATEGIA 2: Sin flags =====
    if install_with_pip(package, []):
        print(f"{Colors.GREEN}    - {package} instalado (sin flags){Colors.END}")
        return True
    
    # ===== ESTRATEGIA 3: Solo --break-system-packages (para sistemas protegidos) =====
    if install_with_pip(package, ['--break-system-packages']):
        print(f"{Colors.GREEN}    - {package} instalado (--break-system-packages){Colors.END}")
        return True
    
    # ===== ESTRATEGIA 4: Solo --user =====
    if install_with_pip(package, ['--user']):
        print(f"{Colors.GREEN}    - {package} instalado (--user){Colors.END}")
        return True
    
    # ===== ESTRATEGIA 5: Con --force-reinstall (para casos extremos) =====
    if install_with_pip(package, ['--force-reinstall', '--break-system-packages']):
        print(f"{Colors.GREEN}    - {package} instalado (--force-reinstall){Colors.END}")
        return True
    
    # ===== ESTRATEGIA 6: En Linux, intentar con pacman (solo para Arch) =====
    if sistema == 'linux' and distro == 'arch-based':
        pkg_name = package.split('==')[0].lower()
        # Mapeo de nombres de paquetes pip -> pacman
        pacman_map = {
            'flask': 'python-flask',
            'pillow': 'python-pillow',
            'pandas': 'python-pandas',
            'qrcode': 'python-qrcode',
            'openpyxl': 'python-openpyxl'
        }
        pacman_pkg = pacman_map.get(pkg_name)
        if pacman_pkg:
            try:
                print(f"    Intentando con pacman -S {pacman_pkg}...")
                subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', pacman_pkg], check=True)
                print(f"{Colors.GREEN}    - {package} instalado con pacman{Colors.END}")
                return True
            except:
                pass
    
    # ===== ESTRATEGIA 7: En Debian/Ubuntu, intentar con apt =====
    if sistema == 'linux' and distro == 'debian-based':
        pkg_name = package.split('==')[0].lower()
        apt_map = {
            'flask': 'python3-flask',
            'pillow': 'python3-pil',
            'pandas': 'python3-pandas',
            'qrcode': 'python3-qrcode',
            'openpyxl': 'python3-openpyxl'
        }
        apt_pkg = apt_map.get(pkg_name)
        if apt_pkg:
            try:
                print(f"    Intentando con apt install {apt_pkg}...")
                subprocess.run(['sudo', 'apt', 'update'], check=False)
                subprocess.run(['sudo', 'apt', 'install', '-y', apt_pkg], check=True)
                print(f"{Colors.GREEN}    - {package} instalado con apt{Colors.END}")
                return True
            except:
                pass
    
    print(f"{Colors.RED}    - Error instalando {package} (todas las estrategias fallaron){Colors.END}")
    return False

def install_dependencies(missing):
    if not missing:
        return True
    
    print(f"\n{Colors.BOLD}Instalando dependencias faltantes (multiples estrategias)...{Colors.END}")
    success = True
    for req in missing:
        if not install_dependency(req):
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
python -m pip install flask==2.3.3 --break-system-packages
python -m pip install pillow==10.0.1 --break-system-packages
python -m pip install pandas==2.0.3 --break-system-packages
python -m pip install qrcode==7.4.2 --break-system-packages
python -m pip install openpyxl==3.1.2 --break-system-packages
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
    
    # Asegurar que pip esta instalado
    if not ensure_pip():
        print(f"{Colors.RED}No se pudo instalar pip. Instalalo manualmente y vuelve a ejecutar.{Colors.END}")
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    
    # Verificar e instalar dependencias
    missing = check_dependencies()
    if missing:
        print(f"\n{Colors.YELLOW}Faltan {len(missing)} dependencias.{Colors.END}")
        respuesta = input("Instalar automaticamente? (s/n): ")
        if respuesta.lower() == 's':
            if not install_dependencies(missing):
                print(f"{Colors.RED}Algunas dependencias no se instalaron.{Colors.END}")
                print(f"{Colors.YELLOW}El servidor podria fallar. Puedes intentar instalarlas manualmente:{Colors.END}")
                print(f"  pip install {', '.join(missing)} --break-system-packages")
                time.sleep(3)
        else:
            print(f"{Colors.YELLOW}No se instalaran dependencias. Continuando de todas formas...{Colors.END}")
    
    run_server()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Saliendo...{Colors.END}")
        sys.exit(0)
