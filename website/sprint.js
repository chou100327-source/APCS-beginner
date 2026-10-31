/* ===== 考前衝刺：一兩天快速複習（流程・必背清單・快問快答閃卡）=====
   資料在 review.js（tools/build_review.py 產生）。進度存在 localStorage。 */
(function () {
  const root = document.getElementById("sprint");
  if (!root || typeof SPRINT === "undefined") return;
  const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const md = s => esc(s).replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/`([^`]+)`/g, "<code>$1</code>");
  const load = (k, d) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } };
  const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };
  const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };

  const DONE = new Set(load("apcs.sprint.musts", []));
  const CARD = load("apcs.sprint.cards", {});          // id → 1 會 / 0 不熟
  const unitName = u => { const m = SPRINT.musts.find(x => x.u === u); return m ? `${u} ${m.n}` : u; };
  const groupOf = u => (SPRINT.musts.find(x => x.u === u) || {}).g;

  root.innerHTML = `
    <div class="sp-head">
      <h2>考前衝刺：一兩天快速複習</h2>
      <p>沒時間從頭讀時，照下面三步走：<b>① 看流程 → ② 必背清單逐條打勾 → ③ 用閃卡自我測驗</b>。進度會記在這台裝置的瀏覽器。</p>
    </div>
    <div class="sp-tabs" role="tablist">
      <button class="sp-tab active" data-p="plan">① 複習流程</button>
      <button class="sp-tab" data-p="must">② 必背清單 <span class="sp-badge" id="sp-must-badge"></span></button>
      <button class="sp-tab" data-p="cards">③ 快問快答 <span class="sp-badge" id="sp-card-badge"></span></button>
    </div>
    <div class="sp-panel" id="sp-plan"></div>
    <div class="sp-panel" id="sp-must" hidden></div>
    <div class="sp-panel" id="sp-cards" hidden></div>`;

  const go = p => {
    root.querySelectorAll(".sp-tab").forEach(b => b.classList.toggle("active", b.dataset.p === p));
    ["plan", "must", "cards"].forEach(x => { root.querySelector("#sp-" + x).hidden = x !== p; });
  };
  root.querySelectorAll(".sp-tab").forEach(b => b.onclick = () => go(b.dataset.p));

  /* ---------- ① 流程 ---------- */
  root.querySelector("#sp-plan").innerHTML = `
    <div class="sp-day">
      <div class="sp-day-h"><span class="sp-day-n">第 1 天</span><span class="sp-day-t">初級核心（約 70 分鐘）</span></div>
      <ol>
        <li><b>必背清單 01～07</b>（約 25 分鐘）：逐條讀、會的打勾，不確定的回頭翻該單元。 <a href="#" data-go="must">打開必背清單</a></li>
        <li><b>快問快答：只選「初級」</b>（約 20 分鐘）：答「還不熟」的會一直回來，直到都會。 <a href="#" data-go="cards">打開閃卡</a></li>
        <li><b>觀念題「初級（全部單元）」測一輪</b>（約 15 分鐘），再做「錯題重練」。</li>
        <li><b>實作題挑 2 題重寫一次</b>（約 10 分鐘看思路即可）：第 6 題位元開關、第 10 題質數篩選。</li>
      </ol>
    </div>
    <div class="sp-day">
      <div class="sp-day-h"><span class="sp-day-n">第 2 天</span><span class="sp-day-t">程式識讀補充＋收尾（約 60 分鐘）</span></div>
      <ol>
        <li><b>必背清單 08～12</b>（陣列、函式、題型技巧、複雜度、遞迴）：這 5 個最重要，約 20 分鐘。</li>
        <li><b>必背清單 13～15</b>（排序、搜尋、堆疊佇列）：快速掃過，約 10 分鐘。</li>
        <li><b>快問快答：選「識讀補充」</b>約 15 分鐘，再到觀念題選「識讀題型」測一輪。</li>
        <li>看一遍「考前地雷提醒」與「解題與考場流程」（本頁往下捲），約 10 分鐘。</li>
        <li><b>早點睡。</b>前一晚不要再學新東西。</li>
      </ol>
    </div>
    <div class="sp-note">
      <b>如果只考「程式實作」</b>：第 2 天可以略過 08～15，改成把實作題 11 題各看一次思路；
      <b>如果兩科都考</b>：照上面兩天走；<b>只剩一天</b>：做第 1 天的 ①②，再挑第 2 天的 08、09、11、12。
    </div>
    <div class="sp-note sp-warn">
      考場提醒：觀念題先掃一遍把會的寫完、卡超過 2 分鐘先跳；實作題從第 1 題按順序寫；
      <b>只印答案、不印提示文字</b>；送出前用範例輸入逐字比對輸出。
    </div>`;
  root.querySelectorAll("#sp-plan a[data-go]").forEach(a => a.onclick = e => { e.preventDefault(); go(a.dataset.go); root.scrollIntoView({ behavior: "smooth", block: "start" }); });

  /* ---------- ② 必背清單 ---------- */
  const total = SPRINT.musts.reduce((n, m) => n + m.items.length, 0);
  const mustPanel = root.querySelector("#sp-must");
  function renderMust(onlyTodo) {
    const groups = ["初級", "識讀補充"];
    mustPanel.innerHTML = `
      <div class="sp-bar">
        <span id="sp-must-prog"></span>
        <label class="sp-check"><input type="checkbox" id="sp-todo" ${onlyTodo ? "checked" : ""}> 只看還沒打勾的</label>
        <button class="btn ghost" id="sp-must-reset">全部取消打勾</button>
      </div>` + groups.map(g => `
      <div class="sp-group">${g === "初級" ? "初級（實作與識讀都會用到）" : "程式識讀補充（依重要程度：越前面越重要）"}</div>` +
      SPRINT.musts.filter(m => m.g === g).map(m => {
        const items = m.items.filter(it => !onlyTodo || !DONE.has(it.id));
        if (!items.length) return "";
        const done = m.items.filter(it => DONE.has(it.id)).length;
        return `<details class="sp-unit" ${done < m.items.length ? "open" : ""}>
          <summary><span>${esc(m.u + " " + m.n)}</span><span class="sp-cnt">${done}/${m.items.length}</span></summary>
          <ul>${items.map(it => `<li><label><input type="checkbox" data-id="${it.id}" ${DONE.has(it.id) ? "checked" : ""}><span>${md(it.t)}</span></label></li>`).join("")}</ul>
        </details>`;
      }).join("")).join("");
    mustPanel.querySelectorAll("input[data-id]").forEach(cb => cb.onchange = () => {
      cb.checked ? DONE.add(cb.dataset.id) : DONE.delete(cb.dataset.id);
      save("apcs.sprint.musts", [...DONE]); updateProg();
      cb.closest("li").classList.toggle("done", cb.checked);
      const d = cb.closest("details"); if (d) { const all = d.querySelectorAll("input[data-id]"); }
      refreshCounts();
    });
    mustPanel.querySelectorAll("input[data-id]:checked").forEach(cb => cb.closest("li").classList.add("done"));
    mustPanel.querySelector("#sp-todo").onchange = e => renderMust(e.target.checked);
    mustPanel.querySelector("#sp-must-reset").onclick = () => { if (confirm("要把必背清單的打勾全部取消嗎？")) { DONE.clear(); save("apcs.sprint.musts", []); renderMust(false); updateProg(); } };
    updateProg();
  }
  function refreshCounts() {
    mustPanel.querySelectorAll("details.sp-unit").forEach(d => {
      const unit = d.querySelector("summary span").textContent.slice(0, 2);
      const m = SPRINT.musts.find(x => x.u === unit);
      d.querySelector(".sp-cnt").textContent = `${m.items.filter(it => DONE.has(it.id)).length}/${m.items.length}`;
    });
  }
  function updateProg() {
    const n = [...DONE].filter(id => SPRINT.musts.some(m => m.items.some(it => it.id === id))).length;
    const el = mustPanel.querySelector("#sp-must-prog");
    if (el) el.textContent = `已記住 ${n} / ${total} 條`;
    const b = root.querySelector("#sp-must-badge"); if (b) b.textContent = `${n}/${total}`;
  }
  renderMust(false);

  /* ---------- ③ 閃卡 ---------- */
  const cardPanel = root.querySelector("#sp-cards");
  let deck = [], pos = 0, shown = false, filter = "初級";
  function buildDeck() {
    let cs = SPRINT.cards.slice();
    if (filter === "初級") cs = cs.filter(c => groupOf(c.u) === "初級");
    else if (filter === "識讀補充") cs = cs.filter(c => groupOf(c.u) === "識讀補充");
    else if (filter === "todo") cs = cs.filter(c => CARD[c.id] !== 1);
    else if (filter !== "all") cs = cs.filter(c => c.u === filter);
    // 還不熟與沒看過的優先，會的放後面
    const first = shuffle(cs.filter(c => CARD[c.id] !== 1)), rest = shuffle(cs.filter(c => CARD[c.id] === 1));
    deck = first.concat(rest); pos = 0; shown = false;
  }
  function stats() {
    const k = Object.values(CARD).filter(v => v === 1).length, w = Object.values(CARD).filter(v => v === 0).length;
    const b = root.querySelector("#sp-card-badge"); if (b) b.textContent = `${k}/${SPRINT.cards.length}`;
    return { k, w, n: SPRINT.cards.length - k - w };
  }
  function renderCards() {
    const st = stats();
    const opts = [["初級", "初級（01～07）"], ["識讀補充", "識讀補充（08～15）"], ["all", "全部"], ["todo", "只看還沒學會的"]]
      .concat(SPRINT.musts.map(m => [m.u, `單元 ${m.u} ${m.n}`]));
    const c = deck[pos];
    cardPanel.innerHTML = `
      <div class="sp-bar">
        <label>範圍：<select id="sp-filter">${opts.map(([v, t]) => `<option value="${v}" ${v === filter ? "selected" : ""}>${esc(t)}</option>`).join("")}</select></label>
        <span class="sp-stat"><b class="ok">會 ${st.k}</b>　<b class="no">不熟 ${st.w}</b>　未看 ${st.n}</span>
        <button class="btn ghost" id="sp-card-reset">重置閃卡進度</button>
      </div>` + (c ? `
      <div class="sp-card" id="sp-card">
        <div class="sp-card-u">${esc(unitName(c.u))}　<span>${pos + 1} / ${deck.length}</span></div>
        <div class="sp-card-q">${md(c.q)}</div>
        <div class="sp-card-a" ${shown ? "" : "hidden"}>${md(c.a)}</div>
        <div class="sp-card-btns">
          ${shown ? `<button class="btn" id="sp-no">還不熟</button><button class="btn primary" id="sp-yes">我會了</button>`
                  : `<button class="btn primary" id="sp-show">看答案（先在心裡想）</button>`}
        </div>
      </div>` : `<div class="sp-empty">這個範圍沒有卡片了。選別的範圍，或按「重置閃卡進度」重新來過。</div>`);
    cardPanel.querySelector("#sp-filter").onchange = e => { filter = e.target.value; buildDeck(); renderCards(); };
    cardPanel.querySelector("#sp-card-reset").onclick = () => { if (confirm("要清掉閃卡的進度嗎？")) { Object.keys(CARD).forEach(k => delete CARD[k]); save("apcs.sprint.cards", CARD); buildDeck(); renderCards(); } };
    const show = cardPanel.querySelector("#sp-show"); if (show) show.onclick = () => { shown = true; renderCards(); };
    const mark = v => { CARD[c.id] = v; save("apcs.sprint.cards", CARD);
      if (v === 0) { deck.push(deck.splice(pos, 1)[0]); }       // 還不熟：排到最後面，稍後再出現
      else pos++;
      if (pos >= deck.length) { const left = deck.filter(x => CARD[x.id] !== 1); if (left.length) { deck = shuffle(left); pos = 0; } else { pos = deck.length; } }
      shown = false; renderCards(); };
    const no = cardPanel.querySelector("#sp-no"), yes = cardPanel.querySelector("#sp-yes");
    if (no) no.onclick = () => mark(0); if (yes) yes.onclick = () => mark(1);
  }
  buildDeck(); renderCards();
})();
