import os
import io
import zipfile
import socket
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory, url_for
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import json
from werkzeug.utils import secure_filename
import tempfile
import shutil
from datetime import datetime
import base64
import time
import unicodedata
import qrcode

app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = 'xonidu-Darian-Alberto-Camacho-Salas'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'diplomas_generados'
app.config['FONTS_FOLDER'] = 'fonts'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'txt', 'csv', 'xlsx', 'xls'}

# Crear carpetas si no existen
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['FONTS_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# ===== FUNCIÓN PARA OBTENER IP =====
def get_server_url():
    """Obtiene la URL del servidor con IP y puerto"""
    try:
        # Obtener IP local
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return f"http://{local_ip}:5000"
    except:
        return "http://localhost:5000"

# ===== FUNCIÓN PARA GENERAR QR =====
def generate_qr_base64(url):
    """Genera un código QR en base64 para mostrar en HTML"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str
    except Exception as e:
        print(f"Error generando QR: {e}")
        return None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_names_from_file(file):
    """Extrae nombres de diferentes tipos de archivos"""
    names = []
    filename = file.filename.lower()
    
    try:
        if filename.endswith('.txt'):
            content = file.read().decode('utf-8', errors='ignore')
            file.seek(0)
            lines = content.strip().split('\n')
            names = [line.strip() for line in lines if line.strip()]
        
        elif filename.endswith('.csv'):
            content = file.read().decode('utf-8', errors='ignore')
            file.seek(0)
            lines = content.strip().split('\n')
            for i, line in enumerate(lines):
                if i == 0 and 'nombre' in line.lower():  # Skip header
                    continue
                parts = line.strip().split(',')
                if parts and parts[0].strip():
                    names.append(parts[0].strip())
        
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
            file.seek(0)
            # Buscar columna que contenga nombres
            for col in df.columns:
                if any(keyword in str(col).lower() for keyword in ['nombre', 'name', 'participante', 'alumno']):
                    names = [str(name).strip() for name in df[col].dropna().tolist() if str(name).strip()]
                    break
            if not names and len(df.columns) > 0:
                # Tomar primera columna
                names = [str(name).strip() for name in df[df.columns[0]].dropna().tolist() if str(name).strip()]
    
    except Exception as e:
        print(f"Error procesando archivo: {e}")
        return []
    
    return names

def normalize_text(text):
    """Normaliza texto para mantener tildes y caracteres especiales"""
    return text

def get_text_dimensions(text, font, draw):
    """Obtiene dimensiones del texto para centrado preciso"""
    try:
        # Método moderno (PIL 8.0.0+)
        if hasattr(draw, 'textbbox'):
            bbox = draw.textbbox((0, 0), text, font=font)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        else:
            # Método antiguo
            return font.getsize(text)
    except:
        # Estimación aproximada
        return len(text) * font.size // 2, font.size

def get_font_path(font_name, style='normal'):
    """Obtiene la ruta completa de una fuente con estilo"""
    # Mapeo de nombres de fuentes a archivos reales
    font_mappings = {
        'arial.ttf': {
            'normal': ['arial.ttf', 'arial.ttf', 'Arial.ttf', 'arial.ttf'],
            'bold': ['arialbd.ttf', 'arialb.ttf', 'Arial-Bold.ttf', 'arialbd.ttf'],
            'italic': ['ariali.ttf', 'ariali.ttf', 'Arial-Italic.ttf', 'ariali.ttf']
        },
        'times.ttf': {
            'normal': ['times.ttf', 'times.ttf', 'TimesNewRoman.ttf', 'times.ttf'],
            'bold': ['timesbd.ttf', 'timesb.ttf', 'TimesNewRomanBold.ttf', 'timesbd.ttf']
        },
        'cour.ttf': {
            'normal': ['cour.ttf', 'cour.ttf', 'CourierNew.ttf', 'cour.ttf'],
            'bold': ['courbd.ttf', 'courb.ttf', 'CourierNewBold.ttf', 'courbd.ttf']
        },
        'verdana.ttf': {
            'normal': ['verdana.ttf', 'verdana.ttf', 'Verdana.ttf', 'verdana.ttf']
        },
        'georgia.ttf': {
            'normal': ['georgia.ttf', 'georgia.ttf', 'Georgia.ttf', 'georgia.ttf']
        }
    }
    
    # Rutas donde buscar fuentes (en orden de prioridad)
    font_paths = [
        app.config['FONTS_FOLDER'],  # Carpeta local fonts/
        os.path.join(os.path.dirname(__file__), 'fonts'),  # Ruta absoluta
        "fonts/",
        "/usr/share/fonts/",
        "/usr/local/share/fonts/",
        "/System/Library/Fonts/",
        "/Library/Fonts/",
        "C:\\Windows\\Fonts\\",
        "C:/Windows/Fonts/"
    ]
    
    # Verificar si es una fuente conocida
    base_name = font_name.lower()
    if base_name in font_mappings and style in font_mappings[base_name]:
        font_variants = font_mappings[base_name][style]
    else:
        # Si no es una fuente conocida, usar el nombre directamente
        font_variants = [font_name]
    
    # Buscar en todas las rutas
    for path in font_paths:
        if not os.path.exists(path):
            continue
            
        for variant in font_variants:
            font_path = os.path.join(path, variant)
            if os.path.exists(font_path):
                print(f"✓ Encontrada fuente: {font_path}")
                return font_path
    
    # Si no se encuentra, usar fuente por defecto del sistema
    return None

def create_fallback_font(font_size):
    """Crea una fuente por defecto si no hay fuentes disponibles"""
    try:
        # Intentar cargar cualquier fuente disponible
        for path in ['/System/Library/Fonts/Helvetica.ttc', 
                    '/System/Library/Fonts/Helvetica.dfont',
                    'C:\\Windows\\Fonts\\arial.ttf']:
            if os.path.exists(path):
                return ImageFont.truetype(path, font_size)
    except:
        pass
    
    # Si no hay fuentes, usar la por defecto de PIL
    try:
        return ImageFont.load_default().font_variant(size=font_size)
    except:
        # Último recurso: crear una fuente simple
        return ImageFont.load_default()

def load_font(font_name, font_size, font_style='normal'):
    """Carga una fuente con estilo con manejo de errores mejorado"""
    try:
        # Primero intentar cargar con estilo específico
        font_path = get_font_path(font_name, font_style)
        
        if font_path and os.path.exists(font_path):
            return ImageFont.truetype(font_path, font_size)
        
        # Si no se encuentra con estilo, buscar la fuente base
        font_path = get_font_path(font_name, 'normal')
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
            
            # Simular estilos si es necesario
            if font_style == 'bold':
                # Para simular negrita, aumentamos ligeramente el tamaño
                return ImageFont.truetype(font_path, int(font_size * 1.1))
            elif font_style == 'italic':
                # Para cursiva no podemos hacer mucho sin la fuente real
                return font
            
            return font
        
        # Si no se encuentra ninguna fuente, usar fallback
        print(f"⚠ No se encontró la fuente {font_name}. Usando fuente por defecto.")
        return create_fallback_font(font_size)
        
    except Exception as e:
        print(f"⚠ Error cargando fuente {font_name}: {e}")
        return create_fallback_font(font_size)

@app.route('/')
def index():
    # Obtener URL y generar QR
    server_url = get_server_url()
    qr_base64 = generate_qr_base64(server_url)
    
    return render_template('index.html', 
                         qr_code=qr_base64, 
                         server_url=server_url)

@app.route('/qr_code')
def qr_code():
    """Endpoint para obtener el código QR como JSON"""
    server_url = get_server_url()
    qr_base64 = generate_qr_base64(server_url)
    
    if qr_base64:
        return jsonify({
            "qr_base64": qr_base64,
            "url": server_url
        })
    else:
        return jsonify({"error": "No se pudo generar el QR"}), 500

@app.route('/upload-template', methods=['POST'])
def upload_template():
    """Maneja la subida de la plantilla del diploma"""
    try:
        if 'template' not in request.files:
            return jsonify({'error': 'No se encontró el archivo de plantilla'}), 400
        
        template_file = request.files['template']
        
        if template_file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        if not allowed_file(template_file.filename):
            return jsonify({'error': 'Formato no permitido. Use JPG, PNG'}), 400
        
        filename = secure_filename(template_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        template_file.save(filepath)
        
        # Obtener dimensiones
        try:
            with Image.open(filepath) as img:
                width, height = img.size
                
                # Crear miniatura para vista previa
                preview_size = (800, 600)
                img_copy = img.copy()
                img_copy.thumbnail(preview_size, Image.Resampling.LANCZOS)
                
                # Guardar miniatura
                preview_filename = 'preview_' + filename
                preview_path = os.path.join(app.config['UPLOAD_FOLDER'], preview_filename)
                
                # Convertir a RGB si es necesario
                if img_copy.mode != 'RGB':
                    img_copy = img_copy.convert('RGB')
                
                img_copy.save(preview_path, 'JPEG', quality=80)
                
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'preview_filename': preview_filename,
                    'filepath': filepath,
                    'dimensions': {'width': width, 'height': height},
                    'url': url_for('uploaded_file', filename=preview_filename)
                })
                
        except Exception as e:
            return jsonify({'error': f'Error procesando imagen: {str(e)}'}), 500
    
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

@app.route('/process-names', methods=['POST'])
def process_names():
    """Procesa los nombres desde diferentes fuentes"""
    try:
        names = []
        source_type = request.form.get('source_type', 'text')
        
        if source_type == 'text':
            text_names = request.form.get('names_text', '')
            if text_names:
                # Mantener tildes y caracteres especiales
                names = [name.strip() for name in text_names.split('\n') if name.strip()]
        
        elif source_type == 'file' and 'names_file' in request.files:
            file = request.files['names_file']
            if file and allowed_file(file.filename):
                names = extract_names_from_file(file)
        
        # Limpiar y validar nombres (manteniendo tildes)
        names = list(dict.fromkeys([name for name in names if name and len(name.strip()) > 0]))
        
        if not names:
            return jsonify({'error': 'No se encontraron nombres válidos'}), 400
        
        return jsonify({
            'success': True,
            'names': names,
            'count': len(names)
        })
    
    except Exception as e:
        return jsonify({'error': f'Error al procesar nombres: {str(e)}'}), 500

@app.route('/preview-position', methods=['POST'])
def preview_position():
    """Crea una vista previa con el texto en posición"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No se recibieron datos JSON'}), 400
            
        template_path = data.get('template_path')
        text_config = data.get('text_config', {})
        
        if not template_path or not os.path.exists(template_path):
            return jsonify({'error': 'Plantilla no encontrada'}), 400
        
        # Configuración
        x = int(text_config.get('x', 100))
        y = int(text_config.get('y', 100))
        font_size = int(text_config.get('font_size', 40))
        font_color = text_config.get('font_color', '#000000')
        font_name = text_config.get('font_name', 'arial.ttf')
        font_style = text_config.get('font_style', 'normal')
        sample_text = text_config.get('sample_text', 'José María Rodríguez')
        align_type = text_config.get('align_type', 'manual')
        
        # Convertir color
        if font_color.startswith('#'):
            font_color = tuple(int(font_color[i:i+2], 16) for i in (1, 3, 5))
        else:
            font_color = (0, 0, 0)
        
        # Cargar imagen
        with Image.open(template_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            draw = ImageDraw.Draw(img)
            img_width, img_height = img.size
            
            # Cargar fuente con estilo
            print(f"🔤 Cargando fuente: {font_name}, estilo: {font_style}, tamaño: {font_size}")
            font = load_font(font_name, font_size, font_style)
            
            # Calcular posición según alineación
            if align_type == 'center_x':
                text_width, text_height = get_text_dimensions(sample_text, font, draw)
                x = (img_width - text_width) // 2
            elif align_type == 'center_xy':
                text_width, text_height = get_text_dimensions(sample_text, font, draw)
                x = (img_width - text_width) // 2
                y = (img_height - text_height) // 2
            elif align_type == 'top_center':
                text_width, text_height = get_text_dimensions(sample_text, font, draw)
                x = (img_width - text_width) // 2
                y = 50
            elif align_type == 'bottom_center':
                text_width, text_height = get_text_dimensions(sample_text, font, draw)
                x = (img_width - text_width) // 2
                y = img_height - text_height - 50
            
            # Dibujar texto
            draw.text((x, y), sample_text, font=font, fill=font_color)
            
            # Guardar en buffer
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=85)
            buffered.seek(0)
            
            # Convertir a base64
            img_str = base64.b64encode(buffered.read()).decode()
            
            return jsonify({
                'success': True,
                'preview': f'data:image/jpeg;base64,{img_str}',
                'position': {'x': x, 'y': y},
                'dimensions': {'width': img_width, 'height': img_height}
            })
    
    except Exception as e:
        print(f"❌ Error en vista previa: {str(e)}")
        return jsonify({'error': f'Error en vista previa: {str(e)}'}), 500

@app.route('/generate-diplomas', methods=['POST'])
def generate_diplomas():
    """Genera los diplomas con los nombres proporcionados"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No se recibieron datos JSON'}), 400
            
        template_path = data.get('template_path')
        names = data.get('names', [])
        text_config = data.get('text_config', {})
        
        if not template_path or not os.path.exists(template_path):
            return jsonify({'error': 'Plantilla no encontrada'}), 400
        
        if not names:
            return jsonify({'error': 'No hay nombres para procesar'}), 400
        
        # Configuración
        x = int(text_config.get('x', 100))
        y = int(text_config.get('y', 100))
        font_size = int(text_config.get('font_size', 40))
        font_color = text_config.get('font_color', '#000000')
        font_name = text_config.get('font_name', 'arial.ttf')
        font_style = text_config.get('font_style', 'normal')
        align_type = text_config.get('align_type', 'manual')
        
        # Convertir color
        if font_color.startswith('#'):
            font_color = tuple(int(font_color[i:i+2], 16) for i in (1, 3, 5))
        else:
            font_color = (0, 0, 0)
        
        # Crear carpeta temporal
        temp_dir = tempfile.mkdtemp()
        generated_files = []
        
        # Cargar plantilla base una vez
        try:
            base_template = Image.open(template_path)
            if base_template.mode != 'RGB':
                base_template = base_template.convert('RGB')
        except Exception as e:
            return jsonify({'error': f'Error al cargar plantilla: {str(e)}'}), 500
        
        # Generar diplomas
        for i, name in enumerate(names):
            try:
                # Crear copia de la plantilla
                img = base_template.copy()
                draw = ImageDraw.Draw(img)
                img_width, img_height = img.size
                
                # Cargar fuente con estilo
                font = load_font(font_name, font_size, font_style)
                
                # Calcular posición según alineación
                final_x, final_y = x, y
                
                if align_type == 'center_x':
                    text_width, text_height = get_text_dimensions(name, font, draw)
                    final_x = (img_width - text_width) // 2
                elif align_type == 'center_xy':
                    text_width, text_height = get_text_dimensions(name, font, draw)
                    final_x = (img_width - text_width) // 2
                    final_y = (img_height - text_height) // 2
                elif align_type == 'top_center':
                    text_width, text_height = get_text_dimensions(name, font, draw)
                    final_x = (img_width - text_width) // 2
                    final_y = 50
                elif align_type == 'bottom_center':
                    text_width, text_height = get_text_dimensions(name, font, draw)
                    final_x = (img_width - text_width) // 2
                    final_y = img_height - text_height - 50
                
                # Dibujar texto (manteniendo tildes)
                draw.text((final_x, final_y), name, font=font, fill=font_color)
                
                # Guardar
                safe_name = ''.join(c for c in name if c.isalnum() or c in (' ', '-', '_', 'ñ', 'Ñ', 'á', 'é', 'í', 'ó', 'ú', 'Á', 'É', 'Í', 'Ó', 'Ú'))[:50]
                output_filename = f"diploma_{i+1:04d}_{safe_name}.jpg"
                output_path = os.path.join(temp_dir, output_filename)
                img.save(output_path, 'JPEG', quality=95)
                generated_files.append(output_filename)
                
                # Guardar copia en output folder
                shutil.copy2(output_path, os.path.join(app.config['OUTPUT_FOLDER'], output_filename))
            
            except Exception as e:
                print(f"⚠ Error con {name}: {e}")
                continue
        
        if not generated_files:
            return jsonify({'error': 'No se generó ningún diploma'}), 500
        
        # Crear ZIP
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f'diplomas_{timestamp}.zip'
        zip_path = os.path.join(app.config['OUTPUT_FOLDER'], zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for filename in generated_files:
                file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                if os.path.exists(file_path):
                    zipf.write(file_path, filename)
        
        # Limpiar archivos individuales del output folder
        for filename in generated_files:
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
        
        # Limpiar temporal
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        return jsonify({
            'success': True,
            'zip_file': zip_filename,
            'count': len(generated_files),
            'download_url': url_for('download_file', filename=zip_filename)
        })
        
    except Exception as e:
        print(f"❌ Error al generar diplomas: {str(e)}")
        return jsonify({'error': f'Error al generar diplomas: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Descarga el archivo generado"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'Archivo no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Error al descargar: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Sirve archivos subidos"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except:
        return '', 404

@app.route('/check-fonts', methods=['GET'])
def check_fonts():
    """Verifica qué fuentes están disponibles"""
    fonts_to_check = [
        'arial.ttf',
        'arialbd.ttf',
        'ariali.ttf',
        'times.ttf',
        'timesbd.ttf',
        'cour.ttf',
        'courbd.ttf'
    ]
    
    available_fonts = []
    missing_fonts = []
    
    for font in fonts_to_check:
        font_path = get_font_path(font, 'normal')
        if font_path and os.path.exists(font_path):
            available_fonts.append(font)
        else:
            missing_fonts.append(font)
    
    return jsonify({
        'available': available_fonts,
        'missing': missing_fonts,
        'fonts_folder': os.path.abspath(app.config['FONTS_FOLDER'])
    })

@app.route('/test-font', methods=['POST'])
def test_font():
    """Prueba si una fuente está disponible"""
    try:
        data = request.json
        font_name = data.get('font_name', 'arial.ttf')
        font_size = data.get('font_size', 40)
        font_style = data.get('font_style', 'normal')
        
        try:
            font = load_font(font_name, font_size, font_style)
            return jsonify({
                'success': True,
                'message': f'Fuente {font_name} ({font_style}) cargada correctamente'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Fuente {font_name} ({font_style}) no disponible: {str(e)}'
            })
    except Exception as e:
        return jsonify({'error': f'Error probando fuente: {str(e)}'}), 500

@app.route('/get-available-fonts', methods=['GET'])
def get_available_fonts_api():
    """Devuelve fuentes disponibles"""
    fonts = [
        {'name': 'Arial Normal', 'file': 'arial.ttf', 'style': 'normal'},
        {'name': 'Arial Negrita', 'file': 'arial.ttf', 'style': 'bold'},
        {'name': 'Arial Cursiva', 'file': 'arial.ttf', 'style': 'italic'},
        {'name': 'Times New Roman Normal', 'file': 'times.ttf', 'style': 'normal'},
        {'name': 'Times New Roman Negrita', 'file': 'times.ttf', 'style': 'bold'},
        {'name': 'Courier New Normal', 'file': 'cour.ttf', 'style': 'normal'},
        {'name': 'Courier New Negrita', 'file': 'cour.ttf', 'style': 'bold'},
    ]
    
    available_fonts = []
    for font in fonts:
        try:
            font_path = get_font_path(font['file'], font['style'])
            if font_path and os.path.exists(font_path):
                available_fonts.append(font)
        except:
            pass
    
    return jsonify({'fonts': available_fonts})

if __name__ == '__main__':
    server_url = get_server_url()
    
    print("=" * 70)
    print("🎓 XONI-DIP - GENERADOR MASIVO DE DIPLOMAS 🎓")
    print("=" * 70)
    
    # Crear carpeta fonts si no existe
    fonts_folder = app.config['FONTS_FOLDER']
    if not os.path.exists(fonts_folder):
        os.makedirs(fonts_folder)
        print(f"📁 Carpeta 'fonts' creada en: {os.path.abspath(fonts_folder)}")
        print("💡 Copia archivos .ttf a esta carpeta para más opciones de fuentes")
    
    # Verificar fuentes disponibles
    print("\n🔍 Verificando fuentes disponibles...")
    
    # Lista de fuentes comunes
    common_fonts = ['arial.ttf', 'times.ttf', 'cour.ttf']
    fonts_found = []
        
    print(f"\n🌐 ACCESO DESDE CUALQUIER DISPOSITIVO:")
    print(f"   • {server_url}")
    
    # Generar QR
    try:
        qr_ascii = qrcode.QRCode()
        qr_ascii.add_data(server_url)
        print("\n📱 Escanea este código QR desde tu teléfono:")
        print("-" * 50)
        qr_ascii.print_ascii()
        print("-" * 50)
    except:
        pass
    
    print(f"\n🚀 Para comenzar:")
    print(f"   1. Abre {server_url} en tu navegador")
    print(f"   2. O escanea el QR desde tu teléfono")
    print(f"   3. Sube una plantilla de diploma")
    print(f"   4. Configura la posición y estilo del texto")
    print(f"   5. Ingresa los nombres con tildes")
    print(f"   6. ¡Genera y descarga!")
    
    print("\n" + "=" * 70)
    
    # Iniciar servidor
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
