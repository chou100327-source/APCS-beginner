/* ===== 考前速查：最常用的 Python 語法（考前快速掃過用） =====
   每個 item：t = 標題；c = 程式碼片段（會語法上色）；或 d = 純文字提醒。 */
const CHEAT = [
  {
    id: "io", name: "輸入輸出", items: [
      { t: "讀一個整數 / 一行字串", c: `n = int(input())        # 一個整數
s = input().strip()     # 一行字串（順手去掉頭尾空白與換行）` },
      { t: "一行多個數字", c: `a, b, c = map(int, input().split())     # 剛好三個
nums = list(map(int, input().split()))  # 不確定幾個，全丟進 list` },
      { t: "讀 N 行（每行一個數）", c: `n = int(input())
arr = [int(input()) for _ in range(n)]
# 同一行 N 個數：arr = list(map(int, input().split()))` },
      { t: "讀到沒有資料為止（EOF）", c: `import sys
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    # 處理 line` },
      { t: "輸出格式", c: `print(a, b)                  # 用空白隔開
print(*nums)                 # 把 list 展開印，也是空白隔開
print(" ".join(map(str, nums)))   # 自己控制分隔符
print(f"{x:.2f}")            # 小數點後 2 位
print(f"{n:03d}")            # 補零到 3 位
print(x, end="")             # 不換行` },
    ]
  },
  {
    id: "num", name: "數字運算", items: [
      { t: "整除、餘數、次方", c: `7 / 2     # 3.5   一定是小數
7 // 2    # 3     整除
7 % 2     # 1     餘數
2 ** 10   # 1024  次方（右結合：2**3**2 = 512）` },
      { t: "負數的坑（跟 C/Java 不一樣）", c: `-7 // 2   # -4   往負無窮捨去（不是 -3）
-7 % 2    #  1   餘數正負跟「除數」相同
int(-3.7) # -3   int() 是往 0 捨去` },
      { t: "拆數字每一位", c: `ones = n % 10          # 個位
tens = (n // 10) % 10  # 十位

total = 0
while n > 0:           # 各位數字總和
    total += n % 10
    n //= 10` },
      { t: "常用函式", c: `abs(-7)          # 7
max(a), min(a)   # 最大 / 最小
sum(a)           # 總和
divmod(17, 5)    # (3, 2) 商與餘數
int(x ** 0.5)    # 開根號取整（判質數用）` },
    ]
  },
  {
    id: "bit", name: "位元運算", items: [
      { t: "五個運算子", c: `a & b    # AND  兩位都是 1 才 1
a | b    # OR   有一位是 1 就 1
a ^ b    # XOR  兩位不同才 1
~a       # NOT  等於 -a-1
a << n   # 左移 = 乘以 2**n
a >> n   # 右移 = 除以 2**n（捨去）` },
      { t: "必背四技巧", c: `(n & 1) == 0                  # 偶數（括號要加！）
n > 0 and (n & (n-1)) == 0    # n 是 2 的次方
n & -n                        # 取出最低位的 1

result = 0                    # 找出唯一出現奇數次的數
for x in nums:
    result ^= x` },
      { t: "位元當開關", c: `state |= (1 << k)     # 打開第 k 個
state &= ~(1 << k)    # 關閉第 k 個
state ^= (1 << k)     # 切換第 k 個
bool(state & (1 << k))     # 第 k 個開著嗎
bin(state).count("1")      # 有幾個開著` },
      { t: "進位轉換", c: `bin(13)          # '0b1101'
int('1101', 2)   # 13
hex(255)         # '0xff'` },
    ]
  },
  {
    id: "cond", name: "條件與迴圈", items: [
      { t: "if / elif / else", c: `if score >= 90:        # 從最嚴格的條件開始寫
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"
r = "偶數" if n % 2 == 0 else "奇數"   # 三元運算式` },
      { t: "邏輯運算與優先順序", c: `# not > and > or；不確定就加括號
a and b      # 都真才真（左邊假就短路）
a or b       # 有一個真就真（左邊真就短路）
not a
60 <= s < 70           # 連鎖比較
x in (1, 2, 3)        # 成員判斷
# 假值：False 0 0.0 "" [] {} None` },
      { t: "range 三種寫法", c: `range(5)            # 0 1 2 3 4
range(1, n + 1)     # 1 ~ n（含頭不含尾）
range(10, 0, -2)    # 10 8 6 4 2` },
      { t: "四個迴圈模板", c: `total = 0                  # 累加
for x in nums: total += x

count = 0                  # 計數
for x in nums:
    if x % 2 == 0: count += 1

best = nums[0]             # 找最大（擂台法）
for x in nums:
    if x > best: best = x

while n > 0:               # 拆數字每一位
    d = n % 10
    n //= 10` },
      { t: "break / continue / for-else", c: `for d in range(2, int(n ** 0.5) + 1):
    if n % d == 0:
        break          # 整個迴圈結束
else:
    print("質數")      # 沒有 break 才會執行` },
    ]
  },
  {
    id: "warn", name: "考前地雷提醒", items: [
      { t: "只印答案", d: "不要印「請輸入…」之類的提示文字，判題是逐字比對，多印就錯。" },
      { t: "input() 一定要轉型", d: "input() 回傳字串，要算數學前先 int() / float()。\"3\" + \"4\" 會得到 \"34\"。" },
      { t: "&、| 與 and、or 不一樣", d: "& | ^ 是對「每個位元」運算；and or not 是對「真假值」運算。^ 是 XOR，不是次方（次方是 **）。" },
      { t: "elif 與連續 if", d: "elif 是擇一（符合就停）；連續 if 每個都會檢查，可能同時執行好幾個。" },
      { t: "負數的 // 與 %", d: "-7 // 2 = -4、-7 % 2 = 1，跟 C/Java 不同，觀念題很愛考。" },
      { t: "縮排只用空白", d: "Tab 與空白混用會 TabError；整份程式統一 4 個空白。" },
      { t: "邊界自己先測", d: "只有 1 筆資料、空輸入、全部相同、第一個與最後一個元素，這四種最容易 WA。" },
      { t: "range 的 off-by-one", d: "要跑 1~n 是 range(1, n+1)；要跑索引 0~n-1 是 range(n)。" },
    ]
  },
];
