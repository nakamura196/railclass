// The map of a class page's lines (ClassPage.astro): the OSM shapes cut out by tools/osm_lines.py (docs/lines/<Q>.geojson,
// ODbL) over OSM's own tiles. Leaflet is loaded from the CDN in the page head, only on pages that have a mapped line.
// Choosing a line in the list zooms to it and brings it to the front; "All lines" goes back.
type L = { id: string; label: string; old: boolean; src: string };

export function lineMap() {
  const el = document.getElementById("lines-data");
  const box = document.getElementById("line-map");
  const Lf = (window as any).L;
  if (!el || !box || !Lf) return;
  const lines: L[] = JSON.parse(el.textContent!);
  const accent = getComputedStyle(box).getPropertyValue("--accent").trim() || "#c0392b";
  const map = Lf.map(box, { scrollWheelZoom: false, worldCopyJump: true, attributionControl: true });
  Lf.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);
  map.setView([30, 0], 1);

  const style = (l: L, on = false) => ({ color: accent, weight: on ? 6 : 4, opacity: l.old ? 0.45 : 0.9, dashArray: l.old ? "6 6" : undefined });
  const layers = new Map<string, any>();
  const all = () => {
    const b = Lf.latLngBounds([]);
    for (const g of layers.values()) b.extend(g.getBounds());
    if (b.isValid()) map.fitBounds(b, { padding: [20, 20], maxZoom: 12 });
  };
  const choose = (id: string | null) => {
    for (const [k, g] of layers) { const l = lines.find(x => x.id === k)!; g.setStyle(style(l, k === id)); if (k === id) g.bringToFront(); }
    for (const b of document.querySelectorAll<HTMLElement>(".lines button[data-line]")) b.toggleAttribute("aria-current", b.dataset.line === id);
    if (id && layers.get(id)) map.fitBounds(layers.get(id).getBounds(), { padding: [20, 20], maxZoom: 13 });
    else all();
  };
  Promise.all(lines.map(l => fetch(l.src).then(r => r.ok ? r.json() : null).catch(() => null).then(gj => {
    if (!gj) return;
    const g = Lf.geoJSON(gj, { style: () => style(l) }).bindTooltip(l.label, { sticky: true }).addTo(map);
    g.on("click", () => choose(l.id));
    layers.set(l.id, g);
  }))).then(all);

  for (const b of document.querySelectorAll<HTMLElement>(".lines button[data-line]"))
    b.addEventListener("click", () => choose(b.hasAttribute("aria-current") ? null : b.dataset.line!));
  document.querySelector(".lines .all-lines")?.addEventListener("click", () => choose(null));
}
