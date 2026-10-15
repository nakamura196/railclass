// The one switch for everything about 3D models: show3d in site.config.json at the repository root (docs/notes/site.md, 2026-10-15).
// Env override RAILCLASS_SHOW3D=1 / 0. Server side only (pages and build scripts); the browser scripts read the shape of the data instead.
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const env = process.env.RAILCLASS_SHOW3D;
// npm scripts run in web/
export const SHOW3D: boolean = env ? ["1", "true", "yes", "on"].includes(env.trim().toLowerCase())
  : !!JSON.parse(readFileSync(resolve(process.cwd(), "../site.config.json"), "utf8")).show3d;
