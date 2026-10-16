"""預先執行教材裡每一段 ```python 程式碼，記錄「每一行執行後各變數的值、印出了什麼」，
輸出到 website/trace.js，讓網站的「逐行走讀」能顯示真實的執行過程。

用法（在專案根目錄）：  python3 tools/build_trace.py
改了教材裡的程式碼之後要重跑一次。沒有輸入資料的程式才會被記錄（用到 input() 的略過）。"""
import glob, io, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fnv(text):
    h = 0x811c9dc5
    for b in text.encode("utf-8"):
        h ^= b
        h = (h * 0x01000193) & 0xffffffff
    return format(h, "08x")

RUNNER = r'''
import sys, io, json, types
src = sys.stdin.read()
CAP = 4000
events = 0
buf = io.StringIO()
real_out = sys.stdout
recs = {}          # lineno -> {"n": int, "runs": []}
pending = {}       # frame -> (lineno, run, prev_snapshot)
cur = [None]
lastln = [0]
last_len = [0]
SKIP = ("<listcomp>", "<genexpr>", "<dictcomp>", "<setcomp>", "<lambda>")

def snap(frame):
    d = {}
    for k, v in frame.f_locals.items():
        if k.startswith("__"): continue
        if isinstance(v, (types.ModuleType, types.FunctionType, type)): continue
        try: r = repr(v)
        except Exception: r = "?"
        d[k] = r if len(r) <= 60 else r[:57] + "..."
    return d

def flush_out():
    s = buf.getvalue()
    if len(s) > last_len[0]:
        if cur[0] is not None:
            cur[0]["o"] = cur[0].get("o", "") + s[last_len[0]:]
        last_len[0] = len(s)

def finish(frame):
    p = pending.pop(frame, None)
    if p is None: return
    ln, run, prev = p
    now = snap(frame)
    run["v"] = {k: v for k, v in now.items() if prev.get(k) != v}
    if len(now) > len(run["v"]) and len(now) <= 8:
        run["a"] = now

def tracer(frame, event, arg):
    global events
    if frame.f_code.co_filename != "<blk>" or frame.f_code.co_name in SKIP:
        return None
    events += 1
    if events > CAP:
        raise RuntimeError("EVENT_CAP")
    flush_out()
    if event == "call":
        return tracer
    if event == "line":
        prev_pending = pending.get(frame)
        finish(frame)
        # 記下上一行的「下一個執行行」，用來判斷 if / while 條件成立與否
        if prev_pending is not None:
            prev_pending[1]["nx"] = frame.f_lineno
        ln = frame.f_lineno
        lastln[0] = ln
        rec = recs.setdefault(ln, {"n": 0, "runs": []})
        rec["n"] += 1
        run = {}
        if len(rec["runs"]) < 8:
            rec["runs"].append(run)
        else:
            rec["last"] = run
        pending[frame] = (ln, run, snap(frame))
        cur[0] = run
    elif event == "return":
        pp = pending.get(frame)
        finish(frame)
        flush_out()
        cur[0] = None
    elif event == "exception":
        pass
    return tracer

err = None
code = compile(src, "<blk>", "exec")
sys.stdout = buf
sys.stdin = io.StringIO("")
sys.settrace(tracer)
try:
    exec(code, {"__name__": "__main__"})
except BaseException as e:
    err = type(e).__name__ + ": " + str(e)
    # 出錯的那一行還沒 finish
finally:
    sys.settrace(None)
    sys.stdout = real_out
flush_out()
# 補上出錯行的紀錄
res = {"err": err, "errLine": lastln[0] if err else None, "lines": {}}
for ln, rec in recs.items():
    runs = rec["runs"] + ([rec["last"]] if "last" in rec else [])
    res["lines"][ln] = {"n": rec["n"], "runs": runs}
print(json.dumps(res, ensure_ascii=False))
'''

def run_block(src):
    try:
        r = subprocess.run([sys.executable, "-I", "-c", RUNNER], input=src, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        return None

def main():
    files = sorted(glob.glob(os.path.join(ROOT, "01-初級", "*.md")) + glob.glob(os.path.join(ROOT, "練習", "*.md")))
    out, seen, skipped = {}, set(), 0
    for f in files:
        text = open(f, encoding="utf-8").read()
        for m in re.finditer(r"```python\n(.*?)```", text, re.S):
            src = m.group(1).rstrip("\n")
            key = fnv(src)
            if key in seen: continue
            seen.add(key)
            if re.search(r"\binput\s*\(|sys\.stdin", src):
                skipped += 1; continue
            res = run_block(src)
            if not res or not res["lines"]:
                skipped += 1; continue
            if res["err"] and res["err"].startswith(("EOFError", "RuntimeError: EVENT_CAP")):
                skipped += 1; continue
            out[key] = res
    js = "/* 由 tools/build_trace.py 產生：教材程式碼的實際執行紀錄（請勿手改） */\nconst TRACE = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"
    open(os.path.join(ROOT, "website", "trace.js"), "w", encoding="utf-8").write(js)
    print(f"記錄 {len(out)} 段程式，略過 {skipped} 段，trace.js {len(js)//1024} KB")

main()
