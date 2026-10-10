// The map of a class page's lines (ClassPage.astro): the OSM shapes cut out by tools/osm_lines.py (docs/lines/<Q>.geojson,
// ODbL) over OpenFreeMap's vector tiles, drawn by MapLibre GL JS as a globe. MapLibre is loaded from the CDN in the page
// head, only on pages that have a mapped line. The base map follows the site's light/dark setting (the header button
// sets <html data-theme>, otherwise the OS). Choosing a line in the list zooms to it and brings it to the front;
// "All lines" goes back.
type L = { id: string; label: string; old: boolean; src: string };
type Box = [number, number, number, number];

const STYLE = { light: "https://tiles.openfreemap.org/styles/positron", dark: "https://tiles.openfreemap.org/styles/dark" };
const dark = () => {
  const t = document.documentElement.dataset.theme;
  return t ? t === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
};
const boxOf = (gj: any): Box | null => {
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
  const lines: L[] = JSON.parse(el.textContent!);
  const accent = getComputedStyle(box).getPropertyValue("--accent").trim() || "#c0392b";
  const map = new ml.Map({ container: box, style: STYLE[dark() ? "dark" : "light"], center: [0, 30], zoom: 1,
    scrollZoom: false, attributionControl: { compact: true } });
  map.addControl(new ml.NavigationControl({ showCompass: false }));

  const shapes = new Map<string, any>();    // line id -> GeoJSON, kept to put back after a style change
  const boxes = new Map<string, Box>();
  let current: string | null = null;
  const layer = (id: string) => `line-${id}`;
  const draw = () => {
    map.setProjection({ type: "globe" });
    for (const [id, gj] of shapes) {
      if (map.getSource(layer(id))) continue;
      const l = lines.find(x => x.id === id)!;
      map.addSource(layer(id), { type: "geojson", data: gj });
      map.addLayer({ id: layer(id), type: "line", source: layer(id), layout: { "line-cap": "round", "line-join": "round" },
        paint: { "line-color": accent, "line-width": id === current ? 6 : 4, "line-opacity": l.old ? 0.45 : 0.9,
          ...(l.old ? { "line-dasharray": [1.5, 1.5] } : {}) } });
      if (id === current) map.moveLayer(layer(id));
    }
  };
  const fit = (b: Box | null, maxZoom: number) => { if (b) map.fitBounds([[b[0], b[1]], [b[2], b[3]]], { padding: 24, maxZoom, duration: 600 }); };
  const choose = (id: string | null) => {
    current = id;
    for (const k of shapes.keys()) if (map.getLayer(layer(k))) map.setPaintProperty(layer(k), "line-width", k === id ? 6 : 4);
    if (id && map.getLayer(layer(id))) map.moveLayer(layer(id));
    for (const b of document.querySelectorAll<HTMLElement>(".lines button[data-line]")) b.toggleAttribute("aria-current", b.dataset.line === id);
    // A list scrolled on its own (map/, positioned so offsetTop counts from it): bring the chosen line into view, without moving the page
    const li = id ? document.querySelector<HTMLElement>(`.lines ul.scroll li[data-line="${id}"]`) : null;
    if (li) { const ul = li.parentElement!; if (li.offsetTop < ul.scrollTop || li.offsetTop + li.offsetHeight > ul.scrollTop + ul.clientHeight) ul.scrollTop = li.offsetTop - 8; }
    fit(id && boxes.has(id) ? boxes.get(id)! : join([...boxes.values()]), id ? 13 : 12);
  };

  // Hovering a line shows its name; clicking it chooses it
  const tip = new ml.Popup({ closeButton: false, closeOnClick: false, className: "line-tip" });
  const hit = (e: any) => map.queryRenderedFeatures([[e.point.x - 4, e.point.y - 4], [e.point.x + 4, e.point.y + 4]],
    { layers: [...shapes.keys()].map(layer).filter(k => map.getLayer(k)) })[0];
  map.on("mousemove", (e: any) => {
    const f = hit(e);
    map.getCanvas().style.cursor = f ? "pointer" : "";
    if (f) tip.setLngLat(e.lngLat).setText(lines.find(l => layer(l.id) === f.layer.id)!.label).addTo(map); else tip.remove();
  });
  map.on("click", (e: any) => { const f = hit(e); if (f) choose(f.layer.id.slice(5)); });

  const loaded = new Promise<void>(ok => map.once("load", () => ok()));
  map.on("style.load", draw);    // the first load and every theme change (setStyle drops the added layers)
  Promise.all(lines.map(l => fetch(l.src).then(r => r.ok ? r.json() : null).catch(() => null).then(gj => {
    if (!gj) return;
    shapes.set(l.id, gj);
    const b = boxOf(gj); if (b) boxes.set(l.id, b);
  }))).then(() => loaded).then(() => { draw(); fit(join([...boxes.values()]), 12); });

  const restyle = () => map.setStyle(STYLE[dark() ? "dark" : "light"], { diff: false });
  new MutationObserver(restyle).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", restyle);

  for (const b of document.querySelectorAll<HTMLElement>(".lines button[data-line]"))
    b.addEventListener("click", () => choose(b.hasAttribute("aria-current") ? null : b.dataset.line!));
  document.querySelector(".lines .all-lines")?.addEventListener("click", () => choose(null));
}
