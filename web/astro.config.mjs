// Pages are built here; data made by the Python tools (docs/models, rdf, iiif, search, ...) is copied
// into public/ by scripts/sync-public.mjs and served unchanged, so their URLs stay as they are.
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://nakamura196.github.io",
  base: "/train-bodies",
  trailingSlash: "ignore",
  // format: view.astro -> view.html, search/index.astro -> search/index.html (the URLs in use).
  // inlineStylesheets: since every class has a page (~28,000 with both languages, 2026-10-10), the CSS is one shared file,
  // not 4 KB copied into each page (about 110 MB of the 1 GB GitHub Pages allows).
  build: { format: "preserve", inlineStylesheets: "never" },
  i18n: {
    locales: ["ja", "en"],
    defaultLocale: "ja",
    routing: { prefixDefaultLocale: false },   // Japanese at the current URLs, English under /en/
  },
});
