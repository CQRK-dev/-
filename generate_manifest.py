import os, json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, '图片')
MANIFEST_PATH = os.path.join(IMAGES_DIR, 'manifest.json')

os.makedirs(IMAGES_DIR, exist_ok=True)
files = [f for f in os.listdir(IMAGES_DIR) if os.path.isfile(os.path.join(IMAGES_DIR, f))]
files = [f for f in files if f != 'manifest.json']
files.sort()
with open(MANIFEST_PATH, 'w', encoding='utf-8') as mf:
    json.dump(files, mf, ensure_ascii=False, indent=2)
print('manifest written with', len(files), 'entries')
