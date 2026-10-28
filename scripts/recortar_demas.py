"""Recorta los seis iconos de demas.png y elimina el fondo exterior blanco."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'images'
source = Image.open(OUT / 'demas.png').convert('RGBA')
# Coordenadas relativas a la lámina de referencia de 1774 × 887.
boxes = {
    'buscar': (266, 33, 586, 347),
    'limpiar': (674, 19, 990, 346),
    'actualizar': (1170, 18, 1475, 352),
    'grafico': (215, 449, 590, 782),
    'salida': (730, 449, 1056, 786),
    'jornada_abierta': (1184, 430, 1534, 778),
}
for name, box in boxes.items():
    sx, sy = source.width / 1774, source.height / 887
    icon = source.crop(tuple(round(v * (sx if i % 2 == 0 else sy)) for i,v in enumerate(box)))
    # Flood fill: conserva blancos del interior de calendarios y documentos.
    exterior = Image.new('L', icon.size)
    exterior.putdata([255 if min(r,g,b) >= 233 and max(r,g,b)-min(r,g,b) < 18 else 0
                      for r,g,b,a in icon.getdata()])
    for x in range(icon.width):
        for y in (0, icon.height-1):
            if exterior.getpixel((x,y)) == 255:
                ImageDraw.floodfill(exterior, (x,y), 128)
    for y in range(icon.height):
        for x in (0, icon.width-1):
            if exterior.getpixel((x,y)) == 255:
                ImageDraw.floodfill(exterior, (x,y), 128)
    alpha = exterior.point(lambda p: 0 if p == 128 else 255)
    icon.putalpha(ImageChops.multiply(icon.getchannel('A'), alpha))
    for size, suffix in ((48,''),(24,'_24')):
        scaled=icon.copy()
        scaled.thumbnail((size-4,size-4),Image.Resampling.LANCZOS)
        canvas=Image.new('RGBA',(size,size))
        canvas.alpha_composite(scaled,((size-scaled.width)//2,(size-scaled.height)//2))
        canvas.save(OUT/f'{name}{suffix}.png')
