// Display text lives in ja.json / en.json (one file per language). Links are built here so every page agrees.
import ja from "./ja.json";
import en from "./en.json";

export type Lang = "ja" | "en";
export const LANGS: Lang[] = ["ja", "en"];
const UI = { ja, en };
export const t = (lang: Lang) => UI[lang];

const BASE = import.meta.env.BASE_URL.replace(/\/?$/, "/");   // "/train-bodies/"

/** A page of the site in this language: page("en", "view.html") -> /train-bodies/en/view.html */
export const page = (lang: Lang, path = "") => BASE + (lang === "ja" ? "" : lang + "/") + path;
/** Generated data, shared by all languages: file("models/mk1.glb") -> /train-bodies/models/mk1.glb */
export const file = (path: string) => BASE + path;
