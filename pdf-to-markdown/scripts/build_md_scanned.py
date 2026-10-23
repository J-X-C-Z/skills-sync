"""
Rebuild a scanned book's markdown, embedding detected figures at their pages.
Reads out/images/<key>/_index.json produced by detect_figs.py
Usage: python build_md_scanned.py <key> <title> <pdf> [outdir]
"""
import sys, os, json, re
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))

def clean(raw):
    lines = [l for l in raw.split("\n") if not l.startswith("<!-- page=")]
    t = "\n".join(lines).replace("\u00ad", "")
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

# lines that are pure page furniture / stray glyphs
JUNK = re.compile(r"^[\s·。．.,、\-—_·]*$")

def main():
    key, title, pdf = sys.argv[1], sys.argv[2], sys.argv[3]
    outdir = sys.argv[4] if len(sys.argv) > 4 else os.path.join(ROOT, "out")
    pagesdir = os.path.join(ROOT, "raw", key, "pages")
    figdir = os.path.join(outdir, "images", key)
    idxfile = os.path.join(figdir, "_index.json")
    figs = {}
    if os.path.exists(idxfile):
        figs = {int(k): v for k, v in json.load(open(idxfile, encoding="utf-8")).items()}

    files = sorted(f for f in os.listdir(pagesdir) if f.endswith(".txt"))
    d = pymupdf.open(pdf)
    parts = [f"# {title}\n",
             f"> 源文件 {d.page_count} 页　｜　已转写 {len(files)} 页　｜　插图 {sum(len(v) for v in figs.values())} 张\n",
             "> ⚠️ **公式说明**：本书为扫描件，OCR 无法还原数学公式（分子分母丢失、上下标压平）。\n"
             "> 标注「公式待补」处需对照原页人工重写 LaTeX。正文与插图可直接使用。\n"]
    nfig = 0
    for f in files:
        i = int(f[1:5])
        txt = clean(open(os.path.join(pagesdir, f), encoding="utf-8").read())
        # drop pure-junk lines
        txt = "\n".join(l for l in txt.split("\n") if not JUNK.match(l))
        parts.append(f"\n<!-- ===== PDF page {i} ===== -->\n")
        # insert figures near the top of the page block (they belong to that page)
        for fn in figs.get(i, []):
            parts.append(f"\n![图 p{i}](images/{key}/{fn})\n")
            nfig += 1
        if txt:
            parts.append(txt + "\n")
    d.close()
    outmd = os.path.join(outdir, f"{key}.md")
    open(outmd, "w", encoding="utf-8").write("\n".join(parts))
    print(f"{key}: pages={len(files)} figs_embedded={nfig} -> {outmd}")

if __name__ == "__main__":
    main()
