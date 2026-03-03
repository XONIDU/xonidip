## 📁 **README.md (VERSIÓN SIMPLIFICADA)**

```markdown
# 🎓 XONIDIP 2026 - Generador de Diplomas

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
pip install -r requisitos.txt
# Si da error de permisos:
pip install -r requisitos.txt --break-system-packages
```
</details>

<details>
<summary><b>🍎 macOS</b></summary>

```bash
pip3 install -r requisitos.txt
# O usando --user:
pip install --user -r requisitos.txt
```
</details>

<details>
<summary><b>🪟 WINDOWS</b></summary>

```bash
pip install -r requisitos.txt
# Si tienes varias versiones:
py -m pip install -r requisitos.txt
```
</details>

### 3. Ejecutar
```bash
python start.py
# o
python3 start.py
```

### 4. Abrir navegador
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

| Paso | Acción |
|------|--------|
| 1️⃣ | Sube tu plantilla (JPG/PNG) |
| 2️⃣ | Ajusta posición del texto |
| 3️⃣ | Ingresa los nombres |
| 4️⃣ | Genera y descarga ZIP |

## 📂 ¿Dónde se guardan los diplomas?
Todos los diplomas generados se guardan en la carpeta:
```
/diplomas_generados/
```

## 🔧 Solución de problemas comunes

**Error: "No module named 'PIL'"**
```bash
pip install Pillow
```

**Error: Puerto 5000 en uso**
- Edita `start.py` y cambia el puerto:
```python
app.run(port=5001)
```

**Fuentes no visibles**
- Copia archivos `.ttf` a la carpeta `fonts/`

## 📞 Contacto

- 📸 **Instagram:** @xonidu
- 📘 **Facebook:** xonidu  
- 📧 **Email:** xonidu@gmail.com

---

**XONIDIP 2026** - Herramienta educativa de automatización
```

## 📝 **Cambios realizados:**

1. **Estructura simplificada** - Solo lo esencial
2. **Instalación por sistema** - Linux, macOS, Windows con comandos claros
3. **Carpeta `diplomas_generados`** - Destacada como lugar de salida
4. **Archivo `start.py`** - Mencionado como archivo principal
5. **Comandos cortos** - Fáciles de copiar/pegar
6. **Sin secciones extensas** - Directo al punto

¿Quieres que ajuste algo más?
