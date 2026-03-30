import os
import io
import zipfile
import socket
import webbrowser
import threading
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
app.config['OUTPUT_FORMATS'] = ['PNG', 'PDF', 'JPG']
app.config['DEFAULT_FORMAT'] = 'PNG'

# Crear carpetas si no existen
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['FONTS_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Variable para controlar si ya se abrió el navegador
browser_opened = False

# ===== FUNCIÓN PARA OBTENER IP =====
def get_server_url():
    """Obtiene la URL del servidor con IP y puerto"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return f"http://{local_ip}:5000"
    except:
        return "http://localhost:5000"

# ===== FUNCIÓN PARA ABRIR NAVEGADOR AUTOMÁTICAMENTE =====
def open_browser_after_delay():
    """Abre el navegador después de que el servidor esté listo"""
    global browser_opened
    time.sleep(2)  # Esperar 2 segundos a que el servidor inicie
    if not browser_opened:
        browser_opened = True
        url = get_server_url()
        try:
            webbrowser.open(url)
            print(f"\n🌐 Navegador abierto automáticamente en: {url}")
        except:
            print(f"\n⚠️ No se pudo abrir el navegador automáticamente")
            print(f"   Abre manualmente: {url}")

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
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str
    except Exception as e:
        print(f"Error generando QR: {e}")
        return None

# ===== FUNCIÓN PARA NORMALIZAR NOMBRES DE ARCHIVO =====
def normalize_filename(name):
    """Normaliza un nombre para uso en nombre de archivo"""
    # Reemplazar caracteres especiales
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U',
        ' ': '_', ',': '', '.': '', "'": '', '"': '',
        '¿': '', '?': '', '¡': '', '!': '', ':': '', ';': '',
        '/': '_', '\\': '_', '*': '', '|': '', '<': '', '>': ''
    }
    
    for special, normal in replacements.items():
        name = name.replace(special, normal)
    
    # Eliminar caracteres no permitidos
    name = ''.join(c for c in name if c.isalnum() or c in ('_', '-'))
    
    # Limitar longitud y evitar nombres vacíos
    name = name[:50] if name else "participante"
    
    return name

# ===== FUNCIÓN PARA GUARDAR EN DIFERENTES FORMATOS =====
def save_diploma(image, name, output_format='PNG'):
    """Guarda el diploma en el formato especificado con nombre personalizado"""
    
    safe_name = normalize_filename(name)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if output_format.upper() == 'PDF':
        # Generar PDF
        output_filename = f"diploma_{safe_name}_{timestamp}.pdf"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Convertir imagen a PDF
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image.save(output_path, 'PDF', resolution=100.0)
        
    elif output_format.upper() == 'JPG':
        # Generar JPG
        output_filename = f"diploma_{safe_name}_{timestamp}.jpg"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image.save(output_path, 'JPEG', quality=95, optimize=True)
        
    else:  # PNG por defecto
        output_filename = f"diploma_{safe_name}_{timestamp}.png"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        image.save(output_path, 'PNG', optimize=True)
    
    return output_filename, output_path

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
                if i == 0 and 'nombre' in line.lower():
                    continue
                parts = line.strip().split(',')
                if parts and parts[0].strip():
                    names.append(parts[0].strip())
        
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
            file.seek(0)
            for col in df.columns:
                if any(keyword in str(col).lower() for keyword in ['nombre', 'name', 'participante', 'alumno']):
                    names = [str(name).strip() for name in df[col].dropna().tolist() if str(name).strip()]
                    break
            if not names and len(df.columns) > 0:
                names = [str(name).strip() for name in df[df.columns[0]].dropna().tolist() if str(name).strip()]
    
    except Exception as e:
        print(f"Error procesando archivo: {e}")
        return []
    
    return names

def get_text_dimensions(text, font, draw):
    """Obtiene dimensiones del texto para centrado preciso"""
    try:
        if hasattr(draw, 'textbbox'):
            bbox = draw.textbbox((0, 0), text, font=font)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        else:
            return font.getsize(text)
    except:
        return len(text) * font.size // 2, font.size

def get_centered_position(x, y, text, font, draw):
    """Calcula la posición para que (x,y) sea el CENTRO del texto"""
    ancho, alto = get_text_dimensions(text, font, draw)
    return x - (ancho // 2), y - (alto // 2)

def get_font_path(font_name, style='normal'):
    """Obtiene la ruta completa de una fuente con estilo"""
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
        }
    }
    
    font_paths = [
        app.config['FONTS_FOLDER'],
        os.path.join(os.path.dirname(__file__), 'fonts'),
        "fonts/",
        "/usr/share/fonts/",
        "/usr/local/share/fonts/",
        "/System/Library/Fonts/",
        "/Library/Fonts/",
        "C:\\Windows\\Fonts\\",
        "C:/Windows/Fonts/"
    ]
    
    base_name = font_name.lower()
    if base_name in font_mappings and style in font_mappings[base_name]:
        font_variants = font_mappings[base_name][style]
    else:
        font_variants = [font_name]
    
    for path in font_paths:
        if not os.path.exists(path):
            continue
        for variant in font_variants:
            font_path = os.path.join(path, variant)
            if os.path.exists(font_path):
                print(f"✓ Encontrada fuente: {font_path}")
                return font_path
    
    return None

def create_fallback_font(font_size):
    """Crea una fuente por defecto si no hay fuentes disponibles"""
    try:
        for path in ['/usr/share/fonts/TTF/DejaVuSans.ttf', 
                    '/usr/share/fonts/liberation/LiberationSans-Regular.ttf',
                    '/System/Library/Fonts/Helvetica.ttc']:
            if os.path.exists(path):
                return ImageFont.truetype(path, font_size)
    except:
        pass
    
    try:
        return ImageFont.load_default().font_variant(size=font_size)
    except:
        return ImageFont.load_default()

def load_font(font_name, font_size, font_style='normal'):
    """Carga una fuente con estilo con manejo de errores mejorado"""
    try:
        font_path = get_font_path(font_name, font_style)
        if font_path and os.path.exists(font_path):
            return ImageFont.truetype(font_path, font_size)
        
        font_path = get_font_path(font_name, 'normal')
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
            if font_style == 'bold':
                return ImageFont.truetype(font_path, int(font_size * 1.1))
            elif font_style == 'italic':
                return font
            return font
        
        print(f"⚠ No se encontró la fuente {font_name}. Usando fuente por defecto.")
        return create_fallback_font(font_size)
        
    except Exception as e:
        print(f"⚠ Error cargando fuente {font_name}: {e}")
        return create_fallback_font(font_size)

@app.route('/')
def index():
    server_url = get_server_url()
    qr_base64 = generate_qr_base64(server_url)
    
    return render_template('index.html', 
                         qr_code=qr_base64, 
                         server_url=server_url)

@app.route('/qr_code')
def qr_code():
    server_url = get_server_url()
    qr_base64 = generate_qr_base64(server_url)
    
    if qr_base64:
        return jsonify({"qr_base64": qr_base64, "url": server_url})
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
        
        try:
            with Image.open(filepath) as img:
                width, height = img.size
                
                # Crear miniatura para vista previa
                preview_size = (800, 600)
                img_copy = img.copy()
                
                # Compatibilidad con versiones de Pillow
                try:
                    img_copy.thumbnail(preview_size, Image.Resampling.LANCZOS)
                except AttributeError:
                    try:
                        img_copy.thumbnail(preview_size, Image.ANTIALIAS)
                    except AttributeError:
                        img_copy.thumbnail(preview_size)
                
                preview_filename = 'preview_' + filename
                preview_path = os.path.join(app.config['UPLOAD_FOLDER'], preview_filename)
                
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
                names = [name.strip() for name in text_names.split('\n') if name.strip()]
        
        elif source_type == 'file' and 'names_file' in request.files:
            file = request.files['names_file']
            if file and allowed_file(file.filename):
                names = extract_names_from_file(file)
        
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
    """Crea una vista previa con el texto centrado en la posición indicada"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No se recibieron datos JSON'}), 400
            
        template_path = data.get('template_path')
        text_config = data.get('text_config', {})
        
        if not template_path or not os.path.exists(template_path):
            return jsonify({'error': 'Plantilla no encontrada'}), 400
        
        # Configuración (estos valores son el CENTRO deseado)
        centro_x = int(text_config.get('x', 100))
        centro_y = int(text_config.get('y', 100))
        font_size = int(text_config.get('font_size', 40))
        font_color = text_config.get('font_color', '#000000')
        font_name = text_config.get('font_name', 'arial.ttf')
        font_style = text_config.get('font_style', 'normal')
        sample_text = text_config.get('sample_text', 'José María Rodríguez')
        
        if font_color.startswith('#'):
            font_color = tuple(int(font_color[i:i+2], 16) for i in (1, 3, 5))
        else:
            font_color = (0, 0, 0)
        
        with Image.open(template_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            draw = ImageDraw.Draw(img)
            
            font = load_font(font_name, font_size, font_style)
            
            # Calcular posición de esquina para que el centro sea (centro_x, centro_y)
            x, y = get_centered_position(centro_x, centro_y, sample_text, font, draw)
            
            # Dibujar un punto rojo en el centro para referencia
            radio = 3
            draw.ellipse((centro_x - radio, centro_y - radio, centro_x + radio, centro_y + radio), fill='red')
            
            # Dibujar texto centrado
            draw.text((x, y), sample_text, font=font, fill=font_color)
            
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=85)
            buffered.seek(0)
            
            img_str = base64.b64encode(buffered.read()).decode()
            
            return jsonify({
                'success': True,
                'preview': f'data:image/jpeg;base64,{img_str}',
                'position': {'x': centro_x, 'y': centro_y},
                'dimensions': {'width': img.width, 'height': img.height}
            })
    
    except Exception as e:
        print(f"❌ Error en vista previa: {str(e)}")
        return jsonify({'error': f'Error en vista previa: {str(e)}'}), 500

@app.route('/generate-diplomas', methods=['POST'])
def generate_diplomas():
    """Genera los diplomas con los nombres centrados en la posición indicada"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No se recibieron datos JSON'}), 400
            
        template_path = data.get('template_path')
        names = data.get('names', [])
        text_config = data.get('text_config', {})
        output_format = data.get('output_format', app.config['DEFAULT_FORMAT'])
        
        if not template_path or not os.path.exists(template_path):
            return jsonify({'error': 'Plantilla no encontrada'}), 400
        
        if not names:
            return jsonify({'error': 'No hay nombres para procesar'}), 400
        
        # Configuración (estos valores son el CENTRO deseado)
        centro_x = int(text_config.get('x', 100))
        centro_y = int(text_config.get('y', 100))
        font_size = int(text_config.get('font_size', 40))
        font_color = text_config.get('font_color', '#000000')
        font_name = text_config.get('font_name', 'arial.ttf')
        font_style = text_config.get('font_style', 'normal')
        
        if font_color.startswith('#'):
            font_color = tuple(int(font_color[i:i+2], 16) for i in (1, 3, 5))
        else:
            font_color = (0, 0, 0)
        
        temp_dir = tempfile.mkdtemp()
        generated_files = []
        file_mapping = {}  # Para mapear nombre original -> archivo generado
        
        try:
            base_template = Image.open(template_path)
            if base_template.mode != 'RGB':
                base_template = base_template.convert('RGB')
        except Exception as e:
            return jsonify({'error': f'Error al cargar plantilla: {str(e)}'}), 500
        
        for i, name in enumerate(names):
            try:
                img = base_template.copy()
                draw = ImageDraw.Draw(img)
                
                font = load_font(font_name, font_size, font_style)
                
                # Calcular posición de esquina para que el centro sea (centro_x, centro_y)
                x, y = get_centered_position(centro_x, centro_y, name, font, draw)
                
                # Dibujar texto centrado
                draw.text((x, y), name, font=font, fill=font_color)
                
                # Guardar con nombre personalizado en el formato seleccionado
                output_filename, output_path = save_diploma(img, name, output_format)
                
                # También guardar en temp_dir para el ZIP
                temp_path = os.path.join(temp_dir, output_filename)
                shutil.copy2(output_path, temp_path)
                
                generated_files.append(output_filename)
                file_mapping[output_filename] = name
                
                print(f"✓ Generado: {output_filename}")
            
            except Exception as e:
                print(f"⚠ Error con {name}: {e}")
                continue
        
        if not generated_files:
            return jsonify({'error': 'No se generó ningún diploma'}), 500
        
        # Crear archivo ZIP con todos los diplomas
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f'diplomas_{timestamp}.zip'
        zip_path = os.path.join(app.config['OUTPUT_FOLDER'], zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in generated_files:
                file_path = os.path.join(temp_dir, filename)
                if os.path.exists(file_path):
                    zipf.write(file_path, filename)
        
        # Limpiar archivos temporales
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        # Limpiar archivos individuales (opcional - mantenerlos o eliminarlos)
        for filename in generated_files:
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)  # Eliminar individuales, solo mantener el ZIP
                except:
                    pass
        
        return jsonify({
            'success': True,
            'zip_file': zip_filename,
            'count': len(generated_files),
            'download_url': url_for('download_file', filename=zip_filename),
            'format': output_format,
            'files': generated_files[:5]  # Mostrar primeros 5 como ejemplo
        })
        
    except Exception as e:
        print(f"❌ Error al generar diplomas: {str(e)}")
        return jsonify({'error': f'Error al generar diplomas: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
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
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except:
        return '', 404

@app.route('/check-fonts', methods=['GET'])
def check_fonts():
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

@app.route('/get-output-formats', methods=['GET'])
def get_output_formats():
    """Devuelve los formatos de salida disponibles"""
    return jsonify({
        'formats': app.config['OUTPUT_FORMATS'],
        'default': app.config['DEFAULT_FORMAT']
    })

if __name__ == '__main__':
    server_url = get_server_url()
    
    print("=" * 70)
    print("XONIDIP - GENERADOR MASIVO DE DIPLOMAS")
    print("=" * 70)
    print("\n✅ CARACTERÍSTICAS:")
    print("   • Formatos de salida: PNG, PDF, JPG")
    print("   • Nombres de archivo personalizados: diploma_Nombre_Apellido.pdf")
    print("   • Soporte mejorado para tildes y caracteres especiales")
    print("   • Apertura automática del navegador")
    
    fonts_folder = app.config['FONTS_FOLDER']
    if not os.path.exists(fonts_folder):
        os.makedirs(fonts_folder)
        print(f"\n📁 Carpeta 'fonts' creada en: {os.path.abspath(fonts_folder)}")
        print("💡 Copia archivos .ttf a esta carpeta para más opciones de fuentes")
    
    print("\n🔍 Verificando fuentes disponibles...")
    
    print(f"\n🌐 ACCESO DESDE CUALQUIER DISPOSITIVO:")
    print(f"   • {server_url}")
    
    # Iniciar hilo para abrir el navegador automáticamente
    browser_thread = threading.Thread(target=open_browser_after_delay)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        qr_ascii = qrcode.QRCode()
        qr_ascii.add_data(server_url)
        print("\n📱 Escanea este código QR desde tu teléfono:")
        print("-" * 50)
        qr_ascii.print_ascii()
        print("-" * 50)
    except:
        pass
    
    print("\n" + "=" * 70)
    print("XONIDU - Darian Alberto Camacho Salas")
    print("Servidor iniciado correctamente")
    print("El navegador se abrirá automáticamente en unos segundos...")
    print("=" * 70)
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
