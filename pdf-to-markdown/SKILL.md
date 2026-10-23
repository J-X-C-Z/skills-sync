---
name: pdf-to-markdown
description: 把书籍/教材/扫描件 PDF 批量转成 Markdown（含插图、页码锚点、公式缺口标记），并提供左右对照的 HTML 视觉验收报告。当用户要求"把 PDF 转成 md / 转写课本 / OCR 扫描书 / 提取 PDF 文字和图片"时使用。
agent_created: true
---

# PDF → Markdown 批量转写

## 核心事实（先说清楚，避免走弯路）

**正文和插图能自动化，公式转 LaTeX 不能。** 实测 460ppi + RapidOCR：

- 中文正文识别质量很高，几乎零误差
- **公式会被彻底打散**。例：`lim(Δx→0)[f(x₀+Δx)−f(x₀)]/Δx` 的 OCR 结果是
  `lim / Ax / Ar-0-0 / f(+△)f(α)` —— 分子分母丢失、上下标压平、希腊字母错乱
- 没有任何程序能把这种碎片还原为正确 LaTeX，只能逐页看原图人工重写

所以交付时**必须明确区分**：自动抽取的正文+插图 vs 需人工补的公式。

## 关键性能数据

| 项 | 实测值 |
|---|---|
| 460ppi 渲染 + OCR | **5–6 秒/页**（纯 CPU） |
| 300 页扫描书 | 约 25–30 分钟 |
| 并行度 | **最多 2 个进程**；开 5 个会把整机压死（连 `ls` 都被杀） |
| GPU | 通常不可用，`onnxruntime` 只有 `CPUExecutionProvider` |

先查 `python -c "import onnxruntime as ort; print(ort.get_available_providers())"`。
若只有 CPU，不要指望 GPU 加速。

## 环境准备

```bash
PY=C:/Users/<user>/.workbuddy-ai/binaries/python/envs/default/Scripts/python.exe
"$PY" -m pip install pymupdf rapidocr-onnxruntime onnxruntime pillow
```

## 执行流程

### 1. 先审计，再动手

```bash
python scripts/audit.py "目录/*.pdf"
```

判断每本书**有没有文本层**（`get_text()` 返回长度）。这决定了工作量：
有文本层的几秒抽完，纯扫描的要 OCR。

### 2. 复制到本地再处理

**不要直接在云盘（WPS/OneDrive/网络盘）上跑。** 实测读 100MB 文件要几分钟，
且容易超时。先 `cp` 到工作区。

另外：**中文文件名会让 Python 报 FileNotFoundError**（编码问题）。
先改名为 ASCII，并**逐个按书名核对**，别按字母序批量重命名——
这会把书和文件错配（踩过这个坑）。

### 3. 抽取（可断点续跑）

```bash
python scripts/extract_book.py <pdf> <outdir> [start] [end]
```

每页写一个 `pages/pNNNN.txt`，首行是 `<!-- page=N mode=text|ocr -->`。
已存在的页会跳过，中断后重跑即续。

### 4. 汇总为 Markdown

```bash
python scripts/build_md.py <key> "<标题>" <pdf> [outdir]
```

- 抽插图到 `out/images/<key>/`
- **过滤整页扫描图**（面积占比 >80% 的跳过），否则每页都会插一张整页图
- 每页留 `<!-- ===== PDF page N ===== -->` 锚点便于回溯

### 5. 标记公式缺口

```bash
python scripts/mark_formulas.py <key>
```

把疑似打散的公式行替换为 `> ⚠️ 公式待补` 提示，保留原始碎片。
**不要假装公式已经转好了**——诚实标注比给出错的 LaTeX 更有价值。

### 6. 视觉验收（必做）

```bash
python scripts/verify_html.py <key> "<标题>" <pdf> 6
```

生成左右对照 HTML：左 PDF 原页，右抽取文本。这是唯一能让人快速
判断转写效果的交付形式。**必须实际打开看一遍**再交付。

## 必须用受管后台任务跑长任务

`nohup ... &` 在本类环境的工具调用之间**不存活**，OCR 会静默僵死。
必须用 `run_in_background: true` 的调用方式，或拆成前台分片跑。

## 扫描书的插图抽取（关键技巧）

扫描书**每页本身就是一整张图**，标准的"提取内嵌图片"会一无所获
（`get_image_info()` 只返回一个覆盖全页的 bbox，按面积过滤后全被排除）。

正确做法（见 `scripts/detect_figs.py`）：

1. 页面按 300dpi 渲染
2. RapidOCR 带**坐标**识别文字，把文字区域画成 mask 并膨胀
3. 从二值化墨迹图中扣掉文字区
4. 剩余连通域中面积 >3.5% 页面的即为图形 → 裁切保存

实测有效：高等数学 432 页抽出 **62 张**函数图像/几何图，裁切干净。

**已知失效场景**：图内含大量文字标注时（如体育教材的人体动作照片，
带箭头和肌肉名称），OCR 会把这些标注识别为文本，导致整张图被 mask 掉，
最终一张都抽不出。这类书需要改用「颜色/连续色调区域检测」而非「墨迹连通域」。

**性能**：约 40 秒/页（含整页 OCR），400 页约需 4.5 小时。比纯 OCR 慢得多，
排期时要单独计算。

## 公式级精修（唯一可行的路径）

自动化到此为止。要真正的 LaTeX 公式，必须**逐页人工重写**：

1. 渲染原页为图片（200 dpi 足够读清公式），**用多模态直接读图**
2. 边读边写 LaTeX：分子分母用 `\frac{}{}`，分段函数用 `\begin{cases}`，
   极限用 `\lim_{n\to\infty}`，不等号用 `\leqslant` `\geqslant`，
   数集用 `\mathbf{R}` `\mathbf{Z}`，空心邻域用 `\mathring{U}`
3. 每页留 `<!-- PDF pNN (书 pMM) -->` 锚点，便于回查
4. 用 `scripts/verify_refined.py` 生成对照页（左原页 / 右渲染后的 md，含 MathJax）

**效率参考**：一页教材（含 5–10 个公式）读图 + 重写约 2–4 分钟。
**不要承诺整本**：400 页的书 = 15–25 小时，必须分章交付、逐章验收。

### 小图漏检要手工补（两步定位法，别靠猜坐标）

`detect_figs.py` 会漏掉**细线条示意图**（数轴、区间、邻域这类），
因为面积和墨迹密度都不够。**不要凭记忆写页码/坐标**，按下面两步来：

**第 1 步：用图题 OCR 定位页码**（最关键，先定页码）

```bash
for i in $(seq -w 25 92); do f=raw/<book>/pages/p00$i.txt; [ -f "$f" ] || continue
  hit=$(grep -oE "图[^0-9]{0,3}1\.[0-9]+" "$f" | sort -u | tr '\n' ' ')
  [ -n "$hit" ] && echo "p00$i: $hit"; done
```

OCR 出的图题虽然常被切碎（`图1.17`、`图 1.16`），但**页码是准的**。

**第 2 步：墨水分块定坐标**（定 y 再定 x）

**首选 `scripts/runs.py`**（纯分数坐标，不依赖 OCR，最省事）：

```bash
P=<managed python>
# 先定 x：在图体所在的 y 带内跑 col（避开图题行、避开正文列）
$P runs.py <pdf> <pno> <y0> <y1> <x0> <x1> col    # -> 输出 x 的连续区间
# 再定 y：在图体所在的 x 带内跑 row（避开相邻正文行）
$P runs.py <pdf> <pno> <y0> <y1> <x0> <x1> row    # -> 输出 y 的连续区间
# 然后按数值区间 +3~5% 余量裁切
$P crop_frac.py <pdf> <pno> <out.png> <x0f> <y0f> <x1f> <y1f> 3.5
```

参数：`thr` 默认 235（虚线/浅色线条用 235，纯黑用 200）；`dmin` 默认 0.004，
并排两图粘连时调大（0.05）；图与图题粘连时调大 `dmin` 或缩小 x 窗口分开测。

**🔴 最重要的教训：不要靠肉眼估计裁切图里的像素位置来反推坐标。**
实测反复出现"目视估计 x 0.15–0.38，数值实测 x 0.20–0.42"这类 **30% 偏差**，
导致同一张图重裁 3–4 次。**模型看图只用来判断"内容是否完整/是否吞进正文"，
坐标一律以 `runs.py` 的数值输出为准。** 网格叠加图（gridfrac）同样会被数错格线，只作辅助。

若确实要自己写：`pm = page.get_pixmap(dpi=150)` → 二值化 → 行/列墨迹投影找连续带
（文字行约 0.02 页高，图带通常 > 0.05；图题 = 图带下方的第一条细带）。
能看图时务必肉眼复核内容完整性；**看不到图时（模型不支持图像）这套是唯一可靠手段**。

**⚠️ 页码编号坑**：`fig-p0NNN-x.png` 与 `raw/.../pNNNN.txt` 都用 **PyMuPDF 0-indexed** 页号，
而 md 里的 `<!-- PDF pNN (书 pMM) -->` 锚点也沿用了这套 0-indexed 编号。
两者混用时极易张冠李戴（本次有 8 处图引用指错页码）。
**一律以图题 OCR 的页码为准。**

## 交付前检查清单

- [ ] md 文件非空，页数与源 PDF 对得上
- [ ] `images/` 里确实有图，且不是整页扫描件
- [ ] **每个 `![](images/...)` 都指向真实存在的文件**（脚本校验一遍，见下）
- [ ] 公式缺口已标记，没有伪造的 LaTeX
- [ ] verify HTML 打开看过，抽查页正文无漏行
- [ ] 向用户说明版权：自用可以，不得分发

分次 Edit 追加内容后，收尾必做两件事（否则会留垃圾）：

```bash
grep -n "待续\|待补\|TODO" out/xxx.md        # 残留占位符
grep -n "^### " out/xxx.md | awk -F: '{print $2}' | sort | uniq -d   # 重复小节标题
python -c "import re,os;t=open('out/xxx.md',encoding='utf-8').read();\
[print('MISSING',p) for _,p in re.findall(r'!\[([^\]]*)\]\((images/[^)]+)\)',t) \
if not os.path.exists(os.path.join('out',p))]"   # 断链图片
```
