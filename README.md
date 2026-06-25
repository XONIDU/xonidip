# XONIDIP 2026 - Generador de Diplomas v4.3.0

**Desarrollado por:** Darian Alberto Camacho Salas  
**Organización:** XONIDU

## ADVERTENCIA
Este código tiene **únicamente fines educativos**. No debe utilizarse para crear documentos oficiales sin autorización.

## Estructura del Proyecto

```
xonidip/
├── start.py                 # LANZADOR UNIVERSAL (ejecuta este)
├── xonidip.py               # PROGRAMA PRINCIPAL (servidor Flask)
├── requisitos.txt           # Dependencias del proyecto
├── README.md                # Este archivo
├── manual_xoni_dip.pdf      # Manual de usuario
├── templates/               # Interfaz web
├── uploads/                 # Plantillas temporales
├── diplomas_generados/      # Aquí se guardan los diplomas
└── fonts/                   # Fuentes personalizadas
```

## Asi de facil: solo ejecuta start.py

El archivo `start.py` hace todo por ti:

- Detecta automaticamente tu sistema operativo y distribucion de Linux
- Verifica que Python esta instalado
- Instala pip si no existe (en cualquier sistema)
- Verifica que dependencias faltan
- Las instala con **multiples estrategias** (hasta 7 metodos diferentes)
- Ejecuta el programa principal
- Abre el navegador automaticamente
- (En Windows) crea los archivos .bat para ejecucion normal y como administrador

## Instalacion de pip automatica

Si pip no esta instalado en tu sistema, `start.py` lo instalara automaticamente usando:

| Sistema | Metodos de instalacion |
|---------|----------------------|
| Windows | ensurepip → get-pip.py |
| Linux (Debian/Ubuntu) | apt → ensurepip → get-pip.py |
| Linux (Arch/Manjaro) | pacman → ensurepip → get-pip.py |
| Linux (Fedora) | dnf → ensurepip → get-pip.py |
| Linux (CentOS) | yum → ensurepip → get-pip.py |
| Linux (openSUSE) | zypper → ensurepip → get-pip.py |
| macOS | brew → ensurepip → get-pip.py |

## Multiples estrategias de instalacion de dependencias

Si una instalacion falla, `start.py` intenta con hasta 7 estrategias diferentes:

1. Flags especificos del sistema (`--break-system-packages` en Arch/Fedora, `--user` en Debian/Mac)
2. Sin flags (pip install normal)
3. Solo `--break-system-packages`
4. Solo `--user`
5. `--force-reinstall --break-system-packages`
6. En Arch Linux: `pacman -S python-xyz`
7. En Debian/Ubuntu: `apt install python3-xyz`

## Instrucciones por sistema

### Windows

```bash
# Abre CMD o PowerShell y escribe:
python start.py
```

Si tienes problemas de permisos:

```bash
# Ejecutar como administrador manualmente
XONIDIP_ADMIN.bat
```

### Linux

```bash
# Abre terminal y escribe:
python3 start.py
```

**Distribuciones soportadas:**
- Debian/Ubuntu/Mint (debian-based)
- Arch/Manjaro (arch-based)
- Fedora
- CentOS/RHEL
- openSUSE
- Otras (linux-generico)

#### Opcion 2 – Comando xoninstall (recomendado para futuras herramientas XONI)

Agrega la siguiente funcion a tu `~/.bashrc`:

```bash
echo 'xoninstall() { if [ -z "$1" ]; then echo "Uso: xoninstall <repo>"; echo "Ej: xoninstall xoniran"; else git clone "https://github.com/XONIDU/$1.git"; cd "$1"; fi }' >> ~/.bashrc
source ~/.bashrc
```

Luego simplemente escribe:

```bash
xoninstall xonidip
cd xonidip
python3 start.py
```

**Nota:** Esta funcion te servira para instalar cualquier otra herramienta futura de XONIDU (ej: `xoninstall xoniran`).

### macOS

```bash
# Abre terminal y escribe:
python3 start.py
```

## Que hace start.py por dentro

Cuando ejecutas `start.py`, automaticamente:

1. Detecta si estas en Windows, Linux o Mac (y la distribucion de Linux)
2. Verifica que Python esta instalado
3. Instala pip si no existe (usando el metodo adecuado para tu sistema)
4. Verifica que dependencias de `requisitos.txt` faltan
5. Las instala con multiples estrategias:
   - En Arch/Fedora: `pip install --break-system-packages`
   - En Debian/Ubuntu: `pip install --user`
   - En Mac: `pip install --user`
   - En Windows: `pip install` normal
   - Si falla, intenta con pacman/apt segun la distro
6. Ejecuta `xonidip.py` (el programa principal)
7. Abre el navegador automaticamente en `http://localhost:5000`
8. En Windows, ademas genera los archivos `.bat` para futuras ejecuciones

## Como usar XONIDIP (en 4 pasos)

| Paso | Que hacer | Descripcion |
|------|-----------|-------------|
| 1 | Subir plantilla | Elige tu diploma (JPG o PNG) |
| 2 | Ajustar posicion | Pon el texto donde quieras |
| 3 | Ingresar nombres | Escribe un nombre por linea |
| 4 | Generar | Crea todos y descarga ZIP |

## Donde estan mis diplomas

Todos los diplomas generados se guardan automaticamente en la carpeta:

```
/diplomas_generados/
```

Tambien puedes descargarlos como ZIP desde la interfaz web.

## Problemas comunes (y soluciones)

### "Python no esta instalado"

```bash
# Descarga Python desde:
https://www.python.org/downloads/

# IMPORTANTE: En Windows, marca "Add Python to PATH" durante la instalacion
```

### "No module named 'Flask'"

```bash
# Solo ejecuta start.py de nuevo (instala lo que falta):
python start.py

# O manualmente:
pip install flask --break-system-packages  # En Arch/Fedora
pip install flask --user                   # En Debian/Ubuntu/Mac
```

### "Error de permisos en Linux"

```bash
# start.py ya usa --break-system-packages automaticamente segun tu distro
python3 start.py

# O manualmente:
pip install -r requisitos.txt --break-system-packages  # Arch/Fedora
pip install -r requisitos.txt --user                   # Debian/Ubuntu
```

### "Error de permisos en Windows"

```bash
# Usa el archivo creado automaticamente:
XONIDIP_ADMIN.bat   # Ejecutar como administrador
```

### "Puerto 5000 en uso"

```bash
# Abre xonidip.py y cambia el puerto (linea final):
app.run(port=5001)

# Luego ve a: http://localhost:5001
```

### "No se ven las tildes"

**Solucion:** Guarda tu archivo de nombres en UTF-8 (el bloc de notas ya lo hace por defecto)

## Contacto y soporte

- Instagram: [@xonidu](https://instagram.com/xonidu)
- Email: xonidu@gmail.com
- GitHub: [XONIDU/xonidip](https://github.com/XONIDU/xonidip)

## Lo que puedes hacer (y lo que no)

| Si | No |
|----|----|
| Generar diplomas para tu curso | Crear documentos falsos |
| Aprender a automatizar | Usarlo sin permiso |
| Probar con nombres inventados | Vender los diplomas |
| Compartir el codigo | Quitar los creditos |
| Modificar para practicas educativas | Usar para documentos oficiales |

## Notas importantes

- Funciona en Windows, Linux y Mac con Python 3.8+
- Soporta tildes y caracteres especiales (a, e, i, o, u, n)
- Puedes usar Excel, CSV o TXT para los nombres
- Los diplomas se generan en PNG, PDF o JPG
- Cada archivo incluye el nombre del participante
- El navegador se abre automaticamente al iniciar
- En Windows, se crean archivos .bat para facil ejecucion (normal y con admin)
- Instalacion automatica de pip en cualquier sistema
- Multiples estrategias de instalacion (hasta 7 metodos diferentes)

## Listo

```
╔════════════════════════════════════╗
║   XONIDIP 2026 - Hecho con amor    ║
║   por Darian Alberto Camacho Salas ║
╚════════════════════════════════════╝
```

---

Si te sirvio, dale estrella en GitHub.  
Si encontraste un error, abre un Issue.  
Si tienes sugerencias, escribeme por Instagram.

**XONIDU** 
