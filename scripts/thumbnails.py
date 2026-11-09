import csv, io, json, os, base64, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageOps

"""Download each ticket photo and write small JPEG thumbnails to photos.json.

Needs Pillow:  pip install pillow   then   python scripts/thumbnails.py
Raw downloads are cached in .photo-cache/ (ignored by git).
"""
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data', 'Commonwealth_Connect_Service_Requests_-_Open_Tickets_20261109.csv')
HERE = ROOT
IMG = os.path.join(ROOT, '.photo-cache')
os.makedirs(IMG, exist_ok=True)
rows = [r for r in csv.DictReader(open(SRC, encoding='utf-8-sig', newline='')) if r['image']]

def get(r):
    tid = r['ticket_id']
    raw = os.path.join(IMG, tid + '.raw')
    try:
        if not os.path.exists(raw):
            req = urllib.request.Request(r['image'], headers={'User-Agent': 'Mozilla/5.0 (course map builder)'})
            with urllib.request.urlopen(req, timeout=40) as resp:
                open(raw, 'wb').write(resp.read())
        im = Image.open(raw)
        im = ImageOps.exif_transpose(im).convert('RGB')
        im.thumbnail((260, 195), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=68, optimize=True, progressive=True)
        return tid, 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        return tid, 'ERR ' + str(e)[:80]

with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(get, rows))
ok = {k: v for k, v in res if not v.startswith('ERR')}
bad = [(k, v) for k, v in res if v.startswith('ERR')]
json.dump(ok, open(os.path.join(HERE, 'photos.json'), 'w'), separators=(',', ':'))
print('ok', len(ok), 'failed', len(bad), bad[:5])
print('bytes', os.path.getsize(os.path.join(HERE, 'photos.json')))
