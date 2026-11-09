"""Build index.html from the ticket CSV, the city GIS layers and scripts/template.html.

Run from anywhere:  python scripts/build.py
"""
import csv, json, datetime as dt, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data', 'Commonwealth_Connect_Service_Requests_-_Open_Tickets_20261109.csv')
GIS = os.path.join(ROOT, 'data', 'gis')
TEMPLATE = os.path.join(ROOT, 'scripts', 'template.html')
OUT = os.path.join(ROOT, 'index.html')

GROUPS = [
    ('bike', ['bike', 'bicycle', 'cycle track']),
    ('parks', ['park ', 'park maintenance', 'park equipment', 'park surface', 'park webbing', 'danehy', 'fresh pond',
               "st. peter", 'pool', 'school yard', 'park grounds', 'kids park', 'sand from park']),
    ('trash', ['trash', 'recycl', 'compost', 'garbage', 'rodent', 'rat', 'bigbelly', 'dump', 'needle',
               'holiday tree', 'food waste', 'graffiti', 'receptacle', 'street cleaning']),
    ('noise', ['noise', 'leaf blower', 'loud', 'construction', 'vibration', 'ringing', 'music', 'party', 'compressor']),
    ('streets', ['pothole', 'pot hole', 'sidewalk', 'manhole', 'drain', 'sinkhole', 'pavement', 'brick', 'concrete',
                 'shovel', 'snow', 'icy', 'plow', 'road', 'flood', 'salt', 'street light', 'streetlight', 'tree',
                 'walk', 'path', 'dpw remedial']),
    ('traffic', ['traffic', 'signal', 'light', 'sign', 'crosswalk', 'parking', 'parked', 'car', 'driveway', 'corner',
                 'green arrow', 'mbta vehicle', 'driving']),
]

def group(t):
    s = t.lower()
    for g, kws in GROUPS:
        if any(k in s for k in kws):
            return g
    return 'other'

rows = list(csv.DictReader(open(SRC, encoding='utf-8-sig', newline='')))
types = sorted({r['issue_type'] for r in rows})
tickets = []
for r in rows:
    c = dt.datetime.strptime(r['ticket_created_date_time'], '%m/%d/%Y %I:%M:%S %p')
    u = dt.datetime.strptime(r['ticket_last_updated_date_time'], '%Y %b %d %I:%M:%S %p')
    desc = ' '.join(r['issue_description'].split())
    if len(desc) > 320:
        desc = desc[:317].rstrip() + '…'
    addr = r['address'].replace(', Massachusetts', ', MA').replace(', United States', '')
    tickets.append([int(r['ticket_id']), types.index(r['issue_type']), c.strftime('%Y-%m-%dT%H:%M'),
                    u.strftime('%Y-%m-%d'), round(float(r['lat']), 5), round(float(r['lng']), 5),
                    addr, desc, 1 if r['image'] else 0])
tickets.sort(key=lambda t: t[2])

def line_coords(geom):
    g = geom['type']
    parts = [geom['coordinates']] if g == 'LineString' else geom['coordinates']
    out = []
    for p in parts:
        q = []
        for x, y in p:
            pt = [round(x, 5), round(y, 5)]
            if not q or q[-1] != pt:
                q.append(pt)
        if len(q) > 1:
            out.append(q)
    return out

streets = json.load(open(os.path.join(GIS, 'street_centerlines.geojson')))
minor, major = [], []
for f in streets['features']:
    if not f['geometry']:
        continue
    (major if f['properties'].get('MajorRoad') in (1, 2) else minor).extend(line_coords(f['geometry']))

nb = json.load(open(os.path.join(GIS, 'neighborhoods.geojson')))
hoods = []
for f in nb['features']:
    g = f['geometry']
    polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
    rings = []
    for poly in polys:
        for ring in poly:
            rings.append([[round(x, 5), round(y, 5)] for x, y in ring])
    hoods.append({'name': f['properties']['NAME'], 'rings': rings})

data = {'asOf': '2026-11-09', 'types': [[t, group(t)] for t in types], 'tickets': tickets,
        'minor': minor, 'major': major, 'hoods': hoods}
js = 'window.TICKETS=' + json.dumps(data, separators=(',', ':'), ensure_ascii=False) + ';'
js = js.replace('</', '<\\/')  # keep descriptions from closing the <script> tag

page = open(TEMPLATE, encoding='utf-8').read().replace('/*DATA*/', js)
head, body = page.split('<header>', 1)
html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + head + '</head>\n<body>\n<header>' + body + '\n</body>\n</html>\n')
open(OUT, 'w', encoding='utf-8').write(html)

import collections
print('wrote', OUT, len(html), 'bytes')
print(collections.Counter(group(t) for t in (types[t[1]] for t in tickets)))
