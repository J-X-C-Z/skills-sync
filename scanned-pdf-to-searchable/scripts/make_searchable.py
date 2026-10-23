#!/usr/bin/env python3
"""
Convert a scanned (image-only) PDF into a searchable "sandwich" PDF.

Strategy: keep every original page image at full fidelity (so formulas / layout
stay pixel-perfect) and overlay an *invisible but selectable* text layer that
OCR produced. This is the correct approach for math / science / textbook PDFs
where formulas cannot be reliably re-typeset by OCR.

Usage:
    python make_searchable.py INPUT.pdf [OUTPUT.pdf] [--dpi 300] [--score 0.4]

Dependencies (install once in a venv):
    pip install pymupdf rapidocr-onnxruntime

Notes:
- RapidOCR pulls its model files on first run (needs internet once).
- A checkpoint full-save runs every 10 pages so a crash loses at most that batch.
- Resume: if OUTPUT already exists, processing continues from its page count.
"""
import sys, os, time, argparse
import numpy as np
import fitz  # pymupdf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--score", type=float, default=0.4, help="min OCR confidence")
    args = ap.parse_args()

    out = args.out or (os.path.splitext(args.src)[0] + "_文字版.pdf")

    # lazy import so a missing OCR engine reports a clear error
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()

    src = fitz.open(args.src)
    total = src.page_count

    if os.path.exists(out):
        out_doc = fitz.open(out)
        print(f"Resuming: {out_doc.page_count} pages already done", flush=True)
    else:
        out_doc = fitz.open()
    start = out_doc.page_count

    t_all = time.time()
    for pno in range(start, total):
        sp = src[pno]
        rect = sp.rect
        # embed the original page image at full fidelity
        op = out_doc.new_page(width=rect.width, height=rect.height)
        op.show_pdf_page(rect, src, pno)

        pix = sp.get_pixmap(dpi=args.dpi)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        result, _ = ocr(img[:, :, ::-1].copy())  # BGR for RapidOCR

        sx = pix.width / rect.width
        sy = pix.height / rect.height
        n = 0
        if result:
            for box, text, score in result:
                if float(score) < args.score or not text.strip():
                    continue
                xs = [p[0] for p in box]; ys = [p[1] for p in box]
                x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
                bx = x0 / sx
                baseline = y1 / sy
                h_pt = (y1 - y0) / sy
                w_pt = (x1 - x0) / sx
                fs = min(h_pt * 0.95, (w_pt / len(text)) * 0.98)
                if fs <= 0:
                    continue
                # render_mode=3 => text is present (selectable/searchable) but invisible
                op.insert_text((bx, baseline), text, fontsize=fs,
                               fontname="china-s", render_mode=3)
                n += 1

        if (pno - start) % 10 == 0:
            out_doc.save(out, deflate=True)
            print(f"page {pno+1}/{total} | regions={n} | "
                  f"elapsed={int(time.time()-t_all)}s", flush=True)

    out_doc.save(out, garbage=1, deflate=True)
    out_doc.close(); src.close()
    print("DONE ->", out, flush=True)


if __name__ == "__main__":
    main()
