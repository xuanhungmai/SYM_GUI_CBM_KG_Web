const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

$$(".tab").forEach(t => t.onclick = () => {
  $$(".tab").forEach(x => x.setAttribute("aria-selected", x === t));
  $$(".pane").forEach(p => p.hidden = p.id !== t.dataset.p);
});
$$("table.kg tbody").forEach(tb => tb.onclick = e => {
  const tr = e.target.closest("tr"); if (!tr) return;
  tb.querySelectorAll("tr.sel").forEach(r => r.classList.remove("sel")); tr.classList.add("sel");
});

const thr = $("#thr");
const showThr = () => $("#thrLbl").textContent = "Ngưỡng chọn P ≥ " + (+thr.value).toFixed(2);
thr.oninput = showThr;

const show = lines => { $("#out").innerHTML = lines.map(l => `<div${l.hl ? ' class="hl"' : ""}>${esc(l.t)}</div>`).join(""); };

$("#run").onclick = async () => {
  const inputs = {}; $$("select.raw").forEach(s => inputs[s.dataset.c] = s.value);
  try {
    const r = await fetch(document.body.dataset.api, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ inputs, threshold: +thr.value })
    });
    const d = await r.json();
    show(r.ok ? d.lines : [{ t: "Lỗi: " + (d.error || r.status), hl: false }]);
  } catch (e) { show([{ t: "Không kết nối được máy chủ: " + e.message, hl: false }]); }
};

$("#clear").onclick = () => { $$("select.raw").forEach(s => s.value = "0.00"); $("#out").innerHTML = ""; };
