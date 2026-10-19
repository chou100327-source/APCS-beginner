/* 程式判題的「教我寫」：每一題的思考步驟、程式骨架、帶註解的參考解答。
   steps：把題目拆成小步驟；skeleton：填空骨架（按鈕可放進編輯器）；solution：完整解答（預設收起來）；
   notes：解答逐段說明；traps：這題最容易錯的地方。 */
const GUIDES = {
  "p01-avg": {
    steps: [
      "看輸入：第一行是人數 N，第二行有 N 個整數（全部在同一行）→ 用 <code>list(map(int, input().split()))</code> 一次讀成串列。",
      "第一個輸出是<b>總分</b>：<code>sum(串列)</code>。",
      "第二個輸出是<b>平均</b>：總分 ÷ N，要印到小數點後 2 位 → <code>f\"{avg:.2f}\"</code>。",
      "用範例 <code>3 / 80 91 77</code> 手算：總分 248，平均 82.666… → 四捨五入成 82.67。",
    ],
    skeleton: `n = int(input())
nums = ____                    # 一行 N 個整數，讀成串列
total = ____                   # 用 sum() 算總分
print(total)
print(f"{total / n:.__f}")     # 平均：取到小數點後幾位？
`,
    solution: `n = int(input())                          # 第一行：人數
nums = list(map(int, input().split()))    # 第二行：N 個整數 → 串列
total = sum(nums)                         # 總分
print(total)                              # 第 1 行輸出
print(f"{total / n:.2f}")                 # 第 2 行輸出：平均，小數點後 2 位
`,
    notes: ["<code>input().split()</code> 把一行切成字串串列，<code>map(int, …)</code> 逐個轉整數，<code>list(…)</code> 裝成串列。", "平均直接在 f-string 裡算：<code>{total / n:.2f}</code>。"],
    traps: ["別忘了 <code>int()</code> 轉型，否則 <code>sum</code> 會出錯。", "只印答案，不要加「總分：」。", "小數位數不對（例如 .1f）會 WA。"],
  },
  "p02-digitsum": {
    steps: [
      "這題要「一位一位」處理整數 → 用 <code>while n > 0</code>，每輪取最右邊一位 <code>n % 10</code>，再用 <code>n //= 10</code> 砍掉它。",
      "準備三個變數：<code>digits</code>（幾位數）、<code>total</code>（各位數字總和）、<code>rev</code>（反轉後的數）。",
      "每一輪：<code>d = n % 10</code>；<code>digits += 1</code>；<code>total += d</code>；<code>rev = rev * 10 + d</code>。",
      "用範例 <code>1200</code> 手算：取出 0、0、2、1 → 位數 4、總和 3、反轉 <code>0021</code> 變成整數 21。",
    ],
    skeleton: `n = int(input())
digits = 0
total = 0
rev = 0
while ____:                    # 還有數字就繼續
    d = ____                   # 取出最右邊一位
    digits += 1
    total += ____
    rev = rev * 10 + ____
    n = ____                   # 砍掉最右邊一位
print(digits)
print(total)
print(rev)
`,
    solution: `n = int(input())
digits = 0                  # 幾位數
total = 0                   # 各位數字總和
rev = 0                     # 反轉後的數
while n > 0:                # n 還有數字就繼續
    d = n % 10              # 取出最右邊一位
    digits += 1
    total += d
    rev = rev * 10 + d      # 把 d 接到 rev 的後面
    n //= 10                # 砍掉最右邊一位
print(digits)
print(total)
print(rev)
`,
    notes: ["這就是單元 03 的「剝數字」模板。", "<code>rev = rev * 10 + d</code>：把舊的 rev 往左移一位，再把新的一位接在後面。"],
    traps: ["反轉的結果是整數，<code>1200</code> 反轉是 <code>21</code>，不是 <code>0021</code>。", "不要用字串處理也可以，但要和題目一致：三個答案分三行印。"],
  },
  "p03-change": {
    steps: [
      "面額由大到小：500、100、50、10、5、1。這是「用最少張數」的貪心做法：先用最大的。",
      "每個面額：<code>n // 面額</code> 是要幾張；<code>n % 面額</code> 是用完這個面額後剩下多少。",
      "六個面額都做同樣的事 → 用 <code>for coin in [...]</code> 迴圈，每輪印出張數、再更新 n。",
      "用範例 <code>678</code> 手算：500 → 1 張剩 178；100 → 1 張剩 78；50 → 1 張剩 28；10 → 2 張剩 8；5 → 1 張剩 3；1 → 3 張。",
    ],
    skeleton: `n = int(input())
for coin in [500, 100, 50, 10, 5, 1]:
    print(n ____ coin)         # 這個面額要幾張？
    n = n ____ coin            # 剩下多少？
`,
    solution: `n = int(input())
for coin in [500, 100, 50, 10, 5, 1]:   # 由大到小
    print(n // coin)                    # 這個面額要幾張（整除）
    n = n % coin                        # 剩下的金額（餘數）
`,
    notes: ["<code>//</code> 取商、<code>%</code> 取餘數，是整數運算最典型的應用。", "六行輸出就是迴圈跑六輪，每輪印一行。"],
    traps: ["順序一定要由大到小。", "每輪要更新 <code>n</code>，不然後面的面額都會重複算整個金額。", "有些面額 0 張也要印出 0。"],
  },
  "p04-leap": {
    steps: [
      "閏年規則：能被 4 整除<b>而且</b>不能被 100 整除，<b>或者</b>能被 400 整除。",
      "寫成條件：<code>(y % 4 == 0 and y % 100 != 0) or y % 400 == 0</code>。",
      "是閏年印「閏年」與 366；否則印「平年」與 365 → 用 <code>if / else</code>。",
      "試幾個年份：2024 閏年、2023 平年、1900 平年（逢百不閏）、2000 閏年（逢四百又閏）。",
    ],
    skeleton: `y = int(input())
if ____:                       # 閏年的條件（and / or 要加括號）
    print("閏年")
    print(366)
else:
    print("平年")
    print(365)
`,
    solution: `y = int(input())
if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0:   # 閏年條件
    print("閏年")
    print(366)
else:
    print("平年")
    print(365)
`,
    notes: ["<code>and</code> 先於 <code>or</code>，所以前兩個條件自然綁在一起，括號是為了讓人一眼看懂。"],
    traps: ["1900 和 2100 是平年（被 100 整除但不被 400 整除）。", "輸出兩行：第一行文字、第二行數字。"],
  },
  "p05-xor": {
    steps: [
      "性質：<code>x ^ x = 0</code>、<code>x ^ 0 = x</code>。成對的數字 XOR 起來會互相抵銷。",
      "所以把全部數字依序 XOR，剩下的就是「只出現一次」的那個。",
      "寫法：<code>r = 0</code>，<code>for x in nums: r ^= x</code>，最後印 r。",
      "用範例 <code>4 1 2 1 2</code> 手算：4 → 5 → 7 → 6 → 4。",
    ],
    skeleton: `n = int(input())
nums = list(map(int, input().split()))
r = 0                          # XOR 的起始值
for x in nums:
    r ____ x                   # 一個個 XOR 進去（用複合指定）
print(r)
`,
    solution: `n = int(input())
nums = list(map(int, input().split()))
r = 0                    # 0 和任何數 XOR 都是那個數本身
for x in nums:
    r ^= x               # 成對的會互相抵銷
print(r)
`,
    notes: ["起始值用 0，因為 <code>0 ^ x = x</code>。", "這題不需要排序、不需要計數，一個迴圈搞定，複雜度 O(n)。"],
    traps: ["不要用 <code>+</code> 或 <code>-</code>。", "XOR 是 <code>^</code>，不是次方。"],
  },
  "p06-bitswitch": {
    steps: [
      "用一個整數 <code>state</code> 當 8 個開關，第 k 位是 1 代表開。一開始 <code>state = 0</code>。",
      "遮罩：<code>1 &lt;&lt; k</code> 是「只有第 k 位為 1」的數。",
      "ON：<code>state |= mask</code>；OFF：<code>state &amp;= ~mask</code>；TOGGLE：<code>state ^= mask</code>。",
      "每行指令用 <code>op, k = input().split()</code> 讀（k 要 <code>int()</code>），依 op 決定做哪一種。",
      "最後印 state，再印 <code>bin(state).count(\"1\")</code>（有幾個開關開著）。",
    ],
    skeleton: `m = int(input())
state = 0
for _ in range(m):
    op, k = input().split()
    k = int(k)
    mask = 1 << k
    if op == "ON":
        state ____ mask         # 打開：OR
    elif op == "OFF":
        state ____ ~mask        # 關閉：AND 加上反相的遮罩
    else:
        state ____ mask         # 切換：XOR
print(state)
print(bin(state).count("1"))
`,
    solution: `m = int(input())
state = 0                         # 8 個開關，全關
for _ in range(m):
    op, k = input().split()       # 例如 "ON 3" → op="ON", k="3"
    k = int(k)
    mask = 1 << k                 # 只有第 k 位是 1
    if op == "ON":
        state |= mask             # 打開第 k 位
    elif op == "OFF":
        state &= ~mask            # 關閉第 k 位
    else:                         # TOGGLE
        state ^= mask             # 切換第 k 位
print(state)                      # 最終狀態的十進位值
print(bin(state).count("1"))      # 開著的開關數量
`,
    notes: ["三個動作對應單元 05 的「位元當開關」。", "<code>bin(state)</code> 是像 <code>'0b1101'</code> 的字串，<code>.count(\"1\")</code> 數出有幾個 1。"],
    traps: ["<code>k</code> 讀進來是字串，要 <code>int()</code>。", "關閉要用 <code>&amp;= ~mask</code>，不是 <code>^=</code>。"],
  },
  "p07-grade": {
    steps: [
      "先讀 N，再用迴圈讀 N 個分數。",
      "每個分數用 <code>if / elif</code> 判斷等第：由最嚴格的條件開始 90、80、70、60，其他是 E。",
      "每個等第要「印出來」並且「計數」。計數用字典 <code>cnt = {\"A\": 0, …}</code> 或五個變數都可以。",
      "迴圈結束後印最後一行 <code>A:x B:x C:x D:x E:x</code>（冒號後面沒有空白，欄位間一個空白）。",
    ],
    skeleton: `n = int(input())
cnt = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
for _ in range(n):
    s = int(input())
    if s >= 90:
        g = "A"
    elif ____:
        g = "B"
    ____                    # 70 分以上是 C
    ____                    # 60 分以上是 D
    else:
        g = "E"
    cnt[g] += 1
    print(g)
print(f"A:{cnt['A']} B:{cnt['B']} C:{cnt['C']} D:{cnt['D']} E:{cnt['E']}")
`,
    solution: `n = int(input())
cnt = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}   # 各等第人數
for _ in range(n):
    s = int(input())
    if s >= 90:             # 從最嚴格的條件開始
        g = "A"
    elif s >= 80:
        g = "B"
    elif s >= 70:
        g = "C"
    elif s >= 60:
        g = "D"
    else:
        g = "E"
    cnt[g] += 1             # 這個等第的人數 +1
    print(g)                # 每人印一行等第
print(f"A:{cnt['A']} B:{cnt['B']} C:{cnt['C']} D:{cnt['D']} E:{cnt['E']}")
`,
    notes: ["條件順序：90 → 80 → 70 → 60，符合就停，所以後面的條件不用再寫「小於上一級」。", "字典 <code>cnt[g] += 1</code> 讓計數很簡潔。"],
    traps: ["邊界：剛好 90 是 A、剛好 60 是 D、59 是 E。", "最後一行格式要一模一樣。"],
  },
  "p08-triangle": {
    steps: [
      "先排除「不是三角形」：任兩邊和不大於第三邊（<code>a + b &lt;= c or a + c &lt;= b or b + c &lt;= a</code>）。",
      "再由特殊到一般：正三角形（三邊相等）→ 等腰（有兩邊相等）→ 直角（畢氏定理）→ 一般。",
      "<b>順序很重要</b>：正三角形也有兩邊相等，所以要排在等腰前面；等腰可能同時是直角，但題目依序判斷，先符合的先印。",
      "直角要檢查三種斜邊：<code>a*a + b*b == c*c</code>、<code>a*a + c*c == b*b</code>、<code>b*b + c*c == a*a</code>。",
    ],
    skeleton: `a, b, c = map(int, input().split())
if ____:                         # 任兩邊和不大於第三邊
    print("不是三角形")
elif a == b == c:
    print("正三角形")
elif ____:                       # 有兩邊相等
    print("等腰三角形")
elif ____:                       # 直角（三種斜邊都要檢查）
    print("直角三角形")
else:
    print("一般三角形")
`,
    solution: `a, b, c = map(int, input().split())
if a + b <= c or a + c <= b or b + c <= a:        # 先排除不是三角形
    print("不是三角形")
elif a == b == c:                                  # 三邊相等
    print("正三角形")
elif a == b or b == c or a == c:                   # 有兩邊相等
    print("等腰三角形")
elif a * a + b * b == c * c or a * a + c * c == b * b or b * b + c * c == a * a:
    print("直角三角形")                            # 畢氏定理，任一邊當斜邊
else:
    print("一般三角形")
`,
    notes: ["這題就是單元 06 的「三角形分類」範例。", "<code>a == b == c</code> 是連鎖比較，等同 <code>a == b and b == c</code>。"],
    traps: ["「不是三角形」一定要最先判斷。", "直角三角形的斜邊不一定是 c。"],
  },
  "p09-classify": {
    steps: [
      "讀 N 與 N 個整數（同一行）→ 串列。",
      "準備五個計數器：正數、負數、零、奇數、偶數。",
      "走訪每個數：先分正／負／零（<code>if / elif / else</code>）；再分奇偶（<code>x % 2 == 0</code> 是偶數，零也算偶數）。",
      "Python 的 <code>-3 % 2</code> 是 1，所以負奇數也會被判成奇數，不需要特別處理。",
      "輸出兩行：<code>正 負 零</code>、<code>奇 偶</code>（空白隔開）。",
    ],
    skeleton: `n = int(input())
nums = list(map(int, input().split()))
pos = neg = zero = 0
odd = even = 0
for x in nums:
    if x > 0:
        pos += 1
    elif ____:
        neg += 1
    else:
        zero += 1
    if x % 2 == ____:
        even += 1
    else:
        odd += 1
print(pos, neg, zero)
print(odd, even)
`,
    solution: `n = int(input())
nums = list(map(int, input().split()))
pos = neg = zero = 0        # 正、負、零
odd = even = 0              # 奇、偶
for x in nums:
    if x > 0:
        pos += 1
    elif x < 0:
        neg += 1
    else:
        zero += 1
    if x % 2 == 0:          # 零也算偶數；Python 的 % 對負數也正常
        even += 1
    else:
        odd += 1
print(pos, neg, zero)
print(odd, even)
`,
    notes: ["兩組統計在同一個迴圈裡各自獨立判斷，所以是「兩個 if 組」而不是 elif 接下去。"],
    traps: ["零不是正數也不是負數，要單獨算。", "奇偶判斷用 <code>% 2</code>，不要用 <code>x // 2</code>。"],
  },
  "p10-prime": {
    steps: [
      "要找 2 到 N 之間的所有質數 → 外層 <code>for x in range(2, n + 1)</code>。",
      "判斷 x 是不是質數：從 2 試到 <code>√x</code>，只要有一個整除就不是質數（找到就 <code>break</code>）。",
      "沒被 <code>break</code>（沒找到因數）就是質數 → 用旗標 <code>ok = True</code> 或 <code>for…else</code>。",
      "把質數收集到串列，最後用 <code>print(*primes)</code> 印出（空白隔開）；串列是空的就印「無」。",
    ],
    skeleton: `n = int(input())
primes = []
for x in range(2, n + 1):
    ok = True
    for d in range(2, int(x ** 0.5) + 1):
        if x % d == ____:
            ok = False
            ____                      # 找到因數就不用再找了
    if ok:
        primes.append(x)
if primes:
    print(*primes)
else:
    print("無")
`,
    solution: `n = int(input())
primes = []                              # 收集質數
for x in range(2, n + 1):                # 1 不是質數，從 2 開始
    ok = True                            # 先假設是質數
    for d in range(2, int(x ** 0.5) + 1):    # 只需要檢查到 √x
        if x % d == 0:                   # 找到因數
            ok = False
            break                        # 不用再找了
    if ok:
        primes.append(x)
if primes:
    print(*primes)                       # 以空白隔開
else:
    print("無")
`,
    notes: ["只檢查到 √x 是因為：如果 x 有大於 √x 的因數，必定有一個小於 √x 的對應因數。", "<code>for x in range(2, n + 1)</code> 在 n = 1 時是空的，所以自然印「無」。"],
    traps: ["N = 1 沒有質數，要印「無」。", "<code>range(2, int(x ** 0.5) + 1)</code> 的 +1 不能漏（例如 x = 4 要檢查到 2）。"],
  },
  "p11-stars": {
    steps: [
      "第 i 層（i 從 1 數到 N）有 <code>2*i - 1</code> 顆星，前面有 <code>N - i</code> 個空白。",
      "用字串重複：<code>\" \" * (n - i) + \"*\" * (2 * i - 1)</code>。",
      "同時累加星星總數：<code>total += 2 * i - 1</code>。",
      "迴圈結束後再多印一行總數。（N 層的總數其實就是 N²，可以拿來驗算。）",
    ],
    skeleton: `n = int(input())
total = 0
for i in range(1, n + 1):
    stars = ____                         # 第 i 層有幾顆星
    print(" " * ____ + "*" * stars)      # 前面補幾個空白？
    total += stars
print(total)
`,
    solution: `n = int(input())
total = 0                                # 星星總數
for i in range(1, n + 1):                # 第 1 層到第 n 層
    stars = 2 * i - 1                    # 第 i 層：1、3、5、…
    print(" " * (n - i) + "*" * stars)   # 左邊補空白讓它置中
    total += stars
print(total)                             # 最後一行：總數（= n * n）
`,
    notes: ["字串乘整數是「重複」：<code>\"*\" * 3</code> 是 <code>***</code>。", "只在左邊補空白，右邊不補。"],
    traps: ["第 1 層空白數是 <code>n - 1</code>，不是 <code>n</code>。", "最後一行要印總數，不是印 n。"],
  },
};
