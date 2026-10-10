// Search page: loads index.json (made by tools/build_search.py) and filters it in the browser.
// The page (SearchPage.astro) passes the language, the URLs and the display text in #search-data.
// The facets come from the index, which copies them from docs/rdf/facets.json; nothing is listed here by hand.
// State lives in the URL: ?q=&<facet>=v1,v2 (iri; "none" = no value) | <facet>=min-max (numbers) | <facet>=1 (boolean)
//                         &sort=&per=&page=&view=grid|list
(() => {
"use strict";
const $ = id => document.getElementById(id);
const C = JSON.parse(document.getElementById("search-data").textContent), S = C.text, JA = C.lang === "ja";
const fmt = (s, o) => s.replace(/\{(\w+)\}/g, (_, k) => o[k]);
const el = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v; else if (k === "text") e.textContent = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else if (v !== false && v != null) e.setAttribute(k, v);
  }
  e.append(...kids.filter(k => k != null));
  return e;
};
const norm = s => (s || "").normalize("NFKC").toLowerCase().replace(/[\s\p{P}\p{S}]+/gu, "");
const words = s => " " + (s || "").normalize("NFKC").toLowerCase().replace(/[\s\p{P}\p{S}]+/gu, " ").trim();
// Latin terms match from the start of a word ("ice" finds "ICE 4", not "Service"); terms with CJK match anywhere.
const CJK = /[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}]/u;
const hit = (t, i) => CJK.test(t) ? text[i].includes(t) : text[i].includes(" " + t);
const COMMONS = "https://commons.wikimedia.org/wiki/Special:FilePath/";
const THUMB = "https://thumb.wikimedia.org/wikipedia/commons/thumb/";   // + hash dir + "/" + file + "/330px-" + file
const FILEPAGE = "https://commons.wikimedia.org/wiki/File:";
const NUM = new Set(["decimal", "integer", "gYear"]);
const fmtN = n => n.toLocaleString(C.locale);

let D, F, text, state;

// Text in the page's language, the other language when there is none.
function L(lbl) { return (JA ? lbl.ja || lbl.en : lbl.en || lbl.ja) || ""; }
function name(i) { return (JA ? D.ja[i] || D.en[i] : D.en[i] || D.ja[i]) || D.id[i]; }
function other(i) { const o = JA ? D.en[i] : D.ja[i]; return D.ja[i] && D.en[i] && D.ja[i] !== D.en[i] ? o : null; }
function vlabel(f, k) { const v = f.values[k]; return (JA ? v[2] || v[1] : v[1] || v[2]) || v[0]; }
const unit = f => f.unit ? fmt(S.unit, { u: f.unit }) : "";

// ---- URL <-> state
function readURL() {
  const p = new URLSearchParams(location.search);
  const s = { q: p.get("q") || "", f: {}, sort: p.get("sort") || "rec", per: +p.get("per") || 24,
              page: Math.max(1, +p.get("page") || 1), view: p.get("view") === "list" ? "list" : "grid" };
  for (const f of F) {
    const v = p.get(f.id); if (!v) continue;
    if (f.datatype === "iri") {
      const pos = new Map(f.values.map((x, k) => [x[0], k]));
      const set = new Set(v.split(",").map(x => x === "none" ? -1 : pos.get(x)).filter(x => x !== undefined));
      if (set.size) s.f[f.id] = set;
    } else if (NUM.has(f.datatype)) {
      const [a, b] = v.split("-").map(x => x === "" ? null : +x);
      if (a != null || b != null) s.f[f.id] = { min: a, max: b };
    } else if (f.datatype === "boolean" && v === "1") s.f[f.id] = true;
  }
  return s;
}
function writeURL(push) {
  const p = new URLSearchParams();
  if (state.q) p.set("q", state.q);
  for (const f of F) {
    const v = state.f[f.id]; if (v == null) continue;
    if (f.datatype === "iri") p.set(f.id, [...v].map(k => k === -1 ? "none" : f.values[k][0]).join(","));
    else if (NUM.has(f.datatype)) p.set(f.id, `${v.min ?? ""}-${v.max ?? ""}`);
    else p.set(f.id, "1");
  }
  if (state.sort !== "rec") p.set("sort", state.sort);
  if (state.per !== 24) p.set("per", state.per);
  if (state.page > 1) p.set("page", state.page);
  if (state.view !== "grid") p.set("view", state.view);
  const url = location.pathname + (p.toString() ? "?" + p : "");
  try { history[push ? "pushState" : "replaceState"](null, "", url); } catch (e) {}
}

// ---- filtering
function pass(f, i) {
  const v = state.f[f.id], col = D[f.id];
  if (f.datatype === "iri") {
    const vals = col[i];
    if (!vals.length) return v.has(-1);
    for (const k of vals) if (v.has(k)) return true;
    return false;
  }
  if (NUM.has(f.datatype)) {
    const x = col[i];
    return x != null && (v.min == null || x >= v.min) && (v.max == null || x <= v.max);
  }
  return !!col[i];
}

// One pass over the items: an item that fails no filter is a hit and counts for every facet;
// an item that fails exactly one filter counts only for that facet (so each facet shows what choosing it would give).
function run() {
  const terms = state.q.split(/\s+/).map(norm).filter(Boolean);
  const active = F.filter(f => state.f[f.id] != null);
  const counts = Object.fromEntries(F.map(f => [f.id, f.datatype === "iri" ? new Map() : { n: 0, min: Infinity, max: -Infinity }]));
  const hits = [];
  const add = (f, i) => {
    const c = counts[f.id], x = D[f.id][i];
    if (f.datatype === "iri") { if (!x.length) c.set(-1, (c.get(-1) || 0) + 1); for (const k of x) c.set(k, (c.get(k) || 0) + 1); }
    else if (NUM.has(f.datatype)) { if (x != null) { c.n++; if (x < c.min) c.min = x; if (x > c.max) c.max = x; } }
    else if (x) c.n++;
  };
  for (let i = 0; i < D.n; i++) {
    if (terms.length && !terms.every(t => hit(t, i))) continue;
    let failed = null, nf = 0;
    for (const f of active) if (!pass(f, i)) { failed = f; if (++nf > 1) break; }
    if (nf === 0) { hits.push(i); for (const f of F) add(f, i); }
    else if (nf === 1) add(failed, i);
  }
  return { hits, counts };
}

function sorters() {
  const out = [["rec", S.sortRec], ["name", S.sortName]];
  for (const f of F) if (NUM.has(f.datatype)) {
    out.push([f.id + "-desc", fmt(S.sortDesc, { f: L(f.label) })], [f.id + "-asc", fmt(S.sortAsc, { f: L(f.label) })]);
  }
  return out;
}
const coll = new Intl.Collator(C.lang);
function sort(hits) {
  const s = state.sort;
  if (s === "name") return hits.sort((a, b) => coll.compare(name(a), name(b)));
  const m = s.match(/^(.+)-(asc|desc)$/);
  if (m && D[m[1]]) {
    const col = D[m[1]], dir = m[2] === "asc" ? 1 : -1;
    return hits.sort((a, b) => (col[a] == null) - (col[b] == null) || dir * (col[a] - col[b]));
  }
  const score = i => (D.models[i].length ? 2 : 0) + (D.img[i] ? 1 : 0);
  return hits.sort((a, b) => score(b) - score(a) || coll.compare(name(a), name(b)));
}

// ---- facets panel
const openFacets = new Set(["kind", "country", "has3d"]);
const showAll = new Set();
const findText = {};
function renderFacets(counts) {
  const box = $("facets"); box.replaceChildren();
  for (const f of F) {
    const v = state.f[f.id];
    const d = el("details", { class: "facet", open: openFacets.has(f.id) || v != null });
    d.addEventListener("toggle", () => d.open ? openFacets.add(f.id) : openFacets.delete(f.id));
    const on = v == null ? null : el("span", { class: "on", text: f.datatype === "iri" ? fmt(S.chosen, { n: v.size }) : S.set });
    d.append(el("summary", {}, el("span", { text: L(f.label) + unit(f) }), on));
    const c = counts[f.id];
    if (f.datatype === "iri") {
      const sel = v || new Set();
      let keys = [...new Set([...c.keys(), ...sel])].filter(k => k !== -1);
      keys.sort((a, b) => sel.has(b) - sel.has(a) || (c.get(b) || 0) - (c.get(a) || 0));
      if (f.values.length > 12) {
        const inp = el("input", { class: "find", type: "search", placeholder: S.findIn, value: findText[f.id] || "", "aria-label": fmt(S.findInLabel, { f: L(f.label) }) });
        inp.addEventListener("input", () => { findText[f.id] = inp.value; renderFacets(counts); const n = $("facets").querySelector(`[data-fid="${f.id}"] .find`); n.focus(); n.setSelectionRange(n.value.length, n.value.length); });
        d.append(inp); d.dataset.fid = f.id;
      }
      const ft = norm(findText[f.id]);
      if (ft) keys = keys.filter(k => norm(f.values[k].join(" ")).includes(ft));
      const lim = showAll.has(f.id) || ft ? keys.length : 8;
      const ul = el("ul");
      const item = (k, label) => {
        const n = c.get(k) || 0;
        const cb = el("input", { type: "checkbox", checked: sel.has(k) });
        cb.addEventListener("change", () => {
          const s = new Set(state.f[f.id] || []); cb.checked ? s.add(k) : s.delete(k);
          if (s.size) state.f[f.id] = s; else delete state.f[f.id];
          state.page = 1; update(true);
        });
        return el("li", { class: n || sel.has(k) ? "" : "zero" }, el("label", {}, cb, el("span", { text: label }), el("span", { class: "n", text: fmtN(n) })));
      };
      for (const k of keys.slice(0, lim)) ul.append(item(k, vlabel(f, k)));
      if (!ft && (c.get(-1) || sel.has(-1)) && (lim >= keys.length)) ul.append(item(-1, S.noValueItem));
      d.append(ul);
      if (!ft && keys.length > 8) {
        d.append(el("button", { type: "button", class: "more", text: showAll.has(f.id) ? S.less : fmt(S.all, { n: fmtN(keys.length) }),
          onclick: () => { showAll.has(f.id) ? showAll.delete(f.id) : showAll.add(f.id); renderFacets(counts); } }));
      }
    } else if (NUM.has(f.datatype)) {
      const cur = v || {};
      const inp = (key, ph) => {
        const i = el("input", { type: "number", inputmode: "numeric", placeholder: ph, value: cur[key] ?? "", "aria-label": fmt(key === "min" ? S.min : S.max, { f: L(f.label) }) });
        i.addEventListener("change", () => {
          const r = { ...(state.f[f.id] || {}) }; r[key] = i.value === "" ? null : +i.value;
          if (r.min == null && r.max == null) delete state.f[f.id]; else state.f[f.id] = r;
          state.page = 1; update(true);
        });
        return i;
      };
      const has = c.n > 0;
      d.append(el("div", { class: "range" }, inp("min", has ? String(c.min) : ""), el("span", { text: S.to }), inp("max", has ? String(c.max) : "")));
      d.append(el("p", { class: "hint", text: has ? fmt(S.withValue, { n: fmtN(c.n), min: c.min, max: c.max }) : S.noneWithValue }));
    } else {
      const cb = el("input", { type: "checkbox", checked: !!v });
      cb.addEventListener("change", () => { cb.checked ? state.f[f.id] = true : delete state.f[f.id]; state.page = 1; update(true); });
      d.append(el("ul", {}, el("li", {}, el("label", {}, cb, el("span", { text: S.yes }), el("span", { class: "n", text: fmtN(c.n) })))));
    }
    box.append(d);
  }
}

function renderChips() {
  const box = $("chips"); box.replaceChildren();
  const chip = (label, drop) => box.append(el("button", { type: "button", class: "chip", text: label, onclick: () => { drop(); state.page = 1; update(true); } }));
  if (state.q) chip(fmt(S.quote, { q: state.q }), () => { state.q = ""; $("q").value = ""; });
  for (const f of F) {
    const v = state.f[f.id]; if (v == null) continue;
    if (f.datatype === "iri") for (const k of v) chip(`${L(f.label)}: ${k === -1 ? S.noValue : vlabel(f, k)}`, () => { v.delete(k); if (!v.size) delete state.f[f.id]; });
    else if (NUM.has(f.datatype)) chip(`${L(f.label)}: ${v.min ?? ""}${S.to}${v.max ?? ""}${f.unit ? " " + f.unit : ""}`, () => delete state.f[f.id]);
    else chip(L(f.label), () => delete state.f[f.id]);
  }
  if (box.children.length > 1) box.append(el("button", { type: "button", class: "chip clear", text: S.clear, onclick: () => { state.f = {}; state.q = ""; $("q").value = ""; state.page = 1; update(true); } }));
}

// ---- results
const iriFacets = () => F.filter(f => f.datatype === "iri" && !f.of).slice(0, 2);   // the first two value facets (type, country) are shown on each result; group facets (f.of) are not
const numFacets = () => F.filter(f => NUM.has(f.datatype));
// Classes described in this site's RDF open their page (rdf/class/<id>.html, in this language); the others open Wikidata.
function href(i) { return D.page[i] ? `${C.classPage}${D.id[i]}.html` : `https://www.wikidata.org/wiki/${D.id[i]}`; }
function vals(f, i, max = 2) { const x = D[f.id][i]; return x.slice(0, max).map(k => vlabel(f, k)).join(S.sep) + (x.length > max ? S.more : ""); }
function numText(f, i) { const x = D[f.id][i]; return x == null ? "" : f.datatype === "gYear" ? fmt(S.year, { y: x }) : `${fmtN(x)}${f.unit ? " " + f.unit : ""}`; }

// The photo's URL: the thumbnail address from the index when there is one (one request), else Special:FilePath (a redirect).
function photo(i) {
  const f = D.img[i], t = D.thumb ? D.thumb[i] : "";
  if (!f) return null;
  if (t.length > 4) return t;
  if (t) { const u = encodeURIComponent(f.replace(/ /g, "_")); return `${THUMB}${t}/${u}/330px-${u}`; }
  return COMMONS + encodeURIComponent(f) + "?width=330";
}
// Credit line under a Commons photo: author (links to the file page, which has the full terms) and licence (links to it).
function credit(i) {
  const f = D.img[i]; if (!f || D.models[i].length) return null;
  const c = D.credit ? D.credit[i] : 0;
  const page = FILEPAGE + encodeURIComponent(f.replace(/ /g, "_"));
  if (!c) return el("p", { class: "credit" }, el("a", { href: page, text: S.photoCommons }));
  const who = D.artists[c[0]] || S.unknownAuthor, [lic, url] = D.licenses[c[1]];
  return el("p", { class: "credit", title: fmt(S.creditTitle, { who, lic: lic || S.unknownLicence }) },
    el("a", { href: page, text: fmt(S.photoBy, { who }) }), el("span", { text: "/" }), url ? el("a", { href: url, text: lic, rel: "license" }) : (lic || S.unknownLicence));
}

function card(i) {
  const m = D.models[i];
  const ph = el("div", { class: "ph" + (m.length ? " model" : "") });
  const src = m.length ? `${C.thumbs}${m[0]}.jpg` : photo(i);
  ph.append(src ? el("img", { src, alt: "", loading: "lazy", decoding: "async" }) : el("span", { class: "none", text: S.noPhoto }));
  if (m.length) ph.append(el("span", { class: "badge", text: m.length > 1 ? `3D ×${m.length}` : "3D" }));
  const meta = [...iriFacets().slice(1).map(f => vals(f, i)), ...numFacets().map(f => numText(f, i))].filter(Boolean).join(" · ");
  return el("div", { class: "card" }, el("a", { class: "main", href: href(i) }, ph,
    el("div", { class: "tx" }, el("b", { text: name(i) }), other(i) ? el("span", { class: "sub", text: other(i) }) : null,
      el("span", { class: "sub", text: iriFacets()[0] ? vals(iriFacets()[0], i) : "" }), meta ? el("span", { class: "meta", text: meta }) : null)),
    credit(i));
}
function table(rows) {
  const ff = iriFacets(), nf = numFacets();
  const head = el("tr", {}, el("th", { text: S.name }), ...ff.map((f, k) => el("th", { class: k ? "" : "hide-s", text: L(f.label) })),
    ...nf.map(f => el("th", { class: "num hide-s", text: L(f.label) })));
  const body = rows.map(i => el("tr", {},
    el("td", {}, el("a", { href: href(i), text: name(i) }), D.models[i].length ? el("span", { class: "tag3d", text: "3D" }) : null,
      other(i) ? el("span", { class: "sub", text: other(i) }) : null),
    ...ff.map((f, k) => el("td", { class: k ? "" : "hide-s", text: vals(f, i, 3) })),
    ...nf.map(f => el("td", { class: "num hide-s", text: numText(f, i) }))));
  return el("table", { class: "list" }, el("thead", {}, head), el("tbody", {}, ...body));
}

function renderPager(total) {
  const box = $("pager"); box.replaceChildren();
  const pages = Math.ceil(total / state.per); if (pages <= 1) return;
  const go = p => el("button", { type: "button", text: String(p), "aria-current": p === state.page ? "page" : false,
    onclick: () => { state.page = p; update(true); scrollTo({ top: 0 }); } });
  box.append(el("button", { type: "button", text: S.prev, disabled: state.page === 1, onclick: () => { state.page--; update(true); scrollTo({ top: 0 }); } }));
  const show = new Set([1, pages, state.page - 2, state.page - 1, state.page, state.page + 1, state.page + 2]);
  let last = 0;
  for (let p = 1; p <= pages; p++) if (show.has(p)) { if (p - last > 1) box.append(el("span", { text: "…" })); box.append(go(p)); last = p; }
  box.append(el("button", { type: "button", text: S.next, disabled: state.page === pages, onclick: () => { state.page++; update(true); scrollTo({ top: 0 }); } }));
}

function update(push) {
  const { hits, counts } = run();
  sort(hits);
  const pages = Math.max(1, Math.ceil(hits.length / state.per));
  if (state.page > pages) state.page = pages;
  const from = (state.page - 1) * state.per, rows = hits.slice(from, from + state.per);
  $("count").replaceChildren(el("b", { text: fmtN(hits.length) }), fmt(hits.length ? S.countRange : S.count, { a: fmtN(from + 1), b: fmtN(from + rows.length) }));
  const out = $("out");
  if (!hits.length) out.replaceChildren(el("p", { class: "empty", text: S.empty }));
  else out.replaceChildren(state.view === "grid" ? el("div", { class: "grid" }, ...rows.map(card)) : table(rows));
  for (const b of document.querySelectorAll(".seg button")) b.setAttribute("aria-pressed", b.dataset.view === state.view);
  $("sort").value = state.sort; $("per").value = String(state.per);
  renderFacets(counts); renderChips(); renderPager(hits.length);
  writeURL(push);
}

async function init() {
  try {
    D = await (await fetch(C.index)).json();
  } catch (e) {
    $("count").textContent = S.loadError; return;
  }
  F = D.facets;
  text = D.id.map((q, i) => `${words(D.en[i])}${words(D.ja[i])} ${norm(D.en[i])} ${norm(D.ja[i])} ${q.toLowerCase()}`);
  $("sort").replaceChildren(...sorters().map(([v, t]) => el("option", { value: v, text: t })));
  state = readURL();
  $("q").value = state.q;
  let timer;
  $("q").addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(() => { state.q = $("q").value.trim(); state.page = 1; update(false); }, 200); });
  $("sort").addEventListener("change", e => { state.sort = e.target.value; state.page = 1; update(true); });
  $("per").addEventListener("change", e => { state.per = +e.target.value; state.page = 1; update(true); });
  for (const b of document.querySelectorAll(".seg button")) b.addEventListener("click", () => { state.view = b.dataset.view; update(true); });
  $("ftoggle").addEventListener("click", () => { const o = $("facets").classList.toggle("open"); $("ftoggle").setAttribute("aria-expanded", o); });
  addEventListener("popstate", () => { state = readURL(); $("q").value = state.q; update(false); });
  update(false);
}
init();
})();
