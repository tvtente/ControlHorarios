"""Extrae los iconos de la lámina original sin sus rótulos ni fondo."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'images'
source = Image.open(OUT / 'iconos_original.png').convert('RGBA')
assert source.size == (1536, 1024), 'La lámina debe medir 1536 × 1024.'


def export(name, bounds, shape, sizes):
    mask = Image.new('L', source.size)
    draw = ImageDraw.Draw(mask)
    shape(draw)
    icon = source.copy()
    icon.putalpha(mask)
    icon = icon.crop(bounds)
    for size, filename in sizes:
        scaled = icon.copy()
        scaled.thumbnail((size - 4, size - 4), Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', (size, size))
        canvas.alpha_composite(scaled, ((size-scaled.width)//2, (size-scaled.height)//2))
        canvas.save(OUT / filename)


export('control', (56, 166, 619, 737),
       lambda d: d.rounded_rectangle((57, 167, 618, 736), radius=126, fill=255),
       [(256, 'control_horarios.png'), (64, 'control_horarios_64.png')])
export('empleado', (670, 157, 908, 439),
       lambda d: d.polygon([(673,415),(675,385),(689,359),(718,341),(747,326),
           (747,307),(732,289),(724,281),(718,263),(718,251),(722,245),
           (720,215),(726,193),(740,177),(764,163),(790,158),(821,161),
           (845,174),(858,196),(861,219),(859,244),(864,252),(860,273),
           (850,286),(837,305),(832,324),(862,339),(890,358),(901,381),
           (906,415),(898,430),(878,436),(697,437),(680,431)], fill=255),
       [(48,'empleado.png'), (24,'empleado_24.png')])
export('reloj', (935, 160, 1201, 433),
       lambda d: d.ellipse((935,160,1200,432), fill=255),
       [(48,'reloj.png'),(24,'reloj_24.png')])
def calendar(d):
    d.rounded_rectangle((1235,183,1484,425),radius=30,fill=255)
    for x in (1284,1409): d.rounded_rectangle((x,157,x+25,222),radius=12,fill=255)
export('calendario',(1235,157,1485,426),calendar,[(48,'calendario.png')])
def entrada(d):
    d.rounded_rectangle((795,538,1052,794),radius=53,fill=255)
    d.rounded_rectangle((772,654,866,694),radius=12,fill=255)
    d.polygon([(848,615),(864,612),(924,664),(925,679),(868,731),
               (852,727),(845,715),(878,676),(846,641)],fill=255)
export('entrada',(770,537,1054,795),entrada,[(48,'entrada.png'),(24,'entrada_24.png')])
def notas(d):
    d.rounded_rectangle((1136,539,1376,798),radius=42,fill=255)
    d.polygon([(1268,752),(1285,692),(1395,575),(1410,573),(1438,596),
               (1438,612),(1326,739),(1277,757)],fill=255)
export('observaciones',(1135,538,1440,800),notas,
       [(48,'observaciones.png'),(24,'observaciones_24.png')])
Image.open(OUT/'control_horarios.png').save(OUT/'control_horarios.ico',
    sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
