"""Reads site.config.json at the repository root: the one switch for everything about 3D models (show3d).

Env override: RAILCLASS_SHOW3D=1 / 0 (also true/false). The Astro site and web/scripts read the same file (web/src/lib/site.ts).
Usage: from site_config import SHOW3D
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def show3d():
    env = os.environ.get("RAILCLASS_SHOW3D")
    if env is not None and env != "":
        return env.strip().lower() in ("1", "true", "yes", "on")
    with open(os.path.join(ROOT, "site.config.json"), encoding="utf-8") as f:
        return bool(json.load(f).get("show3d", True))


SHOW3D = show3d()
