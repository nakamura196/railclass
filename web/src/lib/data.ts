// Reads the JSON in docs/ at build time (written by the Python tools / by hand) and picks the text for a language.
import { readFileSync, existsSync, statSync } from "node:fs";
import type { Lang } from "../i18n";
import { SHOW3D } from "./site";

import { resolve } from "node:path";

// npm scripts run in web/; import.meta.url is not usable here because the build bundles this module elsewhere.
const DOCS = resolve(process.cwd(), "../docs");
const docsPath = (p: string) => resolve(DOCS, p);
const readJSON = (p: string) => JSON.parse(readFileSync(docsPath(p), "utf8"));

export type Model = { id: string; group: string; groupLabel: string; title: string; line: string; size: number[]; wikidata?: string; added: string; kb: number };

export function models(lang: Lang) {
  const data = readJSON("data/models.json");
  // English: label_en / title_en / line_en, written by skytrain/tools/gallery.py (falls back to the Japanese)
  const en = lang === "en";
  const groups = data.groups.map((g: any) => ({ id: g.id, label: (en && g.label_en) || g.label }));
  const label = Object.fromEntries(groups.map((g: any) => [g.id, g.label]));
  const items: Model[] = data.items.map((it: any) => ({
    ...it, groupLabel: label[it.group],
    title: (en && it.title_en) || it.title,
    line: (en && it.line_en) || it.line,
  }));
  return { ext: data.ext as string, groups, items };
}

/** Newest first; within a day, later entries in models.json are newer. */
export const newest = (items: Model[]) =>
  items.map((it, i) => ({ it, i })).sort((a, b) => b.it.added.localeCompare(a.it.added) || b.i - a.i).map(x => x.it);

/** The news items for the site as it is now: with show3d false (site.config.json), an item with "hide_if_off" is dropped and "off" is merged over the others.
 *  Same rule as web/scripts/sync-public.mjs applies to the published data/news.json. */
export function newsItems(items: any[], show3d: boolean) {
  if (show3d) return items;
  return items.filter(n => !n.hide_if_off).map(({ off, ...n }) => !off ? n : { ...n, ...off, en: { ...n.en, ...off.en } });
}

export function news(lang: Lang) {
  return newsItems(readJSON("data/news.json").items, SHOW3D).map((n: any) => ({
    date: n.date, url: n.url,
    title: (lang !== "ja" && n[lang]?.title) || n.title,
    body: (lang !== "ja" && n[lang]?.body) || n.body,
  }));
}

/** Counts made by the search build (docs/search/stats.json); null when not built yet. */
export function stats(): Record<string, number> | null {
  return existsSync(docsPath("search/stats.json")) ? readJSON("search/stats.json") : null;
}

export const fmtSize = (s: number[]) => s.map(v => v.toFixed(v % 1 ? 1 : 0)).join(" × ");

export type Part = { id: string; label: string; text: string; kind: string; kindKey: string; at: number[]; cam: { pos: number[]; look: number[] } | null };

/** The part annotations of a model, read from its IIIF Manifest (docs/iiif/<id>/manifest.json, tools/build_iiif.py):
 *  the commenting annotations with their PointSelector, and the camera each one is scoped to (position and lookAt). */
export function modelParts(id: string, lang: Lang): Part[] {
  const p = `iiif/${id}/manifest.json`;
  if (!existsSync(docsPath(p))) return [];
  const anns: any[] = [];
  const walk = (o: any) => {
    if (Array.isArray(o)) o.forEach(walk);
    else if (o && typeof o === "object") { if (o.type === "Annotation" && o.motivation) anns.push(o); Object.values(o).forEach(walk); }
  };
  walk(readJSON(p));
  const byId = new Map(anns.map(a => [a.id, a]));
  const pt = (s: any) => [s.x, s.y, s.z];
  const str = (l: any) => { const v = l?.[lang] ?? l?.ja ?? l?.en ?? Object.values(l ?? {})[0]; return Array.isArray(v) ? v.join(" ") : v ?? ""; };
  // The category is written in Japanese only (KIND in tools/build_iiif.py)
  const KIND: Record<string, [string, string]> = { "実車の特徴": ["real", "Real car"], "模型の都合": ["toy", "Toy adaptation"], "推測": ["guess", "Inferred"] };
  return anns.filter(a => a.motivation.includes("commenting")).map(a => {
    const body = Array.isArray(a.body) ? a.body : [a.body];
    const text = (purpose: string) => (body.find((b: any) => b.purpose === purpose && b.language === lang) ?? body.find((b: any) => b.purpose === purpose))?.value ?? "";
    const sel = [a.target?.selector].flat().find((s: any) => s?.type === "PointSelector");
    const c = (a.scope ?? []).map((s: any) => byId.get(s.id)).find((x: any) => x?.body?.type === "PerspectiveCamera");
    const cs = c && [c.target?.selector].flat().find((s: any) => s?.type === "PointSelector");
    const k = text("tagging"), kk = KIND[k];
    return { id: a.id.split("/").pop(), label: str(a.label), text: text("describing"),
             kind: lang === "en" && kk ? kk[1] : k, kindKey: kk?.[0] ?? "",
             at: sel ? pt(sel) : [0, 0, 0], cam: cs && c.body.lookAt ? { pos: pt(cs), look: pt(c.body.lookAt) } : null };
  }).filter(x => x.label);
}

export const hasManifest = (id: string) => existsSync(docsPath(`iiif/${id}/manifest.json`));

// The download files of a model, one per format (docs/downloads/<id>/formats.json, by ~/git/3d/skytrain/tools/export_formats.py).
// The GLB is not among them: it is <id>.glb on the models Worker, linked on its own.
// The files are not public: path is the Worker's path (downloads/<id>/<file>), turned into a signed URL by lib/auth3d.ts.
export type Download = { key: string; label: string; path: string; bytes: number };
export function downloads(id: string, lang: Lang): Download[] {
  const p = docsPath(`downloads/${id}/formats.json`);
  if (!existsSync(p)) return [];
  return JSON.parse(readFileSync(p, "utf8")).files.map((f: any) => ({
    key: f.key, label: (f.label[lang] ?? f.label.en)[0], path: `downloads/${id}/${f.file}`, bytes: f.bytes }));
}
export const docsBytes = (p: string) => statSync(docsPath(p)).size;
export const fmtBytes = (n: number) => n >= 1e6 ? `${(n / 1e6).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1e3))} KB`;

export type Line = { id: string; label: string; status: string; until: string; source: string; map: boolean; color: string };

// The colour of a line on the maps: its official colour (Wikidata P465, docs/lines/_colors.json, tools/line_colors.py), else one of
// these, picked by the Q number so a line keeps its colour everywhere. Each line its own colour, so that lines side by side can be told apart.
const PALETTE = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf", "#8c564b", "#e377c2", "#bcbd22", "#7f7f7f", "#393b79", "#ad494a"];
let colors: Record<string, string> | null = null;
export const lineColor = (id: string): string => {
  colors ??= existsSync(docsPath("lines/_colors.json")) ? readJSON("lines/_colors.json") : {};
  return colors![id] ?? PALETTE[Number(id.slice(1)) % PALETTE.length];
};

// tools/class_lines.tsv (hand-filled, sources) first, then tools/class_lines_wd.tsv (Wikidata P3438); the first (class, line) wins
const lineRows = (): Record<string, string>[] => {
  const seen = new Set<string>(), out: Record<string, string>[] = [];
  for (const f of ["class_lines.tsv", "class_lines_wd.tsv"]) {
    const p = resolve(process.cwd(), "../tools", f);
    if (!existsSync(p)) continue;
    const [head, ...rows] = readFileSync(p, "utf8").trim().split("\n").map(r => r.split("\t"));
    for (const r of rows) {
      const o: Record<string, string> = Object.fromEntries(head.map((h, i) => [h, r[i] ?? ""]));
      const k = `${o.class}\t${o.line}`;
      if (!o.line || seen.has(k)) continue;
      seen.add(k); out.push(o);
    }
  }
  return out;
};

export type MapLine = { id: string; label: string; current: boolean; map: boolean; classes: string[]; color: string };

/** Every line of the class-line tables (hand-filled and Wikidata) with the classes on it (for the map page). current = some class still runs on it. */
export function allLines(): MapLine[] {
  const by = new Map<string, MapLine>();
  for (const r of lineRows()) {
    if (!r.line) continue;
    const l = by.get(r.line) ?? { id: r.line, label: r.lineLabel, current: false, map: existsSync(docsPath(`lines/${r.line}.geojson`)), classes: [], color: lineColor(r.line) };
    if (r.status.split(" ")[0] === "current") l.current = true;
    if (!l.classes.includes(r.class)) l.classes.push(r.class);
    by.set(r.line, l);
  }
  return [...by.values()].sort((a, b) => Number(b.map) - Number(a.map) || a.label.localeCompare(b.label));
}

/** The lines a class runs (ran) on: the class-line tables (hand-filled with sources, then Wikidata P3438). map = an OSM shape was cut out
 *  for it (docs/lines/<Q>.geojson, tools/osm_lines.py; ODbL, kept apart from the dataset). */
export function classLines(id: string): Line[] {
  const seen = new Set<string>();
  return lineRows()
    .filter(r => r.class === id && r.line && !seen.has(r.line) && seen.add(r.line))
    .map(r => {
      const [status, until = ""] = r.status.split(" ");
      return { id: r.line, label: r.lineLabel, status, until, source: r.source_url, map: existsSync(docsPath(`lines/${r.line}.geojson`)), color: lineColor(r.line) };
    })
    .sort((a, b) => Number(b.status === "current") - Number(a.status === "current"));
}

/** The dataset description (docs/data/dataset.json, tools/build_void.py): counts, files and their sizes. */
export function dataset(): Record<string, any> {
  return readJSON("data/dataset.json");
}
