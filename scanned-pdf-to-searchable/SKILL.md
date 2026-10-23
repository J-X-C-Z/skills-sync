---
name: scanned-pdf-to-searchable
description: Convert a scanned (image-only) PDF into a searchable "sandwich" PDF that keeps the original page images intact while adding an invisible, selectable, and Ctrl+F-searchable OCR text layer. This skill should be used when a user wants to "turn a scanned PDF into text / make a PDF searchable / 把扫描版 PDF 转成文字版 / 给 PDF 加文字层", especially for Chinese/math/science textbooks where formulas must not be re-typeset.
agent_created: true
---

# Scanned PDF → Searchable PDF (sandwich)

## Overview

Turn a scanned, image-only PDF into a PDF whose text can be selected and searched,
without sacrificing any visual fidelity. The original page images are embedded
unchanged (formulas, diagrams, layout all stay pixel-perfect) and an *invisible*
OCR text layer is overlaid on top. This is the correct approach for math/science
textbooks: general OCR cannot reliably re-typeset formulas, so re-flowing the text
into a "real" text PDF would mangle the content.

## When to use

- User says: make a scanned PDF searchable / 转成文字版 / 加文字层 / OCR the PDF.
- Source PDF has 0 extractable chars per page but contains images (scanned book,
  photocopier output, RICOH/Canon scanner producer).
- The document contains heavy math/formulas/tables where precise re-typesetting is
  impossible. **Do NOT** attempt to re-flow into a reportlab text PDF in that case.

## Workflow

### 1. Detect whether OCR is actually needed

```python
import fitz
doc = fitz.open(path)
pg = doc[0]
print(len(pg.get_text().strip()), len(pg.get_images(full=True)))
# text_chars == 0 and images >= 1  => scanned, needs OCR
```

If a text layer already exists, just re-save or skip — no OCR needed.

### 2. Set up the environment (one time)

Use the managed Python venv and install:

```
pip install pymupdf rapidocr-onnxruntime
```

`rapidocr-onnxruntime` is pure-pip (no external Tesseract binary) and supports
Chinese out of the box; model files download automatically on first run.

### 3. Run the converter

The bundled script does everything: embed original image via `show_pdf_page`,
OCR each page with RapidOCR, and overlay invisible text with `render_mode=3`.

```bash
python scripts/make_searchable.py INPUT.pdf [OUTPUT.pdf] --dpi 300 --score 0.4
```

Parameters:
- `--dpi`: OCR render resolution. 300 is a good default; lower (200) is faster
  with slightly weaker accuracy.
- `--score`: drop OCR regions below this confidence (0.4 keeps most text, filters
  garbage). RapidOCR scores are typically 0.6–0.95.

### 4. Caveats to relay to the user

- Body Chinese/Latin text becomes searchable; **formulas are captured only as
  approximate OCR glyphs** (for search, not reading) while the real formula image
  stays perfectly visible.
- Residual OCR typos (e.g. 高→商) are normal; the layer is for find/select, not
  proofreading.
- Some pages (blank/figure-only) may yield no text — that is expected.

## Key implementation details (non-obvious)

- **Invisible but selectable text:** use `page.insert_text(point, text,
  fontname="china-s", render_mode=3)`. Render mode 3 paints nothing yet keeps the
  text object in the content stream, so it is selectable/searchable.
- **Coordinate mapping:** render the page with `page.get_pixmap(dpi=DPI)` to get an
  image of size `(W,H)`; map image-pixel box → page-points with
  `sx = W/rect.width`, `sy = H/rect.height`, then `x_pt = px/sx`, `y_pt = py/sy`.
  Derive `fontsize = min(box_h*0.95, box_w/len(text)*0.98)` so the overlay aligns
  with the image text.
- **Save correctly:** `doc.save(out, incremental=True)` ONLY works on a doc opened
  FROM DISK. For an in-memory doc, always use a normal full `doc.save(out)` — do
  NOT use `incremental=True` or it raises "incremental needs original file".
  Checkpoint every N pages with a normal save for crash safety / resume.
- **Resume:** if OUTPUT exists, open it and start from `out.page_count`.
- Copy the source to a simple ASCII path first if its filename has unicode or
  parentheses — many tools mishandle such paths.

## Resources

- `scripts/make_searchable.py` — ready-to-run converter (argparse CLI).
