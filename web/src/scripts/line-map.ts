// The map of a class page's lines (ClassPage.astro): the OSM shapes cut out by tools/osm_lines.py (docs/lines/<Q>.geojson,
// ODbL) over OpenFreeMap's vector tiles, drawn by MapLibre GL JS (map/: flat, centred on Vancouver; a class page: a globe). MapLibre is loaded from the CDN in the page
// head, only on pages that have a mapped line. The base map follows the site's light/dark setting (the header button
// sets <html data-theme>, otherwise the OS). Choosing a line in the list zooms to it and highlights it; "All lines" goes back.
// #lines-data is either an array of {id, label, old, src} (class page: one file per line) or {all, old: [ids]} (map/: one
// lines/_all.geojson with every shape, features id = Q). Either way all shapes go into one source with two layers
// (current: solid, old: dashed and fainter) and a highlight layer filtered by the chosen id.
// Each line is drawn in its own colour (official colour from Wikidata P465, else a fixed palette; web/src/lib/data.ts lineColor),
// so that lines side by side (Vancouver's Expo and Millennium lines) can be told apart; a thin casing in the base map's
// background colour keeps light colours (yellow) visible on the light map.
// map/'s _all.geojson is coarse (about 200 m, tools/osm_lines.py TOL_ALL) so the world map loads fast; the detailed
// lines/<Q>.geojson replaces a line's shape when it is chosen, or when zoomed in (DETAIL_ZOOM) for the lines in view.
type L = { id: string; label: string; old: boolean; src: string; color: string };
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
const DETAIL_ZOOM = 9;    // map/: from this zoom, the lines in view get their detailed shape
const MAX_FETCH = 40;     // at most this many detailed files at one time (a city with many lines)
const meets = (a: Box, b: Box) => a[0] <= b[2] && b[0] <= a[2] && a[1] <= b[3] && b[1] <= a[3];
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
  const colors: Record<string, string> = lines ? Object.fromEntries(lines.map(l => [l.id, l.color])) : data.colors ?? {};
  // map/ (one combined file) opens on the flat world centred on Vancouver, where every line is in view at once;
  // a class page keeps the globe and fits its lines. Only map/ zooms on the wheel: a class page is a long page to scroll past it
  const world = !lines;
  const VAN: [number, number] = [-123.12, 49.28];
  const worldZoom = () => Math.max(0, Math.log2(box.clientWidth / 512));    // the whole width of the world
  let proj = world ? "mercator" : "globe";
  const map = new ml.Map({ container: box, style: STYLE[dark() ? "dark" : "light"], center: world ? VAN : [0, 30], zoom: world ? worldZoom() : 1,
    scrollZoom: world, attributionControl: { compact: true } });
  map.addControl(new ml.NavigationControl({ showCompass: false }));
  if (world) map.addControl(new ml.GlobeControl());

  let shapes: any = { type: "FeatureCollection", features: [] };    // every shape, kept to put back after a style change
  const boxes = new Map<string, Box>();
  const labels = new Map<string, string>();
  let current: string | null = null;
  let ready = false;
  const has3d: string[] = lines ? [] : data.has3d ?? [];
  let only3d = false;    // map/: only the lines a class with a 3D model runs on
  const keep = (f: any[]) => only3d ? ["all", f, ["in", ["get", "lid"], ["literal", has3d]]] : f;    // the shapes are in; a line chosen before that is shown once they are
  const hl = (id: string | null) => ["==", ["get", "lid"], id ?? ""];
  const fade = (id: string | null) => ({ "lines-case": id ? 0.25 : 0.9, "lines-cur": id ? 0.25 : 0.95, "lines-old": id ? 0.15 : 0.6 });    // the others step back while one is chosen
  const draw = () => {
    map.setProjection({ type: proj });
    if (map.getSource("lines")) return;
    map.addSource("lines", { type: "geojson", data: shapes });
    const layout = { "line-cap": "round", "line-join": "round" };
    const color = ["coalesce", ["get", "color"], accent];
    const casing = dark() ? "#111111" : "#ffffff";
    map.addLayer({ id: "lines-case", type: "line", source: "lines", layout, filter: keep(["!=", ["get", "old"], 1]), paint: { "line-color": casing, "line-width": 6.5, "line-opacity": fade(current)["lines-case"] } });
    map.addLayer({ id: "lines-cur", type: "line", source: "lines", layout, filter: keep(["!=", ["get", "old"], 1]), paint: { "line-color": color, "line-width": 4, "line-opacity": fade(current)["lines-cur"] } });
    map.addLayer({ id: "lines-old", type: "line", source: "lines", layout, filter: keep(["==", ["get", "old"], 1]), paint: { "line-color": color, "line-width": 4, "line-opacity": fade(current)["lines-old"], "line-dasharray": [1.5, 1.5] } });
    map.addLayer({ id: "lines-hl-case", type: "line", source: "lines", layout, filter: hl(current), paint: { "line-color": casing, "line-width": 10, "line-opacity": 1 } });
    map.addLayer({ id: "lines-hl", type: "line", source: "lines", layout, filter: hl(current), paint: { "line-color": color, "line-width": 7, "line-opacity": 1 } });
  };
  const fit = (b: Box | null, maxZoom: number) => { if (b) map.fitBounds([[b[0], b[1]], [b[2], b[3]]], { padding: 24, maxZoom, duration: 600 }); };
  const choose = (id: string | null) => {
    current = id;
    for (const k of ["lines-hl-case", "lines-hl"]) if (map.getLayer(k)) map.setFilter(k, hl(id));
    for (const [k, v] of Object.entries(fade(id))) if (map.getLayer(k)) map.setPaintProperty(k, "line-opacity", v);
    for (const b of document.querySelectorAll<HTMLElement>(".lines button[data-line]")) b.toggleAttribute("aria-current", b.dataset.line === id);
    // A list scrolled on its own (map/, positioned so offsetTop counts from it): bring the chosen line into view, without moving the page
    const li = id ? document.querySelector<HTMLElement>(`.lines ul.scroll li[data-line="${id}"]`) : null;
    if (li) { const ul = li.parentElement!; if (li.offsetTop < ul.scrollTop || li.offsetTop + li.offsetHeight > ul.scrollTop + ul.clientHeight) ul.scrollTop = li.offsetTop - 8; }
    if (!ready) return;
    if (id) detail([id]);
    if (!id && world) map.flyTo({ center: VAN, zoom: worldZoom(), duration: 600 });
    else fit(id && boxes.has(id) ? boxes.get(id)! : join([...boxes.values()]), id ? 13 : 12);
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
      f.properties = { ...f.properties, lid, old: oldIds.has(lid) ? 1 : 0, color: colors[lid] ?? accent };
      if (!f.geometry) continue;
      const b = boxOf(f); if (!b) continue;
      const a = boxes.get(lid);
      boxes.set(lid, a ? [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[2], b[2]), Math.max(a[3], b[3])] : b);
    }
    shapes = { type: "FeatureCollection", features: fs };
  }).then(() => loaded).then(() => {
    draw(); (map.getSource("lines") as any)?.setData(shapes);
    ready = true;
    if (current || !world) choose(current);
  });

  // map/: swap in the detailed shape of a line (lines/<Q>.geojson next to _all.geojson), once per line
  const detailed = new Set<string>();
  const base = world ? String(data.all).replace(/_all\.geojson$/, "") : "";
  const detail = (ids: string[]) => {
    const want = ids.filter(id => !detailed.has(id)).slice(0, MAX_FETCH);
    if (!world || !want.length) return;
    for (const id of want) detailed.add(id);
    Promise.all(want.map(id => get(`${base}${id}.geojson`).then(gj => [id, gj?.features?.[0]?.geometry] as const)))
      .then(got => {
        const g = new Map(got.filter(([, geom]) => geom));
        if (!g.size) return;
        shapes = { ...shapes, features: shapes.features.map((f: any) => g.has(f.properties.lid) ? { ...f, geometry: g.get(f.properties.lid) } : f) };
        (map.getSource("lines") as any)?.setData(shapes);
      });
  };
  if (world) map.on("moveend", () => {
    if (!ready || map.getZoom() < DETAIL_ZOOM) return;
    const b = map.getBounds(); const v: Box = [b.getWest(), b.getSouth(), b.getEast(), b.getNorth()];
    detail([...boxes].filter(([id, bx]) => meets(bx, v) && (!only3d || has3d.includes(id))).map(([id]) => id));
  });

  const restyle = () => (proj = map.getProjection()?.type ?? proj, map.setStyle(STYLE[dark() ? "dark" : "light"], { diff: false }));
  new MutationObserver(restyle).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", restyle);

  for (const b of document.querySelectorAll<HTMLElement>(".lines button[data-line]"))
    b.addEventListener("click", () => choose(b.hasAttribute("aria-current") ? null : b.dataset.line!));
  document.querySelector(".lines .all-lines")?.addEventListener("click", () => choose(null));
  document.getElementById("only3d")?.addEventListener("change", e => {
    only3d = (e.target as HTMLInputElement).checked;
    document.querySelector(".lines ul.scroll")?.classList.toggle("f3d", only3d);
    for (const k of ["lines-case", "lines-cur"]) if (map.getLayer(k)) map.setFilter(k, keep(["!=", ["get", "old"], 1]));
    if (map.getLayer("lines-old")) map.setFilter("lines-old", keep(["==", ["get", "old"], 1]));
    if (only3d && current && !has3d.includes(current)) choose(null);
  });
}
