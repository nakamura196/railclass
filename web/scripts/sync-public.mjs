// Copies the generated data in docs/ into public/ so Astro serves it as is (same URLs as on the old Pages site).
// The class and model pages (rdf/class/*.html, rdf/model/*.html) are made by Astro; an old .html left in docs/ is not
// copied, so it cannot shadow them. The notes are not copied.
import { cpSync, existsSync, rmSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { SHOW3D } from "./site-config.mjs";   // site.config.json: show3d false = nothing about 3D models is published

const docs = fileURLToPath(new URL("../../docs/", import.meta.url));
const pub = fileURLToPath(new URL("../public/", import.meta.url));
const DIRS = ["site", "data", "models", "thumbs", "rdf", "search", "iiif", "lines", "downloads"];   // site/: icon and share image (og-image.json); downloads/ is not in git: copied only when present
// Local copies of the Commons photos (tools/fetch_photos.py). Not in git (data/ is not), so they reach the site only
// through a local build; without them the search page falls back to Wikimedia's thumbnails.
const photos = fileURLToPath(new URL("../../data/photos/", import.meta.url));

const BUILT = /^rdf\/(class|model)\/[^/]+\.html$/;   // made by Astro
// show3d false: these are left out. data/models.json is the model list; facets.json is copied without the facets that exist only for the models
const MODEL_DIRS = ["models", "thumbs", "iiif", "downloads"];
const MODEL_FILES = /^(data\/models\.json|rdf\/model\/|site\/og-)/;

rmSync(pub, { recursive: true, force: true });
mkdirSync(pub);
for (const d of DIRS) {
  if (!SHOW3D && MODEL_DIRS.includes(d)) { console.log(`sync: skip ${d}/ (show3d is false)`); continue; }
  if (!existsSync(docs + d)) { console.log(`sync: skip ${d}/ (not in docs/)`); continue; }
  cpSync(docs + d, pub + d, { recursive: true, filter: src => !src.endsWith(".DS_Store") && !BUILT.test(src.slice(docs.length)) && (SHOW3D || !MODEL_FILES.test(src.slice(docs.length))) });
  console.log(`sync: ${d}/`);
}
if (!SHOW3D && existsSync(pub + "rdf/facets.json")) {   // the facet list of the RDF work: drop has3d and the colour facet (taken from the models' liveries)
  const f = JSON.parse(readFileSync(pub + "rdf/facets.json", "utf8"));
  delete f.note;   // the note explains the model facets
  f.facets = f.facets.filter(x => x.id !== "has3d" && x.on !== "livery");
  writeFileSync(pub + "rdf/facets.json", JSON.stringify(f, null, 1));
}
if (!SHOW3D && existsSync(pub + "data/news.json")) {   // news: drop the items about the models, use the "off" wording of the others (same rule as lib/data.ts newsItems)
  const n = JSON.parse(readFileSync(pub + "data/news.json", "utf8"));
  n.items = n.items.filter(i => !i.hide_if_off).map(({ off, ...i }) => !off ? i : { ...i, ...off, en: { ...i.en, ...off.en } });
  writeFileSync(pub + "data/news.json", JSON.stringify(n, null, 1));
}
if (existsSync(photos)) {
  cpSync(photos, pub + "photos", { recursive: true, filter: src => !src.endsWith(".tsv") && !src.endsWith(".DS_Store") && !src.endsWith(".tmp") });
  console.log("sync: photos/ (from data/photos)");
} else console.log("sync: skip photos/ (no data/photos)");
