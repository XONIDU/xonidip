# 🎓 XONIDIP 2026 - Generador de Diplomas v4.2.0

**Desarrollado por:** Darian Alberto Camacho Salas

## ⚠️ ADVERTENCIA
Este código tiene **únicamente fines educativos**. No debe utilizarse para crear documentos oficiales sin autorización.

## 📁 Estructura del Proyecto

```
xonidip/
├── start.py                 # 🟢 LANZADOR UNIVERSAL (¡EJECUTA ESTE!)
├── xonidip.py               # 🔵 PROGRAMA PRINCIPAL (servidor Flask)
├── requisitos.txt           # Dependencias del proyecto
├── README.md                # Este archivo
├── manual_xoni_dip.pdf      # Manual de usuario
├── templates/               # Interfaz web
├── uploads/                 # Plantillas temporales
├── diplomas_generados/      # Aquí se guardan los diplomas
└── fonts/                   # Fuentes personalizadas
```

## 🚀 **ASÍ DE FÁCIL: SOLO EJECUTA start.py**

**¡Ya no necesitas hacer nada más!** El archivo `start.py` hace TODO por ti:

✅ Detecta automáticamente tu sistema operativo  
✅ Verifica qué dependencias faltan  
✅ Las instala con los comandos correctos  
✅ Ejecuta el programa principal  
✅ Abre el navegador automáticamente  

## 🪟 **PARA WINDOWS**

```bash
# Abre CMD o PowerShell y escribe:
python start.py
```

Si tienes problemas de permisos, el script crea automáticamente:
- `XONIDIP.bat` - Ejecución normal
- `XONIDIP_ADMIN.bat` - Ejecución como administrador

## 🐧 **PARA LINUX**

```bash
# Abre terminal y escribe:
python3 start.py
```

## 🍎 **PARA macOS**

```bash
# Abre terminal y escribe:
python3 start.py
```

## 📦 **¿QUÉ HACE start.py POR DENTRO?**

Cuando ejecutas `start.py`, automáticamente:

1. 🔍 **Detecta** si estás en Windows, Linux o Mac
2. 📋 **Verifica** qué dependencias de `requisitos.txt` faltan
3. 📥 **Instala** las que faltan:
   - En Linux: `pip install --break-system-packages`
   - En Mac: `pip install --user`
   - En Windows: `pip install` normal (con verificación de pip)
4. 🚀 **Ejecuta** `xonidip.py` (el programa principal)
5. 🌐 **Abre** el navegador automáticamente en http://localhost:5000

## 📱 **CÓMO USAR XONIDIP (EN 4 PASOS)**

| Paso | Qué hacer | Descripción |
|------|-----------|-------------|
| 1️⃣ | **Subir plantilla** | Elige tu diploma (JPG o PNG) |
| 2️⃣ | **Ajustar posición** | Pon el texto donde quieras |
| 3️⃣ | **Ingresar nombres** | Escribe un nombre por línea |
| 4️⃣ | **Generar** | ¡Crea todos y descarga ZIP! |

## 📂 **¿DÓNDE ESTÁN MIS DIPLOMAS?**

Todos los diplomas generados se guardan automáticamente en la carpeta:
```
/diplomas_generados/
```

También puedes descargarlos como ZIP desde la interfaz web.

## 🔧 **PROBLEMAS COMUNES (Y SOLUCIONES)**

### ❌ **"Python no está instalado"**
```bash
# Descarga Python desde:
https://www.python.org/downloads/

# IMPORTANTE: En Windows, marca "Add Python to PATH" durante la instalación
```

### ❌ **"No module named 'Flask'"**
```bash
# Solo ejecuta start.py de nuevo (instala lo que falta):
python start.py
```

### ❌ **"Error de permisos en Linux"**
```bash
# start.py ya usa --break-system-packages automáticamente
python3 start.py
```

### ❌ **"Error de permisos en Windows"**
```bash
# Usa el archivo creado automáticamente:
XONIDIP_ADMIN.bat   # Ejecutar como administrador
```

### ❌ **"Puerto 5000 en uso"**
```bash
# Abre xonidip.py y cambia el puerto (línea final):
app.run(port=5001)

# Luego ve a: http://localhost:5001
```

### ❌ **"No se ven las tildes"**
**SOLUCIÓN:** Guarda tu archivo de nombres en UTF-8 (el bloc de notas ya lo hace por defecto)

## 📞 **¿NECESITAS AYUDA?**

- 📸 **Instagram:** [@xonidu](https://instagram.com/xonidu)
- 📧 **Email:** xonidu@gmail.com
- 💻 **GitHub:** [XONIDU/xonidip](https://github.com/XONIDU/xonidip)

## ✅ **LO QUE PUEDES HACER (Y LO QUE NO)**

| ✅ SÍ | ❌ NO |
|-------|-------|
| Generar diplomas para tu curso | Crear documentos falsos |
| Aprender a automatizar | Usarlo sin permiso |
| Probar con nombres inventados | Vender los diplomas |
| Compartir el código | Quitar los créditos |
| Modificar para prácticas educativas | Usar para documentos oficiales |

## 📋 **NOTAS IMPORTANTES**

- ✅ Funciona en **Windows, Linux y Mac** con Python 3.8+
- ✅ Soporta **tildes y caracteres especiales** (á, é, í, ó, ú, ñ)
- ✅ Puedes usar **Excel, CSV o TXT** para los nombres
- ✅ Los diplomas se generan en **PNG, PDF o JPG**
- ✅ Cada archivo incluye el **nombre del participante**
- ✅ El navegador se **abre automáticamente** al iniciar
- ✅ En Windows, se crean archivos `.bat` para fácil ejecución

## 🎉 **¡LISTO!**

```
╔════════════════════════════════════╗
║   XONIDIP 2026 - Hecho con ❤️      ║
║   por Darian Alberto Camacho Salas ║
╚════════════════════════════════════╝
```

---

⭐ **¿Te sirvió?** Dale estrella en GitHub  
🐛 **¿Encontraste un error?** Abre un "Issue"  
📢 **¿Sugerencias?** Escríbeme por Instagram

---

**XONIDU** - Enseñando automatización, construyendo conocimiento
