// Reads the JSON in docs/ at build time (written by the Python tools / by hand) and picks the text for a language.
import { readFileSync, existsSync } from "node:fs";
import type { Lang } from "../i18n";
import modelsEn from "../i18n/models.en.json";

import { resolve } from "node:path";

// npm scripts run in web/; import.meta.url is not usable here because the build bundles this module elsewhere.
const DOCS = resolve(process.cwd(), "../docs");
const docsPath = (p: string) => resolve(DOCS, p);
const readJSON = (p: string) => JSON.parse(readFileSync(docsPath(p), "utf8"));

export type Model = { id: string; group: string; groupLabel: string; title: string; line: string; size: number[]; wikidata?: string; added: string; kb: number };

export function models(lang: Lang) {
  const data = readJSON("data/models.json");
  const en = lang === "en" ? (modelsEn as any) : null;
  const groups = data.groups.map((g: any) => ({ id: g.id, label: en?.groups[g.id] ?? g.label }));
  const label = Object.fromEntries(groups.map((g: any) => [g.id, g.label]));
  const items: Model[] = data.items.map((it: any) => ({
    ...it, groupLabel: label[it.group],
    title: en?.items[it.id]?.title ?? it.title,
    line: en?.items[it.id]?.line ?? it.line,
  }));
  return { ext: data.ext as string, groups, items };
}

/** Newest first; within a day, later entries in models.json are newer. */
export const newest = (items: Model[]) =>
  items.map((it, i) => ({ it, i })).sort((a, b) => b.it.added.localeCompare(a.it.added) || b.i - a.i).map(x => x.it);

export function news(lang: Lang) {
  return readJSON("data/news.json").items.map((n: any) => ({
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
