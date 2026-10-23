import sys, pymupdf
from PIL import Image
pdf = sys.argv[1]; pno = int(sys.argv[2]); out = sys.argv[3]
x0f,y0f,x1f,y1f = [float(v) for v in sys.argv[4:8]]
scale = float(sys.argv[8]) if len(sys.argv) > 8 else 3.0
doc = pymupdf.open(pdf)
pix = doc[pno].get_pixmap(matrix=pymupdf.Matrix(scale, scale))
tmp = f"out/_tmp_frac_{pno:04d}.png"; pix.save(tmp)
im = Image.open(tmp).convert("RGB")
W,H = im.size
b = (int(x0f*W), int(y0f*H), int(x1f*W), int(y1f*H))
im.crop(b).save(out)
print(pno, b, im.size, "->", Image.open(out).size)
