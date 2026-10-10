// Top page: counts from search/stats.json (made by the search build), new models from data/models.json, news from data/news.json.
const getJSON = url => fetch(url).then(r => { if (!r.ok) throw new Error(url + " " + r.status); return r.json(); });
const el = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  e.append(...kids);
  return e;
};

getJSON("search/stats.json").then(stats => {
  for (const dd of document.querySelectorAll("[data-stat]")) {
    const n = stats[dd.dataset.stat];
    if (typeof n === "number") dd.textContent = n.toLocaleString("ja-JP");
  }
}).catch(() => {});   // no stats yet: the dashes stay

getJSON("data/models.json").then(data => {
  const groupLabel = Object.fromEntries(data.groups.map(g => [g.id, g.label]));
  // newest first; within a day, the later entries in models.json are the newer ones
  const items = data.items.map((it, i) => ({ ...it, i })).sort((a, b) => b.added.localeCompare(a.added) || b.i - a.i);

  const hero = items.find(it => it.group !== "bus") || items[0];   // the hero shows a train: this is a railway site first
  const mv = document.getElementById("hero-mv");
  mv.src = `models/${hero.id}.${data.ext}`;
  mv.poster = `thumbs/${hero.id}.jpg`;
  const cap = document.getElementById("hero-cap");
  cap.href = `view.html#${hero.id}`;
  cap.textContent = `${groupLabel[hero.group]} · ${hero.title} →`;

  const list = document.getElementById("new-list");
  for (const it of items.slice(0, 6)) {
    const img = el("img", { src: `thumbs/${it.id}.jpg`, alt: "", loading: "lazy" });
    list.append(el("li", {}, el("a", { href: `view.html#${it.id}` },
      img, el("span", { class: "grp" }, groupLabel[it.group]), el("b", {}, it.title), el("time", { datetime: it.added }, it.added))));
  }
}).catch(() => { document.getElementById("hero-mat").hidden = true; });

getJSON("data/news.json").then(news => {
  const list = document.getElementById("news-list");
  for (const n of news.items.slice(0, 5)) {
    const title = n.url ? el("a", { href: n.url }, n.title) : n.title;
    const li = el("li", {}, el("time", { datetime: n.date }, n.date), el("b", {}, title));
    if (n.body) li.append(el("p", {}, n.body));
    list.append(li);
  }
}).catch(() => {});
