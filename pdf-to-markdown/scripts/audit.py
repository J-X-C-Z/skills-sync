import pymupdf, os, json, re, sys

BOOKS = r"C:\Users\Jxcz2\WPS Cloud\WPSDrive\1888369756\WPS企业云盘\中山大学\我的企业文档\课本"
res = []
for name in sorted(os.listdir(BOOKS)):
    if not name.lower().endswith(".pdf"):
        continue
    p = os.path.join(BOOKS, name)
    try:
        d = pymupdf.open(p)
    except Exception as e:
        res.append({"file": name, "error": str(e)}); continue
    n = d.page_count
    tot = 0; imgp = 0; k = 0
    for i in (0, n//4, n//2, (3*n)//4, n-1):
        if not (0 <= i < n): continue
        k += 1
        pg = d[i]
        tot += len(pg.get_text("text").strip())
        if pg.get_images(full=True): imgp += 1
    res.append({"file": name[:60], "pages": n, "avg_chars": round(tot/max(k,1),1), "imgp": f"{imgp}/{k}"})
    d.close()
    print(json.dumps(res[-1], ensure_ascii=False), flush=True)
print("TOTAL_PAGES", sum(r.get("pages",0) for r in res), flush=True)
