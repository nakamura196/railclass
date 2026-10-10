// The class pages (rdf/class/<id>.html): one per class RDF file in docs/rdf/class/ (tools/build_rdf.py).
// The values shown come from the search index (docs/search/index.json, tools/build_search.py), which already has the
// labels in both languages, the values inherited from skos:broader and the colours from the models' liveries,
// so the page and the search agree. The RDF file gives the links (Wikidata, broader, models) and the Turtle shown.
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import type { Lang } from "../i18n";

const DOCS = resolve(process.cwd(), "../docs");
const CLASS_DIR = resolve(DOCS, "rdf/class");
const BASE = "https://nakamura196.github.io/train-bodies/rdf/";
const WD = "http://www.wikidata.org/entity/";

const many = (v: any) => (v == null ? [] : Array.isArray(v) ? v : [v]);
const iri = (v: any) => String(v?.["@id"] ?? v).replace(/^wd:/, WD);
const local = (u: string, kind: "class" | "model") => u.startsWith(BASE + kind + "/") ? u.slice(BASE.length + kind.length + 1) : null;
const qid = (u: string) => u.startsWith(WD) ? u.slice(WD.length) : null;

export type FacetRow = { label: string; values: { text: string; search?: string }[] };
export type ClassPage = {
  id: string; name: string; other: string | null; wikidata: string | null; derivedFrom: string | null;
  broader: { id: string; name: string }[]; narrower: { id: string; name: string }[];
  facets: FacetRow[]; models: string[]; photo: { src: string; page: string; who: string | null; lic: string | null; licUrl: string | null } | null;
  ttl: string;
};

let INDEX: any;
function index() {
  if (!INDEX) {
    const p = resolve(DOCS, "search/index.json");
    INDEX = existsSync(p) ? JSON.parse(readFileSync(p, "utf8")) : null;
  }
  return INDEX;
}

/** The ids of the classes that have an RDF file (and so a page). */
export function classIds(): string[] {
  return existsSync(CLASS_DIR) ? readdirSync(CLASS_DIR).filter(f => f.endsWith(".jsonld")).map(f => f.slice(0, -7)).sort() : [];
}

function labels(n: any) {
  const out: Record<string, string> = {};
  for (const x of many(n["skos:prefLabel"] ?? n["rdfs:label"])) if (x?.["@language"]) out[x["@language"]] = x["@value"];
  return out;
}
const pick = (l: Record<string, string>, lang: Lang) => (lang === "ja" ? l.ja || l.en : l.en || l.ja) || "";

const THUMB = "https://thumb.wikimedia.org/wikipedia/commons/thumb/";
const FILEPAGE = "https://commons.wikimedia.org/wiki/File:";

export function classPage(id: string, lang: Lang, fmtN: (n: number) => string, yearText: (y: number) => string): ClassPage {
  const node = JSON.parse(readFileSync(resolve(CLASS_DIR, id + ".jsonld"), "utf8"));
  const all = classIds().map(c => [c, JSON.parse(readFileSync(resolve(CLASS_DIR, c + ".jsonld"), "utf8"))] as const);
  const nameOf = (c: string) => pick(labels(all.find(([k]) => k === c)?.[1] ?? {}), lang) || c;
  const l = labels(node);
  const name = pick(l, lang) || id;
  const otherName = lang === "ja" ? l.en : l.ja;

  const D = index();
  const row = D ? D.id.indexOf(id) : -1;
  const facets: FacetRow[] = [];
  let photo: ClassPage["photo"] = null;
  if (row >= 0) {
    for (const f of D.facets) {
      if (f.of || f.datatype === "boolean") continue;           // the group facet repeats "kind"; has3d is shown by the models
      const flabel = (lang === "ja" ? f.label.ja || f.label.en : f.label.en || f.label.ja) + (f.unit ? ` (${f.unit})` : "");
      const x = D[f.id][row];
      if (f.datatype === "iri") {
        if (!x.length) continue;
        facets.push({ label: flabel, values: x.map((k: number) => {
          const v = f.values[k];
          return { text: (lang === "ja" ? v[2] || v[1] : v[1] || v[2]) || v[0], search: `${f.id}=${encodeURIComponent(v[0])}` };
        }) });
      } else if (x != null) {
        facets.push({ label: flabel, values: [{ text: f.datatype === "gYear" ? yearText(x) : fmtN(x) }] });
      }
    }
    const file = D.img[row];
    if (file) {
      const u = encodeURIComponent(file.replace(/ /g, "_")), t = D.thumb?.[row] || "", k = D.photo?.[row] || "";
      const src = k ? `photos/${k}.webp` : t.length > 4 ? t : t ? `${THUMB}${t}/${u}/330px-${u}` : `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(file)}?width=330`;
      const c = D.credit?.[row];
      const [lic, licUrl] = c ? D.licenses[c[1]] : [null, null];
      photo = { src, page: FILEPAGE + u, who: c ? D.artists[c[0]] || null : null, lic: lic || null, licUrl: licUrl || null };
    }
  }

  const exact = many(node["skos:exactMatch"]).map(iri).map(qid).find(Boolean) ?? null;
  const derived = many(node["prov:wasDerivedFrom"]).map(iri)[0] ?? null;
  return {
    id, name, other: otherName && otherName !== name ? otherName : null,
    wikidata: exact, derivedFrom: derived,
    broader: many(node["skos:broader"]).map(iri).map(u => local(u, "class")).filter(Boolean).map(c => ({ id: c!, name: nameOf(c!) })),
    narrower: all.filter(([, n]) => many(n["skos:broader"]).map(iri).some(u => local(u, "class") === id)).map(([c]) => ({ id: c, name: nameOf(c) })),
    facets,
    models: many(node["schema:subjectOf"]).map(iri).map(u => local(u, "model")).filter(Boolean) as string[],
    photo,
    ttl: readFileSync(resolve(CLASS_DIR, id + ".ttl"), "utf8"),
  };
}

/** Which class page shows each model (the class whose RDF has schema:subjectOf the model); for view.html#<model>. */
export function modelClasses(): Record<string, string> {
  const out: Record<string, string> = {};
  for (const c of classIds()) {
    const node = JSON.parse(readFileSync(resolve(CLASS_DIR, c + ".jsonld"), "utf8"));
    for (const u of many(node["schema:subjectOf"]).map(iri)) { const m = local(u, "model"); if (m && !out[m]) out[m] = c; }
  }
  return out;
}
