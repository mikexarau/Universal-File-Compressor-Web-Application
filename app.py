from flask import Flask, request, send_from_directory, render_template
from werkzeug.utils import secure_filename
from PIL import Image
from moviepy.editor import VideoFileClip
import os
from comprimirpdf import compress

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def compress_file(file_path, scale, quality):
    if file_path:
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        save_path = os.path.join(DOWNLOAD_FOLDER, f"{file_name}-compressed{file_extension}")
                
        if file_extension.lower() in [".jpg", ".jpeg", ".png"]:
            image = Image.open(file_path)
            width, height = image.size
            new_width = int(width * scale / 100)
            new_height = int(height * scale / 100)
            new_image = image.resize((new_width, new_height))
            new_image.save(save_path, optimize=True, quality=quality)
        elif file_extension.lower() in [".mp4", ".avi", ".mov"]:
            video = VideoFileClip(file_path)
            new_width = int(video.w * scale / 100)
            new_height = int(video.h * scale / 100)
            new_video = video.resize(width=new_width, height=new_height)
            if file_extension.lower() == ".mov":
                save_path = f"{file_name}-compressed.mp4"
            new_video.write_videofile(save_path)
        elif file_extension.lower() == ".pdf":
            compress_quality = quality
            compress_quality //= 25
            compress(file_path, save_path, compress_quality)

        return save_path

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        scale = request.form.get('scale', type=int)
        if scale is None:
            scale = 50
    
        quality = request.form.get('quality', type=int)
        if quality is None:
            quality = 85

        output_file = compress_file(filepath, scale, quality)
        return os.path.basename(output_file)

    return render_template('index.html')

@app.route('/downloads/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

