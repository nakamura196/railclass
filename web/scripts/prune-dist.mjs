// After astro build: with show3d false, delete the files in dist/_astro that belong to the 3D components (their scripts, styles and
// the IIIF logo). Astro emits them even though no page links them, because the components are imported (dynamically) by pages.
// Nothing links them; web/scripts/check-dist.mjs checks that every _astro file a page links is still there.
import { existsSync, readdirSync, rmSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { SHOW3D } from "./site-config.mjs";

const dir = fileURLToPath(new URL("../dist/_astro/", import.meta.url));
if (SHOW3D || !existsSync(dir)) process.exit(0);
let n = 0;
for (const f of readdirSync(dir)) if (/3D|3d|ModelPage|ViewPage|iiif/.test(f)) { rmSync(dir + f); n++; }
console.log(`prune: ${n} file(s) of the 3D components removed from dist/_astro`);
