import sys, pymupdf
from PIL import Image
import numpy as np
pdf = sys.argv[1]; pno = int(sys.argv[2])
y0f = float(sys.argv[3]); y1f = float(sys.argv[4])
x0f = float(sys.argv[5]); x1f = float(sys.argv[6])
thr = int(sys.argv[7]) if len(sys.argv)>7 else 200
scale = 3.0
doc = pymupdf.open(pdf)
pix = doc[pno].get_pixmap(matrix=pymupdf.Matrix(scale, scale))
tmp = f"out/_blk_{pno:04d}.png"; pix.save(tmp)
a = np.array(Image.open(tmp).convert("L"))
H,W = a.shape
sub = a[int(y0f*H):int(y1f*H), int(x0f*W):int(x1f*W)]
m = (sub < thr).astype(np.uint8)
print("区域像素:", sub.shape, "墨迹占比: %.3f" % m.mean())
rows = m.mean(axis=1); cols = m.mean(axis=0)
# 打印行密度（每 1% 页高）
hh = H
print("--- 行剖面 (整页分数 y : 该行墨迹占比) ---")
step = max(1, sub.shape[0]//40)
for i in range(0, sub.shape[0], step):
    yfrac = y0f + i/H
    print(f"  y={yfrac:.3f}  {'#'*int(rows[i]*60)} {rows[i]:.2f}")
print("--- 列剖面 ---")
stepc = max(1, sub.shape[1]//40)
for j in range(0, sub.shape[1], stepc):
    xfrac = x0f + j/W
    print(f"  x={xfrac:.3f}  {'#'*int(cols[j]*60)} {cols[j]:.2f}")
