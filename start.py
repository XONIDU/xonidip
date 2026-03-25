#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XONIDIP 2026 - Lanzador Universal
Este script ahora es el ENCARGADO de ejecutar xonidip.py
Detecta automáticamente el sistema y usa los comandos correctos
Desarrollado por: Darian Alberto Camacho Salas
Somos XONIDU
"""

import subprocess
import sys
import os
import webbrowser
import time
import platform
import threading

# Colores para terminal
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
        """Verifica si la terminal soporta colores"""
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                return kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                return False
        return True

# Desactivar colores si no hay soporte
if not Colors.supports_color():
    for attr in dir(Colors):
        if not attr.startswith('_') and attr != 'supports_color':
            setattr(Colors, attr, '')

# Dependencias necesarias para xonidip.py
REQUISITOS = [
    'flask==2.3.3',
    'pillow==10.0.1',
    'pandas==2.0.3',
    'qrcode==7.4.2',
    'openpyxl==3.1.2'
]

def get_system():
    """Detecta el sistema operativo"""
    return platform.system().lower()

def get_linux_distro():
    """Detecta la distribución de Linux específica"""
    if get_system() != 'linux':
        return None
    
    try:
        # Intentar leer /etc/os-release
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'ubuntu' in content:
                    return 'ubuntu'
                elif 'debian' in content:
                    return 'debian'
                elif 'fedora' in content:
                    return 'fedora'
                elif 'centos' in content:
                    return 'centos'
                elif 'arch' in content:
                    return 'arch'
                elif 'manjaro' in content:
                    return 'manjaro'
                elif 'mint' in content:
                    return 'mint'
                elif 'opensuse' in content:
                    return 'opensuse'
        
        # Intentar con lsb_release
        try:
            result = subprocess.run(['lsb_release', '-i'], capture_output=True, text=True)
            if 'Ubuntu' in result.stdout:
                return 'ubuntu'
            elif 'Debian' in result.stdout:
                return 'debian'
            elif 'Fedora' in result.stdout:
                return 'fedora'
            elif 'CentOS' in result.stdout:
                return 'centos'
        except:
            pass
        
        return 'linux-generico'
    except:
        return 'linux-generico'

def get_python_command():
    """Obtiene el comando Python correcto según el sistema"""
    if get_system() == 'windows':
        return ['python']
    else:
        # En Linux/Mac, probar python3 primero
        try:
            subprocess.run(['python3', '--version'], capture_output=True, check=True)
            return ['python3']
        except:
            return ['python']

def get_pip_command():
    """Obtiene el comando pip correcto según el sistema"""
    return [sys.executable, '-m', 'pip']

def get_install_flags():
    """Obtiene los flags de instalación según el sistema y distro"""
    flags = []
    sistema = get_system()
    distro = get_linux_distro()
    
    if sistema == 'linux':
        # Diferentes flags según la distro
        if distro in ['ubuntu', 'debian', 'mint']:
            flags.append('--break-system-packages')
        elif distro in ['fedora', 'centos', 'rhel']:
            flags.append('--user')
        elif distro in ['arch', 'manjaro']:
            flags.append('--break-system-packages')
        elif distro == 'opensuse':
            flags.append('--user')
        else:
            flags.append('--break-system-packages')
    
    elif sistema == 'darwin':  # Mac
        flags.append('--user')
    
    return flags

def print_banner():
    """Muestra el banner de XONIDIP"""
    sistema = get_system()
    distro = get_linux_distro()
    
    sistema_texto = {
        'windows': 'WINDOWS',
        'linux': f'LINUX ({distro.upper()})' if distro else 'LINUX',
        'darwin': 'MACOS'
    }.get(sistema, 'DESCONOCIDO')
    
    banner = f"""
{Colors.BLUE}{Colors.BOLD}╔══════════════════════════════════════════════════════════╗
║                     XONIDIP 2026 v4.2.0                     ║
║              Generador Profesional de Diplomas               ║
║                                                            ║
║               Sistema detectado: {sistema_texto}            ║
║                                                            ║
║               Desarrollado por: Darian Alberto               ║
║                      Camacho Salas                           ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
    """
    print(banner)

def check_python():
    """Verifica que Python está instalado"""
    try:
        cmd = get_python_command() + ['--version']
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except:
        return False

def check_dependencies():
    """Verifica qué dependencias necesita xonidip.py"""
    print(f"\n{Colors.BOLD}Verificando dependencias para XONIDIP...{Colors.END}")
    
    missing = []
    for req in REQUISITOS:
        package = req.split('==')[0]
        try:
            __import__(package.replace('-', '_'))
            print(f"{Colors.GREEN}  - {package} OK{Colors.END}")
        except ImportError:
            print(f"{Colors.YELLOW}  - {package} (faltante){Colors.END}")
            missing.append(req)
    
    return missing

def install_dependencies(missing):
    """Instala las dependencias faltantes según el sistema"""
    if not missing:
        print(f"\n{Colors.GREEN}Todas las dependencias estan instaladas{Colors.END}")
        return True
    
    print(f"\n{Colors.BOLD}Instalando dependencias faltantes...{Colors.END}")
    
    pip_cmd = get_pip_command()
    flags = get_install_flags()
    
    sistema = get_system()
    distro = get_linux_distro()
    
    print(f"{Colors.YELLOW}Sistema: {sistema}{Colors.END}")
    if distro:
        print(f"{Colors.YELLOW}Distribucion: {distro}{Colors.END}")
    if flags:
        print(f"{Colors.YELLOW}Flags: {' '.join(flags)}{Colors.END}")
    
    success = True
    for req in missing:
        print(f"  Instalando {req}...")
        try:
            cmd = pip_cmd + ['install', req] + flags
            subprocess.run(cmd, check=True)
            print(f"{Colors.GREEN}  - {req} instalado{Colors.END}")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}  Error instalando {req}{Colors.END}")
            print(f"     {e}")
            success = False
    
    if success:
        print(f"\n{Colors.GREEN}Todas las dependencias instaladas correctamente{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}Algunas dependencias no se instalaron{Colors.END}")
        print(f"   Puedes instalarlas manualmente con:")
        print(f"   {get_install_command()}")
    
    return success

def get_install_command():
    """Obtiene el comando de instalación según el sistema"""
    sistema = get_system()
    distro = get_linux_distro()
    
    if sistema == 'windows':
        return "pip install -r requisitos.txt"
    elif sistema == 'linux':
        if distro in ['ubuntu', 'debian', 'mint', 'arch', 'manjaro']:
            return "pip install -r requisitos.txt --break-system-packages"
        else:
            return "pip install --user -r requisitos.txt"
    elif sistema == 'darwin':
        return "pip3 install -r requisitos.txt --user"
    else:
        return "pip install -r requisitos.txt"

def open_browser():
    """Abre el navegador después de unos segundos"""
    time.sleep(3)
    url = 'http://localhost:5000'
    try:
        webbrowser.open(url)
        print(f"{Colors.GREEN}Navegador abierto en {url}{Colors.END}")
    except:
        print(f"{Colors.YELLOW}No se pudo abrir el navegador automaticamente{Colors.END}")
        print(f"   Abre manualmente: {url}")

def main():
    """Función principal - Ejecuta xonidip.py"""
    # Limpiar pantalla según sistema
    if get_system() == 'windows':
        os.system('cls')
    else:
        os.system('clear')
    
    # Mostrar banner
    print_banner()
    
    sistema = get_system()
    distro = get_linux_distro()
    
    print(f"{Colors.BOLD}Sistema operativo:{Colors.END} {sistema}")
    if distro:
        print(f"{Colors.BOLD}Distribucion:{Colors.END} {distro}")
    print(f"{Colors.BOLD}Python:{Colors.END} {sys.version.split()[0]}")
    print(f"{Colors.BOLD}Ruta:{Colors.END} {os.path.dirname(os.path.abspath(__file__))}")
    
    # Verificar que Python está instalado
    if not check_python():
        print(f"\n{Colors.RED}Error: Python no esta instalado o no esta en el PATH{Colors.END}")
        mostrar_instrucciones_python()
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")
        return
    
    # Verificar dependencias
    missing = check_dependencies()
    
    # Instalar dependencias si faltan
    if missing:
        print(f"\n{Colors.YELLOW}Faltan {len(missing)} dependencias{Colors.END}")
        respuesta = input(f"Instalar ahora? (s/n): ")
        if respuesta.lower() == 's':
            if not install_dependencies(missing):
                print(f"\n{Colors.YELLOW}Continuando a pesar de errores...{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}No se instalaran dependencias. Puede haber errores.{Colors.END}")
    
    # Verificar que existe xonidip.py (el programa principal)
    if not os.path.exists('xonidip.py'):
        print(f"\n{Colors.RED}Error: No se encuentra xonidip.py{Colors.END}")
        print(f"   Asegurate de que xonidip.py esta en la misma carpeta")
        print(f"   Archivos encontrados: {', '.join(os.listdir('.')[:5])}")
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}Iniciando XONIDIP (programa principal)...{Colors.END}")
    
    # Hilo para abrir el navegador
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Ejecutar xonidip.py (el programa principal de diplomas)
    try:
        python_cmd = get_python_command()
        print(f"{Colors.BOLD}Ejecutando:{Colors.END} {' '.join(python_cmd + ['xonidip.py'])}")
        print(f"{Colors.BOLD}Servidor:{Colors.END} http://localhost:5000")
        print(f"{Colors.BOLD}Para detener:{Colors.END} Ctrl+C")
        print("-" * 60)
        
        subprocess.run(python_cmd + ['xonidip.py'])
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Servidor detenido por el usuario{Colors.END}")
    except FileNotFoundError as e:
        print(f"\n{Colors.RED}Error: No se encuentra Python o xonidip.py{Colors.END}")
        print(f"   {e}")
    except Exception as e:
        print(f"\n{Colors.RED}Error ejecutando xonidip.py: {e}{Colors.END}")
    
    print(f"\n{Colors.BLUE}Gracias por usar XONIDIP 2026{Colors.END}")
    if sistema != 'windows':
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")

def mostrar_instrucciones_python():
    """Muestra instrucciones para instalar Python según el sistema"""
    sistema = get_system()
    distro = get_linux_distro()
    
    if sistema == 'windows':
        print(f"   Descarga Python desde: https://www.python.org/downloads/")
        print(f"   IMPORTANTE: Al instalar, marca 'Add Python to PATH'")
    elif sistema == 'linux':
        if distro in ['ubuntu', 'debian', 'mint']:
            print(f"   Instala con: sudo apt update")
            print(f"   sudo apt install python3 python3-pip python3-venv")
        elif distro in ['fedora', 'centos']:
            print(f"   Instala con: sudo dnf install python3 python3-pip")
        elif distro in ['arch', 'manjaro']:
            print(f"   Instala con: sudo pacman -S python python-pip")
        elif distro == 'opensuse':
            print(f"   Instala con: sudo zypper install python3 python3-pip")
        else:
            print(f"   Instala Python 3 desde: https://www.python.org/downloads/")
    elif sistema == 'darwin':
        print(f"   Instala con: brew install python3")
        print(f"   O descarga desde: https://www.python.org/downloads/")

def crear_accesos_directos():
    """Crea accesos directos según el sistema"""
    sistema = get_system()
    
    if sistema == 'windows':
        # Crear .bat para Windows
        with open('INICIAR_XONIDIP.bat', 'w') as f:
            f.write("""@echo off
title XONIDIP 2026
color 1F
echo ========================================
echo      XONIDIP 2026 - Generador de Diplomas
echo      Desarrollado por Darian Alberto
echo ========================================
echo.
python start.py
pause
""")
        print(f"{Colors.GREEN}Creado INICIAR_XONIDIP.bat - Haz doble clic para ejecutar{Colors.END}")
    
    elif sistema == 'linux':
        # Crear .sh para Linux
        with open('INICIAR_XONIDIP.sh', 'w') as f:
            f.write("""#!/bin/bash
echo "========================================"
echo "      XONIDIP 2026 - Generador de Diplomas"
echo "      Desarrollado por Darian Alberto"
echo "========================================"
echo ""
python3 start.py
read -p "Presiona Enter para salir"
""")
        os.chmod('INICIAR_XONIDIP.sh', 0o755)
        print(f"{Colors.GREEN}Creado INICIAR_XONIDIP.sh - Ejecuta con: ./INICIAR_XONIDIP.sh{Colors.END}")
    
    elif sistema == 'darwin':
        # Crear .command para Mac
        with open('INICIAR_XONIDIP.command', 'w') as f:
            f.write("""#!/bin/bash
cd "$(dirname "$0")"
echo "========================================"
echo "      XONIDIP 2026 - Generador de Diplomas"
echo "      Desarrollado por Darian Alberto"
echo "========================================"
echo ""
python3 start.py
""")
        os.chmod('INICIAR_XONIDIP.command', 0o755)
        print(f"{Colors.GREEN}Creado INICIAR_XONIDIP.command - Haz doble clic para ejecutar{Colors.END}")

if __name__ == '__main__':
    try:
        # Crear accesos directos
        crear_accesos_directos()
        
        # Ejecutar programa principal
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Saliendo...{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error inesperado: {e}{Colors.END}")
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")
