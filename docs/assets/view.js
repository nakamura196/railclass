// Viewer: list of models (cards by group) + one model on the mat. Data: data/models.json (written by skytrain/tools/gallery.py).
// view.html#<model-id> opens that model.
const fmt = s => s.map(v => v.toFixed(v % 1 ? 1 : 0)).join(" × ");

fetch("data/models.json").then(r => r.json()).then(DATA => {
  const mv = document.getElementById("mv");
  const shelf = document.getElementById("shelf");
  const byId = Object.fromEntries(DATA.items.map(i => [i.id, i]));
  const groupLabel = Object.fromEntries(DATA.groups.map(g => [g.id, g.label]));

  for (const g of DATA.groups) {
    const sec = document.createElement("section");
    const h = document.createElement("h3"); h.textContent = g.label; sec.append(h);
    const cards = document.createElement("div"); cards.className = "cards";
    for (const it of DATA.items.filter(i => i.group === g.id)) {
      const b = document.createElement("button");
      b.type = "button"; b.className = "card"; b.dataset.id = it.id;
      const img = document.createElement("img"); img.src = `thumbs/${it.id}.jpg`; img.alt = ""; img.loading = "lazy";
      const t = document.createElement("b"); t.textContent = it.title;
      const s = document.createElement("span"); s.textContent = `${fmt(it.size)} mm`;
      b.append(img, t, s);
      b.addEventListener("click", () => { show(it.id); if (matchMedia("(max-width: 900px)").matches) document.querySelector(".stage").scrollIntoView({ behavior: "smooth" }); });
      cards.append(b);
    }
    sec.append(cards); shelf.append(sec);
  }

  function show(id) {
    const it = byId[id] || DATA.items[0];
    mv.src = `models/${it.id}.${DATA.ext}`;
    mv.poster = `thumbs/${it.id}.jpg`;
    document.getElementById("grp").textContent = groupLabel[it.group];
    document.getElementById("name").textContent = it.title;
    document.getElementById("line").textContent = it.line;
    const wd = document.getElementById("wd");
    wd.replaceChildren();
    if (it.wikidata) {
      const a = document.createElement("a");
      a.href = `https://www.wikidata.org/wiki/${it.wikidata}`; a.textContent = `Wikidata ${it.wikidata}`;
      wd.append("形式: ", a);
    }
    document.getElementById("tag").textContent = `${it.id} · ${fmt(it.size)} mm · ${it.kb} KB`;
    for (const c of shelf.querySelectorAll(".card")) c.setAttribute("aria-current", c.dataset.id === it.id);
    try { history.replaceState(null, "", "#" + it.id); } catch (e) {}
  }

  for (const b of document.querySelectorAll(".views [data-orbit]")) {
    b.addEventListener("click", () => {
      mv.cameraOrbit = b.dataset.orbit; mv.fieldOfView = "auto"; mv.jumpCameraToGoal?.();
      for (const o of document.querySelectorAll(".views [data-orbit]")) o.setAttribute("aria-pressed", o === b);
    });
  }
  const spin = document.getElementById("spin");
  spin.addEventListener("click", () => {
    const on = !mv.autoRotate; mv.autoRotate = on; spin.setAttribute("aria-pressed", on);
  });

  show(location.hash.slice(1));
});
