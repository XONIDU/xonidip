import os
import io
import zipfile
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

app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = 'xonidu-Darian-Alberto-Camacho-Salas'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'diplomas_generados'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'txt', 'csv', 'xlsx', 'xls'}

# Crear carpetas si no existen
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

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

def get_font_path(font_name):
    """Obtiene la ruta completa de una fuente"""
    font_paths = [
        "fonts/",  # Carpeta local
        "/usr/share/fonts/truetype/liberation/",
        "/usr/share/fonts/truetype/dejavu/",
        "/System/Library/Fonts/",
        "C:\\Windows\\Fonts\\",
        "C:/Windows/Fonts/"
    ]
    
    # Primero verificar en carpeta fonts/
    local_font = os.path.join("fonts", font_name)
    if os.path.exists(local_font):
        return local_font
    
    # Buscar en rutas comunes
    for path in font_paths:
        font_path = os.path.join(path, font_name)
        if os.path.exists(font_path):
            return font_path
    
    # Si no se encuentra, usar fuente por defecto
    return None

def load_font(font_name, font_size):
    """Carga una fuente con manejo de errores"""
    try:
        font_path = get_font_path(font_name)
        if font_path:
            return ImageFont.truetype(font_path, font_size)
        else:
            # Intentar cargar directamente
            return ImageFont.truetype(font_name, font_size)
    except:
        # Usar fuentes incluidas en el sistema
        try:
            return ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                return ImageFont.truetype("DejaVuSans.ttf", font_size)
            except:
                # Fuente por defecto
                return ImageFont.load_default()

@app.route('/')
def index():
    return render_template('index.html')

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
            font = load_font(font_name, font_size)
            
            # Aplicar estilo si es posible
            if font_style == 'bold' and hasattr(font, 'font_variant'):
                try:
                    # Intentar cargar versión en negrita
                    bold_font_name = font_name.replace('.ttf', 'bd.ttf').replace('.TTF', 'bd.TTF')
                    font = load_font(bold_font_name, font_size)
                except:
                    pass
            elif font_style == 'italic':
                try:
                    italic_font_name = font_name.replace('.ttf', 'i.ttf').replace('.TTF', 'i.TTF')
                    font = load_font(italic_font_name, font_size)
                except:
                    pass
            
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
            
            # Dibujar texto con fuente actual
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
                font = load_font(font_name, font_size)
                
                # Aplicar estilo si es posible
                if font_style == 'bold':
                    try:
                        bold_font_name = font_name.replace('.ttf', 'bd.ttf').replace('.TTF', 'bd.TTF')
                        font = load_font(bold_font_name, font_size)
                    except:
                        pass
                elif font_style == 'italic':
                    try:
                        italic_font_name = font_name.replace('.ttf', 'i.ttf').replace('.TTF', 'i.TTF')
                        font = load_font(italic_font_name, font_size)
                    except:
                        pass
                
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
                print(f"Error con {name}: {e}")
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

@app.route('/test-font', methods=['POST'])
def test_font():
    """Prueba si una fuente está disponible"""
    try:
        data = request.json
        font_name = data.get('font_name', 'arial.ttf')
        font_size = data.get('font_size', 40)
        
        try:
            font = load_font(font_name, font_size)
            return jsonify({
                'success': True,
                'message': f'Fuente {font_name} cargada correctamente'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Fuente {font_name} no disponible: {str(e)}'
            })
    except Exception as e:
        return jsonify({'error': f'Error probando fuente: {str(e)}'}), 500

@app.route('/get-available-fonts', methods=['GET'])
def get_available_fonts_api():
    """Devuelve fuentes disponibles"""
    fonts = [
        {'name': 'Arial', 'file': 'arial.ttf'},
        {'name': 'Arial Negrita', 'file': 'arialbd.ttf'},
        {'name': 'Arial Cursiva', 'file': 'ariali.ttf'},
        {'name': 'Times New Roman', 'file': 'times.ttf'},
        {'name': 'Times New Roman Negrita', 'file': 'timesbd.ttf'},
        {'name': 'Courier New', 'file': 'cour.ttf'},
        {'name': 'Courier New Negrita', 'file': 'courbd.ttf'},
        {'name': 'Verdana', 'file': 'verdana.ttf'},
        {'name': 'Verdana Negrita', 'file': 'verdanab.ttf'},
        {'name': 'Georgia', 'file': 'georgia.ttf'},
        {'name': 'Georgia Negrita', 'file': 'georgiab.ttf'}
    ]
    
    available_fonts = []
    for font in fonts:
        try:
            if get_font_path(font['file']):
                available_fonts.append(font)
        except:
            pass
    
    # Siempre incluir Arial como fallback
    if not any(f['file'] == 'arial.ttf' for f in available_fonts):
        available_fonts.append({'name': 'Arial', 'file': 'arial.ttf'})
    
    return jsonify({'fonts': available_fonts})

if __name__ == '__main__':
    print("=" * 70)
    print("🎓 XONI-DIP - GENERADOR MASIVO DE DIPLOMAS 🎓")
    print("=" * 70)
    
    # Crear carpeta fonts si no existe
    if not os.path.exists('fonts'):
        os.makedirs('fonts')
        print("📁 Carpeta 'fonts' creada.")
        print("💡 Tip: Copia tus fuentes .ttf aquí para más opciones")
    
    print(f"\n📁 Directorios:")
    print(f"   • Plantillas: {os.path.abspath('uploads')}")
    print(f"   • Diplomas: {os.path.abspath('diplomas_generados')}")
    print(f"   • Templates: {os.path.abspath('templates')}")
    print(f"   • Fuentes: {os.path.abspath('fonts')}")
    
    print(f"\n🌐 Acceso:")
    print(f"   • URL: http://localhost:5000")
    print(f"   • Host: 0.0.0.0")
    print(f"   • Puerto: 5000")
    
    print(f"\n✅ Características:")
    print(f"   • Tildes y caracteres especiales soportados (á, é, í, ó, ú, ñ)")
    print(f"   • Fuentes con estilos (normal, negrita, cursiva)")
    print(f"   • Tamaño de fuente ajustable (10-200px)")
    print(f"   • Posicionamiento preciso")
    print(f"   • Vista previa en tiempo real")
    
    print(f"\n🚀 Para comenzar:")
    print(f"   1. Abre http://localhost:5000 en tu navegador")
    print(f"   2. Sube una plantilla de diploma (JPG, PNG)")
    print(f"   3. Configura la posición y estilo del texto")
    print(f"   4. Ingresa los nombres con tildes")
    print(f"   5. ¡Genera y descarga!")
    print("\n" + "=" * 70)
    
    # Verificar dependencias
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("✅ Pillow instalado correctamente")
    except ImportError:
        print("❌ ERROR: Ejecuta: pip install Pillow")
        exit(1)
    
    # Iniciar servidor
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
