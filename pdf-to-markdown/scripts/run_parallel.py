"""
Parallel OCR driver.
Splits a book's page range into N chunks and runs them as separate processes,
so ONNX gets real multi-core throughput (intra-op threads are already used,
but separate processes scale better and avoid GIL contention).

Each worker writes raw/<key>/pages/pNNNN.txt ; reruns skip existing pages,
so this is fully resumable.

Usage: python run_parallel.py <key> <pdfpath> [workers] [chunk_size]
"""
import sys, os, subprocess, time

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = r"C:\Users\Jxcz2\.workbuddy-ai\binaries\python\envs\default\Scripts\python.exe"
WORKER = os.path.join(ROOT, "extract_book.py")

def main():
    key, pdf = sys.argv[1], sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    chunk = int(sys.argv[4]) if len(sys.argv) > 4 else 40

    import pymupdf
    d = pymupdf.open(pdf); n = d.page_count; d.close()

    outdir = os.path.join(ROOT, "raw", key)
    pagesdir = os.path.join(outdir, "pages")
    os.makedirs(pagesdir, exist_ok=True)

    todo = [i for i in range(n)
            if not (os.path.exists(os.path.join(pagesdir, f"p{i:04d}.txt"))
                    and os.path.getsize(os.path.join(pagesdir, f"p{i:04d}.txt")) > 0)]
    print(f"[{key}] total={n} remaining={len(todo)} workers={workers}", flush=True)

    # build chunks
    chunks = []
    for s in range(0, len(todo), chunk):
        grp = todo[s:s + chunk]
        chunks.append((grp[0], grp[-1] + 1))
    # interleave so each worker gets a spread of the book
    buckets = [[] for _ in range(workers)]
    for j, c in enumerate(chunks):
        buckets[j % workers].append(c)

    procs = []
    for w, b in enumerate(buckets):
        if not b:
            continue
        # contiguous merge within a bucket to reduce process count
        for (s, e) in b:
            p = subprocess.Popen([PY, "-u", WORKER, pdf,
                                  os.path.join(outdir, f"chunk{w}"), str(s), str(e)],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            procs.append(p)
    # note: each chunk writes into its own dir then we merge below
    for p in procs:
        p.wait()

    # merge chunk dirs
    for w in range(workers):
        cd = os.path.join(outdir, f"chunk{w}", "pages")
        if not os.path.isdir(cd):
            continue
        for f in os.listdir(cd):
            src = os.path.join(cd, f)
            dst = os.path.join(pagesdir, f)
            if not os.path.exists(dst):
                os.replace(src, dst)
    print(f"[{key}] done: {len(os.listdir(pagesdir))}/{n}", flush=True)

if __name__ == "__main__":
    main()
