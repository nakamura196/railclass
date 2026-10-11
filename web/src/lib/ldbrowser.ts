// Link to the same resource in LD Browser (https://browser.ldas.jp, nakamura196/ld-browser), in the page's language.
export const ldBrowser = (lang: string, uri: string) =>
  `https://browser.ldas.jp/${lang === "en" ? "en/" : ""}?u=${encodeURIComponent(uri)}`;
