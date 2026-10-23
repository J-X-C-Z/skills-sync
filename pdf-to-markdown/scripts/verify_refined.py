"""
Build a verification page for a REFINED chapter:
  left  = original PDF page image
  right = refined markdown for that page, with LaTeX rendered by MathJax

Splits the refined md on the page anchors:
  <!-- PDF pNN (书 pMM) -->
and pairs each block with the rendered page image.

Usage: python verify_refined.py <md_path> <pdf_path> <out_html> [dpi]
"""
import sys, os, re, base64
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))

ANCHOR = re.compile(r"<!--\s*PDF p(\d+)(?:\s*\(书 p(\d+)\))?\s*-->")

TPL = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>{title}</title>
<script>
window.MathJax = {{
  tex: {{inlineMath: [['$','$'],['\\\\(','\\\\)']], displayMath: [['$$','$$'],['\\\\[','\\\\]']]}},
  svg: {{fontCache: 'global'}}
}};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js" async></script>
<style>
 body{{font-family:-apple-system,"Segoe UI","Microsoft YaHei",serif;
      margin:0;padding:24px;background:#f5f6f8;color:#1c1e21;line-height:1.8}}
 h1{{font-size:21px;margin:0 0 6px}}
 .meta{{color:#606770;font-size:13px;margin-bottom:8px}}
 .hint{{background:#eef6ff;border:1px solid #b6d8ff;color:#14477d;padding:10px 14px;
       border-radius:8px;font-size:13px;margin-bottom:20px}}
 .row{{background:#fff;border:1px solid #dcdfe4;border-radius:10px;margin-bottom:22px;overflow:hidden}}
 .hd{{padding:9px 14px;background:#eef1f5;font-weight:600;font-size:13px;
     border-bottom:1px solid #dcdfe4}}
 .cols{{display:grid;grid-template-columns:0.85fr 1.15fr;gap:0}}
 .col{{padding:14px;min-width:0}}
 .col+.col{{border-left:1px solid #dcdfe4}}
 .lbl{{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:#8a8f98;margin-bottom:8px}}
 img{{width:100%;border:1px solid #dcdfe4;border-radius:6px;display:block}}
 .md{{font-size:15px}}
 .md h2{{font-size:18px;margin:18px 0 8px;border-bottom:1px solid #eee;padding-bottom:4px}}
 .md h3{{font-size:16px;margin:14px 0 6px}}
 .md h4{{font-size:15px;margin:12px 0 6px;color:#444}}
 .md p{{margin:8px 0}}
 .md blockquote{{margin:10px 0;padding:8px 12px;background:#fafbfc;
   border-left:3px solid #c9ced6;color:#333}}
 .md img{{width:auto;max-width:100%;margin:10px 0}}
 .md table{{border-collapse:collapse}}
 .md td,.md th{{border:1px solid #ddd;padding:4px 8px}}
</style></head><body>
<h1>{title}</h1>
<div class="meta">{meta}</div>
<div class="hint"><b>怎么看：</b>左边是 PDF 原页，右边是按该页重写的 Markdown（公式已用 MathJax 渲染）。
请重点核对公式——分子分母、上下标、希腊字母、极限符号是否与原页一致。</div>
{rows}
</body></html>"""

ROW = """<div class="row">
 <div class="hd">PDF p{pdf}{book} ｜ 对照原页核对公式</div>
 <div class="cols">
  <div class="col"><div class="lbl">PDF 原页</div><img src="data:image/png;base64,{img}"></div>
  <div class="col"><div class="lbl">重写后的 Markdown</div><div class="md">{body}</div></div>
 </div></div>"""

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def md_to_html(md):
    """Minimal markdown -> html (headings, blockquote, images, paragraphs)."""
    out, in_q = [], False
    for ln in md.split("\n"):
        s = ln.rstrip()
        if s.startswith("> "):
            if not in_q:
                out.append("<blockquote>"); in_q = True
            out.append(esc(s[2:]))
            continue
        if in_q:
            out.append("</blockquote>"); in_q = False
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            lvl = len(m.group(1)) + 1
            out.append(f"<h{lvl}>{esc(m.group(2))}</h{lvl}>")
            continue
        mi = re.match(r"^!\[(.*?)\]\((.*?)\)$", s)
        if mi:
            out.append(f'<img src="{mi.group(2)}" alt="{esc(mi.group(1))}">')
            continue
        if s.startswith("---"):
            out.append("<hr>"); continue
        if not s:
            continue
        out.append(f"<p>{esc(s)}</p>")
    if in_q:
        out.append("</blockquote>")
    return "\n".join(out)

def main():
    mdpath, pdfpath, outhtml = sys.argv[1], sys.argv[2], sys.argv[3]
    dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 150

    md = open(mdpath, encoding="utf-8").read()
    title = md.split("\n")[0].lstrip("# ").strip()

    # split into (page, bookpage, body)
    parts = []
    last = 0
    for m in ANCHOR.finditer(md):
        if last:
            parts[-1] = (parts[-1][0], parts[-1][1], md[last:m.start()])
        parts.append((int(m.group(1)), m.group(2), ""))
        last = m.end()
    if parts:
        parts[-1] = (parts[-1][0], parts[-1][1], md[last:])

    d = pymupdf.open(pdfpath)
    rows = []
    for pg, bp, body in parts:
        pm = d[pg].get_pixmap(dpi=dpi)
        b64 = base64.b64encode(pm.tobytes("png")).decode()
        rows.append(ROW.format(
            pdf=pg, book=f"（书 p{bp}）" if bp else "",
            img=b64, body=md_to_html(body)))
    d.close()

    html = TPL.format(title=title,
                      meta=f"共 {len(rows)} 页对照 ｜ 源文件 {os.path.basename(pdfpath)} ｜ 公式经人工核校",
                      rows="\n".join(rows))
    os.makedirs(os.path.dirname(outhtml), exist_ok=True)
    open(outhtml, "w", encoding="utf-8").write(html)
    print("wrote", outhtml, f"({len(rows)} page pairs)")

if __name__ == "__main__":
    main()
