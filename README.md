# 🎓 XONIDIP 2026 - Generador de Diplomas v4.2.0

**Desarrollado por:** Darian Alberto Camacho Salas

## ⚠️ ADVERTENCIA
Este código tiene **únicamente fines educativos**. No debe utilizarse para crear documentos oficiales sin autorización.

## 📁 Estructura del Proyecto

```
xonidip/
├── start.py                 # Servidor principal (ejecutar este)
├── requisitos.txt           # Dependencias del proyecto
├── README.md                # Este archivo
├── manual_xoni_dip.pdf      # Manual de usuario
├── templates/               # Interfaz web
├── uploads/                 # Plantillas temporales
├── diplomas_generados/      # Aquí se guardan los diplomas
└── fonts/                   # Fuentes personalizadas
```

## 🚀 Instalación Rápida

### 1. Clonar o descargar
```bash
git clone https://github.com/XONIDU/xonidip.git
cd xonidip
```

### 2. Instalar dependencias

<details>
<summary><b>🐧 LINUX</b></summary>

```bash
# Instalación normal
pip install -r requisitos.txt

# Si da error de permisos del sistema (recomendado para Linux)
pip install -r requisitos.txt --break-system-packages

# O usando pipx (alternativa)
pipx install flask pillow pandas qrcode openpyxl
```
</details>

<details>
<summary><b>🍎 macOS</b></summary>

```bash
# Instalación normal
pip3 install -r requisitos.txt

# Si usas Python 3 por defecto
pip install -r requisitos.txt

# Para evitar problemas de permisos
pip install --user -r requisitos.txt
```
</details>

<details>
<summary><b>🪟 WINDOWS</b></summary>

```bash
# Instalación normal
pip install -r requisitos.txt

# Si tienes varias versiones de Python
py -m pip install -r requisitos.txt

# En PowerShell
python -m pip install -r requisitos.txt
```
</details>

### 3. Verificar instalación
```bash
# Listar paquetes instalados
pip list

# Deberías ver: Flask, Pillow, pandas, qrcode, openpyxl
```

### 4. Ejecutar
```bash
python start.py
# o
python3 start.py
```

### 5. Abrir navegador
```
http://localhost:5000
```

## 📦 requisitos.txt (dependencias)
```
Flask==2.3.3
Pillow==10.0.1
pandas==2.0.3
qrcode==7.4.2
openpyxl==3.1.2
```

## 📱 Uso Básico

| Paso | Acción | Descripción |
|------|--------|-------------|
| 1️⃣ | **Subir plantilla** | Selecciona tu diploma base (JPG/PNG) |
| 2️⃣ | **Ajustar posición** | Coloca el texto donde quieras |
| 3️⃣ | **Ingresar nombres** | Escribe un nombre por línea |
| 4️⃣ | **Generar** | Crea todos los diplomas y descarga ZIP |

## 📂 ¿Dónde se guardan los diplomas?

Todos los diplomas generados se guardan automáticamente en la carpeta:
```
/diplomas_generados/
```

También puedes descargarlos como archivo ZIP desde la interfaz web.

## 🔧 Solución de problemas comunes

| Problema | Solución |
|----------|----------|
| **No module named 'Flask'** | Ejecuta: `pip install -r requisitos.txt` |
| **Error de permisos** | Usa: `pip install --user -r requisitos.txt` |
| **Puerto 5000 en uso** | Edita `start.py` y cambia a `port=5001` |
| **Fuentes no visibles** | Copia archivos `.ttf` a la carpeta `fonts/` |
| **No se ven las tildes** | Asegúrate que el archivo de nombres esté en UTF-8 |

## 📞 Contacto y Soporte

¿Dudas sobre instalación o uso?

- 📸 **Instagram:** [@xonidu](https://instagram.com/xonidu)
- 📧 **Email:** xonidu@gmail.com
- 💻 **GitHub:** [XONIDU/xonidip](https://github.com/XONIDU/xonidip)

## 📋 Notas adicionales

- ✅ Funciona en cualquier sistema operativo con Python 3.8+
- ✅ Soporta tildes y caracteres especiales (á, é, í, ó, ú, ñ)
- ✅ Puedes usar Excel, CSV o TXT para los nombres
- ✅ Los diplomas se generan en PNG, PDF o JPG
- ✅ Cada archivo incluye el nombre del participante

---

## SOMOS XONIDU
