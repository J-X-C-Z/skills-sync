"""
Extract raw page text for one PDF:
  - if the page has a real text layer -> use it
  - else -> render at 460 dpi and OCR (rapidocr)
Writes one .txt per page into outdir/pages/, plus a progress file.
Usage: python extract_book.py <pdf_path> <outdir> [start] [end]
"""
import sys, os, time, json
import pymupdf, numpy as np

DPI = 460

def main():
    pdf, outdir = sys.argv[1], sys.argv[2]
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    end = int(sys.argv[4]) if len(sys.argv) > 4 else -1

    pages_dir = os.path.join(outdir, "pages")
    os.makedirs(pages_dir, exist_ok=True)

    d = pymupdf.open(pdf)
    n = d.page_count
    if end < 0 or end > n:
        end = n

    ocr = None
    t_start = time.time()
    for i in range(start, end):
        out_txt = os.path.join(pages_dir, f"p{i:04d}.txt")
        if os.path.exists(out_txt) and os.path.getsize(out_txt) > 0:
            continue
        pg = d[i]
        raw = pg.get_text("text").strip()
        mode = "text"
        if len(raw) < 40:  # scanned page
            mode = "ocr"
            if ocr is None:
                from rapidocr_onnxruntime import RapidOCR
                ocr = RapidOCR()
            pm = pg.get_pixmap(dpi=DPI)
            img = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)
            if pm.n == 4:
                img = img[:, :, :3]
            res, _ = ocr(img)
            raw = "\n".join(r[1] for r in res) if res else ""
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(f"<!-- page={i} mode={mode} -->\n{raw}\n")
        el = time.time() - t_start
        done = i - start + 1
        print(f"[{os.path.basename(outdir)}] p{i}/{end-1} {mode} "
              f"chars={len(raw)} elapsed={el:.0f}s eta={el/done*(end-start-done):.0f}s",
              flush=True)
    d.close()
    with open(os.path.join(outdir, "_RAW_DONE.json"), "w") as f:
        json.dump({"pages": n, "range": [start, end]}, f)

if __name__ == "__main__":
    main()
