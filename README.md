# 🎓 XONIDIP 2026 - Generador de Diplomas v4.2.0

**Desarrollado por:** Darian Alberto Camacho Salas

## ⚠️ ADVERTENCIA
Este código tiene **únicamente fines educativos**. No debe utilizarse para crear documentos oficiales sin autorización.

## 📁 Estructura del Proyecto

```
xonidip/
├── start.py                 # Servidor principal
├── xonidip.py               # LANZADOR AUTOMÁTICO (¡USA ESTE!)
├── requisitos.txt           # Dependencias del proyecto
├── README.md                # Este archivo
├── manual_xoni_dip.pdf      # Manual de usuario
├── templates/               # Interfaz web
├── uploads/                 # Plantillas temporales
├── diplomas_generados/      # Aquí se guardan los diplomas
└── fonts/                   # Fuentes personalizadas
```

## 🚀 **NOVEDAD: XONIDIP.PY - LANZADOR AUTOMÁTICO**

Hemos creado un **lanzador automático** llamado `xonidip.py` que:

✅ **INSTALA** todas las dependencias por ti  
✅ **VERIFICA** que Python esté instalado  
✅ **EJECUTA** el servidor automáticamente  
✅ **ABRE** el navegador en la página correcta  
✅ **SOLO UN CLIC** y todo funciona  

## 🪟 **PARA WINDOWS - ASÍ DE FÁCIL**

### **OPCIÓN 1: LA MÁS FÁCIL (RECOMENDADA)**

```bash
# 1. Abre PowerShell o CMD en la carpeta del proyecto
# 2. Escribe esto y presiona ENTER:

python xonidip.py
```

### **OPCIÓN 2: DOBLE CLIC (MÁS FÁCIL AÚN)**

1. Abre la carpeta donde descargaste XONIDIP
2. Haz **doble clic** en el archivo `xonidip.py`
3. ¡Listo! Se abrirá automáticamente en tu navegador

### **OPCIÓN 3: INSTALACIÓN MANUAL (SI PREFIERES)**

```bash
# Paso 1: Instalar dependencias
pip install -r requisitos.txt

# Paso 2: Ejecutar el servidor
python start.py

# Paso 3: Abrir navegador
# Ve a: http://localhost:5000
```

## 🐧 **PARA LINUX - ASÍ DE FÁCIL**

```bash
# Paso 1: Entrar a la carpeta
cd xonidip

# Paso 2: Dar permisos al lanzador (solo primera vez)
chmod +x xonidip.py

# Paso 3: Ejecutar el lanzador (con --break-system-packages)
python3 xonidip.py --break-system-packages

# O si prefieres instalar manualmente:
pip install -r requisitos.txt --break-system-packages
python3 start.py
```

## 🍎 **PARA macOS - ASÍ DE FÁCIL**

```bash
# Paso 1: Entrar a la carpeta
cd xonidip

# Paso 2: Ejecutar el lanzador
python3 xonidip.py

# O manualmente:
pip3 install -r requisitos.txt
python3 start.py
```

## 📱 **CÓMO USARLO (EN 4 PASOS)**

| Paso | Qué hacer | Descripción |
|------|-----------|-------------|
| 1️⃣ | **Subir plantilla** | Elige tu diploma (JPG o PNG) |
| 2️⃣ | **Ajustar posición** | Pon el texto donde quieras |
| 3️⃣ | **Ingresar nombres** | Escribe un nombre por línea |
| 4️⃣ | **Generar** | ¡Crea todos y descarga ZIP! |

## 📂 **¿DÓNDE ESTÁN MIS DIPLOMAS?**
Dentro de la carpeta:
```
/diplomas_generados/
```
(Puedes copiarlos, enviarlos por email, imprimirlos...)

## 🔧 **PROBLEMAS COMUNES (Y SOLUCIONES)**

### ❌ "No module named 'Flask'"
```bash
# SOLUCIÓN: Instala las dependencias
pip install -r requisitos.txt

# En Linux (si da error):
pip install -r requisitos.txt --break-system-packages
```

### ❌ "Error de permisos"
```bash
# SOLUCIÓN LINUX:
pip install -r requisitos.txt --break-system-packages

# SOLUCIÓN MAC:
pip install --user -r requisitos.txt
```

### ❌ "Puerto 5000 en uso"
```bash
# SOLUCIÓN: Abre start.py y cambia el puerto (línea final):
app.run(port=5001)

# Luego ve a: http://localhost:5001
```

### ❌ "No se ven las tildes"
**SOLUCIÓN:** Guarda tu archivo de nombres en UTF-8 (el bloc de notas ya lo hace por defecto)

## 📞 ¿NECITAS AYUDA?

- 📸 **Instagram:** @xonidu
- 📧 **Email:** xonidu@gmail.com
- 💻 **GitHub:** XONIDU/xonidip

## ✅ COSAS QUE PUEDES HACER

| Sí | No |
|----|----|
| ✅ Generar diplomas para tu curso | ❌ Crear documentos falsos |
| ✅ Aprender a automatizar | ❌ Usarlo sin permiso |
| ✅ Probar con nombres inventados | ❌ Vender los diplomas |
| ✅ Compartir el código | ❌ Quitar los créditos |

## 🎉 ¡Y LISTO!

```
╔════════════════════════════════════╗
║   XONIDIP 2026 - Hecho con ❤️      ║
║   por Darian Alberto Camacho Salas ║
╚════════════════════════════════════╝
```

---

