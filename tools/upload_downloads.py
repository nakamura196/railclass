"""Publish the download files (STL, OBJ, MTL, USDZ) as assets of one GitHub release, not on GitHub Pages.

Usage: python3 tools/upload_downloads.py [--dry-run]     (run by scripts/deploy-pages.zsh before the build)
  Reads docs/downloads/<model>/formats.json (not in git, made by ~/git/3d/skytrain/tools/export_formats.py) and uploads
  each file whose sha256 differs from the asset already on the release (or that is not there yet), so a deploy sends only
  what changed. The release (tag DL_TAG) is made on first use. Asset names are flat: <model>.<ext> is unique per model.
Why: the Pages site is near its 1 GB limit (900 MB on 2026-10-12, of which downloads 138 MB), and these files grow
  with every model, while nothing on the page needs them to show the model (the viewer uses docs/models/<id>.glb).
Links: the site and the IIIF manifests point at DL_BASE + file (web/src/lib/data.ts, tools/build_iiif.py).
"""
import glob, hashlib, json, os, subprocess, sys

REPO = "nakamura196/railclass"
DL_TAG = "downloads"
DL_BASE = f"https://github.com/{REPO}/releases/download/{DL_TAG}/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def gh(*args, check=True):
    return subprocess.run(["gh", *args], check=check, capture_output=True, text=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    dry = "--dry-run" in sys.argv
    local = {}
    for fj in sorted(glob.glob(os.path.join(ROOT, "docs", "downloads", "*", "formats.json"))):
        d = os.path.dirname(fj)
        for f in json.load(open(fj))["files"]:
            p = os.path.join(d, f["file"])
            if f["file"] in local:
                sys.exit(f"upload_downloads: {f['file']} is in two models; asset names must be unique")
            if sha256(p) != f["sha256"]:
                sys.exit(f"upload_downloads: {p} does not match its formats.json (re-run export_formats.py)")
            local[f["file"]] = (p, f["sha256"])

    if gh("release", "view", DL_TAG, "-R", REPO, check=False).returncode != 0:
        print(f"upload_downloads: making release {DL_TAG}")
        if not dry:
            gh("release", "create", DL_TAG, "-R", REPO, "--latest=false", "--title", "3D model downloads",
               "--notes", "STL, OBJ (+MTL) and USDZ files of the RailClass 3D models (CC BY 4.0). "
               "Linked from https://railclass.ldas.jp/ — the files here are replaced when a model changes.")
    rel = json.loads(gh("api", f"repos/{REPO}/releases/tags/{DL_TAG}", check=False).stdout or "{}")
    remote = {a["name"]: (a.get("digest") or "").removeprefix("sha256:") for a in rel.get("assets", [])}

    todo = [p for name, (p, h) in local.items() if remote.get(name) != h]
    print(f"upload_downloads: {len(local)} files, {len(local) - len(todo)} already on the release, {len(todo)} to upload")
    for i in range(0, len(todo), 20):
        if not dry:
            gh("release", "upload", DL_TAG, "-R", REPO, "--clobber", *todo[i:i + 20])
    extra = sorted(set(remote) - set(local))
    if extra:
        print(f"upload_downloads: on the release but not local (left as is): {' '.join(extra)}")


if __name__ == "__main__":
    main()
