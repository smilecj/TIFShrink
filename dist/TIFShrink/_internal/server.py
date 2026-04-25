#!/usr/bin/env python3
"""
TIFShrink Backend - 本地 TIFF 压缩服务 v2.0

支持的所有压缩算法:
- Deflate (默认，最佳压缩率)
- LZW
- PackBits
- JPEG (TIFF嵌入式)
- 无压缩
隐私保证：所有处理在本地完成，不上传任何数据

使用方法：
    pip install Pillow flask
    python server.py
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import io
import os
import sys
import zipfile
import uuid
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 启用跨域资源共享

@app.route('/')
def index():
    """返回主页面"""
    index_path = os.path.join(os.path.dirname(__file__), 'index.html')
    if getattr(sys, 'frozen', False):
        index_path = os.path.join(sys._MEIPASS, 'index.html')
    return send_file(index_path, mimetype='text/html')

@app.route('/favicon.ico')
def favicon():
    """返回 favicon 图标"""
    try:
        import base64
        from io import BytesIO

        icon_data = base64.b64decode(
            'AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAABILAAASCwAAAAAAAAAAAAD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wCKqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/////8A////AP///wD///8A////AP///wCKqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/////AP///wD///8A////AP///wCKqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/////wD///8A////AP///wCKqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/////8A////AP///wCKqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/////AP///wCKqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/////wD///8Aiqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/////8A////AIqq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/////AP///wCKqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/////AP///wCKqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/////AP///wCKqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/////AP///wCKqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/////8A////AP///wCKqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/iqr3/4qq9/+Kqvf/////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//8AAP//AAD4HwAA8A8AAPAPAADwDwAA8A8AAPAPAADwDwAA8A8AAPgPAAD//wAA//8AAP//AAD//wAA//8AAA=='
        )

        return send_file(
            BytesIO(icon_data),
            mimetype='image/x-icon',
            as_attachment=False,
            download_name='favicon.ico'
        )
    except Exception:
        return '', 204

# 临时文件存储
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

# 支持的压缩算法
COMPRESSION_ALGORITHMS = {
    'deflate': {
        'name': 'Deflate',
        'description': '最佳压缩率（推荐）',
        'tiff_value': 'tiff_deflate',
        'supported_modes': ['RGB', 'L', 'P', 'RGBA']
    },
    'lzw': {
        'name': 'LZW',
        'description': '经典无损压缩',
        'tiff_value': 'tiff_lzw',
        'supported_modes': ['RGB', 'L', 'P', 'RGBA']
    },
    'packbits': {
        'name': 'PackBits',
        'description': '快速压缩，适合黑白图',
        'tiff_value': 'packbits',
        'supported_modes': ['RGB', 'L', 'P', 'RGBA']
    },
    'jpeg': {
        'name': 'JPEG',
        'description': 'TIFF内嵌JPEG，有损压缩',
        'tiff_value': 'tiff_jpeg',
        'quality_param': True,
        'supported_modes': ['RGB', 'L']
    },
    'none': {
        'name': '无压缩',
        'description': '保持原始数据',
        'tiff_value': 'raw',
        'supported_modes': ['RGB', 'L', 'P', 'RGBA']
    },
    'packbits': {
        'name': 'PackBits',
        'description': '快速压缩，适合黑白图',
        'tiff_value': 'packbits',
        'supported_modes': ['RGB', 'L', 'P', 'RGBA']
    }
}

def get_image_info(img: Image.Image) -> dict:
    """获取图片信息"""
    return {
        'width': img.width,
        'height': img.height,
        'mode': img.mode,
        'format': getattr(img, 'format', 'Unknown'),
    }

def prepare_image(img: Image.Image, compression: str) -> Image.Image:
    """
    根据压缩方式准备图片
    JPEG 压缩需要特定模式
    """
    if compression == 'jpeg':
        # JPEG 压缩只支持 L 或 RGB
        if img.mode == 'RGBA':
            # 白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            return background
        elif img.mode == 'P':
            return img.convert('RGB')
        elif img.mode == 'L':
            return img
        return img.convert('RGB')
    elif compression == 'none':
        # 无压缩，保持原样
        return img
    else:
        # 其他压缩方式
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            return background
        elif img.mode == 'P':
            return img.convert('RGB')
        return img

def compress_tiff(image_bytes: bytes, compression: str = 'deflate', quality: int = 95) -> tuple:
    """
    压缩 TIFF 图片
    
    Args:
        image_bytes: 输入图片字节
        compression: 压缩方式
        quality: 质量参数 (对 JPEG 压缩有效)
    
    Returns:
        (压缩后的图片字节, 压缩信息)
    """
    # 打开图片
    img = Image.open(io.BytesIO(image_bytes))
    original_info = get_image_info(img)
    
    # 准备图片
    img = prepare_image(img, compression)
    
    # 创建输出 buffer
    output = io.BytesIO()
    
    # 获取压缩配置
    comp_config = COMPRESSION_ALGORITHMS.get(compression, COMPRESSION_ALGORITHMS['deflate'])
    tiff_comp = comp_config['tiff_value']
    
    # 构建保存参数
    save_kwargs = {
        'format': 'TIFF',
        'compression': tiff_comp
    }
    
    # 如果是 JPEG 压缩，添加质量参数
    if compression == 'jpeg' and 'quality_param' in comp_config:
        save_kwargs['quality'] = quality
    
    # 保存
    img.save(output, **save_kwargs)
    output.seek(0)
    compressed_bytes = output.read()
    
    # 获取压缩后信息
    compressed_img = Image.open(io.BytesIO(compressed_bytes))
    compressed_info = get_image_info(compressed_img)
    
    return compressed_bytes, {
        'algorithm': compression,
        'algorithm_name': comp_config['name'],
        'original': original_info,
        'compressed': compressed_info,
        'original_size': len(image_bytes),
        'compressed_size': len(compressed_bytes),
        'saved_bytes': len(image_bytes) - len(compressed_bytes),
        'saved_percent': round((1 - len(compressed_bytes) / len(image_bytes)) * 100, 2) if len(image_bytes) > 0 else 0
    }

def compress_image(image_bytes: bytes, output_format: str, compression: str = 'deflate', quality: int = 95) -> tuple:
    """
    压缩/转换图片
    
    Returns:
        (处理后的图片字节, 处理信息)
    """
    img = Image.open(io.BytesIO(image_bytes))
    original_info = get_image_info(img)
    
    # 根据输出格式处理
    if output_format == 'tiff':
        return compress_tiff(image_bytes, compression, quality)
    
    output = io.BytesIO()
    
    if output_format == 'png':
        if img.mode == 'RGBA':
            img.save(output, format='PNG', optimize=True)
        else:
            img.save(output, format='PNG', optimize=True)
            
    elif output_format == 'jpeg':
        if img.mode in ('RGBA', 'P'):
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            else:
                img = img.convert('RGB')
        img.save(output, format='JPEG', quality=quality, optimize=True)
        
    elif output_format == 'pdf':
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode == 'P':
            img = img.convert('RGB')
        
        # A4 at 72 DPI
        a4_width, a4_height = 595, 842
        scale = min(a4_width / img.width, a4_height / img.height)
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        x_offset = (a4_width - new_width) // 2
        y_offset = (a4_height - new_height) // 2
        
        canvas = Image.new('RGB', (a4_width, a4_height), 'white')
        canvas.paste(img_resized, (x_offset, y_offset))
        canvas.save(output, format='PDF')
    
    output.seek(0)
    compressed_bytes = output.read()
    
    return compressed_bytes, {
        'format': output_format,
        'original': original_info,
        'compressed': get_image_info(Image.open(io.BytesIO(compressed_bytes))),
        'original_size': len(image_bytes),
        'compressed_size': len(compressed_bytes),
        'saved_bytes': len(image_bytes) - len(compressed_bytes),
        'saved_percent': round((1 - len(compressed_bytes) / len(image_bytes)) * 100, 2) if len(image_bytes) > 0 else 0
    }

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'service': 'TIFShrink Backend',
        'version': '2.0.0',
        'algorithms': list(COMPRESSION_ALGORITHMS.keys()),
        'privacy': 'all processing is done locally'
    })

@app.route('/api/algorithms', methods=['GET'])
def get_algorithms():
    """获取支持的压缩算法列表"""
    return jsonify({
        'algorithms': {
            key: {
                'name': val['name'],
                'description': val['description']
            }
            for key, val in COMPRESSION_ALGORITHMS.items()
        }
    })

@app.route('/api/info', methods=['POST'])
def info():
    """获取图片信息"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        img = Image.open(file)
        
        return jsonify({
            'success': True,
            'info': get_image_info(img)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compress', methods=['POST'])
def compress():
    """
    压缩单张图片
    
    参数:
        file: 图片文件
        format: 输出格式 'tiff', 'png', 'jpeg', 'pdf'
        compression: TIFF压缩方式 'deflate', 'lzw', 'packbits', 'jpeg', 'none'
        quality: 质量参数 1-100
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        output_format = request.form.get('format', 'tiff')
        compression = request.form.get('compression', 'deflate')
        quality = int(request.form.get('quality', '95'))
        
        # 验证压缩算法
        if compression not in COMPRESSION_ALGORITHMS:
            return jsonify({'error': f'Unsupported compression: {compression}'}), 400
        
        # 读取输入
        input_bytes = file.read()
        
        # 压缩
        output_bytes, result = compress_image(input_bytes, output_format, compression, quality)
        
        # 保存临时文件
        ext = output_format if output_format != 'jpeg' else 'jpg'
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(TEMP_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(output_bytes)
        
        result['download_token'] = filename
        result['success'] = True
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Compress error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<token>', methods=['GET'])
def download(token):
    """下载处理后的文件"""
    filepath = os.path.join(TEMP_DIR, os.path.basename(token))
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    original_name = request.args.get('name', 'image')
    ext = os.path.splitext(token)[1].lstrip('.')
    
    if ext == 'jpg':
        ext = 'jpeg'
        mimetype = 'image/jpeg'
    elif ext == 'tif':
        mimetype = 'image/tiff'
    elif ext == 'pdf':
        mimetype = 'application/pdf'
    else:
        mimetype = f'image/{ext}'
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=f"{os.path.splitext(original_name)[0]}.{ext}",
        mimetype=mimetype
    )

@app.route('/api/batch', methods=['POST'])
def batch():
    """
    批量处理
    
    参数:
        files: 多个图片文件
        format: 输出格式
        compression: TIFF压缩方式
        quality: 质量参数
    """
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        output_format = request.form.get('format', 'tiff')
        compression = request.form.get('compression', 'deflate')
        quality = int(request.form.get('quality', '95'))
        
        results = []
        
        for file in files:
            try:
                input_bytes = file.read()
                output_bytes, result = compress_image(input_bytes, output_format, compression, quality)
                
                # 保存临时文件
                ext = output_format if output_format != 'jpeg' else 'jpg'
                filename = f"{uuid.uuid4().hex}.{ext}"
                filepath = os.path.join(TEMP_DIR, filename)
                with open(filepath, 'wb') as f:
                    f.write(output_bytes)
                
                results.append({
                    'name': file.filename,
                    'success': True,
                    **result,
                    'download_token': filename
                })
            except Exception as e:
                results.append({
                    'name': file.filename,
                    'success': False,
                    'error': str(e)
                })
        
        # 创建 ZIP
        zip_filename = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_filepath = os.path.join(TEMP_DIR, zip_filename)
        
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
            for result in results:
                if result['success']:
                    filepath = os.path.join(TEMP_DIR, result['download_token'])
                    ext = os.path.splitext(result['download_token'])[1].lstrip('.')
                    arcname = f"{os.path.splitext(result['name'])[0]}.{ext}"
                    zf.write(filepath, arcname)
        
        total_input = sum(r.get('original_size', 0) for r in results if r['success'])
        total_output = sum(r.get('compressed_size', 0) for r in results if r['success'])
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': {
                'total': len(files),
                'success': sum(1 for r in results if r['success']),
                'failed': sum(1 for r in results if not r['success']),
                'total_input_size': total_input,
                'total_output_size': total_output,
                'total_saved_percent': round((1 - total_output / total_input) * 100, 2) if total_input > 0 else 0
            },
            'zip_token': zip_filename
        })
        
    except Exception as e:
        logger.error(f"Batch error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-download/<token>', methods=['GET'])
def batch_download(token):
    """下载批量处理的 ZIP"""
    filepath = os.path.join(TEMP_DIR, os.path.basename(token))
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=token,
        mimetype='application/zip'
    )

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """清理临时文件"""
    try:
        count = 0
        for filename in os.listdir(TEMP_DIR):
            filepath = os.path.join(TEMP_DIR, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
                count += 1
        
        return jsonify({'success': True, 'cleaned': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                  TIFShrink Backend v2.0.0                       ║
║                                                               ║
║  本地 TIFF 压缩服务                                           ║
║                                                               ║
║  支持的压缩算法:                                              ║
║    • Deflate  - 经典算法，兼容性好                            ║
║    • LZW      - 经典无损压缩                                   ║
║    • PackBits - 快速压缩                                       ║
║    • JPEG     - TIFF内嵌JPEG，有损                            ║
║    • 无压缩   - 保持原始数据                                    ║
║                                                               ║
║  隐私保证：所有处理在本地完成，不上传任何数据                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # 检查依赖
    try:
        from PIL import Image
        print("[OK] Pillow 已安装")
    except ImportError:
        print("[ERROR] 请安装 Pillow: pip install Pillow")
        exit(1)
    
    try:
        import flask
        print("[OK] Flask 已安装")
    except ImportError:
        print("[ERROR] 请安装 Flask: pip install Flask")
        exit(1)
    
    print(f"\n服务地址: http://127.0.0.1:5000")
    print("按 Ctrl+C 停止服务\n")
    
    # 启动服务
    app.run(host='127.0.0.1', port=5000, debug=False)
