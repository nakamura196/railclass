// Pages are built here; data made by the Python tools (docs/models, rdf, iiif, search, ...) is copied
// into public/ by scripts/sync-public.mjs and served unchanged, so their URLs stay as they are.
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://nakamura196.github.io",
  base: "/train-bodies",
  trailingSlash: "ignore",
  build: { format: "preserve" },   // view.astro -> view.html, search/index.astro -> search/index.html (the URLs in use)
  i18n: {
    locales: ["ja", "en"],
    defaultLocale: "ja",
    routing: { prefixDefaultLocale: false },   // Japanese at the current URLs, English under /en/
  },
});
