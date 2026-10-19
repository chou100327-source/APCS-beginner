/* ===== 隨機生成的觀念題：每次出題數字都不一樣 =====
   QUIZGEN.make({ u: "03 算術運算" | null, n: 題數 }) → [{ w, u, s:"gen", q, o, a:0, e }]
   每個模板自己算出正解（用 Python 的規則：// 往負無窮、% 跟除數同號、round 銀行家捨入…），
   錯誤選項都是「常見錯誤想法」算出來的結果。_py 是對應的 Python 程式（只用在自動檢查）。 */
(function () {
  const rint = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
  const pick = arr => arr[Math.floor(Math.random() * arr.length)];
  const shuffle = arr => { const a = arr.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const fdiv = (a, b) => Math.floor(a / b);
  const fmod = (a, b) => a - b * Math.floor(a / b);
  const tdiv = (a, b) => Math.trunc(a / b);
  const tmod = (a, b) => a - b * Math.trunc(a / b);
  const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const code = s => `<pre class="q-code">${esc(s)}</pre>`;
  const c = s => `<code>${esc(s)}</code>`;
  const bin = n => (n < 0 ? "-" : "") + Math.abs(n).toString(2);
  const roundHalfEven = x => { const r = Math.round(x); return (Math.abs(x % 1) === 0.5 && r % 2 !== 0) ? r - 1 : r; };
  // Python 的 round()：.5 取偶數（對負數也是）
  const pyRound = x => { const f = Math.floor(x), d = x - f; if (d < 0.5) return f; if (d > 0.5) return f + 1; return f % 2 === 0 ? f : f + 1; };

  /* 整理成 4 個互不相同的選項：第 0 個是正解 */
  function opts(correct, wrongs, fill) {
    const out = [String(correct)];
    for (const w of wrongs) { const s = String(w); if (!out.includes(s)) out.push(s); if (out.length === 4) break; }
    let k = 1;
    const isList = /^\[.*\]$/.test(String(correct));
    const nums = isList ? String(correct).slice(1, -1).split(",").map(x => x.trim()).filter(Boolean).map(Number) : [];
    while (out.length < 4) {
      let s;
      if (fill) s = String(fill(k));
      else if (isList) {
        if (!nums.length) s = "[" + (k % 2 ? k : -k) + "]";
        else { const v = nums.slice(); const i = k % v.length; v[i] = v[i] + k * (k % 2 ? 1 : -1); s = "[" + v.join(", ") + "]"; }
      } else s = String(Number(correct) + k * (k % 2 ? 1 : -1));
      if (!out.includes(s)) out.push(s);
      k++;
      if (k > 30) break;
    }
    return out.slice(0, 4);
  }
  const mk = (u, q, o, e, py, expect) => ({ w: "初級", u, s: "gen", q, o: o.map(esc), a: 0, e, _py: py, _expect: expect });

  const U1 = "01 輸入與輸出", U2 = "02 資料型態與變數", U3 = "03 算術運算", U4 = "04 邏輯運算", U5 = "05 位元運算", U6 = "06 條件判斷", U7 = "07 迴圈";

  const T = [];

  /* ---------- 01 ---------- */
  T.push({ u: U1, f() {
    const a = rint(1, 9), b = rint(10, 99), cc = rint(100, 999);
    const sep = pick(["-", ", ", "/", ""]), end = pick(["!", "", "."]);
    const src = `print(${a}, ${b}, ${cc}, sep="${sep}", end="${end}")\nprint("X")`;
    const first = `${a}${sep}${b}${sep}${cc}${end}`;
    const correct = first + "X";
    const wrong = [`${a} ${b} ${cc}${end}X`, `${first} ⏎ X`, `${a}${b}${cc}${end}X`, `${a}${sep}${b}${sep}${cc}X`, `${first}`];
    return mk(U1, code(src) + "螢幕上看到的完整內容是？（⏎ 代表換行；不要把行尾的換行算進去）",
      opts(correct, wrong.filter(w => w !== correct)),
      `sep 是 3 個值之間的分隔（這次是「${sep || "什麼都沒有"}」），end 取代這個 print 結尾的換行（這次是「${end || "什麼都沒有"}」）。第一個 print 印出 ${first}，因為結尾不是換行，第二個 print 的 X 直接接在同一行後面。`,
      src);
  } });

  T.push({ u: U1, f() {
    let x;
    do { x = (rint(1, 9) + rint(10000, 99999) / 100000).toFixed(5); } while (x.endsWith("0"));
    const xv = parseFloat(x), d = pick([1, 2, 3]);
    const correct = xv.toFixed(d);
    const wrong = [xv.toFixed(d + 1), xv.toFixed(Math.max(0, d - 1)), String(Math.trunc(xv * 10 ** d) / 10 ** d), String(xv)];
    const src = `x = ${x}\nprint(f"{x:.${d}f}")`;
    return mk(U1, code(src) + "輸出是？", opts(correct, wrong.filter(w => w !== correct)),
      `:.${d}f 表示「小數點後取 ${d} 位（四捨五入）」。${x} 取 ${d} 位後是 ${correct}。`,
      `x = ${x}\nprint(f"{x:.${d}f}")`);
  } });

  T.push({ u: U1, f() {
    const n = rint(1, 99), w = pick([3, 4, 5]);
    const correct = String(n).padStart(w, "0");
    const wrong = [String(n).padStart(w, " "), String(n), String(n).padEnd(w, "0")];
    return mk(U1, code(`n = ${n}\nprint(f"{n:0${w}d}")`) + "輸出是？（若有空白，以 □ 表示）",
      opts(correct, wrong.map(s => s.replace(/ /g, "□")).filter(w => w !== correct)),
      `0${w}d：整數、總寬度 ${w}、不足的位數在前面補 0。`,
      `n = ${n}\nprint(f"{n:0${w}d}")`);
  } });

  /* ---------- 02 ---------- */
  T.push({ u: U2, f() {
    const x = pick([-9.7, -4.5, -2.3, 2.5, 3.5, 4.5, 6.7, 7.9, 8.2, -7.5, 0.5, 1.5]);
    const op = pick(["int", "round", "floor", "ceil"]);
    const fn = { int: Math.trunc, round: pyRound, floor: Math.floor, ceil: Math.ceil }[op];
    const correct = fn(x);
    const wrong = [Math.trunc(x), Math.round(x), Math.floor(x), Math.ceil(x), Math.trunc(x) + 1];
    const imp = op === "floor" || op === "ceil" ? "import math\n" : "";
    const call = op === "floor" ? "math.floor" : op === "ceil" ? "math.ceil" : op;
    return mk(U2, code(`${imp}print(${call}(${x}))`) + "輸出是？",
      opts(correct, wrong.filter(w => w !== correct)),
      op === "int" ? `int() 往 0 的方向捨去小數：${x} → ${correct}（不是四捨五入）。` :
      op === "round" ? `round() 是四捨五入，但剛好 .5 時取「最接近的偶數」（銀行家捨入）：round(${x}) = ${correct}。` :
      op === "floor" ? `math.floor() 往「下」（負無窮）取整：${x} → ${correct}。` : `math.ceil() 往「上」（正無窮）取整：${x} → ${correct}。`,
      `${imp}print(${call}(${x}))`);
  } });

  T.push({ u: U2, f() {
    const a = rint(2, 9), b = rint(2, 9);
    const form = rint(0, 2);
    let src, correct, wrong, exp;
    if (form === 0) {
      src = `a = ${a}\nb = ${b}\na = a + b\nb = a - b\na = a - b\nprint(a, b)`;
      correct = `${b} ${a}`; wrong = [`${a} ${b}`, `${a + b} ${b}`, `${a + b} ${a}`, `${b} ${a + b}`];
      exp = `a、b 先變成 (a+b, b)，再 b = (a+b) - b = ${a}，最後 a = (a+b) - ${a} = ${b}。結果 a、b 互換：${b} ${a}。`;
    } else if (form === 1) {
      src = `a = ${a}\nb = ${b}\na, b = b, a + b\nprint(a, b)`;
      correct = `${b} ${a + b}`; wrong = [`${a + b} ${b}`, `${b} ${a}`, `${a} ${a + b}`, `${b} ${b + b}`];
      exp = `右邊整包先算好：(b, a + b) = (${b}, ${a + b})，再一次存回左邊的 a、b。`;
    } else {
      src = `x = ${a}\ny = x\nx = x + ${b}\nprint(x, y)`;
      correct = `${a + b} ${a}`; wrong = [`${a + b} ${a + b}`, `${a} ${a + b}`, `${a} ${a}`, `${b} ${a}`];
      exp = `y = x 是把 ${a} 複製給 y；之後 x 變成 ${a + b}，不會影響 y，所以印出 ${a + b} ${a}。`;
    }
    return mk(U2, code(src) + "輸出是？", opts(correct, wrong.filter(w => w !== correct)), exp, src);
  } });

  T.push({ u: U2, f() {
    const pool = [["0", false], ["0.0", false], ['""', false], ['" "', true], ['"0"', true], ["[]", false], ["[0]", true], ["None", false], ["-1", true], ['"False"', true]];
    const ask = pick(["真", "假"]), want = ask === "真";
    const good = shuffle(pool.filter(p => p[1] === want)), bad = shuffle(pool.filter(p => p[1] !== want));
    const correct = good[0], others = bad.slice(0, 3);
    return mk(U2, `下列哪一個值放進 if 判斷時會被當成「${ask}」？`, [correct[0], ...others.map(p => p[0])],
      `只有 0、0.0、空字串、空串列、None 這些「零或空」會被當成假，其他都是真。${correct[0]} 是${ask}；其他三個是${want ? "假" : "真"}。`,
      `print(bool(${correct[0]}))`, want ? "True" : "False");
  } });

  /* ---------- 03 ---------- */
  T.push({ u: U3, f() {
    const a = pick([-1, -1, 1]) * rint(3, 40), b = pick([-1, 1, 1, 1]) * rint(2, 9);
    const q = fdiv(a, b), r = fmod(a, b);
    const correct = `${q} ${r}`;
    const wrong = [`${tdiv(a, b)} ${tmod(a, b)}`, `${r} ${q}`, `${q + 1} ${r}`, `${q} ${-r}`, `${tdiv(a, b)} ${r}`];
    return mk(U3, code(`print(${a} // ${b}, ${a} % ${b})`) + "輸出是？",
      opts(correct, wrong.filter(w => w !== correct)),
      `${a} ÷ ${b} = ${(a / b).toFixed(2).replace(/\.?0+$/, "")}，Python 的 // 往「負無窮」方向捨去得 ${q}；餘數 = ${a} - (${q}) × (${b}) = ${r}，正負號跟除數相同。驗算：${q} × ${b} + ${r} = ${a}。`,
      `print(${a} // ${b}, ${a} % ${b})`);
  } });

  T.push({ u: U3, f() {
    const x = rint(2, 9), y = rint(2, 6), z = rint(2, 5), w = rint(2, 9);
    const forms = [
      [`${x} + ${y} * ${z}`, x + y * z, [(x + y) * z], "先乘後加"],
      [`${x} * ${y} ** 2 - ${z}`, x * y ** 2 - z, [(x * y) ** 2 - z, x * (y ** 2 - z)], "** 最先、再 *、最後 -"],
      [`${x * 3} // ${y} * ${z}`, fdiv(x * 3, y) * z, [fdiv(x * 3, y * z)], "// 與 * 同層，由左往右"],
      [`${x} + ${w} % ${y} * ${z}`, x + (fmod(w, y)) * z, [(x + fmod(w, y)) * z, x + fmod(w, y * z)], "% 與 * 同層由左往右，最後才加"],
      [`2 ** ${z} ** 2`, 2 ** (z ** 2), [(2 ** z) ** 2], "** 是右結合：先算 " + z + " ** 2"],
      [`${x + 10} - ${y} - ${z}`, x + 10 - y - z, [x + 10 - (y - z)], "同層由左往右"],
    ];
    const [expr, val, wr, why] = pick(forms);
    return mk(U3, code(`print(${expr})`) + "輸出是？", opts(val, wr.filter(v => v !== val)),
      `${why}：${expr} = ${val}。`, `print(${expr})`);
  } });

  T.push({ u: U3, f() {
    const n = rint(1000, 99999);
    const kind = pick(["sum", "rev", "cnt", "odd"]);
    const ds = String(n).split("").map(Number);
    let body, ans, wrong, exp;
    if (kind === "sum") { body = "s = 0\nwhile n > 0:\n    s += n % 10\n    n //= 10\nprint(s)"; ans = ds.reduce((a, b) => a + b, 0); wrong = [n, ds.length, ans + 1, ans - 1]; exp = `逐位取出 ${[...ds].reverse().join("、")} 並累加，總和 ${ans}。`; }
    else if (kind === "rev") { body = "r = 0\nwhile n > 0:\n    r = r * 10 + n % 10\n    n //= 10\nprint(r)"; ans = Number([...ds].reverse().join("")); wrong = [n, ds.reduce((a, b) => a + b, 0), Number([...ds].reverse().join("")) + 1]; exp = `每輪把最右邊一位接到 r 的後面，等於把數字倒過來：${ans}（尾端的 0 會消失，因為它是整數）。`; }
    else if (kind === "cnt") { body = "c = 0\nwhile n > 0:\n    c += 1\n    n //= 10\nprint(c)"; ans = ds.length; wrong = [ds.length + 1, ds.length - 1, ds.reduce((a, b) => a + b, 0)]; exp = `每輪砍掉一位，砍幾次就是幾位數：${ans}。`; }
    else { body = "c = 0\nwhile n > 0:\n    if n % 10 % 2 == 1:\n        c += 1\n    n //= 10\nprint(c)"; ans = ds.filter(d => d % 2 === 1).length; wrong = [ds.length, ds.filter(d => d % 2 === 0).length, ans + 1]; exp = `逐位檢查：${ds.join("、")} 之中奇數有 ${ans} 個。`; }
    const src = `n = ${n}\n${body}`;
    return mk(U3, code(src) + "輸出是？", opts(ans, wrong.filter(v => v !== ans)), exp, src);
  } });

  T.push({ u: U3, f() {
    const s = rint(3600, 86399), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
    const pad = v => String(v).padStart(2, "0");
    const correct = `${pad(h)}:${pad(m)}:${pad(sec)}`;
    const wrong = [`${pad(h)}:${pad(Math.floor(s / 60) % 100)}:${pad(sec)}`, `${pad(h)}:${pad(sec)}:${pad(m)}`, `${pad(m)}:${pad(h)}:${pad(sec)}`, `${pad(h)}:${pad(m)}:${pad(Math.floor(s / 60) % 60)}`];
    const src = `s = ${s}\nh = s // 3600\nm = s % 3600 // 60\nsec = s % 60\nprint(f"{h:02d}:{m:02d}:{sec:02d}")`;
    return mk(U3, code(src) + "輸出是？", opts(correct, wrong.filter(w => w !== correct)),
      `${s} ÷ 3600：時 = ${h}，剩 ${s % 3600} 秒；${s % 3600} ÷ 60：分 = ${m}；秒 = ${s} % 60 = ${sec}。02d 讓每項補零成兩位。`, src);
  } });

  T.push({ u: U3, f() {
    const n = rint(20, 200), k = rint(3, 9);
    const correct = Math.floor(n / k);
    const src = `n = ${n}\nc = 0\nfor i in range(1, n + 1):\n    if i % ${k} == 0:\n        c += 1\nprint(c)`;
    return mk(U3, code(src) + "輸出是？", opts(correct, [correct + 1, correct - 1, n % k, Math.floor(n / k) + (n % k ? 1 : 0)].filter(v => v !== correct)),
      `1 到 ${n} 之間 ${k} 的倍數有 ⌊${n} ÷ ${k}⌋ = ${correct} 個（${n} = ${correct} × ${k} + ${n % k}）。`, src);
  } });

  /* ---------- 04 ---------- */
  T.push({ u: U4, f() {
    const A = rint(0, 1) === 1, B = rint(0, 1) === 1, C = rint(0, 1) === 1;
    const P = v => v ? "True" : "False";
    const forms = [
      ["a and b or c", (A && B) || C], ["a or b and c", A || (B && C)], ["not a or b", (!A) || B],
      ["not (a and b)", !(A && B)], ["a and not b or c", (A && !B) || C], ["not a and not b", !A && !B],
    ];
    const [expr, val] = pick(forms);
    const src = `a = ${P(A)}\nb = ${P(B)}\nc = ${P(C)}\nprint(${expr})`;
    const correct = P(val), wrong = [P(!val)];
    return mk(U4, code(src) + "輸出是？", [correct, P(!val), "None", "會噴錯"].map(esc),
      `優先順序 not > and > or。把 a = ${P(A)}、b = ${P(B)}、c = ${P(C)} 代入 ${expr}，結果是 ${correct}。`, src);
  } });

  T.push({ u: U4, f() {
    const isLeap = y => (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
    const ask = pick([true, false]);
    const yes = [], no = [];
    for (let i = 0; i < 60; i++) { const y = rint(1850, 2150); (isLeap(y) ? yes : no).push(y); }
    const traps = [1900, 2100, 1800, 2200], goodTraps = [2000, 1600, 2400];
    const Y = shuffle(yes.concat(goodTraps)), N = shuffle(no.concat(traps));
    const correct = ask ? Y[0] : N[0];
    const others = [...new Set((ask ? N : Y).filter(y => y !== correct))].slice(0, 3);
    if (others.length < 3) return T[T.length - 1].f();
    return mk(U4, `依照「四年一閏、逢百不閏、逢四百又閏」，下列哪一個年份是${ask ? "閏年" : "平年"}？`, [correct, ...others].map(String),
      `${correct}：${correct % 400 === 0 ? "能被 400 整除 → 閏年" : correct % 100 === 0 ? "能被 100 整除但不能被 400 整除 → 平年" : correct % 4 === 0 ? "能被 4 整除、不能被 100 整除 → 閏年" : "不能被 4 整除 → 平年"}。`,
      `y = ${correct}\nprint(${ask ? "" : "not "}((y % 4 == 0 and y % 100 != 0) or y % 400 == 0))`, "True");
  } });

  T.push({ u: U4, f() {
    const x = rint(-5, 12), y = rint(-5, 12), lo = rint(-3, 3), hi = lo + rint(3, 7);
    const forms = [
      [`${lo} < x < ${hi}`, lo < x && x < hi, `x = ${x}`],
      [`x > ${lo} or y > ${hi}`, x > lo || y > hi, `x = ${x}, y = ${y}`],
      [`not (x >= ${lo} and y <= ${hi})`, !(x >= lo && y <= hi), `x = ${x}, y = ${y}`],
      [`x % 2 == 0 and y % 2 == 0`, fmod(x, 2) === 0 && fmod(y, 2) === 0, `x = ${x}, y = ${y}`],
      [`x != y or x > 0`, x !== y || x > 0, `x = ${x}, y = ${y}`],
    ];
    const [expr, val, setup] = pick(forms);
    const src = `${setup.replace(", ", "\n").replace(/ = /g, " = ")}\nprint(${expr})`;
    return mk(U4, code(src) + "輸出是？", [val ? "True" : "False", val ? "False" : "True", "None", "會噴錯"].map(esc),
      `${setup} 代入 ${expr}，結果是 ${val ? "True" : "False"}。`, src);
  } });

  /* ---------- 05 ---------- */
  T.push({ u: U5, f() {
    const a = rint(3, 30), b = rint(3, 30), op = pick(["&", "|", "^"]);
    const fn = { "&": (x, y) => x & y, "|": (x, y) => x | y, "^": (x, y) => x ^ y };
    const val = fn[op](a, b);
    const w = Math.max(a.toString(2).length, b.toString(2).length);
    const pad = n => n.toString(2).padStart(w, "0");
    const wrong = ["&", "|", "^"].filter(o => o !== op).map(o => fn[o](a, b)).concat([a + b, val + 1]);
    return mk(U5, code(`print(${a} ${op} ${b})`) + "輸出是？", opts(val, wrong.filter(v => v !== val)),
      `${a} = ${pad(a)}、${b} = ${pad(b)}，逐位${op === "&" ? "AND（都是 1 才得 1）" : op === "|" ? "OR（有 1 就得 1）" : "XOR（不同才得 1）"} → ${pad(val)} = ${val}。`,
      `print(${a} ${op} ${b})`);
  } });

  T.push({ u: U5, f() {
    const a = rint(1, 40), k = rint(1, 4), left = pick([true, false]);
    const val = left ? a << k : a >> k;
    const wrong = [left ? a >> k : a << k, left ? a * k : Math.floor(a / k), val + 1, val * 2];
    return mk(U5, code(`print(${a} ${left ? "<<" : ">>"} ${k})`) + "輸出是？", opts(val, wrong.filter(v => v !== val)),
      left ? `左移 ${k} 位 = 乘以 2 的 ${k} 次方 = × ${2 ** k}：${a} × ${2 ** k} = ${val}。` : `右移 ${k} 位 = 除以 2 的 ${k} 次方再捨去：${a} // ${2 ** k} = ${val}。`,
      `print(${a} ${left ? "<<" : ">>"} ${k})`);
  } });

  T.push({ u: U5, f() {
    const toBin = pick([true, false]);
    const n = rint(9, 120);
    if (toBin) {
      const correct = bin(n);
      const flip = (s, i) => s.slice(0, i) + (s[i] === "1" ? "0" : "1") + s.slice(i + 1);
      const wrong = [correct.split("").reverse().join(""), flip(correct, correct.length - 1), flip(correct, 1), bin(n + 1), bin(n - 1)];
      return mk(U5, `十進位的 ${n} 轉成二進位是？`, opts(correct, wrong.filter(v => v !== correct), k => bin(n + k * 2)),
        `用「除以 2 取餘數」或拆成 2 的次方：${n} = ${correct.split("").map((b, i) => b === "1" ? 2 ** (correct.length - 1 - i) : null).filter(v => v !== null).join(" + ")}。`,
        `print(bin(${n})[2:])`);
    }
    const s = bin(n);
    const wrong = [parseInt(s.split("").reverse().join(""), 2), n + 1, n - 1, parseInt(s, 10) % 1000];
    return mk(U5, `二進位 ${s} 轉成十進位是？`, opts(n, wrong.filter(v => v !== n)),
      `把有 1 的位置權重加起來：${s.split("").map((b, i) => b === "1" ? 2 ** (s.length - 1 - i) : null).filter(v => v !== null).join(" + ")} = ${n}。`,
      `print(int("${s}", 2))`);
  } });

  T.push({ u: U5, f() {
    const k = rint(1, 4);
    const base = shuffle([rint(1, 30), rint(31, 60), rint(61, 99), rint(100, 200)]).slice(0, k + 1);
    const lone = base[0];
    const arr = shuffle(base.flatMap((v, i) => i === 0 ? [v] : [v, v]));
    const correct = lone;
    const wrong = [arr.reduce((a, b) => a + b, 0), Math.max(...arr), 0, arr.length];
    const src = `r = 0\nfor x in ${JSON.stringify(arr).replace(/,/g, ", ")}:\n    r ^= x\nprint(r)`;
    return mk(U5, code(src) + "輸出是？", opts(correct, wrong.filter(v => v !== correct)),
      `x ^ x = 0，成對的數互相抵銷，只剩落單的 ${lone}。`, src);
  } });

  T.push({ u: U5, f() {
    const k = rint(0, 5), flags = rint(1, 63);
    const op = pick(["on", "off", "toggle"]);
    const mask = 1 << k;
    const val = op === "on" ? flags | mask : op === "off" ? flags & ~mask : flags ^ mask;
    const stmt = op === "on" ? `flags |= 1 << ${k}` : op === "off" ? `flags &= ~(1 << ${k})` : `flags ^= 1 << ${k}`;
    const wrong = [flags | mask, flags & ~mask, flags ^ mask, flags & mask, flags + mask].filter(v => v !== val);
    return mk(U5, code(`flags = ${flags}   # 二進位 ${bin(flags).padStart(6, "0")}\n${stmt}\nprint(flags)`) + "輸出是？", opts(val, wrong),
      `1 << ${k} = ${mask}（二進位 ${bin(mask).padStart(6, "0")}）。${op === "on" ? "OR 讓該位變 1" : op === "off" ? "AND ~mask 讓該位變 0" : "XOR 讓該位反轉"}：結果 ${bin(val).padStart(6, "0")} = ${val}。`,
      `flags = ${flags}\n${stmt}\nprint(flags)`);
  } });

  /* ---------- 06 ---------- */
  T.push({ u: U6, f() {
    const s = rint(40, 100);
    const bad = pick([true, false]);
    const th = bad ? [60, 70, 80, 90] : [90, 80, 70, 60];
    const g = bad ? ["D", "C", "B", "A"] : ["A", "B", "C", "D"];
    let lines = "";
    th.forEach((t, i) => { lines += `${i === 0 ? "if" : "elif"} s >= ${t}:\n    print("${g[i]}")\n`; });
    lines += `else:\n    print("E")`;
    const src = `s = ${s}\n${lines}`;
    let res = "E"; for (let i = 0; i < th.length; i++) if (s >= th[i]) { res = g[i]; break; }
    const right = s >= 90 ? "A" : s >= 80 ? "B" : s >= 70 ? "C" : s >= 60 ? "D" : "E";
    const wrong = ["A", "B", "C", "D", "E"].filter(v => v !== res);
    return mk(U6, code(src) + "輸出是？", [res, ...shuffle(wrong).slice(0, 3)],
      bad ? `elif 由上往下、符合就停。條件順序是由小到大，${s} 只要 >= 60 就在第一個條件被抓走（${res}），後面全部跳過。分段判斷要從最嚴格的條件開始寫。` :
            `由上往下檢查，第一個成立的條件決定結果：${s} → ${res}（正確順序下等第應為 ${right}）。`, src);
  } });

  T.push({ u: U6, f() {
    const x = rint(-3, 14);
    const src = `x = ${x}\ny = 0\nif x > 10:\n    y += 1\nif x > 5:\n    y += 2\nelif x > 0:\n    y += 3\nelse:\n    y += 4\nprint(y)`;
    let y = 0; if (x > 10) y += 1; if (x > 5) y += 2; else if (x > 0) y += 3; else y += 4;
    const wrong = [y + 1, y - 1, 1 + 2 + 3, 3, 6].filter(v => v !== y);
    return mk(U6, code(src) + "輸出是？", opts(y, wrong),
      `這裡有「兩組」判斷：第一個單獨的 if（x > 10），以及後面的 if / elif / else（擇一）。x = ${x}：第一組${x > 10 ? "成立，y += 1" : "不成立"}；第二組${x > 5 ? "走第一個分支 y += 2" : x > 0 ? "走 elif，y += 3" : "走 else，y += 4"}。所以 y = ${y}。`, src);
  } });

  T.push({ u: U6, f() {
    const a = rint(1, 20), b = rint(1, 20), cc = rint(1, 20);
    const forms = [
      ["a >= b and a >= c", "a", a, a >= b && a >= cc], ["b >= a and b >= c", "b", b, b >= a && b >= cc], ["c >= a and c >= b", "c", cc, cc >= a && cc >= b],
    ];
    const m = Math.max(a, b, cc);
    const src = `a, b, c = ${a}, ${b}, ${cc}\nm = a\nif b > m:\n    m = b\nif c > m:\n    m = c\nprint(m)`;
    return mk(U6, code(src) + "輸出是？", opts(m, [Math.min(a, b, cc), a, a + b + cc, b].filter(v => v !== m)),
      `擂台法：先讓 m = a = ${a}，b 挑戰${b > a ? "成功" : "失敗"}，c 再挑戰，最後 m = ${m}。`, src);
  } });

  /* ---------- 07 ---------- */
  T.push({ u: U7, f() {
    const a = rint(0, 6), b = a + rint(5, 14), s = rint(1, 4);
    let total = 0, cnt = 0; for (let i = a; i < b; i += s) { total += i; cnt++; }
    const askCount = pick([true, false]);
    const src = `t = 0\nfor i in range(${a}, ${b}, ${s}):\n    t ${askCount ? "+= 1" : "+= i"}\nprint(t)`;
    let incl = 0, cnt2 = 0; for (let i = a; i <= b; i += s) { incl += i; cnt2++; }
    const val = askCount ? cnt : total;
    const wrong = askCount ? [cnt + 1, cnt - 1, b - a, cnt2] : [incl, total - a, total + b, cnt];
    return mk(U7, code(src) + "輸出是？", opts(val, wrong.filter(v => v !== val)),
      `range(${a}, ${b}, ${s}) 產生 ${(() => { const L = []; for (let i = a; i < b; i += s) L.push(i); return L.length <= 8 ? L.join("、") : L.slice(0, 4).join("、") + "、…、" + L[L.length - 1]; })()}（含 ${a}、不含 ${b}），共 ${cnt} 個，${askCount ? `所以 t = ${cnt}` : `加總是 ${total}`}。`, src);
  } });

  T.push({ u: U7, f() {
    const form = rint(0, 2), n = rint(3, 7), m = rint(3, 6);
    let val, src, exp, wrong;
    if (form === 0) { val = n * m; src = `c = 0\nfor i in range(${n}):\n    for j in range(${m}):\n        c += 1\nprint(c)`; exp = `外層 ${n} 次 × 內層 ${m} 次 = ${val}。`; wrong = [n + m, n * m + 1, n * (m - 1), (n - 1) * m]; }
    else if (form === 1) { val = n * (n + 1) / 2; src = `c = 0\nfor i in range(1, ${n + 1}):\n    for j in range(i):\n        c += 1\nprint(c)`; exp = `內層次數依序是 1、2、…、${n}，總和 ${val}（內層次數跟著外層變，不能直接相乘）。`; wrong = [n * n, n * (n - 1) / 2, n * (n + 1), val + n]; }
    else { val = n * (n + 1) / 2; src = `c = 0\nfor i in range(${n}):\n    for j in range(i, ${n}):\n        c += 1\nprint(c)`; exp = `內層次數依序是 ${n}、${n - 1}、…、1，總和 ${val}。`; wrong = [n * n, n * (n - 1) / 2, n * (n + 1), val - 1]; }
    return mk(U7, code(src) + "輸出是？", opts(val, wrong.filter(v => v !== val)), exp, src);
  } });

  T.push({ u: U7, f() {
    const lim = rint(5, 12), mod = rint(2, 4);
    const kind = pick(["break", "continue"]);
    const stopAt = rint(4, lim - 1);
    let out = [];
    for (let i = 1; i <= lim; i++) {
      if (kind === "break") { if (i === stopAt) break; out.push(i); }
      else { if (i % mod === 0) continue; out.push(i); }
    }
    const src = kind === "break"
      ? `for i in range(1, ${lim + 1}):\n    if i == ${stopAt}:\n        break\n    print(i, end=" ")`
      : `for i in range(1, ${lim + 1}):\n    if i % ${mod} == 0:\n        continue\n    print(i, end=" ")`;
    const fmt = a => a.join(" ") + " ";
    const correct = fmt(out);
    let all = []; for (let i = 1; i <= lim; i++) all.push(i);
    const wrong = kind === "break"
      ? [fmt(all.filter(i => i <= stopAt)), fmt(all.filter(i => i > stopAt)), fmt(all.filter(i => i !== stopAt)), fmt(all.filter(i => i < stopAt - 1))]
      : [fmt(all.filter(i => i % mod === 0)), fmt(all), fmt(all.filter(i => i % mod !== 0).slice(0, -1)), fmt(all.filter(i => i % mod !== 0 && i > 1))];
    return mk(U7, code(src) + "輸出是？（每個數字後面有一個空白）", opts(correct, wrong.filter(v => v !== correct), k => fmt(all.slice(0, Math.max(1, out.length - k)))),
      kind === "break" ? `break 讓整個迴圈在 i = ${stopAt} 時結束，只印出前面的數字。` : `continue 跳過 ${mod} 的倍數（不印），其他的都印出來。`, src);
  } });

  T.push({ u: U7, f() {
    const g = rint(2, 12), a0 = g * rint(2, 9), b0 = g * rint(2, 9);
    if (a0 === b0) return T[T.length - 1].f();
    const gcd = (x, y) => y === 0 ? x : gcd(y, x % y);
    const val = gcd(a0, b0);
    const src = `a, b = ${a0}, ${b0}\nwhile b != 0:\n    a, b = b, a % b\nprint(a)`;
    return mk(U7, code(src) + "輸出是？（輾轉相除法）", opts(val, [Math.min(a0, b0), Math.max(a0, b0), (a0 * b0) / val, val * 2, a0 % b0].filter(v => v !== val)),
      `輾轉相除法求最大公因數：反覆做 (a, b) → (b, a % b)，直到 b = 0，這時 a 就是答案 ${val}。`, src);
  } });

  T.push({ u: U7, f() {
    const n = rint(9, 500);
    let c = 0, m = n; while (m > 1) { m = Math.floor(m / 2); c++; }
    const src = `n = ${n}\nc = 0\nwhile n > 1:\n    n //= 2\n    c += 1\nprint(c)`;
    return mk(U7, code(src) + "輸出是？", opts(c, [c + 1, c - 1, Math.floor(n / 2), Math.ceil(Math.log2(n)) + (Number.isInteger(Math.log2(n)) ? 1 : 0)].filter(v => v !== c)),
      `每輪把 n 砍半，直到 n ≤ 1：${n} → ${(() => { const L = []; let t = n; while (t > 1) { t = Math.floor(t / 2); L.push(t); } return L.slice(0, 6).join(" → ") + (L.length > 6 ? " → …" : ""); })()}，共砍 ${c} 次。`, src);
  } });

  T.push({ u: U7, f() {
    const x = rint(2, 6), n = rint(3, 6);
    let t = 1; for (let i = 1; i <= n; i++) t *= i;
    const src = `r = 1\nfor i in range(1, ${n + 1}):\n    r *= i\nprint(r)`;
    return mk(U7, code(src) + "輸出是？", opts(t, [t / n, t * (n + 1), t + n, (n * (n + 1)) / 2].filter(v => v !== t)),
      `連乘 1 × 2 × … × ${n} = ${t}（${n} 的階乘）。累積變數 r 要從 1 開始，不能是 0。`, src);
  } });


  /* ======================= 識讀補充 08~15 ======================= */
  const U8 = "08 一維陣列與串列", U9 = "09 函式", U11 = "11 時間複雜度", U12 = "12 遞迴", U13 = "13 排序演算法", U14 = "14 搜尋演算法", U15 = "15 堆疊與佇列";
  const L = a => "[" + a.join(", ") + "]";
  const distinctList = (n, lo, hi) => { const s = new Set(); while (s.size < n) s.add(rint(lo, hi)); return [...s]; };

  T.push({ u: U8, f() {
    const a = distinctList(8, 1, 60), n = a.length;
    const form = rint(0, 4);
    let expr, val;
    if (form === 0) { const i = rint(0, 3), j = rint(i + 2, 7); expr = `a[${i}:${j}]`; val = a.slice(i, j); }
    else if (form === 1) { const k = rint(2, 4); expr = `a[::${k}]`; val = a.filter((_, i) => i % k === 0); }
    else if (form === 2) { expr = `a[::-1]`; val = a.slice().reverse(); }
    else if (form === 3) { const k = rint(2, 4); expr = `a[-${k}:]`; val = a.slice(n - k); }
    else { const k = rint(1, 3); expr = `a[:${k}] + a[-${k}:]`; val = a.slice(0, k).concat(a.slice(n - k)); }
    const correct = L(val);
    const wrong = [L(val.slice(0, -1)), L(val.slice().reverse()), L(a.slice(0, val.length)), L(val.concat([a[0]]))];
    const src = `a = ${L(a)}\nprint(${expr})`;
    return mk(U8, code(src) + "輸出是？", opts(correct, wrong.filter(v => v !== correct), k => L(val.map(x => x + k))),
      `切片含頭不含尾；a 有 ${n} 個元素，索引 0 ~ ${n - 1}，負索引 -1 是最後一個。${expr} 的結果是 ${correct}。`, src);
  } });

  T.push({ u: U8, f() {
    let a = distinctList(4, 1, 30);
    const ops = [];
    const lines = [`a = ${L(a)}`];
    const n = rint(3, 4);
    for (let k = 0; k < n; k++) {
      const op = pick(["append", "insert", "pop", "pop0", "remove"]);
      if (op === "append") { const v = rint(31, 60); a.push(v); lines.push(`a.append(${v})`); }
      else if (op === "insert") { const i = rint(0, a.length - 1), v = rint(61, 90); a.splice(i, 0, v); lines.push(`a.insert(${i}, ${v})`); }
      else if (op === "pop" && a.length > 2) { a.pop(); lines.push(`a.pop()`); }
      else if (op === "pop0" && a.length > 2) { a.shift(); lines.push(`a.pop(0)`); }
      else if (op === "remove" && a.length > 2) { const v = pick(a); a.splice(a.indexOf(v), 1); lines.push(`a.remove(${v})`); }
      else { const v = rint(31, 60); a.push(v); lines.push(`a.append(${v})`); }
    }
    lines.push("print(a)");
    const correct = L(a);
    const wrong = [L(a.slice().reverse()), L(a.slice(1)), L(a.slice(0, -1)), L(a.slice().sort((x, y) => x - y))];
    const src = lines.join("\n");
    return mk(U8, code(src) + "輸出是？", opts(correct, wrong.filter(v => v !== correct), k => L(a.map(x => x + k))),
      `依序執行每個動作並記錄串列：append 加在尾端、insert(i, x) 插在索引 i、pop() 拿走最後一個、pop(i) 拿走第 i 個、remove(x) 移除第一個等於 x 的。最後是 ${correct}。`, src);
  } });

  T.push({ u: U9, f() {
    const k = rint(2, 5), c0 = rint(1, 6), x = rint(1, 5);
    const forms = [
      [`def f(x):\n    return x * ${k} + ${c0}\nprint(f(${x}))`, x * k + c0, "先乘後加"],
      [`def f(x):\n    return x * ${k} + ${c0}\nprint(f(f(${x})))`, (x * k + c0) * k + c0, "由內往外：先算 f(" + x + ") 再拿結果代入"],
      [`def f(a, b=${k}):\n    return a + b\nprint(f(${x}), f(${x}, ${c0}))`, null, "沒給 b 就用預設值"],
      [`def f(x):\n    x = x + ${k}\n    return x\nv = ${x}\nf(v)\nprint(v)`, x, "函式裡的 x 是區域變數，外面的 v 不變；而且 f(v) 的回傳值沒有被接住"],
      [`def f(x):\n    print(x)\nr = f(${x})\nprint(r)`, null, "沒有 return 回傳 None"],
    ];
    const [src, val, why] = pick(forms);
    let correct, wrong;
    if (src.includes("b=")) { correct = `${x + k} ${x + c0}`; wrong = [`${x + k} ${x + k}`, `${x} ${x + c0}`, `${x + k} ${c0}`, `${x + c0} ${x + k}`]; }
    else if (src.includes("r = f")) { correct = `${x} None`; wrong = [`${x} ${x}`, `None None`, `None ${x}`, `${x}`]; }
    else { correct = String(val); wrong = [val + k, val - c0, x, val * 2, src.includes("f(f(") ? x * k + c0 : val + 1]; }
    const py = src.includes("r = f") ? src.replace("print(x)", 'print(x, end=" ")').replace("print(r)", "print(r)") : src;
    return mk(U9, code(src) + "輸出是？" + (src.includes("r = f") ? "（兩個 print 的輸出之間用空白隔開，這裡以空白連成一行）" : ""),
      opts(correct, wrong.filter(v => String(v) !== correct)), `${why}。結果：${correct}。`, py);
  } });

  T.push({ u: U11, f() {
    const kind = pick(["n", "n2", "n3"]), mult = rint(2, 5);
    const power = kind === "n" ? 1 : kind === "n2" ? 2 : 3;
    const label = kind === "n" ? "O(n)" : kind === "n2" ? "O(n²)" : "O(n³)";
    const correct = mult ** power;
    const wrong = [mult, mult * 2, mult ** 2, mult ** 3, mult + power, mult * power].filter(v => v !== correct);
    return mk(U11, `某演算法的時間複雜度是 ${label}。如果輸入規模 n 變成原來的 ${mult} 倍，執行時間大約變成原來的幾倍？`,
      opts(correct, wrong), `時間與 n${power === 1 ? "" : "^" + power} 成正比：${mult}${power === 1 ? "" : "^" + power} = ${correct} 倍。`, `print(${mult} ** ${power})`);
  } });

  T.push({ u: U11, f() {
    const n = rint(3, 9);
    const form = rint(0, 3);
    let src, val, exp, wrong;
    if (form === 0) { src = `c = 0\nfor i in range(${n}):\n    c += 1\nfor j in range(${n}):\n    c += 1\nprint(c)`; val = 2 * n; exp = `兩個迴圈並排是相加：${n} + ${n} = ${val}（複雜度仍是 O(n)）。`; wrong = [n * n, n, 2 * n + 1, n + 1]; }
    else if (form === 1) { const m = rint(2, 6); src = `c = 0\nfor i in range(${n}):\n    for j in range(${m}):\n        c += 1\nprint(c)`; val = n * m; exp = `巢狀相乘：${n} × ${m} = ${val}。`; wrong = [n + m, n * m + n, (n - 1) * m, n * (m - 1)]; }
    else if (form === 2) { src = `c = 0\nfor i in range(${n}):\n    for j in range(i + 1):\n        c += 1\nprint(c)`; val = n * (n + 1) / 2; exp = `內層次數 1、2、…、${n}，總和 ${val}。`; wrong = [n * n, n * (n - 1) / 2, n * (n + 1), val + 1]; }
    else { const m = 2 ** rint(3, 8); src = `n = ${m}\nc = 0\nwhile n > 1:\n    n //= 2\n    c += 1\nprint(c)`; val = Math.log2(m); exp = `每輪砍半：${m} → … → 1，共砍 log₂${m} = ${val} 次。`; wrong = [val + 1, val - 1, m / 2, m]; }
    return mk(U11, code(src) + "輸出是？（這也是「最關鍵那一行」的執行次數）", opts(val, wrong.filter(v => v !== val)), exp, src);
  } });

  T.push({ u: U12, f() {
    const kind = pick(["fact", "sum", "fib", "up", "down", "pow"]);
    let src, val, exp, wrong;
    if (kind === "fact") { const n = rint(3, 6); let r = 1; for (let i = 2; i <= n; i++) r *= i; src = `def f(n):\n    if n <= 1:\n        return 1\n    return n * f(n - 1)\nprint(f(${n}))`; val = r; exp = `f(${n}) = ${n} × f(${n - 1}) …… 一直乘到 1：${r}。`; wrong = [r / n, n * (n + 1) / 2, r + n, r * n]; }
    else if (kind === "sum") { const n = rint(3, 8); src = `def t(n):\n    if n == 0:\n        return 0\n    return n + t(n - 1)\nprint(t(${n}))`; val = n * (n + 1) / 2; exp = `t(${n}) = ${n} + t(${n - 1}) = … = 1 + 2 + … + ${n} = ${val}。`; wrong = [val - n, val + n, n * n, val + 1]; }
    else if (kind === "fib") { const n = rint(5, 9); const f = [0, 1]; for (let i = 2; i <= n; i++) f.push(f[i - 1] + f[i - 2]); src = `def fib(n):\n    if n <= 1:\n        return n\n    return fib(n - 1) + fib(n - 2)\nprint(fib(${n}))`; val = f[n]; exp = `數列 ${f.join("、")}：fib(${n}) = ${val}。`; wrong = [f[n - 1], f[n + 1] || f[n] + 1, f[n] + 1, f[n - 2]]; }
    else if (kind === "pow") { const x = rint(2, 4), n = rint(2, 5); src = `def p(x, n):\n    if n == 0:\n        return 1\n    return x * p(x, n - 1)\nprint(p(${x}, ${n}))`; val = x ** n; exp = `p(${x}, ${n}) = ${x}^${n} = ${val}。`; wrong = [x * n, x ** (n - 1), x ** (n + 1), x + n]; }
    else { const n = rint(3, 5), up = kind === "up"; src = `def p(n):\n    if n == 0:\n        return\n    ${up ? "p(n - 1)\n    print(n, end=\" \")" : "print(n, end=\" \")\n    p(n - 1)"}\np(${n})`;
      const seq = []; for (let i = 1; i <= n; i++) seq.push(i); const cor = (up ? seq : seq.slice().reverse()).join(" ") + " ";
      const oth = (up ? seq.slice().reverse() : seq).join(" ") + " ";
      return mk(U12, code(src) + "輸出是？（每個數字後面有一個空白）", opts(cor, [oth, Array(n).fill(n).join(" ") + " ", [0, ...seq].join(" ") + " ", seq.slice(1).join(" ") + " "].filter(v => v !== cor)),
        up ? `先遞迴再印：先走到最深層 p(0)，回來時才依序印 1、2、…、${n}。` : `先印再遞迴：每一層先印自己的 n，所以由 ${n} 印到 1。`, src); }
    return mk(U12, code(src) + "輸出是？", opts(val, wrong.filter(v => v !== val)), exp, src);
  } });

  T.push({ u: U13, f() {
    const a = distinctList(5, 1, 9);
    const algo = pick(["bubble", "select", "insert"]);
    const k = rint(1, 2);        // 做完第 k 輪
    const b = a.slice(); const n = b.length;
    if (algo === "bubble") { for (let i = 0; i < k; i++) for (let j = 0; j < n - 1 - i; j++) if (b[j] > b[j + 1]) { const t = b[j]; b[j] = b[j + 1]; b[j + 1] = t; } }
    else if (algo === "select") { for (let i = 0; i < k; i++) { let m = i; for (let j = i + 1; j < n; j++) if (b[j] < b[m]) m = j; const t = b[i]; b[i] = b[m]; b[m] = t; } }
    else { for (let i = 1; i <= k; i++) { const key = b[i]; let j = i - 1; while (j >= 0 && b[j] > key) { b[j + 1] = b[j]; j--; } b[j + 1] = key; } }
    const names = { bubble: "氣泡排序", select: "選擇排序", insert: "插入排序" };
    const other = a.slice().sort((x, y) => x - y);
    const wrong = [];
    ["bubble", "select", "insert"].filter(z => z !== algo).forEach(z => { const c2 = a.slice(); const nn = c2.length;
      if (z === "bubble") { for (let i = 0; i < k; i++) for (let j = 0; j < nn - 1 - i; j++) if (c2[j] > c2[j + 1]) { const t = c2[j]; c2[j] = c2[j + 1]; c2[j + 1] = t; } }
      else if (z === "select") { for (let i = 0; i < k; i++) { let m = i; for (let j = i + 1; j < nn; j++) if (c2[j] < c2[m]) m = j; const t = c2[i]; c2[i] = c2[m]; c2[m] = t; } }
      else { for (let i = 1; i <= k; i++) { const key = c2[i]; let j = i - 1; while (j >= 0 && c2[j] > key) { c2[j + 1] = c2[j]; j--; } c2[j + 1] = key; } }
      wrong.push(L(c2)); });
    wrong.push(L(other), L(a));
    const idxNote = algo === "bubble" ? `氣泡：每輪把目前最大的換到最後面。` : algo === "select" ? `選擇：每輪找出剩下最小的，換到最前面。` : `插入：每輪把下一個元素插進前面已排好的部分。`;
    const pyA = JSON.stringify(a).replace(/,/g, ", ");
    const py = algo === "bubble"
      ? `a = ${pyA}\nn = len(a)\nfor i in range(${k}):\n    for j in range(n - 1 - i):\n        if a[j] > a[j + 1]:\n            a[j], a[j + 1] = a[j + 1], a[j]\nprint(a)`
      : algo === "select"
      ? `a = ${pyA}\nn = len(a)\nfor i in range(${k}):\n    m = i\n    for j in range(i + 1, n):\n        if a[j] < a[m]:\n            m = j\n    a[i], a[m] = a[m], a[i]\nprint(a)`
      : `a = ${pyA}\nfor i in range(1, ${k + 1}):\n    key = a[i]\n    j = i - 1\n    while j >= 0 and a[j] > key:\n        a[j + 1] = a[j]\n        j -= 1\n    a[j + 1] = key\nprint(a)`;
    return mk(U13, `用${names[algo]}對 ${L(a)} 由小到大排序，做完第 ${k} 輪後，串列是？`, opts(L(b), wrong.filter(v => v !== L(b))),
      `${idxNote}做完第 ${k} 輪：${L(b)}。`, py);
  } });

  T.push({ u: U14, f() {
    const n = pick([7, 9, 11, 15]);
    const a = distinctList(n, 1, 99).sort((x, y) => x - y);
    const idx = rint(0, n - 1), t = a[idx];
    let lo = 0, hi = n - 1, steps = 0; const mids = [];
    while (lo <= hi) { const mid = Math.floor((lo + hi) / 2); steps++; mids.push(a[mid]); if (a[mid] === t) break; if (a[mid] < t) lo = mid + 1; else hi = mid - 1; }
    const askFirst = pick([true, false]);
    const py = `a = ${JSON.stringify(a).replace(/,/g, ", ")}\nt = ${t}\nlo, hi = 0, len(a) - 1\nc = 0\nm0 = None\nwhile lo <= hi:\n    mid = (lo + hi) // 2\n    c += 1\n    if m0 is None:\n        m0 = a[mid]\n    if a[mid] == t:\n        break\n    if a[mid] < t:\n        lo = mid + 1\n    else:\n        hi = mid - 1\nprint(${askFirst ? "m0" : "c"})`;
    if (askFirst) {
      const correct = mids[0];
      return mk(U14, `在已排序的 ${L(a)} 中用二分搜尋找 ${t}。（lo = 0、hi = ${n - 1}，mid = (lo + hi) // 2）第一次比較的是哪個值？`,
        opts(correct, [a[Math.floor(n / 2) - 1], a[Math.floor(n / 2) + 1], a[0], a[n - 1], t].filter(v => v !== correct), k => correct + k),
        `mid = (0 + ${n - 1}) // 2 = ${Math.floor((n - 1) / 2)}，第一次比較的是 a[${Math.floor((n - 1) / 2)}] = ${correct}。`, py);
    }
    return mk(U14, `在已排序的 ${L(a)} 中用二分搜尋找 ${t}（lo = 0、hi = ${n - 1}，mid = (lo + hi) // 2），總共會比較幾次才找到？`,
      opts(steps, [steps + 1, steps - 1, idx + 1, n].filter(v => v !== steps && v > 0)),
      `依序比較的值：${mids.join(" → ")}，共 ${steps} 次。（線性搜尋會需要 ${idx + 1} 次。）`, py);
  } });

  T.push({ u: U15, f() {
    const stack = pick([true, false]);
    const items = []; const lines = []; const cur = [];
    const n = rint(5, 7); let nextV = rint(1, 5);
    for (let i = 0; i < n; i++) {
      if (cur.length > 0 && Math.random() < 0.4) {
        if (stack) { cur.pop(); lines.push("pop"); } else { cur.shift(); lines.push("dequeue"); }
      } else { cur.push(nextV); lines.push((stack ? "push " : "enqueue ") + nextV); nextV += rint(1, 3); }
    }
    const correct = L(cur);
    const wrong = [L(cur.slice().reverse()), L(stack ? cur.slice(1) : cur.slice(0, -1)), L(cur.slice(0, -1)), L([])];
    const codeLines = stack ? ["s = []"] : ["from collections import deque", "q = deque()"];
    lines.forEach(l => { const [op, v] = l.split(" ");
      if (op === "push") codeLines.push(`s.append(${v})`); else if (op === "pop") codeLines.push("s.pop()");
      else if (op === "enqueue") codeLines.push(`q.append(${v})`); else codeLines.push("q.popleft()"); });
    codeLines.push(stack ? "print(s)" : "print(list(q))");
    return mk(U15, `${stack ? "堆疊（左為底、右為頂）" : "佇列（左為前、右為後）"}一開始是空的，依序執行：${lines.join("、")}。最後內容是？`,
      opts(correct, wrong.filter(v => v !== correct)),
      stack ? "堆疊後進先出：pop 拿走最後放進去的。" : "佇列先進先出：dequeue 拿走最前面（最早進來的）。", codeLines.join("\n"));
  } });

  /* ---------- 對外介面 ---------- */
  function make(opt) {
    const u = opt && opt.u, n = (opt && opt.n) || 5;
    const pool = T.filter(t => !u || t.u === u);
    const picked = [];
    let bag = shuffle(pool);
    for (let i = 0; i < n; i++) {
      if (!bag.length) bag = shuffle(pool);
      const t = bag.pop();
      let q = null;
      for (let k = 0; k < 6 && !q; k++) {
        try { q = t.f(); } catch (e) { q = null; }
        if (q && q.o && new Set(q.o).size < 4) q = null;
      }
      if (q) { delete q.__x; picked.push(q); }
    }
    return picked;
  }
  window.QUIZGEN = { make, templates: T, _T: T };
})();
