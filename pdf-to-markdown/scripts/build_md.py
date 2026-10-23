"""
Build a Markdown file for one book from raw/pages/*.txt, extracting figures.

- Reads raw/<key>/pages/pNNNN.txt  (text layer OR OCR text)
- Extracts non-trivial raster images from each page -> out/images/<key>/fig-pNNNN-N.png
- Filters out page-background scans (full-page single image = scanned page, skipped)
- Adds an HTML comment marker per page for traceability
Usage: python build_md.py <key> <title> <pdfpath> [outdir]
"""
import sys, os, re, io, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))

def clean(txt):
    # strip the marker line
    lines = [l for l in txt.split("\n") if not l.startswith("<!-- page=")]
    t = "\n".join(lines)
    t = t.replace("\u00ad", "")          # soft hyphen
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def extract_figures(doc, i, key, outimg, minpx=120):
    """Return list of saved figure relpaths for page i (excluding full-page scans)."""
    saved = []
    pg = doc[i]
    prect = pg.rect
    infos = pg.get_image_info(xrefs=True)
    for n, info in enumerate(infos):
        try:
            w, h = info["width"], info["height"]
        except Exception:
            continue
        # skip full-page scans / tiny decorations
        bbox = info.get("bbox")
        if bbox:
            bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
            covers = (bw * bh) / max(prect.width * prect.height, 1)
            if covers > 0.80:
                continue
            if bw < minpx/4 or bh < minpx/4:
                continue
        if w < minpx or h < minpx:
            continue
        xref = info.get("xref", 0)
        try:
            if xref:
                pix = pymupdf.Pixmap(doc, xref)
            else:
                pix = pymupdf.Pixmap(io.BytesIO(info["image"]))
        except Exception:
            continue
        if pix.n - pix.alpha >= 4:
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        fn = f"fig-p{i:04d}-{n}.png"
        fp = os.path.join(outimg, fn)
        try:
            pix.save(fp)
            saved.append(fn)
        except Exception:
            pass
    return saved

def main():
    key, title, pdfpath = sys.argv[1], sys.argv[2], sys.argv[3]
    outdir = sys.argv[4] if len(sys.argv) > 4 else os.path.join(ROOT, "out")
    pagesdir = os.path.join(ROOT, "raw", key, "pages")
    outimg = os.path.join(outdir, "images", key)
    os.makedirs(outimg, exist_ok=True)
    os.makedirs(outdir, exist_ok=True)

    files = sorted(f for f in os.listdir(pagesdir) if f.endswith(".txt"))
    doc = pymupdf.open(pdfpath)

    parts = [f"# {title}\n", f"> 源文件页数：{doc.page_count}　｜　已提取页：{len(files)}\n"]

    nimg = 0
    for f in files:
        i = int(f[1:5])
        raw = open(os.path.join(pagesdir, f), encoding="utf-8").read()
        txt = clean(raw)
        figs = extract_figures(doc, i, key, outimg)
        nimg += len(figs)
        parts.append(f"\n<!-- ===== PDF page {i} ===== -->\n")
        if txt:
            parts.append(txt + "\n")
        for fg in figs:
            parts.append(f"\n![fig](images/{key}/{fg})\n")
    doc.close()

    outmd = os.path.join(outdir, f"{key}.md")
    with open(outmd, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    print(f"{key}: pages={len(files)} figures={nimg} -> {outmd}")

if __name__ == "__main__":
    main()
