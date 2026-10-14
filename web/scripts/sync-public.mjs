// Copies the generated data in docs/ into public/ so Astro serves it as is (same URLs as on the old Pages site).
// The class and model pages (rdf/class/*.html, rdf/model/*.html) are made by Astro; an old .html left in docs/ is not
// copied, so it cannot shadow them. The notes are not copied.
import { cpSync, existsSync, rmSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";

const docs = fileURLToPath(new URL("../../docs/", import.meta.url));
const pub = fileURLToPath(new URL("../public/", import.meta.url));
const DIRS = ["site", "data", "models", "thumbs", "rdf", "search", "iiif", "lines", "downloads"];   // site/: icon and share image (og-image.json); downloads/ is not in git: copied only when present
// Local copies of the Commons photos (tools/fetch_photos.py). Not in git (data/ is not), so they reach the site only
// through a local build; without them the search page falls back to Wikimedia's thumbnails.
const photos = fileURLToPath(new URL("../../data/photos/", import.meta.url));

const BUILT = /^rdf\/(class|model)\/[^/]+\.html$/;   // made by Astro

rmSync(pub, { recursive: true, force: true });
mkdirSync(pub);
for (const d of DIRS) {
  if (!existsSync(docs + d)) { console.log(`sync: skip ${d}/ (not in docs/)`); continue; }
  cpSync(docs + d, pub + d, { recursive: true, filter: src => !src.endsWith(".DS_Store") && !BUILT.test(src.slice(docs.length)) });
  console.log(`sync: ${d}/`);
}
if (existsSync(photos)) {
  cpSync(photos, pub + "photos", { recursive: true, filter: src => !src.endsWith(".tsv") && !src.endsWith(".DS_Store") && !src.endsWith(".tmp") });
  console.log("sync: photos/ (from data/photos)");
} else console.log("sync: skip photos/ (no data/photos)");
