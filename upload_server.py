from flask import Flask, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, '图片')
MANIFEST_PATH = os.path.join(IMAGES_DIR, 'manifest.json')
ALLOWED_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}

os.makedirs(IMAGES_DIR, exist_ok=True)

app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')

def update_manifest():
    files = [f for f in os.listdir(IMAGES_DIR) if os.path.isfile(os.path.join(IMAGES_DIR, f))]
    # ignore manifest itself
    files = [f for f in files if f != 'manifest.json']
    files.sort()
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as mf:
        json.dump(files, mf, ensure_ascii=False, indent=2)

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'no file'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'empty filename'}), 400
    filename = secure_filename(f.filename)
    name, ext = os.path.splitext(filename)
    if ext.lower() not in ALLOWED_EXT:
        return jsonify({'error':'invalid extension'}), 400
    dest = os.path.join(IMAGES_DIR, filename)
    # avoid overwrite: if exists, append counter
    counter = 1
    while os.path.exists(dest):
        filename = f"{name}_{counter}{ext}"
        dest = os.path.join(IMAGES_DIR, filename)
        counter += 1
    f.save(dest)
    update_manifest()
    return jsonify({'filename': filename}), 200

@app.route('/delete', methods=['DELETE'])
def delete_file():
    name = request.args.get('name')
    if not name:
        return jsonify({'error':'no name'}), 400
    # prevent path traversal
    if os.path.sep in name or '..' in name:
        return jsonify({'error':'invalid name'}), 400
    target = os.path.join(IMAGES_DIR, name)
    if not os.path.exists(target):
        return jsonify({'error':'not found'}), 404
    try:
        os.remove(target)
        update_manifest()
        return jsonify({'deleted': name}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/图片/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGES_DIR, filename)

if __name__ == '__main__':
    update_manifest()
    app.run(host='0.0.0.0', port=8000, debug=True)
