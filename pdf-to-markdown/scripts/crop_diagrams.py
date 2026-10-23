"""
Crop the small line-drawing diagrams that the auto-detector missed.
Coordinates are page fractions (x0,y0,x1,y1), verified by visual probe.
"""
import pymupdf, os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "images", "math")
os.makedirs(OUT, exist_ok=True)

CROPS = [
    (28, "fig-p0028-0.png", 0.255, 0.724, 0.735, 0.782),  # 图 1.1 数轴
    (30, "fig-p0030-0.png", 0.285, 0.118, 0.755, 0.198),  # 图 1.2 |a-b| 与 |x|
    (30, "fig-p0030-1.png", 0.270, 0.645, 0.740, 0.712),  # 图 1.3 邻域
]

d = pymupdf.open(os.path.join(ROOT, "src_pdf", "math.pdf"))
DPI = 400
for page, name, x0f, y0f, x1f, y1f in CROPS:
    pg = d[page]
    r = pg.rect
    clip = pymupdf.Rect(r.width*x0f, r.height*y0f, r.width*x1f, r.height*y1f)
    pm = pg.get_pixmap(dpi=DPI, clip=clip)
    fp = os.path.join(OUT, name)
    pm.save(fp)
    print(f"{name}: page={page} size={Image.open(fp).size}")
d.close()
