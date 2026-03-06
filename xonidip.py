#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
XONIDIP 2026 - Lanzador para WINDOWS
Un solo clic para instalar dependencias y ejecutar el sistema
Desarrollado por: Darian Alberto Camacho Salas
"""

import subprocess
import sys
import os
import webbrowser
import time
import threading

# Colores para terminal (Windows compatible)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

# Dependencias necesarias
REQUISITOS = [
    'flask==2.3.3',
    'pillow==10.0.1',
    'pandas==2.0.3',
    'qrcode==7.4.2',
    'openpyxl==3.1.2'
]

def print_banner():
    """Muestra el banner de XONIDIP"""
    banner = f"""
{Colors.BLUE}{Colors.BOLD}╔══════════════════════════════════════════════════════════╗
║                     XONIDIP 2026 v4.2.0                     ║
║              Generador Profesional de Diplomas               ║
║                      para WINDOWS                            ║
║                                                              ║
║               Desarrollado por: Darian Alberto               ║
║                      Camacho Salas                           ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
    """
    print(banner)

def check_python():
    """Verifica que Python está instalado"""
    try:
        subprocess.run(['python', '--version'], capture_output=True, check=True)
        return True
    except:
        return False

def install_dependencies():
    """Instala las dependencias necesarias en Windows"""
    print(f"\n{Colors.BOLD}📦 Verificando dependencias...{Colors.END}")
    
    # Verificar qué dependencias faltan
    missing = []
    for req in REQUISITOS:
        package = req.split('==')[0]
        try:
            __import__(package.replace('-', '_'))
            print(f"{Colors.GREEN}  ✅ {package}{Colors.END}")
        except ImportError:
            print(f"{Colors.YELLOW}  ⚠️  {package} (faltante){Colors.END}")
            missing.append(req)
    
    if not missing:
        print(f"\n{Colors.GREEN}✅ Todas las dependencias están instaladas{Colors.END}")
        return True
    
    print(f"\n{Colors.BOLD}📥 Instalando dependencias faltantes...{Colors.END}")
    
    # Instalar cada dependencia
    success = True
    for req in missing:
        print(f"  Instalando {req}...")
        try:
            # En Windows usamos pip directamente
            subprocess.run([sys.executable, '-m', 'pip', 'install', req], check=True)
            print(f"{Colors.GREEN}  ✅ {req} instalado{Colors.END}")
        except subprocess.CalledProcessError:
            print(f"{Colors.RED}  ❌ Error instalando {req}{Colors.END}")
            success = False
    
    if success:
        print(f"\n{Colors.GREEN}✅ Todas las dependencias instaladas correctamente{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Algunas dependencias no se instalaron{Colors.END}")
        print(f"   Puedes instalarlas manualmente con:")
        print(f"   pip install -r requisitos.txt")
    
    return success

def open_browser():
    """Abre el navegador después de unos segundos"""
    time.sleep(3)
    webbrowser.open('http://localhost:5000')
    print(f"{Colors.GREEN}✅ Navegador abierto en http://localhost:5000{Colors.END}")

def main():
    """Función principal"""
    # Limpiar pantalla
    os.system('cls')
    
    # Mostrar banner
    print_banner()
    
    print(f"{Colors.BOLD}Sistema detectado:{Colors.END} Windows")
    print(f"{Colors.BOLD}Python:{Colors.END} {sys.version.split()[0]}")
    
    # Verificar que Python está instalado
    if not check_python():
        print(f"\n{Colors.RED}❌ Error: Python no está instalado o no está en el PATH{Colors.END}")
        print(f"   Descarga Python desde: https://www.python.org/downloads/")
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")
        return
    
    # Instalar dependencias
    install_dependencies()
    
    # Verificar que existe start.py
    if not os.path.exists('start.py'):
        print(f"\n{Colors.RED}❌ Error: No se encuentra start.py{Colors.END}")
        print(f"   Asegúrate de ejecutar este script en la misma carpeta que contiene:")
        print(f"   - start.py")
        print(f"   - templates/")
        print(f"   - fonts/")
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}🚀 Iniciando XONIDIP...{Colors.END}")
    print(f"{Colors.YELLOW}   El servidor se iniciará en: http://localhost:5000{Colors.END}")
    print(f"{Colors.YELLOW}   Presiona Ctrl+C para detener el servidor{Colors.END}\n")
    
    # Hilo para abrir el navegador
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Ejecutar start.py
    try:
        # En Windows usamos python
        subprocess.run(['python', 'start.py'])
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Servidor detenido por el usuario{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error ejecutando start.py: {e}{Colors.END}")
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")

def create_windows_batch():
    """Crea un archivo .bat para ejecutar con doble clic"""
    batch_content = """@echo off
title XONIDIP 2026
echo ========================================
echo      XONIDIP 2026 - Generador de Diplomas
echo      Desarrollado por Darian Alberto
echo ========================================
echo.
python xonidip.py
pause
"""
    
    if not os.path.exists('ejecutar.bat'):
        with open('ejecutar.bat', 'w') as f:
            f.write(batch_content)
        print(f"{Colors.GREEN}✅ Archivo 'ejecutar.bat' creado para doble clic{Colors.END}")

if __name__ == '__main__':
    try:
        # Crear archivo .bat para facilitar ejecución
        create_windows_batch()
        
        # Ejecutar programa principal
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Saliendo...{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error inesperado: {e}{Colors.END}")
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")
