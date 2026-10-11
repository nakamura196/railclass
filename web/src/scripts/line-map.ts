// The map of a class page's lines (ClassPage.astro): the OSM shapes cut out by tools/osm_lines.py (docs/lines/<Q>.geojson,
// ODbL) over OpenFreeMap's vector tiles, drawn by MapLibre GL JS as a globe. MapLibre is loaded from the CDN in the page
// head, only on pages that have a mapped line. The base map follows the site's light/dark setting (the header button
// sets <html data-theme>, otherwise the OS). Choosing a line in the list zooms to it and highlights it; "All lines" goes back.
// #lines-data is either an array of {id, label, old, src} (class page: one file per line) or {all, old: [ids]} (map/: one
// lines/_all.geojson with every shape, features id = Q). Either way all shapes go into one source with two layers
// (current: solid, old: dashed and fainter) and a highlight layer filtered by the chosen id.
type L = { id: string; label: string; old: boolean; src: string };
type Box = [number, number, number, number];

const STYLE = { light: "https://tiles.openfreemap.org/styles/positron", dark: "https://tiles.openfreemap.org/styles/dark" };
const dark = () => {
  const t = document.documentElement.dataset.theme;
  return t ? t === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
};
const boxOf = (gj: any): Box | null => {    // gj: a FeatureCollection or one Feature
  let b: Box | null = null;
  const walk = (c: any) => {
    if (typeof c[0] === "number") { b = b ? [Math.min(b[0], c[0]), Math.min(b[1], c[1]), Math.max(b[2], c[0]), Math.max(b[3], c[1])] : [c[0], c[1], c[0], c[1]]; }
    else for (const x of c) walk(x);
  };
  for (const f of gj.features ?? [gj]) if (f.geometry) walk(f.geometry.coordinates);
  return b;
};
const join = (bs: Box[]): Box | null => bs.length ? bs.reduce((a, b) => [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[2], b[2]), Math.max(a[3], b[3])]) : null;

export function lineMap() {
  const el = document.getElementById("lines-data");
  const box = document.getElementById("line-map");
  const ml = (window as any).maplibregl;
  if (!el || !box || !ml) return;
  const data = JSON.parse(el.textContent!);
  const lines: L[] | null = Array.isArray(data) ? data : null;
  const oldIds = new Set<string>(lines ? lines.filter(l => l.old).map(l => l.id) : data.old ?? []);
  const accent = getComputedStyle(box).getPropertyValue("--accent").trim() || "#c0392b";
  const map = new ml.Map({ container: box, style: STYLE[dark() ? "dark" : "light"], center: [0, 30], zoom: 1,
    scrollZoom: false, attributionControl: { compact: true } });
  map.addControl(new ml.NavigationControl({ showCompass: false }));

  let shapes: any = { type: "FeatureCollection", features: [] };    // every shape, kept to put back after a style change
  const boxes = new Map<string, Box>();
  const labels = new Map<string, string>();
  let current: string | null = null;
  const hl = (id: string | null) => ["==", ["get", "lid"], id ?? ""];
  const fade = (id: string | null) => ({ "lines-cur": id ? 0.25 : 0.9, "lines-old": id ? 0.15 : 0.45 });    // the others step back while one is chosen
  const draw = () => {
    map.setProjection({ type: "globe" });
    if (map.getSource("lines")) return;
    map.addSource("lines", { type: "geojson", data: shapes });
    const layout = { "line-cap": "round", "line-join": "round" };
    map.addLayer({ id: "lines-cur", type: "line", source: "lines", layout, filter: ["!=", ["get", "old"], 1], paint: { "line-color": accent, "line-width": 4, "line-opacity": fade(current)["lines-cur"] } });
    map.addLayer({ id: "lines-old", type: "line", source: "lines", layout, filter: ["==", ["get", "old"], 1], paint: { "line-color": accent, "line-width": 4, "line-opacity": fade(current)["lines-old"], "line-dasharray": [1.5, 1.5] } });
    map.addLayer({ id: "lines-hl", type: "line", source: "lines", layout, filter: hl(current), paint: { "line-color": accent, "line-width": 6, "line-opacity": 1 } });
  };
  const fit = (b: Box | null, maxZoom: number) => { if (b) map.fitBounds([[b[0], b[1]], [b[2], b[3]]], { padding: 24, maxZoom, duration: 600 }); };
  const choose = (id: string | null) => {
    current = id;
    if (map.getLayer("lines-hl")) map.setFilter("lines-hl", hl(id));
    for (const [k, v] of Object.entries(fade(id))) if (map.getLayer(k)) map.setPaintProperty(k, "line-opacity", v);
    for (const b of document.querySelectorAll<HTMLElement>(".lines button[data-line]")) b.toggleAttribute("aria-current", b.dataset.line === id);
    // A list scrolled on its own (map/, positioned so offsetTop counts from it): bring the chosen line into view, without moving the page
    const li = id ? document.querySelector<HTMLElement>(`.lines ul.scroll li[data-line="${id}"]`) : null;
    if (li) { const ul = li.parentElement!; if (li.offsetTop < ul.scrollTop || li.offsetTop + li.offsetHeight > ul.scrollTop + ul.clientHeight) ul.scrollTop = li.offsetTop - 8; }
    fit(id && boxes.has(id) ? boxes.get(id)! : join([...boxes.values()]), id ? 13 : 12);
  };

  // Hovering a line shows its name; clicking it chooses it
  const tip = new ml.Popup({ closeButton: false, closeOnClick: false, className: "line-tip" });
  const hit = (e: any) => map.queryRenderedFeatures([[e.point.x - 4, e.point.y - 4], [e.point.x + 4, e.point.y + 4]],
    { layers: ["lines-cur", "lines-old"].filter(k => map.getLayer(k)) })[0];
  map.on("mousemove", (e: any) => {
    const f = hit(e);
    map.getCanvas().style.cursor = f ? "pointer" : "";
    if (f) tip.setLngLat(e.lngLat).setText(labels.get(f.properties.lid) ?? f.properties.label ?? "").addTo(map); else tip.remove();
  });
  map.on("click", (e: any) => { const f = hit(e); if (f) choose(f.properties.lid); });

  const loaded = new Promise<void>(ok => map.once("load", () => ok()));
  map.on("style.load", draw);    // the first load and every theme change (setStyle drops the added layers)
  const get = (u: string) => fetch(u).then(r => r.ok ? r.json() : null).catch(() => null);
  const sources: Promise<any[]> = lines
    ? Promise.all(lines.map(l => get(l.src).then(gj => (gj?.features ?? []).map((f: any) => ({ ...f, id: l.id })))))
        .then(a => { for (const l of lines) labels.set(l.id, l.label); return a.flat(); })
    : get(data.all).then(gj => gj?.features ?? []);
  sources.then(fs => {
    for (const f of fs) {
      const lid = String(f.id ?? f.properties?.id ?? "");
      f.properties = { ...f.properties, lid, old: oldIds.has(lid) ? 1 : 0 };
      if (!f.geometry) continue;
      const b = boxOf(f); if (!b) continue;
      const a = boxes.get(lid);
      boxes.set(lid, a ? [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[2], b[2]), Math.max(a[3], b[3])] : b);
    }
    shapes = { type: "FeatureCollection", features: fs };
  }).then(() => loaded).then(() => { draw(); (map.getSource("lines") as any)?.setData(shapes); fit(join([...boxes.values()]), 12); });

  const restyle = () => map.setStyle(STYLE[dark() ? "dark" : "light"], { diff: false });
  new MutationObserver(restyle).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", restyle);

  for (const b of document.querySelectorAll<HTMLElement>(".lines button[data-line]"))
    b.addEventListener("click", () => choose(b.hasAttribute("aria-current") ? null : b.dataset.line!));
  document.querySelector(".lines .all-lines")?.addEventListener("click", () => choose(null));
}
