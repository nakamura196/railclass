// Fills the shared site header and footer (markup lives here once, so every page stays the same).
// <header class="site-header" data-base="../" data-current="search">  data-base: path back to docs/; data-current: nav key of this page.
(() => {
  const NAV = [
    { key: "search", label: "探す", href: "search/" },
    { key: "view", label: "3D で見る", href: "view.html" },
    { key: "map", label: "地図" },                               // B の navPlace が出たら search/ の地図へ
    { key: "data", label: "データ", href: "index.html#data" },
    { key: "about", label: "このサイトについて", href: "index.html#about" },
    { key: "en", label: "English" },
  ];
  const el = (tag, attrs = {}, ...kids) => {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    e.append(...kids);
    return e;
  };

  const header = document.querySelector(".site-header");
  if (header) {
    const base = header.dataset.base || "";
    const ul = el("ul");
    for (const n of NAV) {
      const item = n.href
        ? el("a", { href: base + n.href }, n.label)
        : el("span", { class: "off" }, n.label, el("span", { class: "soon" }, "準備中"));
      if (n.key === header.dataset.current && n.href) item.setAttribute("aria-current", "page");
      ul.append(el("li", {}, item));
    }
    header.replaceChildren(el("div", { class: "wrap" },
      el("a", { class: "brand", href: base + "index.html" }, el("b", {}, "Train Bodies"), el("span", {}, "世界の鉄道車両と 3D モデル")),
      el("nav", { "aria-label": "サイト" }, ul)));
  }

  const footer = document.querySelector(".site-footer");
  if (footer) {
    const base = footer.dataset.base || "";
    const links = (title, list) => el("div", {}, el("h2", {}, title),
      el("ul", {}, ...list.map(([label, href]) => el("li", {}, el("a", { href: /^https?:/.test(href) ? href : base + href }, label)))));
    footer.replaceChildren(el("div", { class: "wrap" },
      el("div", {},
        el("p", {}, el("b", {}, "Train Bodies"), " — 世界の鉄道車両の形式を調べ、3D プリントで作った車体のモデルと結ぶデータベース。"),
        el("p", {}, "作者: 中村 覚（東京大学）")),
      links("サイト", [["探す", "search/"], ["3D で見る", "view.html"], ["お知らせ", "index.html#news"], ["このサイトについて", "index.html#about"]]),
      links("データ", [["モデルの一覧（JSON）", "data/models.json"], ["お知らせ（JSON）", "data/news.json"], ["ソース（GitHub）", "https://github.com/nakamura196/train-bodies"]]),
      el("div", { class: "legal" },
        el("p", {}, "個人が作った非公式のサイトです。プラレール（タカラトミー）、各鉄道会社・バス会社（DB・ÖBB・DSB・Renfe・Amtrak・TransLink など）とは関係ありません。商標と社章はそれぞれの権利者のものです。"),
        el("p", {}, "形式の情報は Wikidata（CC0）によります。3D モデルと画像の利用条件は整備中です。"),
        el("p", {}, "© 2026 中村 覚"))));
  }
})();
