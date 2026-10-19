"""產生 website/quiz_extra.js：追加的觀念題（s:"exam" 是「仿歷屆題型」，s:"bank" 是一般題）。
凡是附程式碼的題目，正確答案都是真的把程式跑出來的（correct=None 時自動取輸出），不是手算。
用法：python3 tools/build_quiz_extra.py"""
import html, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = []
PROBLEMS = []

def run(code, stdin=""):
    r = subprocess.run([sys.executable, "-I", "-c", code], input=stdin, capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, (code, r.stderr)
    return r.stdout.rstrip("\n")

import re
def esc_html(t):
    """題目／選項／解說都是用 innerHTML 顯示：不是標籤的 < 要跳脫，<class 'int'> 這種也要"""
    t = t.replace("<class '", "&lt;class '").replace("'>", "'&gt;")
    return re.sub(r"<(?![a-zA-Z/]|&)", "&lt;", t)

def pre(code):
    return '<pre class="q-code">' + html.escape(code, quote=False) + "</pre>"

def add(unit, stem, _c, wrong, exp, exam=False, code=None, stdin="", t=None, **kw):
    correct = kw.get("correct", _c)
    if code is not None:
        out = run(code, stdin)
        assert "\n" not in out, ("輸出請保持單行", code)
        if correct is None:
            correct = out
        else:
            assert correct == out, ("程式輸出與正解不符", code, out, correct)
        stem = pre(code) + stem
    if correct in wrong or len(set(wrong)) != 3:
        PROBLEMS.append((stem[-60:], correct, wrong))
        return
    extra = {"t": t} if t else {}
    Q.append(dict(**extra, w="初級", u=unit, s="exam" if exam else "bank", q=esc_html(stem) if code is None else stem,
                  o=[esc_html(x) for x in [correct] + wrong], a=0, e=esc_html(exp)))

U1, U2, U3, U4, U5, U6, U7 = ("01 輸入與輸出", "02 資料型態與變數", "03 算術運算", "04 邏輯運算",
                              "05 位元運算", "06 條件判斷", "07 迴圈")

# ============================ 01 輸入與輸出 ============================
add(U1, "執行後螢幕上顯示什麼？", None, ["A B C D", "ABCD", "A B C"],
    "前兩個 print 用 end=\"\" 不換行，A、B、C 黏在一起（ABC），第 3 個 print 結尾是一個空白，所以接著 D，輸出 ABC D。",
    exam=True, code='print("A", end="")\nprint("B", end="")\nprint("C", end=" ")\nprint("D")', correct="ABC D")
add(U1, "輸入兩行：第一行 <code>10</code>、第二行 <code>3</code>。程式輸出什麼？", None, ["13", "7", "30"],
    "input() 讀進來都是字串，沒轉型就用 + 是「字串相接」，所以是 '10' + '3' = '103'。要做加法必須先 int()。",
    exam=True, code='a = input()\nb = input()\nprint(a + b)', stdin="10\n3\n", correct="103")
add(U1, "<code>print(1, 2, 3, sep=\"+\")</code> 輸出什麼？", "1+2+3", ["1 + 2 + 3", "6", "1,2,3"],
    "sep 是「值與值之間」的分隔符號，這裡被換成 +，所以印出 1+2+3；它並不會做加法。")
add(U1, "想把輸入的一行 <code>7 3</code> 分別存進整數 a、b，哪一行正確？", "<code>a, b = map(int, input().split())</code>",
    ["<code>a, b = int(input())</code>", "<code>a, b = input().split(int)</code>", "<code>a, b = map(input().split(), int)</code>"],
    "input() 讀一行 → split() 切成字串串列 → map(int, …) 逐個轉整數 → 一次指派給 a、b。map 的第一個參數是「函式」，第二個才是資料。", exam=True)
add(U1, "<code>x = 3.14159</code>，<code>print(f\"{x:.2f}\")</code> 輸出？", "3.14", ["3.1", "3.142", "3.14159"],
    ".2f 是「小數點後 2 位（四捨五入）」；寫 .3f 才會是 3.142。")
add(U1, "<code>print(f\"{5:03d}\")</code> 輸出什麼？", "005", ["5", "500", "0.5"],
    "03d：整數、總寬度 3、不足的前面補 0。時間格式 09:05 就是用 02d。")
add(U1, "下列哪個做法最容易讓判題系統判錯？", "多印了「請輸入一個整數：」這類提示文字",
    ["用 f-string 印出小數", "用 print(*nums) 印出一排數字", "最後一行印完後換行"],
    "判題是逐字比對輸出，任何多餘的提示文字都會被當成答案的一部分而判錯。", exam=True)
add(U1, "執行後螢幕上顯示什麼？", None, ["1 2 3", "123 ", "1 2 3 "],
    "end=\"\" 讓每次 print 結尾既不換行也不加空白，所以 1、2、3 黏在一起得到 123，最後那個 print() 才換行。",
    exam=True, code='for i in range(1, 4):\n    print(i, end="")\nprint()', correct="123")
add(U1, "輸入第一行 <code>3</code>，接下來三行分別是 <code>5</code>、<code>8</code>、<code>2</code>。程式輸出什麼？", None, ["8", "3", "582"],
    "n = 3 之後迴圈讀三行，累加 5 + 8 + 2 = 15。",
    code='n = int(input())\ns = 0\nfor _ in range(n):\n    s += int(input())\nprint(s)', stdin="3\n5\n8\n2\n", correct="15")
add(U1, "<code>nums = [4, 7, 1]</code>，<code>print(*nums, sep=\"-\")</code> 輸出什麼？", "4-7-1", ["[4-7-1]", "4 7 1", "4, 7, 1"],
    "星號把串列拆成一個一個值，再用 sep 當分隔符號：4-7-1，沒有中括號。")

# ============================ 02 資料型態與變數 ============================
add(U2, "執行後輸出什麼？", None, ["3 3", "5 5", "3 5"],
    "y = x 當下把 3 複製給 y；之後 x 改成 5，不會影響 y。所以印出 5 3。",
    exam=True, code='x = 3\ny = x\nx = 5\nprint(x, y)', correct="5 3")
add(U2, "<code>print(type(10 / 2))</code> 輸出？", "<class 'float'>", ["<class 'int'>", "<class 'str'>", "<class 'bool'>"],
    "/ 一律是真除法，回傳 float（5.0）；要整數商要用 //。")
add(U2, "<code>print(int(\"7\") + int(\"3\"), \"7\" + \"3\")</code> 輸出？", "10 73", ["10 10", "73 73", "73 10"],
    "int() 之後是整數相加得 10；兩個字串用 + 是接起來，得 '73'。", exam=True)
add(U2, "下列哪個轉換會發生 ValueError？", "<code>int(\"12.5\")</code>", ["<code>int(12.5)</code>", "<code>float(\"12.5\")</code>", "<code>str(12.5)</code>"],
    "int() 不接受含小數點的「字串」，但接受小數「數值」（會捨去）。要轉 '12.5' 必須先 float()。", exam=True)
add(U2, "<code>print(bool([]), bool([0]))</code> 輸出？", "False True", ["True True", "False False", "True False"],
    "空串列是 False；裡面有一個元素（就算是 0）就不是空的，所以是 True。")
add(U2, "下列哪一個是「不合法」的變數名稱？", "<code>3rd_value</code>", ["<code>_value</code>", "<code>value3</code>", "<code>Value</code>"],
    "變數名稱不能以數字開頭；其餘三個都合法（注意 Value 與 value 是不同名稱）。", exam=True)
add(U2, "<code>print(type(\"5\" * 2), \"5\" * 2)</code> 輸出？", "<class 'str'> 55", ["<class 'int'> 10", "<class 'str'> 10", "<class 'int'> 55"],
    "字串乘整數是「重複」，結果仍是字串 '55'。")
add(U2, "執行後 x 與 y 分別是？", None, ["1 2", "1 1", "2 2"],
    "x, y = y, x 會先把右邊整包算好 (2, 1) 再一次存回，所以兩個值互換。",
    code='x, y = 1, 2\nx, y = y, x\nprint(x, y)', correct="2 1")
add(U2, "<code>print(int(-2.9), int(2.9))</code> 輸出？", "-2 2", ["-3 2", "-3 3", "-2 3"],
    "int() 往 0 的方向捨去：-2.9 → -2、2.9 → 2；要往下取整才是 math.floor。")
add(U2, "執行後印出什麼？", None, ["3 5", "8 8", "3 8"],
    "第三行 a = a + b 讓 a 變成 8，b 維持 5，所以印出 8 5。",
    exam=True, code='a = 3\nb = 5\na = a + b\nprint(a, b)', correct="8 5")

# ============================ 03 算術運算 ============================
add(U3, "執行後輸出什麼？", None, ["8", "10", "12"],
    "先乘除後加減：3 * 2 = 6，再由左往右 1 + 6 = 7，7 + 2 = 9。",
    exam=True, code='print(1 + 3 * 2 + 2)', correct="9")
add(U3, "執行後輸出什麼？", None, ["17", "512", "64"],
    "** 是右結合：2 ** 3 ** 2 = 2 ** 9 = 512；再 512 // 64 = 8；最後 10 + 8 = 18。",
    exam=True, code='print(10 + 2 ** 3 ** 2 // 64)', correct="18")
add(U3, "執行後輸出什麼？", None, ["4729", "2", "22"],
    "rev = rev * 10 + 最右邊一位：9 → 92 → 927 → 9274，剛好把數字倒過來。",
    exam=True, code='n = 4729\nrev = 0\nwhile n > 0:\n    rev = rev * 10 + n % 10\n    n //= 10\nprint(rev)', correct="9274")
add(U3, "<code>print(17 // 5, 17 % 5, 17 / 5)</code> 輸出？", "3 2 3.4", ["3 2 3", "3.4 2 3", "3 3 3.4"],
    "17 = 3×5 + 2，商 3、餘 2；/ 是真除法 3.4。")
add(U3, "<code>print(-17 // 5, -17 % 5)</code> 輸出？", "-4 3", ["-3 -2", "-3 2", "-4 -3"],
    "-17 ÷ 5 = -3.4，往負無窮捨去是 -4；餘數 = -17 - (-4 × 5) = 3。")
add(U3, "<code>print(round(0.5), round(1.5), round(2.5))</code> 輸出？", "0 2 2", ["1 2 3", "0 2 3", "1 1 3"],
    "Python 的 round() 遇到剛好 .5 取最接近的偶數（銀行家捨入）：0.5 → 0、1.5 → 2、2.5 → 2。")
add(U3, "把 3725 秒換算，其中「分鐘」那一項正確的算式是？", "<code>3725 % 3600 // 60</code>", ["<code>3725 // 60</code>", "<code>3725 % 60</code>", "<code>3725 // 3600</code>"],
    "先 % 3600 去掉整小時，剩 125 秒，再 // 60 得 2 分。", exam=True)
add(U3, "下列哪一個運算的結果「型態」是 float？", "<code>8 // 2.0</code>", ["<code>8 // 2</code>", "<code>8 % 3</code>", "<code>2 ** 3</code>"],
    "只要運算中有一邊是小數，結果就是 float（8 // 2.0 = 4.0）；其他三個兩邊都是整數，結果是 int。")
add(U3, "執行後 x 是多少？", None, ["56", "25", "100"],
    "10 → 15 → 15 // 2 = 7 → 7 ** 2 = 49。",
    code='x = 10\nx += 5\nx //= 2\nx **= 2\nprint(x)', correct="49")
add(U3, "現在是星期 5（0~6 繞圈），過 10 天後的星期值最適合怎麼算？", "<code>(5 + 10) % 7</code>", ["<code>(5 + 10) // 7</code>", "<code>(5 + 10) / 7</code>", "<code>(5 + 10) ** 7</code>"],
    "取餘數可以讓數字在 0 到 6 之間循環：15 % 7 = 1。", exam=True)
add(U3, "<code>print(7 % 3 * 2, 7 % (3 * 2))</code> 輸出？", "2 1", ["14 1", "2 7", "1 1"],
    "7 % 3 * 2：% 與 * 同層由左往右，(7 % 3) * 2 = 1 * 2 = 2；7 % (3 * 2) = 7 % 6 = 1。")

# ============================ 04 邏輯運算 ============================
add(U4, "<code>print(not True or True and False)</code> 輸出？", "False", ["True", "None", "會噴錯"],
    "優先順序 not > and > or：not True = False；True and False = False；False or False = False。", exam=True)
add(U4, "<code>print(5 > 3 and 2 > 4 or 7 > 6)</code> 輸出？", "True", ["False", "5", "會噴錯"],
    "and 先算：True and False = False；再 False or True = True。", exam=True)
add(U4, "下列哪一個與 <code>not (x > 3 or y < 5)</code> 等價？", "<code>x <= 3 and y >= 5</code>", ["<code>x <= 3 or y >= 5</code>", "<code>x < 3 and y > 5</code>", "<code>x > 3 and y < 5</code>"],
    "笛摩根：not (A or B) = (not A) and (not B)；> 的相反是 <=，< 的相反是 >=。", exam=True)
add(U4, "執行後輸出什麼？", None, ["yes", "會噴錯（除以 0）", "什麼都不印"],
    "x != 0 為 False，and 短路，右邊的 10 / x 不會被執行，所以不會除以 0，走 else 印出 no。",
    exam=True, code='x = 0\nif x != 0 and 10 / x > 1:\n    print("yes")\nelse:\n    print("no")', correct="no")
add(U4, "<code>print(0 or \"\" or [] or 5)</code> 輸出？", "5", ["0", "True", "[]"],
    "or 回傳第一個為真的值；前面的 0、空字串、空串列都是假，所以是 5。")
add(U4, "<code>print(3 and 0 and 5)</code> 輸出？", "0", ["3", "5", "False"],
    "and 遇到第一個為假的值就回傳它：3 為真繼續；0 為假，回傳 0。")
add(U4, "下列哪個值放進 <code>if</code> 判斷會被當成「真」？", "<code>\"0\"</code>", ["<code>0.0</code>", "<code>\"\"</code>", "<code>None</code>"],
    "字串 \"0\" 有一個字元，不是空字串，所以是真；0.0、空字串、None 都是假。", exam=True)
add(U4, "判斷 y 是閏年的條件，下列何者正確？", "<code>y % 4 == 0 and y % 100 != 0 or y % 400 == 0</code>",
    ["<code>y % 4 == 0 and y % 100 == 0 or y % 400 == 0</code>", "<code>y % 4 == 0 or y % 100 != 0 and y % 400 == 0</code>", "<code>y % 400 == 0 and y % 4 == 0 and y % 100 != 0</code>"],
    "四年一閏、逢百不閏、逢四百又閏。and 先於 or，所以前兩個條件先綁在一起，再 or 上 y % 400 == 0。", exam=True)
add(U4, "<code>print(1 < 5 < 3)</code> 輸出？", "False", ["True", "5", "會噴錯"],
    "連鎖比較等同 1 < 5 and 5 < 3，後半為假，結果是 False。")
add(U4, "下列敘述何者「錯誤」？", "<code>and</code> 與 <code>&</code> 完全相同，可以互換", ["<code>or</code> 在左邊為真時，右邊不會被執行", "<code>not</code> 的優先順序高於 <code>and</code>", "<code>==</code> 是比較，<code>=</code> 是指定"],
    "and 是邏輯運算（對真假值），& 是位元運算（對每個 bit）：12 and 10 是 10，12 & 10 是 8。", exam=True)
add(U4, "<code>a = 5</code>、<code>b = 0</code>，下列哪個運算式會出錯？", "<code>a / b > 1 and b != 0</code>", ["<code>b != 0 and a / b > 1</code>", "<code>b == 0 or a / b > 1</code>", "<code>b != 0 and 1 / b</code>"],
    "第一個先算 a / b，b 是 0 就除以零；其餘三個都靠短路求值避開了除法。", exam=True)

# ============================ 05 位元運算 ============================
add(U5, "執行後輸出什麼？", None, ["14", "6", "12"],
    "12 = 1100、10 = 1010；AND 只有兩邊都是 1 的位才得 1：1000 = 8。",
    exam=True, code='print(12 & 10)', correct="8")
add(U5, "<code>print(13 | 6, 13 ^ 6)</code> 輸出？", "15 11", ["15 15", "7 11", "4 15"],
    "13 = 1101、6 = 0110；OR = 1111 = 15；XOR（不同才 1）= 1011 = 11。", exam=True)
add(U5, "<code>print(1 << 5, 64 >> 3)</code> 輸出？", "32 8", ["5 3", "32 21", "6 8"],
    "左移 5 位 = ×32；右移 3 位 = 64 ÷ 8 = 8。")
add(U5, "十進位的 100 轉成二進位是？", "1100100", ["1100010", "1001100", "110010"],
    "100 = 64 + 32 + 4 → 位權 64 32 16 8 4 2 1 對應 1 1 0 0 1 0 0。", exam=True)
add(U5, "二進位 <code>101101</code> 轉成十進位是？", "45", ["43", "41", "53"],
    "32 + 8 + 4 + 1 = 45。", exam=True)
add(U5, "下列哪個整數「不是」2 的次方？", "96", ["64", "128", "1"],
    "96 = 1100000 有兩個 1；2 的次方只有一個位元是 1。用 n & (n - 1) 判斷：96 & 95 = 64 ≠ 0。")
add(U5, "要把 flags 的第 2 個位元「切換」（0 變 1、1 變 0），該怎麼寫？", "<code>flags ^= (1 << 2)</code>", ["<code>flags |= (1 << 2)</code>", "<code>flags &= ~(1 << 2)</code>", "<code>flags &= (1 << 2)</code>"],
    "XOR 1 會切換該位；OR 1 是打開、AND ~mask 是關閉。", exam=True)
add(U5, "執行後輸出什麼？", None, ["0", "34", "9"],
    "成對的 6 與 9 互相抵銷（x ^ x = 0），剩下落單的 4。",
    exam=True, code='r = 0\nfor x in [6, 9, 6, 4, 9]:\n    r ^= x\nprint(r)', correct="4")
add(U5, "<code>print(~7, ~-8)</code> 輸出？", "-8 7", ["-7 8", "8 -7", "-8 -7"],
    "~x = -x - 1：~7 = -8；~(-8) = 8 - 1 = 7。")
add(U5, "<code>print(25 & 1, 26 & 1)</code> 輸出？", "1 0", ["0 1", "1 1", "0 0"],
    "n & 1 取最低位：奇數是 1、偶數是 0。")
add(U5, "<code>bin(10).count(\"1\")</code> 的結果是？", "2", ["4", "1", "3"],
    "bin(10) = '0b1010'，裡面有 2 個 '1'。")
add(U5, "<code>a = 0b1100</code>，執行 <code>a &= ~(1 << 2)</code> 之後，a 是多少？", "8", ["12", "4", "0"],
    "1 << 2 = 0100，取反後是 …1011；1100 AND 1011 = 1000 = 8。第 2 位被關掉了。", exam=True)

# ============================ 06 條件判斷 ============================
add(U6, "s = 85，執行後輸出什麼？", None, ["B", "C", "什麼都不印"],
    "elif 由上往下、符合就停：85 >= 60 一進來就成立，印出 A，後面全部跳過（條件順序寫反的經典錯誤）。",
    exam=True, code='s = 85\nif s >= 60:\n    print("A")\nelif s >= 80:\n    print("B")\nelse:\n    print("C")', correct="A")
add(U6, "x = 8，執行後輸出什麼？", None, ["a", "b", "什麼都不印"],
    "兩個獨立的 if 都成立，所以兩個 print 都會執行；end=\" \" 讓它們印在同一行：a b。",
    exam=True, code='x = 8\nif x > 5:\n    print("a", end=" ")\nif x > 7:\n    print("b", end=" ")', correct="a b ")
add(U6, "x = 8，把上一題的第二個 <code>if</code> 改成 <code>elif</code>，輸出會變成？", "a", ["a b", "b", "什麼都不印"],
    "if / elif 是同一組擇一，第一個條件成立後 elif 不會被檢查，只印 a。", exam=True)
add(U6, "下列哪一行有語法錯誤？", "<code>if x > 3 print(x)</code>", ["<code>if x > 3: print(x)</code>", "<code>y = 1 if x > 3 else 0</code>", "<code>if 3 < x < 10:</code>"],
    "if 的條件後面要有冒號 :。其餘三個都合法（單行 if、三元運算式、連鎖比較）。", exam=True)
add(U6, "三邊 3、4、5，依序判斷「不是三角形」「正三角形」「等腰」「直角」「一般」，輸出是？", "直角三角形", ["一般三角形", "等腰三角形", "不是三角形"],
    "能構成三角形、三邊不全等、也沒有兩邊相等；3² + 4² = 5²，所以是直角三角形。")
add(U6, "三個數 a、b、c 要找最大值，擂台法的正確做法是？", "先令 m = a，再依序拿 b、c 與 m 比，更大就換人", ["先令 m = 0，再依序比較", "先把三個數相加", "先排序再取中間"],
    "m = 0 在全是負數時會錯；以第一個數當初始擂主最安全。")
add(U6, "n = 0，執行後輸出什麼？", None, ["正數", "負數", "什麼都不印"],
    "n > 0、n < 0 都不成立，走最後的 else，印出「零」。",
    exam=True, code='n = 0\nif n > 0:\n    print("正數")\nelif n < 0:\n    print("負數")\nelse:\n    print("零")', correct="零")
add(U6, "<code>print(\"及格\" if 59 >= 60 else \"不及格\")</code> 輸出？", "不及格", ["及格", "True", "False"],
    "三元運算式：條件不成立就取 else 後面的值。")
add(U6, "x = 4，執行後 y 是多少？", None, ["1", "3", "4"],
    "第一組 if（x > 10）不成立，y 仍是 0；第二組 if / elif 中 x > 3 成立，y 加 2，後面的 elif 就被跳過了。",
    exam=True, code='x = 4\ny = 0\nif x > 10:\n    y += 1\nif x > 3:\n    y += 2\nelif x > 0:\n    y += 3\nprint(y)', correct="2")
add(U6, "下列敘述何者「正確」？", "Python 靠縮排決定程式區塊的範圍", ["Python 用大括號 {} 表示區塊", "else 後面一定要接條件", "elif 可以出現在 if 的前面"],
    "縮排錯誤會造成 IndentationError 或邏輯跑掉；else 不能加條件；elif 必須接在 if 之後。", exam=True)

# ============================ 07 迴圈 ============================
add(U7, "執行後輸出什麼？", None, ["2 4 6 ", "1 2 3 4 5 6 ", "1 3 5"],
    "continue 會跳過偶數；只有奇數 1、3、5 被印出（每個後面有一個空白）。",
    exam=True, code='for i in range(1, 7):\n    if i % 2 == 0:\n        continue\n    print(i, end=" ")', correct="1 3 5 ")
add(U7, "執行後輸出什麼？", None, ["10", "21", "5"],
    "range(1, 6) 是 1 到 5，加總 15。",
    exam=True, code='t = 0\nfor i in range(1, 6):\n    t += i\nprint(t)', correct="15")
add(U7, "執行後輸出什麼？", None, ["1 2 3 4 ", "1 2 ", "4 "],
    "i = 4 時 break，整個迴圈結束；前面印了 1、2、3。",
    exam=True, code='for i in range(1, 10):\n    if i == 4:\n        break\n    print(i, end=" ")', correct="1 2 3 ")
add(U7, "執行後輸出什麼？", None, ["16", "4", "6"],
    "內層次數依序是 1、2、3、4，總共 10 次；內層次數跟著外層變，不能直接相乘。",
    exam=True, code='c = 0\nfor i in range(1, 5):\n    for j in range(i):\n        c += 1\nprint(c)', correct="10")
add(U7, "執行後輸出什麼？", None, ["7", "4", "3"],
    "外層 3 次 × 內層 4 次 = 12 次。",
    exam=True, code='c = 0\nfor i in range(3):\n    for j in range(4):\n        c += 1\nprint(c)', correct="12")
add(U7, "<code>list(range(10, 0, -3))</code> 的結果是？", "[10, 7, 4, 1]", ["[10, 7, 4, 1, -2]", "[9, 6, 3]", "[10, 7, 4]"],
    "從 10 每次減 3：10、7、4、1，下一個 -2 已經不大於終點 0，所以停止。")
add(U7, "要走過 1 到 n（含 n），下列哪個 range 正確？", "<code>range(1, n + 1)</code>", ["<code>range(1, n)</code>", "<code>range(n)</code>", "<code>range(0, n + 1)</code>"],
    "range 含頭不含尾，所以終點要寫 n + 1。", exam=True)
add(U7, "下列哪一段程式會變成無窮迴圈？", "<code>n = 5</code>，<code>while n > 0:</code>，裡面只有 <code>print(n)</code>", ["<code>n = 5</code>，<code>while n > 0:</code>，裡面有 <code>n -= 1</code>", "<code>for i in range(5): print(i)</code>", "<code>n = 1</code>，<code>while n < 100:</code>，裡面有 <code>n *= 2</code>"],
    "第一段的 n 永遠不變，條件 n > 0 永遠成立。其餘三個的條件都會在有限輪之後變假。", exam=True)
add(U7, "求 1×2×3×4×5，連乘的累積變數一開始應設成？", "1", ["0", "-1", "5"],
    "連乘的初始值是 1；設成 0 的話，乘什麼都是 0。")
add(U7, "迴圈 <code>for…else</code> 中，<code>else</code> 何時執行？", "迴圈完整跑完、沒有被 break 時", ["迴圈被 break 時", "迴圈一次都沒有跑時才會", "每一輪結束時"],
    "常用在「找遍了都沒找到」。只要中途 break，else 就不會執行。", exam=True)
add(U7, "執行後輸出什麼？", None, ["12", "48", "72"],
    "輾轉相除法求 72 與 48 的最大公因數：(72, 48) → (48, 24) → (24, 0)，答案 24。",
    exam=True, code='a, b = 72, 48\nwhile b != 0:\n    a, b = b, a % b\nprint(a)', correct="24")
add(U7, "判斷整數 n 是不是質數，檢查因數時迴圈只需要檢查到？", "<code>√n</code>（<code>int(n ** 0.5)</code>）", ["<code>n</code>", "<code>n - 1</code>", "<code>n // 2 + 10</code>"],
    "若 n 有大於 √n 的因數，必然同時有小於 √n 的對應因數，所以檢查到 √n 就夠，可大幅減少次數。", exam=True)
add(U7, "執行後輸出什麼？", None, ["0 1 2 ", "1 2 3 ", "3 "],
    "n 從 3 開始每輪減 1，印出 3、2、1，n 變成 0 時條件 n > 0 不成立，迴圈結束。",
    exam=True, code='n = 3\nwhile n > 0:\n    print(n, end=" ")\n    n -= 1', correct="3 2 1 ")
add(U7, "執行後 total 是多少？", None, ["12", "15", "9"],
    "i 從 1 開始；i = 3 時加 3；i = 5 時 break，迴圈直接結束，6 根本沒機會被加，所以 total 是 3。",
    exam=True, code='total = 0\nfor i in range(1, 7):\n    if i == 5:\n        break\n    if i % 3 == 0:\n        total += i\nprint(total)', correct="3")


# ============================ 識讀補充 08~15 ============================
U8, U9, U10, U11, U12, U13, U14, U15 = ("08 一維陣列與串列", "09 函式", "10 識讀題型技巧", "11 時間複雜度",
                                      "12 遞迴", "13 排序演算法", "14 搜尋演算法", "15 堆疊與佇列")
# ---- 08 陣列 ----
add(U8, "執行後輸出什麼？", None, ["[1, 2, 3, 4]", "[3, 4, 5]", "[1, 2, 3]"],
    "a[1:4] 取索引 1、2、3，對應 2、3、4（含頭不含尾）。", exam=True, t="追蹤",
    code='a = [1, 2, 3, 4, 5]\nprint(a[1:4])', correct="[2, 3, 4]")
add(U8, "執行後輸出什麼？", None, ["[3, 1, 2]", "[1, 2, 3]", "會噴錯"],
    "sort() 原地排序但回傳 None，把 None 指派回 a，a 就成了 None。", exam=True, t="追蹤",
    code='a = [3, 1, 2]\na = a.sort()\nprint(a)', correct="None")
add(U8, "執行後輸出什麼？", None, ["[1, 2, 3]", "[9, 2, 3] [1, 2, 3]", "[1, 2, 3] [9, 2, 3]"],
    "b = a 沒有複製，兩個名字指向同一個串列，改 b[0] 等於改 a[0]，所以兩個都是 [9, 2, 3]。", exam=True, t="追蹤",
    code='a = [1, 2, 3]\nb = a\nb[0] = 9\nprint(a, b)', correct="[9, 2, 3] [9, 2, 3]")
add(U8, "執行後輸出什麼？", None, ["[4, 2, 0]", "[5, 4, 3]", "[0, 2, 4]"],
    "step = -2 從最後一個往前每隔一個：索引 5、3、1 對應 5、3、1。", t="追蹤",
    code='a = [0, 1, 2, 3, 4, 5]\nprint(a[::-2])', correct="[5, 3, 1]")
add(U8, "下列程式的功能是「把串列元素加總」，空格應填入？", "<code>total += x</code>", ["<code>total = x</code>", "<code>total -= x</code>", "<code>x += total</code>"],
    "累加要把每個元素加進 total：total += x。total = x 只會留下最後一個；x += total 改的是迴圈變數。\n（程式：total = 0；for x in nums: ____ ）".replace("\n", " "),
    exam=True, t="填空")
add(U8, "想複製串列 a 成為獨立的 b（改 b 不影響 a），下列哪個「不正確」？", "<code>b = a</code>", ["<code>b = a[:]</code>", "<code>b = a.copy()</code>", "<code>b = list(a)</code>"],
    "b = a 只是多一個名字；其他三種都會建立新串列。", exam=True, t="除錯")
add(U8, "<code>a = [4, 9, 2]</code>，執行 <code>for x in a: x = x * 2</code> 之後，<code>a</code> 是？", "[4, 9, 2]", ["[8, 18, 4]", "[8, 9, 2]", "[4, 9, 4]"],
    "x 只是複製出來的值，改 x 不會改到串列；要改串列必須用索引 a[i] = a[i] * 2。", exam=True, t="除錯")
add(U8, "建立 2 列 3 行、全為 0 的二維串列，並只把第 0 列第 1 行設為 5，下列哪個寫法的結果是 <code>[[0, 5, 0], [0, 0, 0]]</code>？", "<code>g = [[0] * 3 for _ in range(2)]</code>，再 <code>g[0][1] = 5</code>", ["<code>g = [[0] * 3] * 2</code>，再 <code>g[0][1] = 5</code>", "<code>g = [0] * 6</code>，再 <code>g[0][1] = 5</code>", "<code>g = [[0] * 2 for _ in range(3)]</code>，再 <code>g[0][1] = 5</code>"],
    "[[0]*3]*2 的兩列是同一個串列，改一格兩列都變；生成式讓每列獨立。", exam=True, t="除錯")
add(U8, "執行後輸出什麼？", None, ["[4, 9, 2, 7]", "[7, 4, 9, 2]", "[4, 9, 7, 2]"],
    "insert(1, 7) 在索引 1 放入 7：[4, 7, 9, 2]。", t="追蹤",
    code='a = [4, 9, 2]\na.insert(1, 7)\nprint(a)', correct="[4, 7, 9, 2]")

# ---- 09 函式 ----
add(U9, "執行後輸出什麼？", None, ["5", "7", "12"],
    "f(3) = 6，f(2) = 4，相加 10。", exam=True, t="追蹤",
    code='def f(x):\n    return x * 2\nprint(f(3) + f(2))', correct="10")
add(U9, "執行後輸出什麼？", None, ["hi", "hi hi", "None"],
    "hello() 呼叫時印出 hi，函式沒有 return 所以 x 是 None，接著印出 None。所以輸出 hi None（兩個 print 因為 end=" " 在同一行）。", exam=True, t="追蹤",
    code='def hello():\n    print("hi", end=" ")\nx = hello()\nprint(x)', correct="hi None")
add(U9, "執行後輸出什麼？", None, ["20", "10 20", "10 10"],
    "函式裡的 x = 20 建立了區域變數，不影響全域的 x，所以外面還是 10；函式裡印 20。輸出 20 10。", exam=True, t="追蹤",
    code='x = 10\ndef f():\n    x = 20\n    print(x, end=" ")\nf()\nprint(x)', correct="20 10")
add(U9, "執行後輸出什麼？", None, ["0", "1", "會噴錯"],
    "有 global 宣告，函式裡的 count += 1 改的是全域變數；呼叫兩次得 2，所以輸出 2。", exam=True, t="追蹤",
    code='count = 0\ndef inc():\n    global count\n    count += 1\ninc()\ninc()\nprint(count)', correct="2")
add(U9, "執行後輸出什麼？", None, ["[5]", "[1]", "None"],
    "串列傳進函式是共用同一個，函式裡 append 會影響外面的 nums。", exam=True, t="追蹤",
    code='def add_one(a):\n    a.append(1)\nnums = [5]\nadd_one(nums)\nprint(nums)', correct="[5, 1]")
add(U9, "下列函式想回傳兩數中較大的，但有 bug，哪一行有問題？<pre class=\"q-code\">def bigger(a, b):\n    if a > b:\n        print(a)\n    else:\n        print(b)\nx = bigger(3, 8) + 1</pre>", "函式用 print 而不是 return，x 會是 None 而無法加 1", ["if a > b 應改為 if a < b", "else 後面不能接冒號", "參數不能叫 a、b"],
    "print 只是顯示，沒有把值交給呼叫端；bigger(3, 8) 的結果是 None，None + 1 會 TypeError。", exam=True, t="除錯")
add(U9, "函式裡想修改全域變數 total，卻沒寫 <code>global total</code> 就執行 <code>total += 5</code>，會怎樣？", "UnboundLocalError", ["total 增加 5", "total 不變，也不報錯", "SyntaxError"],
    "沒有 global，total += 5 讓 Python 當成區域變數，卻在賦值前就讀取，會出現 UnboundLocalError。", t="除錯")
add(U9, "下列函式用來算 n 的階乘（n!），空格應填入？<pre class=\"q-code\">def fact(n):\n    r = 1\n    for i in range(1, n + 1):\n        ____\n    return r</pre>", "<code>r *= i</code>", ["<code>r += i</code>", "<code>r = i</code>", "<code>i *= r</code>"],
    "連乘要把每個 i 乘進 r；+= 是加總；r = i 只留最後一個。", exam=True, t="填空")

# ---- 10 題型技巧 ----
add(U10, "執行後輸出什麼？", None, ["0 3", "-1 4", "3 3"],
    "追蹤：a=5,b=2 → a=3,b=3 → a=0,b=4；a > 0 不成立，結束，輸出 0 4。", exam=True, t="追蹤",
    code='a = 5\nb = 2\nwhile a > 0:\n    a -= b\n    b += 1\nprint(a, b)', correct="0 4")
add(U10, "判斷質數的函式對哪個輸入會得到「錯誤」結果？<pre class=\"q-code\">def is_prime(n):\n    for d in range(2, n):\n        if n % d == 0:\n            return False\n    return True</pre>", "1", ["7", "9", "13"],
    "n = 1 時 range(2, 1) 是空的，直接 return True，但 1 不是質數；缺少 n < 2 的處理。", exam=True, t="除錯")
add(U10, "找最大值的程式 <code>best = nums[0]</code>，<code>for x in nums:</code>，<code>    if ____: best = x</code>，空格應填入？", "<code>x > best</code>", ["<code>x < best</code>", "<code>x == best</code>", "<code>x != 0</code>"],
    "比現在的擂主大就換人；x < best 會找到最小值。", exam=True, t="填空")
add(U10, "每次可以走 1 階或 2 階，走到第 6 階有幾種走法？（1 階：1 種，2 階：2 種，之後每階 = 前兩階相加）", "13", ["8", "11", "21"],
    "1、2、3、5、8、13：第 6 階是 13 種。", exam=True, t="計算邏輯")
add(U10, "下列哪一種做法最能有效「找出程式的 bug」？", "用範例輸入跑一遍，再用最小值、空資料、剛好等於邊界值等輸入測試", ["把整段程式重新寫一遍", "只看一般的輸入", "只看變數名稱是否好懂"],
    "除錯要靠「會讓它出錯的輸入」：先確認一般情況，再測邊界。", exam=True, t="除錯")

# ---- 11 時間複雜度 ----
add(U11, "執行後輸出什麼？", None, ["8", "12", "24"],
    "雙層迴圈總共 4 × 4 = 16 次。", exam=True, t="效能",
    code='n = 4\nc = 0\nfor i in range(n):\n    for j in range(n):\n        c += 1\nprint(c)', correct="16")
add(U11, "執行後輸出什麼？", None, ["7", "9", "10"],
    "每次把 n 砍半：256 → 128 → 64 → 32 → 16 → 8 → 4 → 2 → 1，共 8 次。", exam=True, t="效能",
    code='n = 256\nc = 0\nwhile n > 1:\n    n //= 2\n    c += 1\nprint(c)', correct="8")
add(U11, "輸入規模 n 變成 3 倍，O(n²) 演算法的執行時間大約變成幾倍？", "9 倍", ["3 倍", "6 倍", "27 倍"],
    "時間與 n² 成正比，n 變 3 倍時間變 3² = 9 倍。", exam=True, t="效能")
add(U11, "下列複雜度，哪一個成長最快（n 很大時最慢）？", "O(2ⁿ)", ["O(n²)", "O(n log n)", "O(log n)"],
    "指數成長最快，其次是 n²、n log n、log n。", exam=True, t="效能")
add(U11, "要算 1 + 2 + … + n，哪種寫法的時間複雜度最低？", "<code>n * (n + 1) // 2</code>", ["<code>for i in range(1, n + 1): total += i</code>", "<code>sum(range(1, n + 1))</code>", "雙層迴圈每一對相加"],
    "公式只算一次是 O(1)；迴圈與 sum(range) 都是 O(n)。", exam=True, t="效能")
add(U11, "某題 N 的上限是 10⁵，下列哪種複雜度的做法通常會超時？", "O(n²)", ["O(n)", "O(n log n)", "O(log n)"],
    "10⁵ 的平方是 10¹⁰，遠超過 1 秒能跑的 10⁷~10⁸ 次。", exam=True, t="效能")

# ---- 12 遞迴 ----
add(U12, "執行後輸出什麼？", None, ["10", "6", "12"],
    "f(4) = 4 × f(3) = 4 × 3 × f(2) = 4 × 3 × 2 × f(1) = 24。", exam=True, t="追蹤",
    code='def f(n):\n    if n <= 1:\n        return 1\n    return n * f(n - 1)\nprint(f(4))', correct="24")
add(U12, "執行後輸出什麼？", None, ["3 2 1", "1 2 3", "3 3 3"],
    "先印再遞迴：每層先印自己的 n，所以依序印 3、2、1。", exam=True, t="追蹤",
    code='def p(n):\n    if n == 0:\n        return\n    print(n, end=" ")\n    p(n - 1)\np(3)', correct="3 2 1 ")
add(U12, "執行後輸出什麼？", None, ["3 2 1 ", "0 1 2 3 ", "3 3 3 "],
    "先遞迴再印：先走到最深層，回來時才依序印 1、2、3。", exam=True, t="追蹤",
    code='def p(n):\n    if n == 0:\n        return\n    p(n - 1)\n    print(n, end=" ")\np(3)', correct="1 2 3 ")
add(U12, "費氏數列 fib(0)=0、fib(1)=1、fib(n)=fib(n-1)+fib(n-2)，fib(7) 的值是？", "13", ["8", "21", "11"],
    "0, 1, 1, 2, 3, 5, 8, 13：fib(7) = 13。", exam=True, t="計算邏輯")
add(U12, "下列遞迴函式有什麼問題？<pre class=\"q-code\">def total(n):\n    return n + total(n - 1)</pre>", "沒有終止條件，會無窮遞迴（RecursionError）", ["n 不能是負數", "不能用 return", "參數名稱不能叫 n"],
    "每次呼叫都會再呼叫自己，永遠不會停下來。需要加 if n == 0: return 0。", exam=True, t="除錯")
add(U12, "遞迴求 n!，空格應填入？<pre class=\"q-code\">def fact(n):\n    if n <= 1:\n        return 1\n    return ____</pre>", "<code>n * fact(n - 1)</code>", ["<code>n + fact(n - 1)</code>", "<code>fact(n) * n</code>", "<code>n * fact(n + 1)</code>"],
    "n! = n × (n-1)!；fact(n) 會直接呼叫自己無窮遞迴；fact(n+1) 越來越遠離終止條件。", exam=True, t="填空")

# ---- 13 排序 ----
add(U13, "選擇排序對 [4, 3, 1, 2] 做完第一輪後，串列是？", "[1, 3, 4, 2]", ["[3, 1, 2, 4]", "[1, 2, 3, 4]", "[3, 4, 1, 2]"],
    "第一輪找最小的 1（索引 2），與索引 0 的 4 交換：[1, 3, 4, 2]。", exam=True, t="追蹤")
add(U13, "氣泡排序對 [4, 3, 1, 2] 做完第一輪後，串列是？", "[3, 1, 2, 4]", ["[1, 3, 4, 2]", "[1, 2, 3, 4]", "[3, 4, 1, 2]"],
    "第一輪最大的 4 一路交換到最後：[3, 1, 2, 4]。", exam=True, t="追蹤")
add(U13, "插入排序對 [4, 3, 1, 2]，做完 i = 1、i = 2 兩輪後（前三個排好），串列是？", "[1, 3, 4, 2]", ["[3, 4, 1, 2]", "[1, 2, 3, 4]", "[3, 1, 2, 4]"],
    "i=1：把 3 插到 4 前 → [3,4,1,2]；i=2：把 1 插到最前 → [1,3,4,2]。", exam=True, t="追蹤")
add(U13, "n 個元素做三種基本排序（選擇、氣泡、插入），最差情況的時間複雜度都是？", "O(n²)", ["O(n)", "O(n log n)", "O(log n)"],
    "它們都是雙層迴圈的 O(n²) 排序法；內建 sort 才是 O(n log n)。", exam=True, t="效能")
add(U13, "資料「幾乎已經排好」時，哪個基本排序最快？", "插入排序", ["選擇排序", "三者一樣快", "無法判斷"],
    "插入排序遇到已排好的部分幾乎不用搬動，接近 O(n)。", t="效能")
add(U13, "氣泡排序內層迴圈應該是 <code>for j in range(____)</code>，第 i 輪（從 0 起算）空格應填入？", "<code>n - 1 - i</code>", ["<code>n</code>", "<code>i</code>", "<code>n + i</code>"],
    "第 i 輪後最後 i 個位置已排好，不必再比；range(n) 會讓 a[j+1] 超出索引。", exam=True, t="填空")

# ---- 14 搜尋 ----
add(U14, "在 [1, 3, 5, 7, 9, 11, 13] 中二分搜尋 11，第一次比較的是哪個值？（lo=0、hi=6）", "7", ["5", "9", "11"],
    "mid = (0 + 6) // 2 = 3，a[3] = 7。", exam=True, t="追蹤")
add(U14, "n 筆已排序資料，二分搜尋最多大約要比較幾次？", "約 log₂n 次", ["約 n 次", "約 n² 次", "固定 1 次"],
    "每次砍半，所以是對數等級。", exam=True, t="效能")
add(U14, "二分搜尋中 <code>a[mid] < target</code>，應該怎麼更新？", "<code>lo = mid + 1</code>", ["<code>hi = mid - 1</code>", "<code>lo = mid</code>", "<code>hi = mid</code>"],
    "目標在右半邊，且 mid 已比過可排除，所以 lo = mid + 1。", exam=True, t="填空")
add(U14, "二分搜尋的程式 <code>mid = (lo + hi) / 2</code> 有什麼 bug？", "/ 得到小數，不能當索引，要用 //", ["括號不能加", "lo 和 hi 不能相加", "mid 不能是整數"],
    "串列索引必須是整數，要用整除 //。", exam=True, t="除錯")
add(U14, "資料沒排序，要找某個值是否存在，應該用？", "線性搜尋", ["二分搜尋", "兩者都可以", "兩者都不行"],
    "二分搜尋必須資料已排序；沒排序就用線性搜尋（或先排序）。", exam=True, t="計算邏輯")

# ---- 15 堆疊佇列 ----
add(U15, "動作：push 5、push 8、pop、push 2、push 9、pop、pop，最後堆疊內容是？（左為底、右為頂）", "[5]", ["[5, 2]", "[5, 8]", "[]"],
    "[5] → [5,8] → [5] → [5,2] → [5,2,9] → [5,2] → [5]。", exam=True, t="追蹤")
add(U15, "依序 enqueue 1、2、3 後連續 dequeue 兩次，取出的順序是？", "1、2", ["3、2", "2、3", "3、1"],
    "佇列先進先出。", exam=True, t="追蹤")
add(U15, "依序 push 1、2、3 後，把全部 pop 出來的順序是？", "3、2、1", ["1、2、3", "2、1、3", "1、3、2"],
    "堆疊後進先出。", exam=True, t="追蹤")
add(U15, "用堆疊檢查括號是否配對，字串 <code>\"([)]\"</code> 的結果是？", "不合法", ["合法", "還要看長度", "無法判斷"],
    "讀到 ) 時頂端是 [，對不上，所以不合法。", exam=True, t="計算邏輯")
add(U15, "下列哪個是「佇列」的特性？", "先進先出", ["後進先出", "隨機取出", "只能從中間取"],
    "Queue = First In, First Out。", exam=True, t="計算邏輯")
add(U15, "用 Python 串列當堆疊時，「拿走頂端」應該用？", "<code>s.pop()</code>", ["<code>s.pop(0)</code>", "<code>s.remove(0)</code>", "<code>s.insert(0, x)</code>"],
    "pop() 預設拿走最後一個（頂端）；pop(0) 拿走第一個（那是佇列的行為）。", exam=True, t="填空")

if PROBLEMS:
    for p_ in PROBLEMS: print("PROBLEM", p_)
    sys.exit(1)
# 稽核：同一份題庫內題幹不可重複
seen = set()
for it in Q:
    assert it["q"] not in seen, it["q"]
    seen.add(it["q"])
js = ('/* 由 tools/build_quiz_extra.py 產生：追加的觀念題（s:"exam" 為仿歷屆題型，s:"bank" 為一般題）。請勿手改。 */\n'
      'if (typeof QUIZ !== "undefined") QUIZ.push(...[\n' + ",\n".join("  " + json.dumps(x, ensure_ascii=False) for x in Q) + "\n]);\n")
open(os.path.join(ROOT, "website", "quiz_extra.js"), "w", encoding="utf-8").write(js)
print(len(Q), "題；其中仿歷屆", sum(1 for x in Q if x["s"] == "exam"))
