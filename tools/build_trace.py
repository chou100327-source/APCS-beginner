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
import sys, io, json, types, ast, builtins
_payload = json.loads(sys.stdin.read())
src = _payload["src"]
sys.path.insert(0, _payload["tools"])
import explain_expr
SRC_LINES = src.split("\n")
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

_inbuf = _payload["stdin"].split("\n") if _payload["stdin"] != "" else []
_ipos = [0]
def _fake_input(prompt=""):
    if _ipos[0] >= len(_inbuf):
        raise EOFError("EOF when reading a line")
    v = _inbuf[_ipos[0]]; _ipos[0] += 1
    if cur[0] is not None:
        cur[0].setdefault("in", []).append(v)
    return v
builtins.input = _fake_input

class _Sub(ast.NodeTransformer):
    def __init__(self, env): self.env = env; self.changed = False
    def visit_Call(self, node):
        # 函式名稱本身不代入，只代入參數
        node.args = [self.visit(a) for a in node.args]
        node.keywords = [self.visit(k) for k in node.keywords]
        if isinstance(node.func, ast.Attribute):
            node.func.value = self.visit(node.func.value)
        return node
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in self.env:
            self.changed = True
            return ast.copy_location(ast.Constant(self.env[node.id]), node)
        return node

def substitute(lineno, prev_repr):
    text = explain_expr.strip_comment(SRC_LINES[lineno - 1])
    if not text: return None
    try:
        t = text[:-1] if text.endswith(":") else text
        if text.startswith(("elif ", "else")):
            t = ("if " + text[5:-1] + ": pass") if text.startswith("elif ") else None
        elif text.endswith(":"):
            t = text + " pass"
        if t is None: return None
        tree = ast.parse(t).body[0]
    except Exception:
        return None
    env = {}
    for k, r in prev_repr.items():
        try: env[k] = ast.literal_eval(r)
        except Exception: pass
    if isinstance(tree, ast.Assign): node = tree.value
    elif isinstance(tree, ast.AugAssign): node = ast.BinOp(left=ast.Name(tree.target.id, ast.Load()) if isinstance(tree.target, ast.Name) else tree.target, op=tree.op, right=tree.value)
    elif isinstance(tree, ast.Expr): node = tree.value
    elif isinstance(tree, (ast.If, ast.While)): node = tree.test
    elif isinstance(tree, ast.For): node = tree.iter
    elif isinstance(tree, ast.Return) and tree.value is not None: node = tree.value
    else: return None
    sub = _Sub(env)
    new = sub.visit(ast.parse(ast.unparse(node), mode="eval").body)
    if not sub.changed: return None
    try:
        a, b = ast.unparse(node), ast.unparse(new)
    except Exception:
        return None
    return b if a != b and len(b) <= 90 else None

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
    if "_pv" in run:
        env = {}
        prev = run.pop("_pv")
        for k, r in prev.items():
            try: env[k] = ast.literal_eval(r)
            except Exception: pass
        try:
            st = explain_expr.steps_for_line(SRC_LINES[ln - 1], env, run.get("in"))
        except Exception:
            st = []
        if st: run["x"] = st
        try:
            m, tips = explain_expr.meaning(SRC_LINES[ln - 1], prev, now, run, st)
        except Exception as e:
            m, tips = None, []
        if m: run["m"] = m
        if tips: run["w"] = tips
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
        sn = snap(frame)
        pending[frame] = (ln, run, sn)
        cur[0] = run
        try:
            sb = substitute(ln, sn)
        except Exception:
            sb = None
        if sb: run["s"] = sb
        if rec["n"] == 1: run["_pv"] = dict(sn)
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
_g = {"__name__": "__main__"}
if _payload.get("pre"):
    exec(compile(_payload["pre"], "<pre>", "exec"), _g)
try:
    exec(code, _g)
except BaseException as e:
    err = type(e).__name__ + ": " + str(e)
    # 出錯的那一行還沒 finish
finally:
    sys.settrace(None)
    sys.stdout = real_out
flush_out()
# 補上出錯行的紀錄
for _i, _l in enumerate(SRC_LINES, 1):
    _t = _l.strip()
    if _i in recs or not _t or _t.startswith("#"):
        continue
    try:
        _m, _w = explain_expr.meaning(_l, {}, {}, {}, [])
    except Exception:
        _m, _w = None, []
    _run = {"nr": 1}
    if _m: _run["m"] = _m
    if _w: _run["w"] = _w
    recs[_i] = {"n": 0, "runs": [_run]}
try:
    _en = explain_expr.error_note(err) if err else ""
except Exception:
    _en = ""
_inf = bool(err and "EVENT_CAP" in err)
if _inf:
    err = None
res = {"inf": _inf, "errNote": _en, "err": err, "errLine": lastln[0] if err else None, "lines": {}}
for ln, rec in recs.items():
    runs = rec["runs"] + ([rec["last"]] if "last" in rec else [])
    res["lines"][ln] = {"n": rec["n"], "runs": runs}
print(json.dumps(res, ensure_ascii=False))
'''

def run_block(src, stdin="", pre=""):
    try:
        r = subprocess.run([sys.executable, "-I", "-c", RUNNER], input=json.dumps({"src": src, "stdin": stdin, "pre": pre, "tools": os.path.dirname(os.path.abspath(__file__))}), capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        return None

INPUTS = [
    ('name = input()', "Alice"),
    ('n = int(input())       # 輸入 5', "5\n3.14"),
    ('# 輸入：3 5 7', "3 5 7"),
    ('# 輸入：4 8 15 16 23 42', "4 8 15 16 23 42"),
    ('# 輸入：\n# 3\n# 90', "3\n90\n85\n77"),
    ('scores = [int(input())', "3\n90\n85\n77"),
    ('n = int(input())\nnums = list(map(int, input().split()))', "4\n1 2 3 4"),
    ('import sys\n\nfor line in sys.stdin', "apple\n\nbanana"),
    ('while True:\n    try:', "apple\nbanana"),
    ('avg = total / 3', "80 91 77"),
    ('year = int(input())', "2024"),
    ('ok = a + b > c', "3 4 5"),
    ('if n > 0:\n    print("正數")', "5"),
    ('if n % 2 == 0:\n    print("偶數")', "5"),
    ('# 寫法 1：用 if-elif', "3 9 5"),
    ('"不是三角形"', "3 4 5"),
    ('y = 0\nif x > 10', "7"),
    ('km = float(input())', "2.2"),
    ('biggest = nums[0]', "4\n3 9 2 7"),
    ('is_prime = n >= 2', "17"),
    ('data = input().split()', "小明 80 91 77"),
    ('x = float(input())\nprint(int(x)', "3.5"),
]
PRE = [
    ('if ______:', 'nums = [3, 9, 2]'),
    ('print(a == b)', 'a = 7\nb = 7.0\nc = "7"'),
    ('temp = x', 'x, y = 1, 2'),
    ('if 10 / x > 1 and x != 0:', 'x = 0'),
    ('if age >= 18 and has_ticket:', 'age = 20\nhas_ticket = True'),
    ('print("及格" if score >= 60', 'score = 76\na, b = 3, 8\nx = -5'),
    ('not (a > 0 and b > 0)', 'a, b = 0, 5\nx, y = 1, 2\nage, has_ticket = 20, False'),
    ('a <= 0 or b <= 0', 'a, b = 0, 5\nx, y = 1, 2\nage, has_ticket = 20, False'),
]
def preamble(src):
    for sub, pre in PRE:
        if sub in src:
            return pre
    return ""

def sample_input(src):
    for sub, val in INPUTS:
        if sub in src:
            return val
    return None

def main():
    files = sorted(glob.glob(os.path.join(ROOT, "01-初級", "*.md")) + glob.glob(os.path.join(ROOT, "02-識讀補充", "*.md")) + glob.glob(os.path.join(ROOT, "練習", "*.md")))
    out, seen, skipped = {}, set(), 0
    for f in files:
        text = open(f, encoding="utf-8").read()
        for m in re.finditer(r"```python\n(.*?)```", text, re.S):
            src = m.group(1).rstrip("\n")
            key = fnv(src)
            if key in seen: continue
            seen.add(key)
            if "______" in src:
                skipped += 1; continue
            stdin = ""
            if re.search(r"\binput\s*\(|sys\.stdin", src):
                stdin = sample_input(src)
                if stdin is None:
                    skipped += 1; continue
            res = run_block(src, stdin, preamble(src))
            if not res or not res["lines"]:
                skipped += 1; continue
            if res["err"] and res["err"].startswith("EOFError"):
                skipped += 1; continue
            if stdin: res["stdin"] = stdin
            out[key] = res
    js = "/* 由 tools/build_trace.py 產生：教材程式碼的實際執行紀錄（請勿手改） */\nconst TRACE = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"
    open(os.path.join(ROOT, "website", "trace.js"), "w", encoding="utf-8").write(js)
    print(f"記錄 {len(out)} 段程式，略過 {skipped} 段，trace.js {len(js)//1024} KB")

main()
