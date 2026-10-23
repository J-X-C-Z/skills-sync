"""
Visual verification: render sampled original PDF pages at 460dpi alongside the
extracted text, producing an HTML report for side-by-side human check.

Usage: python verify_html.py <key> <title> <pdfpath> [nsamples]
"""
import sys, os, base64, io, random
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))

TPL = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>视觉验收 · {title}</title>
<style>
 body{{font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;
      margin:0;padding:24px;background:#f5f6f8;color:#1c1e21;}}
 h1{{font-size:20px;margin:0 0 4px}}
 .meta{{color:#606770;font-size:13px;margin-bottom:20px}}
 .row{{background:#fff;border:1px solid #dcdfe4;border-radius:10px;
      margin-bottom:20px;overflow:hidden}}
 .hd{{padding:10px 14px;background:#eef1f5;font-weight:600;font-size:13px;
     border-bottom:1px solid #dcdfe4;display:flex;justify-content:space-between}}
 .cols{{display:grid;grid-template-columns:1fr 1fr;gap:0}}
 .col{{padding:14px;min-width:0}}
 .col+.col{{border-left:1px solid #dcdfe4}}
 .lbl{{font-size:11px;letter-spacing:.06em;text-transform:uppercase;
      color:#8a8f98;margin-bottom:8px}}
 img{{width:100%;border:1px solid #dcdfe4;border-radius:6px;display:block}}
 pre{{white-space:pre-wrap;word-break:break-word;font-size:12.5px;
     line-height:1.65;margin:0;max-height:900px;overflow:auto;
     background:#fafbfc;border:1px solid #e4e6eb;border-radius:6px;padding:10px}}
 .warn{{background:#fff4e5;border:1px solid #ffd08a;color:#8a5300;
       padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:18px}}
</style></head><body>
<h1>视觉验收 · {title}</h1>
<div class="meta">源文件 {npages} 页 ｜ 抽查 {nsamples} 页 ｜ 渲染 460 ppi ｜ 左：PDF 原页　右：抽取文本</div>
<div class="warn"><b>验收要点：</b>① 正文是否漏行/串行　② 公式是否被打散（OCR 页必然有）　③ 插图是否被抽取。
数学/物理/电路页的公式碎片属已知限制，需人工重写为 LaTeX。</div>
{rows}
</body></html>"""

ROW = """<div class="row">
 <div class="hd"><span>PDF page {i}</span><span>{mode}</span></div>
 <div class="cols">
  <div class="col"><div class="lbl">原页</div><img src="data:image/png;base64,{img}"></div>
  <div class="col"><div class="lbl">抽取文本（{nchar} 字符）</div><pre>{txt}</pre></div>
 </div></div>"""

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def main():
    key, title, pdfpath = sys.argv[1], sys.argv[2], sys.argv[3]
    ns = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    pagesdir = os.path.join(ROOT, "raw", key, "pages")
    doc = pymupdf.open(pdfpath)
    n = doc.page_count
    avail = sorted(int(f[1:5]) for f in os.listdir(pagesdir) if f.endswith(".txt"))
    # spread samples across the extracted range
    if len(avail) > ns:
        idx = [avail[int(k * (len(avail) - 1) / (ns - 1))] for k in range(ns)]
    else:
        idx = avail
    rows = []
    for i in idx:
        fp = os.path.join(pagesdir, f"p{i:04d}.txt")
        raw = open(fp, encoding="utf-8").read()
        mode = "ocr" if "mode=ocr" in raw.split("\n")[0] else "text"
        txt = "\n".join(l for l in raw.split("\n") if not l.startswith("<!--"))
        pm = doc[i].get_pixmap(dpi=110)          # light render for the report
        b64 = base64.b64encode(pm.tobytes("png")).decode()
        rows.append(ROW.format(i=i, mode=mode, img=b64,
                               txt=esc(txt.strip()[:2500]), nchar=len(txt.strip())))
    doc.close()
    html = TPL.format(title=title, npages=n, nsamples=len(idx), rows="\n".join(rows))
    out = os.path.join(ROOT, "out", f"verify-{key}.html")
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", out)

if __name__ == "__main__":
    main()
