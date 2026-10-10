// Checks the built site (web/dist) against the data it was built from, so a change in the data's shape cannot silently
// empty the pages again (2026-10-10: the class JSON-LD became an @graph, the pages lost their name and their 3D viewer,
// and the build still passed). The expected values are read another way than the pages read them: the 3D models and
// labels from the Turtle (not the JSON-LD), the lines from tools/class_lines.tsv and docs/lines/.
// Usage (after npm run build): npm test        Exit 1 with the list of failures.
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../../", import.meta.url));
const dist = root + "web/dist/";
const docs = root + "docs/";
const bad = [];
const fail = (where, what) => bad.push(`${where}: ${what}`);
const read = p => readFileSync(p, "utf8");
let checked = 0;

if (!existsSync(dist + "index.html")) { console.error("check: no web/dist (run npm run build first)"); process.exit(1); }

// Classes, from the Turtle
const CLS = docs + "rdf/class/";
const classes = readdirSync(CLS).filter(f => f.endsWith(".ttl")).map(f => f.slice(0, -4)).sort();
if (classes.length === 0) fail("docs/rdf/class", "no class RDF");
const ttl = Object.fromEntries(classes.map(c => [c, read(CLS + c + ".ttl")]));
const modelsOf = c => {
  const m = ttl[c].match(/schema:subjectOf\s+([^;.]+)/);
  return m ? [...m[1].matchAll(/mdl:([\w-]+)/g)].map(x => x[1]) : [];
};
const exact = c => ttl[c].match(/skos:exactMatch\s+wd:(Q\d+)/)?.[1] ?? null;

// Lines, from the table and the cut-out shapes
const tsv = read(root + "tools/class_lines.tsv").trim().split("\n").map(r => r.split("\t"));
const H = tsv[0];
const rows = tsv.slice(1).map(r => Object.fromEntries(H.map((h, i) => [h, r[i] ?? ""])));
const linesOf = c => [...new Set(rows.filter(r => r.class === c && r.line).map(r => r.line))];
const shape = q => existsSync(`${docs}lines/${q}.geojson`);

const strip = s => s.replace(/<[^>]+>/g, "").trim();
for (const lang of ["ja", "en"]) {
  const pre = lang === "ja" ? "" : "en/";
  for (const c of classes) {
    const p = `${pre}rdf/class/${c}.html`;
    if (!existsSync(dist + p)) { fail(p, "page missing"); continue; }
    const h = read(dist + p);
    checked++;
    // Name: a class with a label must not fall back to its id
    const h1 = strip(h.match(/<h1[^>]*>([\s\S]*?)<\/h1>/)?.[1] ?? "");
    if (!h1) fail(p, "no <h1>");
    else if (/prefLabel/.test(ttl[c]) && h1 === c) fail(p, `name fell back to the id (${h1})`);
    // Wikidata link
    const q = exact(c);
    if (q && !h.includes(`https://www.wikidata.org/wiki/${q}"`)) fail(p, `no Wikidata link to ${q}`);
    // 3D models: a viewer exactly when the class has models, and every model's GLB on it
    const ms = modelsOf(c);
    const mv = h.includes("<model-viewer");
    if (ms.length && !mv) fail(p, `no 3D viewer (models: ${ms.join(" ")})`);
    if (!ms.length && mv) fail(p, "3D viewer without a model");
    for (const m of ms) if (!h.includes(`/models/${m}.glb`)) fail(p, `model ${m} not on the page`);
    // Lines: one list item per line; a map when at least one line has a shape, with each shape linked
    const ls = linesOf(c);
    const items = (h.match(/<li[^>]*data-line="/g) ?? []).length;
    if (items !== ls.length) fail(p, `${items} line(s) listed, ${ls.length} in tools/class_lines.tsv`);
    const mapped = ls.filter(shape);
    const map = h.includes('id="line-map"');
    if (mapped.length && !map) fail(p, `no map (shapes: ${mapped.join(" ")})`);
    if (!mapped.length && map) fail(p, "map without a shape");
    for (const l of mapped) if (!h.includes(`/lines/${l}.geojson`)) fail(p, `shape ${l} not linked`);
    if (map && !h.includes("leaflet.js")) fail(p, "map without Leaflet");
    if (map && !h.includes("OpenStreetMap contributors")) fail(p, "map without the OSM credit");
  }
}

// Every model has a class page that shows it, and view.html#<model> sends it there
const models = readdirSync(docs + "rdf/model").filter(f => f.endsWith(".ttl")).map(f => f.slice(0, -4));
const shown = new Set(classes.flatMap(modelsOf));
for (const m of models) if (!shown.has(m)) fail(`model ${m}`, "on no class page");
const view = existsSync(dist + "view.html") ? read(dist + "view.html") : "";
if (!view) fail("view.html", "missing");
for (const m of models) if (view && !view.includes(`"${m}":"`)) fail("view.html", `no redirect for ${m}`);

// Line shapes: published, valid, with the ODbL notice
for (const f of existsSync(docs + "lines") ? readdirSync(docs + "lines").filter(f => f.endsWith(".geojson")) : []) {
  const where = `lines/${f}`;
  if (!existsSync(dist + where)) { fail(where, "not in dist"); continue; }
  try {
    const g = JSON.parse(read(dist + where));
    const ft = g.features?.[0];
    if (g.type !== "FeatureCollection" || !ft?.geometry?.coordinates?.length) fail(where, "no geometry");
    if (ft?.properties?.license !== "ODbL-1.0" || !/OpenStreetMap contributors/.test(ft?.properties?.attribution ?? "")) fail(where, "no ODbL notice");
  } catch (e) { fail(where, "not JSON"); }
}
if (existsSync(docs + "lines") && !existsSync(dist + "lines/README.md")) fail("lines/README.md", "licence note not published");

// Search: the index is there and not empty
const stats = existsSync(dist + "search/stats.json") ? JSON.parse(read(dist + "search/stats.json")) : null;
if (!stats || !Object.values(stats).some(v => typeof v === "number" && v > 0)) fail("search/stats.json", "missing or empty");
if (!existsSync(dist + "search/index.json")) fail("search/index.json", "missing");

// This site shows the author's name only, not the university (本人の指示, 2026-10-10)
const scan = [...["", "en/"].map(p => p + "index.html"), ...models.filter(m => existsSync(`${dist}iiif/${m}/manifest.json`)).map(m => `iiif/${m}/manifest.json`)];
for (const p of scan) if (existsSync(dist + p) && /東京大学|University of Tokyo/.test(read(dist + p))) fail(p, "names the university");
for (const c of classes) for (const p of [`rdf/class/${c}.html`, `en/rdf/class/${c}.html`])
  if (existsSync(dist + p) && /東京大学|University of Tokyo/.test(read(dist + p))) fail(p, "names the university");

if (bad.length) {
  console.error(`check: ${bad.length} failure(s)\n  ` + bad.join("\n  "));
  process.exit(1);
}
console.log(`check: ok (${checked} class pages, ${models.length} models, ${rows.length} line rows)`);
