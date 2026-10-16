"""把一行 Python 的運算式「一步一步算」寫出來（給逐行走讀用）。

steps_for_line(text, env) -> [ [式子, 結果, 說明], ... ]
  text  這一行的原始碼（單行）
  env   執行這行之前、變數目前的值 {名稱: 值}
由 build_trace.py 呼叫；全部是離線計算，不會在網站上跑。"""
import ast, math, copy

SAFE = {
    "int": int, "float": float, "str": str, "bool": bool, "len": len, "sum": sum, "max": max, "min": min,
    "abs": abs, "round": round, "divmod": divmod, "pow": pow, "bin": bin, "hex": hex, "oct": oct,
    "sorted": sorted, "list": list, "tuple": tuple, "set": set, "range": range, "type": type,
    "ord": ord, "chr": chr, "isinstance": isinstance, "format": format, "reversed": reversed,
    "enumerate": enumerate, "zip": zip, "map": map, "any": any, "all": all,
}
SAFE_METHODS = {"split", "strip", "lstrip", "rstrip", "join", "replace", "find", "upper", "lower", "count",
                "startswith", "endswith", "isdigit", "isalpha", "isupper", "islower", "index", "format", "title",
                "bit_length", "copy"}
MATH_OK = {"sqrt", "floor", "ceil", "gcd", "pi", "fabs", "pow", "log", "log2", "log10"}

FUNC_NOTE = {
    "int": "int()：轉成整數。小數是「直接捨去小數部分」（往 0 的方向），不是四捨五入；字串必須是純整數字串。",
    "float": "float()：轉成小數（浮點數）。",
    "str": "str()：轉成字串（文字）。",
    "bool": "bool()：判斷真假。0、0.0、空字串、空串列、None 是 False，其他都是 True。",
    "len": "len()：算有幾個元素（字串就是幾個字元）。",
    "sum": "sum()：把串列裡所有數字加起來。",
    "max": "max()：取最大的。",
    "min": "min()：取最小的。",
    "abs": "abs()：絕對值（去掉負號）。",
    "round": "round()：四捨五入；剛好 .5 時取最接近的偶數（銀行家捨入），所以 round(2.5) 是 2。",
    "divmod": "divmod(a, b)：一次算出（商, 餘數），等於 (a // b, a % b)。",
    "pow": "pow(a, b)：a 的 b 次方，等於 a ** b。",
    "bin": "bin()：轉成二進位字串，前面的 0b 只是「這是二進位」的標記。",
    "hex": "hex()：轉成十六進位字串。",
    "oct": "oct()：轉成八進位字串。",
    "sorted": "sorted()：回傳排好序的新串列，原本的不變。",
    "list": "list()：把東西裝成串列。",
    "type": "type()：查看這個值是什麼型態。",
    "ord": "ord()：字元對應的編碼數字。",
    "chr": "chr()：編碼數字對應的字元。",
    "range": "range()：產生一串整數（含頭不含尾）。",
    "format": "format()：依指定格式轉成字串。",
}
METHOD_NOTE = {
    "split": ".split()：依空白（或指定的字）切開，結果是串列。",
    "strip": ".strip()：去掉頭尾的空白與換行。",
    "join": "\"分隔字\".join(串列)：把串列裡的字串用分隔字接成一個字串。",
    "replace": ".replace(舊, 新)：把所有「舊」換成「新」，產生新字串。",
    "find": ".find()：找第一次出現的位置，找不到回傳 -1。",
    "upper": ".upper()：全部變大寫。", "lower": ".lower()：全部變小寫。",
    "count": ".count()：算出現幾次。",
    "bit_length": ".bit_length()：二進位要用幾位來表示。",
}

def strip_comment(text):
    """去掉行尾註解（用 tokenize，字串裡的 # 不算）"""
    import tokenize, io
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text.strip() + "\n").readline):
            if tok.type == tokenize.COMMENT:
                return text.strip()[:tok.start[1]].rstrip()
    except Exception:
        pass
    return text.strip()

class Skip(Exception):
    pass

def vrepr(v, maxlen=60):
    if callable(v) and getattr(v, "__name__", None) and not isinstance(v, range):
        return v.__name__
    if isinstance(v, float):
        r = repr(v)
    else:
        r = repr(v)
    return r if len(r) <= maxlen else r[:maxlen - 3] + "..."

def binstr(n):
    return format(n, "b") if n >= 0 else "-" + format(-n, "b")

def op_note(op, a, b, res):
    """二元運算的說明"""
    t = type(op).__name__
    num = (int, float)
    try:
        if t == "Add":
            if isinstance(a, str) and isinstance(b, str):
                return "兩段字串用 + 是「接起來」，不是加法。"
            if isinstance(a, list):
                return "串列用 + 是「接起來」。"
            return "加法。"
        if t == "Sub": return "減法。"
        if t == "Mult":
            if isinstance(a, str) or isinstance(b, str):
                return "字串乘以整數是「重複那麼多次」。"
            if isinstance(a, list) or isinstance(b, list):
                return "串列乘以整數是「重複那麼多次」。"
            return "乘法。"
        if t == "Div":
            return f"/ 是真除法，結果一定是小數（float），就算整除也是 {res}。"
        if t == "FloorDiv":
            exact = a / b
            if isinstance(exact, float) and exact != int(exact):
                return f"// 是整除（只要商）。{a} ÷ {b} = {exact:g}，往「負無窮」方向捨去，所以是 {res}。" + ("（負數時是往更小的數捨去，不是往 0 捨去！）" if res < 0 else "")
            return f"// 是整除（只要商）：{a} ÷ {b} 剛好整除，商是 {res}。"
        if t == "Mod":
            q = a // b
            return f"% 是取餘數。{a} = ({q}) × ({b}) + ({res})，所以餘數是 {res}。" + (" 餘數的正負號跟「除數」相同（Python 的規則）。" if (a < 0 or b < 0) else "")
        if t == "Pow":
            return "次方（** 是右結合：連著寫時由右往左算）。"
        if t in ("BitAnd", "BitOr", "BitXor") and isinstance(a, int) and isinstance(b, int) and a >= 0 and b >= 0:
            w = max(a.bit_length(), b.bit_length(), 1)
            sa, sb, sr = format(a, f"0{w}b"), format(b, f"0{w}b"), format(res, f"0{w}b")
            nm = {"BitAnd": "AND（兩邊都是 1 才得 1）", "BitOr": "OR（任一邊是 1 就得 1）", "BitXor": "XOR（兩邊不同才得 1）"}[t]
            return f"位元 {nm}：{a}={sa}、{b}={sb}，逐位比對 → {sr}，也就是 {res}。"
        if t == "BitAnd" and isinstance(a, int) and isinstance(b, int) and b == -a and a > 0:
            return f"n & -n 的技巧：-n 是 n 的「補數」，兩者 AND 之後只會留下 n 最低位的那個 1，所以得到 {res}。"
        if t == "LShift":
            return f"左移 {b} 位 = 乘以 2 的 {b} 次方（{a} × {2 ** b} = {res}）。"
        if t == "RShift":
            return f"右移 {b} 位 = 除以 2 的 {b} 次方再捨去（{a} // {2 ** b} = {res}）。"
    except Exception:
        return ""
    return ""

def compare_note(op, a, b, res):
    t = type(op).__name__
    nm = {"Eq": "等於", "NotEq": "不等於", "Lt": "小於", "LtE": "小於等於", "Gt": "大於", "GtE": "大於等於",
          "In": "是否在裡面", "NotIn": "是否不在裡面", "Is": "是否為同一個", "IsNot": "是否不是同一個"}.get(t, "比較")
    extra = ""
    if t == "Eq" and type(a) != type(b) and isinstance(a, (int, float)) and isinstance(b, (int, float)):
        extra = "（整數與小數只比數值，所以 7 == 7.0 是 True）"
    if t == "Eq" and type(a) != type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        extra = "（型態不同，整數和字串永遠不相等）"
    return f"比較「{nm}」→ {res}。{extra}"

class Ctx:
    def __init__(self, env, inputs=None):
        self.env = env
        self.steps = []
        self.inputs = list(inputs or [])

    def add(self, expr, val, note=""):
        e = unparse(expr)
        v = vrepr(val)
        if e == v:  # 沒有任何變化就不用列
            return
        if self.steps and self.steps[-1][0] == e and self.steps[-1][1] == v:
            return
        self.steps.append([e, v, note])

def unparse(node):
    if isinstance(node, ast.AST):
        return ast.unparse(node)
    return str(node)

def const(v):
    return ast.Constant(v) if isinstance(v, (int, float, str, bool, type(None))) else ast.Constant(v)

def lit(v):
    """把 Python 值包成語法節點（串列用 List 節點，這樣 unparse 才好看）"""
    if isinstance(v, list):
        return ast.List([lit(x) for x in v], ast.Load())
    if isinstance(v, tuple):
        return ast.Tuple([lit(x) for x in v], ast.Load())
    if callable(v) and getattr(v, "__name__", None):
        return ast.Name(v.__name__, ast.Load())
    return ast.Constant(v)

def pure_call(node):
    f = node.func
    if isinstance(f, ast.Name):
        return f.id in SAFE
    if isinstance(f, ast.Attribute):
        if isinstance(f.value, ast.Name) and f.value.id == "math":
            return f.attr in MATH_OK
        return f.attr in SAFE_METHODS
    return False

def ev(node, env):
    code = compile(ast.fix_missing_locations(ast.Expression(copy.deepcopy(node))), "<e>", "eval")
    g = {"__builtins__": SAFE, "math": math}
    g.update(env)
    return eval(code, g)

def walk(node, cx):
    """回傳這個節點的值；沿途把每個運算步驟記進 cx.steps"""
    env = cx.env
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in env:
            return env[node.id]
        if node.id in SAFE:
            return SAFE[node.id]
        raise Skip()
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        items = [walk(e, cx) for e in node.elts]
        v = items if isinstance(node, ast.List) else (tuple(items) if isinstance(node, ast.Tuple) else set(items))
        return v
    if isinstance(node, ast.UnaryOp):
        x = walk(node.operand, cx)
        new = ast.UnaryOp(node.op, lit(x))
        v = ev(new, {})
        t = type(node.op).__name__
        note = {"Not": f"not 把真假反過來：not {x!r} → {v}。" + ("（0、空字串、空串列都算假）" if not isinstance(x, bool) else ""),
                "USub": "負號。", "UAdd": "正號。",
                "Invert": f"~ 是位元 NOT，結果等於 -x-1：-({x}) - 1 = {v}。"}.get(t, "")
        cx.add(new, v, note)
        return v
    if isinstance(node, ast.BinOp):
        a = walk(node.left, cx)
        b = walk(node.right, cx)
        new = ast.BinOp(lit(a), node.op, lit(b))
        v = ev(new, {})
        cx.add(new, v, op_note(node.op, a, b, v))
        return v
    if isinstance(node, ast.BoolOp):
        isand = isinstance(node.op, ast.And)
        vals = []
        decided = None
        for i, e in enumerate(node.values):
            v = walk(e, cx)
            vals.append(v)
            if isand and not v:
                decided = (i, v); break
            if (not isand) and v:
                decided = (i, v); break
        result = decided[1] if decided else vals[-1]
        shown = ast.BoolOp(node.op, [lit(x) for x in vals])
        if len(vals) == 1:
            shown = lit(vals[0])
        if decided and decided[0] < len(node.values) - 1:
            skipped = len(node.values) - decided[0] - 1
            note = (f"{'and' if isand else 'or'} 左邊已經{'是假' if isand else '是真'}，結果就確定了，"
                    f"右邊 {skipped} 個條件<b>不會被執行</b>（短路求值）。")
        elif isand:
            note = "and：每一個都是真，所以結果是真（回傳最後一個值）。" if result else "and：只要有一個是假，結果就是假。"
        else:
            note = "or：每一個都是假，所以結果是假（回傳最後一個值）。" if not result else "or：只要有一個是真，結果就是真。"
        if len(vals) == 1:
            cx.steps.append([f"{vrepr(vals[0])} {'and' if isand else 'or'} …", vrepr(result), note])
        else:
            cx.add(shown, result, note)
        return result
    if isinstance(node, ast.Compare):
        left = walk(node.left, cx)
        cur = left
        allv = True
        parts = []
        for op, cmp in zip(node.ops, node.comparators):
            r = walk(cmp, cx)
            v = ev(ast.Compare(lit(cur), [op], [lit(r)]), {})
            parts.append((cur, op, r, v))
            cur = r
            if not v:
                allv = False
                break
        if len(parts) == 1:
            a, op, b, v = parts[0]
            cx.add(ast.Compare(lit(a), [op], [lit(b)]), v, compare_note(op, a, b, v))
        else:
            for a, op, b, v in parts:
                cx.add(ast.Compare(lit(a), [op], [lit(b)]), v, compare_note(op, a, b, v))
            cx.add(node, allv, "連鎖比較：每一段都成立，整個才成立。") if False else None
        return allv
    if isinstance(node, ast.IfExp):
        t = walk(node.test, cx)
        v = walk(node.body if t else node.orelse, cx)
        cx.steps.append([f"… if {vrepr(t)} else …", vrepr(v), f"條件是 {t}，所以取{'前面（if 左邊）' if t else 'else 後面'}的值。"])
        return v
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "input":
            if not cx.inputs:
                raise Skip()
            v = cx.inputs.pop(0)
            cx.steps.append(["input()", repr(v), "input() 從輸入讀走「一整行」，拿到的永遠是字串（就算看起來是數字）。"])
            return v
        if not pure_call(node):
            raise Skip()
        f = node.func
        if isinstance(f, ast.Attribute):
            recv = walk(f.value, cx) if not (isinstance(f.value, ast.Name) and f.value.id == "math") else None
        args = [walk(a, cx) for a in node.args]
        kws = {k.arg: walk(k.value, cx) for k in node.keywords if k.arg}
        # 重新組一個只含常數的呼叫來求值
        new_args = [lit(a) for a in args]
        new_kws = [ast.keyword(k, lit(v)) for k, v in kws.items()]
        if isinstance(f, ast.Attribute):
            func = ast.Attribute(lit(recv), f.attr, ast.Load()) if recv is not None else f
        else:
            func = f
        new = ast.Call(func, new_args, new_kws)
        v = ev(new, {})
        if isinstance(v, (map, filter, range, zip, enumerate, reversed)) and not isinstance(v, range):
            v = list(v)
        note = ""
        if isinstance(f, ast.Name):
            note = FUNC_NOTE.get(f.id, "")
            if f.id == "int" and args and isinstance(args[0], bool):
                note = f"int() 把布林轉成整數：True 變 1、False 變 0，所以 int({args[0]}) → {v}。"
            elif f.id == "int" and args and isinstance(args[0], str):
                note = f"int() 把字串 {args[0]!r} 轉成整數 {v}（字串頭尾的空白會被忽略；但有小數點或字母就會 ValueError）。"
            if f.id == "int" and args and isinstance(args[0], float):
                note = f"int() 把小數的小數部分直接砍掉（往 0 的方向）：{args[0]} → {v}。不是四捨五入。"
            if f.id == "bool":
                note = f"bool({args[0]!r})：" + ("是「空的／零」，所以是 False。" if not v else "有東西（不是零、不是空的），所以是 True。")
            if f.id == "type":
                note = "type() 查看型態：" + ("整數 int" if isinstance(args[0], int) and not isinstance(args[0], bool) else "小數 float" if isinstance(args[0], float) else "字串 str" if isinstance(args[0], str) else "布林 bool" if isinstance(args[0], bool) else "串列 list" if isinstance(args[0], list) else "") + "。"
        elif isinstance(f, ast.Attribute):
            note = METHOD_NOTE.get(f.attr, "")
            if isinstance(f.value, ast.Name) and f.value.id == "math":
                note = {"sqrt": "math.sqrt()：平方根（結果是小數）。", "floor": "math.floor()：往下取整（往負無窮）。",
                        "ceil": "math.ceil()：往上取整（往正無窮）。", "gcd": "math.gcd()：最大公因數。"}.get(f.attr, "")
        cx.add(new, v, note)
        if isinstance(v, range):
            return v
        return v
    if isinstance(node, ast.Subscript):
        base = walk(node.value, cx)
        sl = node.slice
        if isinstance(sl, ast.Slice):
            parts = [walk(x, cx) if x is not None else None for x in (sl.lower, sl.upper, sl.step)]
            idx = slice(*parts)
            v = base[idx]
            newsl = ast.Slice(*(lit(p) if p is not None else None for p in parts))
            cx.add(ast.Subscript(lit(base), newsl, ast.Load()), v, "切片 [起:止:間隔]：含起不含止。")
        else:
            i = walk(sl, cx)
            v = base[i]
            cx.add(ast.Subscript(lit(base), lit(i), ast.Load()), v, "用索引取元素：從 0 開始數，負數是從尾巴倒數。")
        return v
    if isinstance(node, ast.JoinedStr):
        out = ""
        for part in node.values:
            if isinstance(part, ast.Constant):
                out += part.value
            else:
                val = walk(part.value, cx)
                spec = ""
                if part.format_spec is not None:
                    spec = "".join(p.value for p in part.format_spec.values if isinstance(p, ast.Constant))
                s = format(val, spec) if spec else str(val)
                if part.conversion not in (-1, None):
                    s = repr(val) if part.conversion == 114 else str(val)
                note = ""
                if spec:
                    note = f"{{{unparse(part.value)}:{spec}}}：把值依格式「{spec}」轉成文字" + describe_spec(spec, val) + "。"
                else:
                    note = f"{{{unparse(part.value)}}}：把值直接轉成文字放進去。"
                cx.steps.append([f"{{{unparse(part.value)}{(':' + spec) if spec else ''}}}", repr(s), note])
                out += s
        cx.steps.append([unparse(node), repr(out), "f-string：大括號 {} 裡的東西先算出來，再塞進文字裡。"])
        return out
    if isinstance(node, (ast.ListComp, ast.GeneratorExp)):
        v = ev(node, cx.env)
        cx.add(node, list(v) if not isinstance(v, list) else v, "串列生成式：把每個元素依規則算出來，裝成一個串列。")
        return list(v) if not isinstance(v, list) else v
    if isinstance(node, ast.Starred):
        return walk(node.value, cx)
    raise Skip()

def describe_spec(spec, val):
    import re
    m = re.fullmatch(r"(?:([<>^]))?(0)?(\d+)?(?:\.(\d+))?([df%])?", spec)
    if not m: return ""
    align, zero, width, prec, kind = m.groups()
    bits = []
    if prec is not None and kind == "f":
        bits.append(f"小數點後取 {prec} 位（四捨五入）")
    if zero and width:
        bits.append(f"不足 {width} 位在前面補 0")
    elif width:
        bits.append(f"佔 {width} 格寬" + ("（靠左）" if align == "<" else "（靠右）"))
    if kind == "%":
        bits.append("以百分比表示")
    return "：" + "、".join(bits) if bits else ""

def steps_for_line(text, env, inputs=None):
    """回傳這一行的運算步驟。無法處理的寫法回傳 []。"""
    text = strip_comment(text)
    if not text or text.startswith("#"):
        return []
    try:
        t = text
        if text.endswith(":"):
            if text.startswith("elif "):
                t = "if " + text[5:] + " pass"
            elif text.startswith("else"):
                return []
            elif text.startswith(("for ", "while ", "if ", "def ", "try")):
                t = text + " pass"
        tree = ast.parse(t).body[0]
    except Exception:
        return []
    cx = Ctx(env, inputs)
    try:
        if isinstance(tree, ast.Assign):
            walk(tree.value, cx)
        elif isinstance(tree, ast.AugAssign):
            tgt = tree.target
            if isinstance(tgt, ast.Name) and tgt.id in env:
                walk(ast.BinOp(ast.Name(tgt.id, ast.Load()), tree.op, tree.value), cx)
            else:
                return []
        elif isinstance(tree, ast.Expr) and isinstance(tree.value, ast.Call) and isinstance(tree.value.func, ast.Name) and tree.value.func.id == "print":
            for a in tree.value.args:
                try:
                    walk(a, cx)
                except Skip:
                    pass
        elif isinstance(tree, ast.Expr):
            walk(tree.value, cx)
        elif isinstance(tree, (ast.If, ast.While)):
            walk(tree.test, cx)
        elif isinstance(tree, ast.For):
            walk(tree.iter, cx)
        elif isinstance(tree, ast.Return) and tree.value is not None:
            walk(tree.value, cx)
        else:
            return []
    except Skip:
        pass
    except Exception:
        return cx.steps if cx.steps else []
    return cx.steps[:10]


# ======================================================================
#  一句話白話說明（帶入真實數值）與小提醒
# ======================================================================
def _c(s):
    return "`" + str(s) + "`"

def _short(s, n=48):
    s = str(s)
    return s if len(s) <= n else s[:n - 1] + "…"

_SRC = [""]
def U(node):
    """盡量用原始碼的寫法（保留括號），取不到才用 ast.unparse"""
    try:
        seg = ast.get_source_segment(_SRC[0], node)
        if seg:
            return seg
    except Exception:
        pass
    return ast.unparse(node)

def _parse(text):
    t = strip_comment(text)
    _SRC[0] = t
    try:
        if t.endswith(":"):
            if t.startswith("elif "):
                t = "if " + t[5:] + " pass"
            elif t.startswith("else"):
                return ("else", None)
            elif t.startswith("try"):
                return ("try", None)
            elif t.startswith("finally"):
                return ("finally", None)
            elif t.startswith("except"):
                return ("except", t)
            else:
                t = t + " pass"
        _SRC[0] = t
        return ("ast", ast.parse(t).body[0])
    except Exception:
        return (None, None)

def _lit_env(d):
    out = {}
    for k, r in d.items():
        try:
            out[k] = ast.literal_eval(r)
        except Exception:
            pass
    return out

def _is_input_call(n):
    return any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "input" for x in ast.walk(n))

def _names(n):
    return {x.id for x in ast.walk(n) if isinstance(x, ast.Name)}

def meaning(text, before, after, run, steps):
    """before/after：這行執行前後的變數（repr 字串字典）。回傳 (一句話, [小提醒])。"""
    kind, tree = _parse(text)
    eb, ea = _lit_env(before), _lit_env(after)
    tips = []
    t = strip_comment(text)
    code = t
    last_val = steps[-1][1] if steps else None

    if kind == "else":
        return ("`else:` 的意思是「上面的 if / elif 都不成立時，才做這一段」。", ["else 後面不能再加條件；要加條件請用 elif。"])
    if kind == "try":
        return ("`try:` 先試著執行底下縮排的程式；如果出錯，就跳去 `except`，程式不會當掉。", [])
    if kind == "except":
        return ("`except` 只有在 try 裡面出錯時才會執行，用來「接住」錯誤，避免程式整個停下來。", [])
    if kind != "ast":
        return (None, [])
    st = tree

    # ---------- 指派 ----------
    if isinstance(st, ast.Assign):
        tgt = st.targets[0]
        val = st.value
        # 交換
        if isinstance(tgt, ast.Tuple) and isinstance(val, ast.Tuple) and len(st.targets) == 1:
            names = [U(x) for x in tgt.elts]
            if set(names) == {U(x) for x in val.elts} and names != [U(x) for x in val.elts]:
                olds = ", ".join(f"{n}={vrepr(eb.get(n))}" for n in names if n in eb)
                news = ", ".join(f"{n}={vrepr(ea.get(n))}" for n in names if n in ea)
                return (f"交換 {', '.join(_c(n) for n in names)} 的值：原本 {olds}，交換後 {news}。右邊會先整包算好，再一次存回左邊，所以不需要暫存變數。", [])

        if isinstance(tgt, ast.Tuple):
            parts = []
            for n in tgt.elts:
                nm = U(n)
                if nm in ea:
                    parts.append(f"{_c(nm)} 得到 {_c(vrepr(ea[nm]))}")
            if parts:
                if _is_input_call(val):
                    inp = run.get("in") or []
                    got = f"（這次讀到 {_c(json_s(inp[0]))}）" if inp else ""
                    src = f"從輸入讀一行{got}，切開並轉換後，依序分給左邊的變數："
                else:
                    src = f"先算右邊 {_c(_short(U(val)))}，再依序分給左邊的變數："
                tip = ["左邊變數的個數要和右邊的值一樣多，不然會出錯。"]
                if _is_input_call(val):
                    tip.append("一行有「固定幾個」數字用這種寫法；不確定幾個就改用 list(map(int, input().split()))。")
                return (f"{src}{'、'.join(parts)}。", tip)
            return (None, [])
        # 多重指派 a = b = c = 0
        if len(st.targets) > 1:
            names = [U(x) for x in st.targets]
            return (f"把 {_c(U(val))} 同時存進 {'、'.join(_c(n) for n in names)}，三個變數各自拿到一份相同的值。", [])
        if isinstance(tgt, ast.Name):
            name = tgt.id
            nv = ea.get(name)
            newtxt = _c(vrepr(nv)) if name in ea else ""
            if _is_input_call(val):
                inp = run.get("in") or []
                got = f"（這次讀到 {_c(json_s(inp[0]))}）" if inp else ""
                conv = ""
                if isinstance(val, ast.Call) and isinstance(val.func, ast.Name) and val.func.id in ("int", "float"):
                    conv = f"再用 {_c(val.func.id + '()')} 轉成{'整數' if val.func.id == 'int' else '小數'} {newtxt}，"
                elif name in ea and not isinstance(nv, str):
                    conv = f"經過處理後得到 {newtxt}，"
                else:
                    conv = f"得到 {newtxt}，"
                tip = []
                if isinstance(val, ast.Call) and isinstance(val.func, ast.Name) and val.func.id == "int":
                    tip.append("一行只能有一個數字；如果一行有好幾個數字，要改用 map(int, input().split())。")
                tip.append("input() 一次讀走「一整行」，下一次 input() 會讀下一行。")
                return (f"從輸入讀一行{got}，{conv}存進變數 {_c(name)}。", tip)
            if isinstance(val, ast.Constant):
                tip = []
                if name in ("sum", "list", "str", "max", "min", "input", "id", "type"):
                    tip.append(f"⚠ {name} 是 Python 內建函式的名字，拿來當變數名會把它蓋掉，之後就不能再呼叫 {name}()。")
                typ = {int: "整數", float: "小數", str: "字串", bool: "布林值", type(None): "None"}.get(type(val.value), "")
                return (f"建立變數 {_c(name)}，把 {_c(vrepr(val.value))}（{typ}）放進去。`=` 是「把右邊存進左邊」，不是數學上的「等於」。", tip)
            if isinstance(val, ast.List) and name in ea and isinstance(ea[name], list):
                L = ea[name]
                first = f"，{_c(name + '[0]')} 是 {_c(vrepr(L[0]))}" if L else "（空串列）"
                return (f"建立串列 {_c(name)}，裡面放 {len(L)} 個元素 {_c(vrepr(L))}。串列的位置（索引）從 0 開始數{first}。", ["串列可以放不同型態的東西，也可以之後修改。"])
            lit_all = isinstance(val, (ast.List, ast.Tuple)) or isinstance(val, ast.ListComp)
            selfref = name in _names(val)
            old = eb.get(name)
            if selfref and name in eb:
                return (f"右邊 {_c(U(val))} 用到 {_c(name)} 原本的值 {_c(vrepr(old))}，算出 {newtxt}，再存回 {_c(name)}（舊值被蓋掉）。", [])
            if isinstance(val, ast.Name) and val.id in eb:
                return (f"取出 {_c(val.id)} 目前的值 {_c(vrepr(eb[val.id]))}，複製一份存進變數 {_c(name)}（{_c(val.id)} 本身不會變）。", [])
            if steps:
                subtxt = f"（變數換成現在的值：{_c(run['s'])}）" if run.get("s") else ""
                return (f"先算右邊 {_c(_short(U(val)))}{subtxt}，結果是 {newtxt}，存進變數 {_c(name)}。算的順序和每一步的結果在下面。", [])
            return (f"把 {_c(_short(U(val)))} 的結果 {newtxt} 存進變數 {_c(name)}。", [])
        return (None, [])

    # ---------- 複合指派 ----------
    if isinstance(st, ast.AugAssign) and isinstance(st.target, ast.Name):
        name = st.target.id
        op = {"Add": "+", "Sub": "-", "Mult": "*", "Div": "/", "FloorDiv": "//", "Mod": "%", "Pow": "**",
              "BitAnd": "&", "BitOr": "|", "BitXor": "^", "LShift": "<<", "RShift": ">>"}.get(type(st.op).__name__, "?")
        rhs = U(st.value)
        rhs_p = rhs if isinstance(st.value, (ast.Name, ast.Constant)) else f"({rhs})"
        o, n = eb.get(name), ea.get(name)
        extra = ""
        if name in eb and name in ea:
            extra = f"：{_c(name)} 原本是 {_c(vrepr(o))}，運算後變成 {_c(vrepr(n))}"
        tip = []
        if op == "/":
            tip.append("/ 一定回傳小數，所以 x /= 4 之後 x 會變成 float（例如 16 變成 4.0）。")
        if op == "+":
            tip.append("Python 沒有 x++，要加 1 就寫 x += 1。")
        return (f"{_c(name + ' ' + op + '= ' + rhs)} 是 {_c(name + ' = ' + name + ' ' + op + ' ' + rhs_p)} 的縮寫{'（右邊整個先算完，才和 ' + _c(name) + ' 運算）' if rhs_p != rhs else ''}{extra}。", tip)

    # ---------- print ----------
    if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) and isinstance(st.value.func, ast.Name) and st.value.func.id == "print":
        call = st.value
        out = run.get("o")
        kw = {k.arg: k.value for k in call.keywords if k.arg}
        tip = []
        if not call.args:
            return ("印出一個空行（只印一個換行）。常用在「內層迴圈跑完後換行」。", [])
        shown = (out or "").replace("\n", "⏎") if out is not None else ""
        def argval(a):
            try:
                c2 = Ctx(eb)
                return vrepr(walk(a, c2))
            except Exception:
                return None
        pieces = []
        for a in call.args:
            if isinstance(a, ast.Starred):
                v = argval(a.value)
                pieces.append(f"{_c('*' + U(a.value))}（把串列 {_c(v) if v else ''} 拆成一個一個值）")
            elif isinstance(a, ast.Constant):
                pieces.append(f"{_c(U(a))}" + ("（文字，會原樣印出，引號不會印）" if isinstance(a.value, str) else ""))
            else:
                v = argval(a)
                pieces.append(f"{_c(_short(U(a)))}" + (f"（現在算出來是 {_c(v)}）" if v is not None else ""))
        head = "印出 " + "、".join(pieces) if len(pieces) <= 3 else f"印出 {len(pieces)} 個值：" + "、".join(pieces[:4]) + "…"
        extras = []
        if "sep" in kw:
            extras.append(f"用 {_c('sep=' + U(kw['sep']))} 當作值與值之間的分隔（預設是空白）")
        elif len(call.args) > 1 or any(isinstance(a, ast.Starred) for a in call.args):
            extras.append("值與值之間預設用一個空白隔開")
        if "end" in kw:
            ev_ = ast.literal_eval(kw["end"]) if isinstance(kw["end"], ast.Constant) else None
            extras.append(f"用 {_c('end=' + U(kw['end']))} 取代結尾的換行" + ("，所以<b>不會換行</b>，下一次 print 會接在同一行後面" if ev_ == "" or ev_ == " " else ""))
        else:
            extras.append("印完會自動換行")
        res = f"。畫面上實際看到：{_c(shown)}（⏎ 代表換行）" if out is not None and shown != "" else ""
        return (head + ("；" + "；".join(extras) if extras else "") + res + "。", tips_print(call))

    # ---------- if / while / for ----------
    if isinstance(st, ast.If):
        cond = t[3:-1].strip() if t.startswith("if ") else (t[5:-1].strip() if t.startswith("elif ") else U(st.test))
        word = "elif" if t.startswith("elif") else "if"
        verdict = run.get("_verdict")
        sub = f"，代入現在的值：{_c(run['s'])}" if run.get("s") else ""
        res = last_val
        r = f"→ 結果是 {_c(res)}" if res is not None else _truth(U(st.test), eb)
        pre = "前面的條件都不成立，才輪到這個" if word == "elif" else "檢查"
        tip = []
        if word == "if":
            tip.append("條件成立 → 執行底下縮排的程式；不成立 → 整段跳過。")
        else:
            tip.append("elif 是「由上往下、符合就停」：前面有一個成立，這個就不會被檢查。")
        return (f"{pre}條件 {_c(cond)}{sub}{(' ' + r) if r else ''}。", tip)
    if isinstance(st, ast.While):
        cond = t[6:-1].strip() if t.startswith("while ") else U(st.test)
        sub = f"，代入現在的值：{_c(run['s'])}" if run.get("s") else ""
        r = f"→ {_c(last_val)}" if last_val is not None else _truth(U(st.test), eb)
        return (f"while 迴圈：每一輪開始前先檢查 {_c(cond)}{sub} {r}。成立就執行底下縮排的程式，跑完再回到這一行檢查；不成立就結束迴圈。",
                ["迴圈裡一定要有東西讓條件最後變成不成立（例如變數一直變小），否則會變成無窮迴圈（TLE）。"])
    if isinstance(st, ast.For):
        tg = U(st.target)
        it = U(st.iter)
        vals = ""
        itv = None
        try:
            itv = walk(st.iter, Ctx(eb))
            if isinstance(itv, (range, list, tuple, str)):
                itv = list(itv)
            else:
                itv = None
        except Exception:
            itv = None
        if itv is not None:
            sh = [vrepr(x, 14) for x in itv]
            if len(sh) == 0:
                vals = f"這次 {_c(it)} 是空的，所以迴圈一次都不會執行。"
            elif len(sh) <= 8:
                vals = f"這次 {_c(tg)} 會依序拿到：{_c(', '.join(sh))}（共 {len(sh)} 輪）。"
            else:
                vals = f"這次 {_c(tg)} 會依序拿到 {_c(sh[0])}、{_c(sh[1])}、{_c(sh[2])}、…、{_c(sh[-1])}，共 {len(sh)} 輪。"
        tip = []
        if isinstance(st.iter, ast.Call) and isinstance(st.iter.func, ast.Name) and st.iter.func.id == "range":
            tip.append("range(a, b) 含頭不含尾，跑 b - a 次；要跑 1 到 n 要寫 range(1, n + 1)。")
        return (f"for 迴圈：讓 {_c(tg)} 依序拿到 {_c(_short(it))} 的每一個值，每拿一個就把底下縮排的程式跑一輪。{vals}", tip)

    # ---------- 流程控制 / 其他 ----------
    if isinstance(st, ast.Break):
        return ("`break`：立刻結束「最內層」的迴圈，直接跳到迴圈後面的程式。", ["break 只會結束最內層那一個迴圈，外層照跑。"])
    if isinstance(st, ast.Continue):
        return ("`continue`：跳過這一輪剩下的程式，直接進入下一輪。", ["在 while 裡，continue 如果放在「更新變數」之前，可能永遠卡在同一輪。"])
    if isinstance(st, ast.FunctionDef):
        args = ", ".join(a.arg for a in st.args.args)
        return (f"定義函式 {_c(st.name)}（參數：{args or '無'}）。<b>定義的時候這段不會執行</b>，要等到有人呼叫 {_c(st.name + '(…)')} 才會跑。", [])
    if isinstance(st, ast.Return):
        v = _c(_short(U(st.value))) if st.value is not None else "None"
        return (f"回傳 {v} 給呼叫它的地方，函式到這裡就結束了。", [])
    if isinstance(st, ast.Pass):
        return ("`pass`：什麼都不做，只是佔位（Python 區塊裡不能是空的）。", [])
    if isinstance(st, (ast.Import, ast.ImportFrom)):
        return ("匯入模組，之後才能用它裡面的功能（例如 math.sqrt()）。", [])
    if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) and steps:
        return (f"執行 {_c(_short(U(st.value)))}（算出 {_c(last_val)}，但結果沒有被印出來或存起來，所以畫面上看不到）。", [])
    if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call):
        return (f"呼叫 {_c(_short(U(st.value)))}，執行它裡面的程式。", [])
    if isinstance(st, ast.Expr):
        shown = f"，這次算出來是 {_c(last_val)}" if last_val is not None else ""
        return (f"單獨寫一個運算式 {_c(_short(U(st.value)))}{shown}。這樣寫不會印出任何東西，只是示範「這個條件長什麼樣子」；實際使用時通常放在 if / while 後面當條件。", [])
    return (None, [])

def json_s(x):
    import json
    return json.dumps(x, ensure_ascii=False)

def tips_print(call):
    tips = []
    ends = [k for k in call.keywords if k.arg == "end" and isinstance(k.value, ast.Constant) and k.value.value in (" ", "")]
    if ends:
        tips.append("用 end=\" \" 印一排數字，最後一個後面也會多一個空白；要避免就用 print(*串列)。")
    if any(isinstance(a, ast.Starred) for a in call.args):
        tips.append("print(*串列) 是最快的「以空白隔開印出整個串列」寫法，結尾不會多空白。")
    return tips


def _truth(cond, env):
    try:
        v = ev(ast.parse(cond, mode="eval").body, env)
    except Exception:
        return ""
    if isinstance(v, bool):
        return f"→ 結果是 {_c(v)}"
    return f"→ {_c(vrepr(v))} 算{'真' if v else '假'}（只有 0、空字串、空串列、None 才算假）"


def error_note(err):
    """常見錯誤的白話解釋"""
    if err.startswith("ValueError") and "invalid literal for int()" in err:
        return "int() 只接受「純整數」的字串。像 '3.5'（有小數點）、'abc'（有字母）、''（空的）都不行，會丟出 ValueError，程式就在這行停下來。想轉 '3.5' 要先 float('3.5') 再 int()。"
    if err.startswith("ZeroDivisionError"):
        return "除以 0 在數學上沒有意義，Python 會丟出 ZeroDivisionError。這就是為什麼要把「x != 0」檢查放在除法的前面（利用短路求值避開）。"
    if err.startswith("NameError"):
        return "用到一個還沒建立（還沒指派值）的變數名稱。變數一定要先 = 指派過，才能拿來用。"
    if err.startswith("TypeError"):
        return "型態不合：例如字串不能直接加整數、或把整數當函式呼叫。要先轉型（int() / str()）再運算。"
    if err.startswith("EOFError"):
        return "輸入已經讀完，卻又呼叫了 input()，所以出錯。"
    if err.startswith("IndexError"):
        return "索引超出範圍：串列只有 0 ~ 長度-1 這些位置。"
    return ""
