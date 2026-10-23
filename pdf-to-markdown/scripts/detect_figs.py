"""
Detect FIGURES inside scanned book pages.

Every page of a scanned book is a single full-page image, so the usual
"extract embedded images" approach yields nothing useful. Instead:

  1. render page at given dpi
  2. OCR with bounding boxes  -> text regions
  3. binarize page, find large connected ink components
  4. components with substantial ink that do NOT overlap text boxes (or overlap
     only slightly) are candidate figures -> crop and save

This reliably catches: function plots, geometric diagrams, circuit diagrams,
circuit/physics illustrations, tables drawn as graphics.

Usage: python detect_figs.py <key> <pdf> [dpi] [min_ink]
"""
import sys, os, json
import numpy as np
import pymupdf
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))

def main():
    key, pdf = sys.argv[1], sys.argv[2]
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    min_ink = float(sys.argv[4]) if len(sys.argv) > 4 else 0.035

    import cv2
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()

    outimg = os.path.join(ROOT, "out", "images", key)
    os.makedirs(outimg, exist_ok=True)
    d = pymupdf.open(pdf)
    n = d.page_count
    page_figs = {}
    total = 0

    for i in range(n):
        pg = d[i]
        pm = pg.get_pixmap(dpi=dpi)
        img = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)
        if pm.n == 4:
            img = img[:, :, :3]
        g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # binary ink
        _, bw = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # text boxes via OCR
        res, _ = ocr(img)
        boxes = []
        if res:
            for r in res:
                pts = np.array(r[0], dtype=np.float32)
                boxes.append(pts)

        # dilate text boxes and mask them out
        mask = np.zeros_like(bw)
        for pts in boxes:
            cv2.fillPoly(mask, [pts.astype(np.int32)], 255)
        mask = cv2.dilate(mask, np.ones((15, 15), np.uint8), iterations=3)
        leftover = cv2.bitwise_and(bw, cv2.bitwise_not(mask))

        # find big components in the leftover (non-text) area
        cnts, _ = cv2.findContours(leftover, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        figs = []
        H, W = g.shape
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            area = w * h
            if area < (0.035 * W * H):        # too small -> noise / stray marks
                continue
            if w < 90 or h < 90:
                continue
            if area > 0.85 * W * H:           # whole page -> not a figure
                continue
            # ink density inside the box
            roi = bw[y:y+h, x:x+w]
            dens = roi.mean() / 255.0
            if dens < min_ink:
                continue
            figs.append((x, y, w, h, dens))

        # keep at most 3 largest per page
        figs.sort(key=lambda t: -(t[2] * t[3]))
        figs = figs[:3]
        names = []
        for j, (x, y, w, h, dens) in enumerate(figs):
            pad = 10
            x0, y0 = max(x-pad, 0), max(y-pad, 0)
            x1, y1 = min(x+w+pad, W), min(y+h+pad, H)
            crop = img[y0:y1, x0:x1, :3]
            fn = f"fig-p{i:04d}-{j}.png"
            Image.fromarray(crop).save(os.path.join(outimg, fn))
            names.append(fn)
            total += 1
        if names:
            page_figs[i] = names

    d.close()
    with open(os.path.join(outimg, "_index.json"), "w", encoding="utf-8") as f:
        json.dump(page_figs, f, ensure_ascii=False)
    print(f"{key}: pages_with_figs={len(page_figs)} total_figs={total}")

if __name__ == "__main__":
    main()
