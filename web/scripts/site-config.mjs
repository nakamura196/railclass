// Reads site.config.json (repository root): show3d, the one switch for everything about 3D models. Env override RAILCLASS_SHOW3D=1 / 0.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const env = process.env.RAILCLASS_SHOW3D;
export const SHOW3D = env
  ? ["1", "true", "yes", "on"].includes(env.trim().toLowerCase())
  : !!JSON.parse(readFileSync(fileURLToPath(new URL("../../site.config.json", import.meta.url)), "utf8")).show3d;
