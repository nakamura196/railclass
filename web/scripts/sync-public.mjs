// Copies the generated data in docs/ into public/ so Astro serves it as is (same URLs as on the old Pages site).
// The pages build_rdf.py still writes for classes (rdf/class/*.html) are left out so they cannot shadow the Astro pages;
// rdf/model/*.html still comes along until it is moved. The notes are not copied.
import { cpSync, existsSync, rmSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";

const docs = fileURLToPath(new URL("../../docs/", import.meta.url));
const pub = fileURLToPath(new URL("../public/", import.meta.url));
const DIRS = ["data", "models", "thumbs", "rdf", "search", "iiif", "downloads"];   // downloads/ is not in git: copied only when present

const BUILT = /^rdf\/class\/[^/]+\.html$/;   // made by Astro now

rmSync(pub, { recursive: true, force: true });
mkdirSync(pub);
for (const d of DIRS) {
  if (!existsSync(docs + d)) { console.log(`sync: skip ${d}/ (not in docs/)`); continue; }
  cpSync(docs + d, pub + d, { recursive: true, filter: src => !src.endsWith(".DS_Store") && !BUILT.test(src.slice(docs.length)) });
  console.log(`sync: ${d}/`);
}
