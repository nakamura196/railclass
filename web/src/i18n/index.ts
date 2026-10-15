// Display text lives in ja.json / en.json (one file per language). Links are built here so every page agrees.
// With show3d false (site.config.json) the "no3d" block of each file is merged over the text: strings and lists replace, null removes a key.
import ja from "./ja.json";
import en from "./en.json";
import { SHOW3D } from "../lib/site";

export type Lang = "ja" | "en";
export const LANGS: Lang[] = ["ja", "en"];

function merge(base: any, over: any): any {
  if (over === null || typeof over !== "object" || Array.isArray(over)) return over;
  const out: any = { ...base };
  for (const [k, v] of Object.entries(over)) {
    if (k === "_note") continue;
    if (v === null) delete out[k];
    else out[k] = merge(base?.[k], v);
  }
  return out;
}
const plain = (u: any) => { const { no3d, ...rest } = u; return rest; };
const UI: { ja: typeof ja; en: typeof en } = SHOW3D
  ? { ja: plain(ja), en: plain(en) } as any
  : { ja: merge(plain(ja), ja.no3d), en: merge(plain(en), en.no3d) };
export const t = (lang: Lang) => UI[lang];

const BASE = import.meta.env.BASE_URL.replace(/\/?$/, "/");   // "/railclass/"

/** A page of the site in this language: page("en", "view.html") -> /railclass/en/view.html */
export const page = (lang: Lang, path = "") => BASE + (lang === "ja" ? "" : lang + "/") + path;
/** Generated data, shared by all languages: file("models/mk1.glb") -> /railclass/models/mk1.glb */
export const file = (path: string) => BASE + path;
