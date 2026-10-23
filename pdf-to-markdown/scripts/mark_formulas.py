"""
Formula-region detector.
Finds lines in OCR text that look like broken math and marks them with a
TODO stub, so the markdown is honest about what still needs human LaTeX work.

Heuristics for "broken math" lines:
  - contains math operators (lim, ∫, ∑, dx, dy, →, ≤, ≥, ≈, √, Δ, λ, θ ...)
  - very short (< 45 chars) and dominated by symbols/digits
  - or contains latin-letter/symbol soup typical of split formulas

Usage: python mark_formulas.py <key> [outdir]
Rewrites out/<key>.md adding "> ⚠️ 公式待补" callouts.
"""
import sys, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))

MATH_HINTS = re.compile(
    r"(lim|∫|∑|∏|√|∂|∇|→|⇒|≤|≥|≠|≈|±|∞|Δ|δ|ε|λ|θ|φ|ω|Ω|α|β|γ|π|"
    r"\bdx\b|\bdy\b|\bdz\b|\bdt\b|\bf\(|\bg\(|sin|cos|tan|log|ln|exp)", re.I)
SYMS = re.compile(r"[=+\-*/^_(){}\[\]<>|\\]")

def looks_like_math(line):
    s = line.strip()
    if len(s) < 2 or len(s) > 60:
        return False
    if MATH_HINTS.search(s):
        return True
    # symbol/digit dominance with almost no CJK
    cjk = sum(1 for c in s if "\u4e00" <= c <= "\u9fff")
    sym = len(SYMS.findall(s))
    if cjk == 0 and sym >= 2 and len(s) <= 40:
        return True
    return False

def main():
    key = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "out")
    src = os.path.join(outdir, f"{key}.md")
    if not os.path.exists(src):
        print("missing", src); return
    lines = open(src, encoding="utf-8").read().split("\n")
    out, marked, i = [], 0, 0
    while i < len(lines):
        ln = lines[i]
        if looks_like_math(ln) and not ln.startswith("#") and not ln.startswith("!"):
            # gather the contiguous run
            run = []
            while i < len(lines) and lines[i].strip() and looks_like_math(lines[i]):
                run.append(lines[i]); i += 1
            marked += 1
            out.append(f"\n> ⚠️ **公式待补（OCR 无法还原，需照原页重写 LaTeX）**\n>\n> 原始识别片段：`" +
                       " / ".join(x.strip() for x in run[:6]) + "`\n")
            continue
        out.append(ln); i += 1
    dst = os.path.join(outdir, f"{key}-marked.md")
    open(dst, "w", encoding="utf-8").write("\n".join(out))
    print(f"{key}: marked {marked} formula runs -> {dst}")

if __name__ == "__main__":
    main()
