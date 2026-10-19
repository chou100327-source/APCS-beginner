// 檢查 guides.js：每一題的參考解答都要通過 problems.js 裡的全部測資。
const fs = require("fs"), cp = require("child_process");
global.window = global;
eval(fs.readFileSync(__dirname + "/../website/problems.js", "utf8") + ";global.PROBLEMS = PROBLEMS;");
eval(fs.readFileSync(__dirname + "/../website/guides.js", "utf8") + ";global.GUIDES = GUIDES;");
const norm = s => s.replace(/\r\n/g, "\n").split("\n").map(l => l.replace(/[ \t]+$/, "")).join("\n").replace(/\n+$/, "");
let bad = 0;
for (const p of PROBLEMS) {
  const g = GUIDES[p.id];
  if (!g) { console.log("沒有 guide:", p.id); bad++; continue; }
  for (const t of p.tests) {
    const r = cp.spawnSync("python3", ["-I", "-c", g.solution], { input: t.in, encoding: "utf8" });
    if (norm(r.stdout) !== norm(t.out)) { bad++; console.log("FAIL", p.id, JSON.stringify(t.in), "got", JSON.stringify(r.stdout), "want", JSON.stringify(t.out), r.stderr.slice(0, 120)); }
  }
  // 骨架必須含有空格標記（____），否則不是填空
  if (!g.skeleton.includes("__")) { console.log("骨架沒有空格", p.id); bad++; }
}
console.log(bad ? "有問題 " + bad : "全部 " + PROBLEMS.length + " 題的參考解答都通過所有測資");
