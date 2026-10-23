import sys, pymupdf, numpy as np
from PIL import Image
# 用法: runs.py <pdf> <pno> <y0> <y1> <x0> <x1> [axis=col|row] [thr=235] [dmin=0.004]
pdf = sys.argv[1]; pno = int(sys.argv[2])
y0, y1, x0, x1 = [float(v) for v in sys.argv[3:7]]
axis = sys.argv[7] if len(sys.argv) > 7 else "col"
thr = int(sys.argv[8]) if len(sys.argv) > 8 else 235
dmin = float(sys.argv[9]) if len(sys.argv) > 9 else 0.004
doc = pymupdf.open(pdf)
pix = doc[pno].get_pixmap(matrix=pymupdf.Matrix(3, 3))
tmp = f"out/_runs_{pno:04d}.png"; pix.save(tmp)
a = np.array(Image.open(tmp).convert("L")); H, W = a.shape
sub = a[int(y0*H):int(y1*H), int(x0*W):int(x1*W)]
m = (sub < thr).astype(np.uint8)
if axis == "col":
    v = m.mean(axis=0); base, span, lo = x0, W, 0.008
else:
    v = m.mean(axis=1); base, span, lo = y0, H, 0.005
runs = []; cur = None
for j in range(len(v)):
    if v[j] > dmin:
        if cur is None: cur = j
    else:
        if cur is not None: runs.append((cur, j-1)); cur = None
if cur is not None: runs.append((cur, len(v)-1))
out = []
for r in runs:
    p, q = base + r[0]/span, base + r[1]/span
    if out and p - out[-1][1] < lo: out[-1] = (out[-1][0], q)
    else: out.append((p, q))
print(axis, [(round(p, 4), round(q, 4)) for p, q in out])
