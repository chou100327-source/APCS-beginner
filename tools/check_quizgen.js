// 檢查 quizgen.js：每個模板各產生很多題，把 _py（對應的 Python 程式）真的跑一遍，確認和正解一致。
const fs = require("fs"), cp = require("child_process");
global.window = global;
eval(fs.readFileSync(__dirname + "/../website/quizgen.js", "utf8"));
const unesc = s => s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
let bad = 0, total = 0;
const perTemplate = +process.argv[2] || 60;
QUIZGEN.templates.forEach((t, ti) => {
  for (let i = 0; i < perTemplate; i++) {
    let q; try { q = t.f(); } catch (e) { console.log("EXC", ti, e.message); bad++; continue; }
    total++;
    const r = cp.spawnSync("python3", ["-I", "-c", q._py], { encoding: "utf8" });
    const got = (r.stdout || "").replace(/\n$/, "");
    const want = q._expect !== undefined ? q._expect : unesc(q.o[0]);
    if (r.status !== 0 || got !== want) { bad++; if (bad < 12) console.log("MISMATCH tpl", ti, "\n", q._py, "\n got:", JSON.stringify(got), "\n want:", JSON.stringify(want), r.stderr.slice(0, 200)); }
    if (new Set(q.o).size < 4) console.log("DUP options tpl", ti, q.o);
  }
});
console.log(`checked ${total}, bad ${bad}`);
