"""Keep a local copy of every class photo shown on the search page and the class pages, so that a photo cannot
disappear (deleted on Commons) or change under its credit line (P18 pointed at another file) between rebuilds.
The data (RDF, search index) still names the Commons file and links to its page; the copy is only for display.

Input:  data/wikidata/facets/_image_credit.tsv   file, ..., thumb (330 px thumbnail URL; tools/fetch_image_credits.py)
Output: data/photos/<key>.webp                   the thumbnail, fitted into 330 x 440, WebP quality 75
        data/photos/_photos.tsv                  file, key, bytes, width, height, source, fetched (UTC date)
  key   the first 12 hex digits of md5 of the file name with underscores (stable, so browser caches stay right)
Files already in _photos.tsv with their .webp present are skipped, so the script can be re-run after an
interruption, and a rebuild only fetches photos that are new (a changed P18 is a new file name).
Files with no thumbnail ("" in _image_credit.tsv: deleted or missing on Commons) are not fetched.
--prune deletes local photos whose file is no longer in _image_credit.tsv; --limit N fetches at most N (for a trial).
Needs ImageMagick (magick) for the conversion.
Usage: python3 tools/fetch_photos.py [--data data] [--limit N] [--prune]
"""
import csv, datetime, hashlib, os, subprocess, sys, tempfile, time, urllib.request

ARGS = sys.argv[1:]
def opt(k, d):
    return ARGS[ARGS.index(k) + 1] if k in ARGS else d
DATA = opt("--data", "data")
SRC = os.path.join(DATA, "wikidata", "facets", "_image_credit.tsv")
DIR = os.path.join(DATA, "photos")
OUT = os.path.join(DIR, "_photos.tsv")
UA = "train-bodies/0.1 (nakamura.satoru@mail.u-tokyo.ac.jp)"
COLS = ["file", "key", "bytes", "width", "height", "source", "fetched"]

def key(f):
    return hashlib.md5(f.replace(" ", "_").encode()).hexdigest()[:12]

def read(p):
    return list(csv.DictReader(open(p), delimiter="\t", quoting=csv.QUOTE_NONE)) if os.path.exists(p) else []

def get(url):
    r = urllib.request.Request(url, headers={"User-Agent": UA})
    for wait in (5, 30, 120, None):
        try:
            return urllib.request.urlopen(r, timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code == 404 or wait is None: raise
            print("retry in", wait, "s:", e); time.sleep(wait)
        except Exception as e:
            if wait is None: raise
            print("retry in", wait, "s:", e); time.sleep(wait)

def convert(raw, dst):
    with tempfile.NamedTemporaryFile(suffix=".img") as t:
        t.write(raw); t.flush()
        subprocess.run(["magick", t.name + "[0]", "-auto-orient", "-strip", "-resize", "330x440>", "-quality", "75", dst],
                       check=True, capture_output=True)
    w, h = subprocess.run(["magick", "identify", "-format", "%w %h", dst], check=True, capture_output=True,
                          text=True).stdout.split()
    return int(w), int(h)

def main():
    os.makedirs(DIR, exist_ok=True)
    want = {r["file"]: r["thumb"] for r in read(SRC) if r["thumb"]}
    have = {r["file"]: r for r in read(OUT) if os.path.exists(os.path.join(DIR, r["key"] + ".webp"))}
    todo = sorted(f for f in want if f not in have)
    limit = int(opt("--limit", "0")) or len(todo)
    print(f"photos: {len(want)} with a thumbnail, {len(have)} local, {len(todo)} to fetch" +
          (f" (this run: {min(limit, len(todo))})" if limit < len(todo) else ""))
    today, failed = datetime.datetime.now(datetime.timezone.utc).date().isoformat(), []
    for n, f in enumerate(todo[:limit], 1):
        k = key(f)
        try:
            w, h = convert(get(want[f]), os.path.join(DIR, k + ".webp"))
        except Exception as e:
            failed.append(f); print("failed:", f, e); continue
        have[f] = dict(file=f, key=k, bytes=os.path.getsize(os.path.join(DIR, k + ".webp")), width=w, height=h,
                       source=want[f], fetched=today)
        if n % 200 == 0:
            write(have); print(n, "of", min(limit, len(todo)))
        time.sleep(0.1)
    if "--prune" in ARGS:
        gone = [f for f in have if f not in want]
        for f in gone:
            os.remove(os.path.join(DIR, have.pop(f)["key"] + ".webp"))
        print("pruned:", len(gone))
    write(have)
    size = sum(int(r["bytes"]) for r in have.values())
    print(f"local photos: {len(have)}, {size / 1e6:.1f} MB, {size / max(len(have), 1) / 1e3:.1f} KB each | failed: {len(failed)}")

def write(have):
    keys = {}
    for r in have.values():
        if keys.setdefault(r["key"], r["file"]) != r["file"]:
            sys.exit(f"key clash: {r['file']} and {keys[r['key']]}")
    with open(OUT + ".tmp", "w") as o:
        o.write("\t".join(COLS) + "\n")
        for f in sorted(have):
            o.write("\t".join(str(have[f][c]) for c in COLS) + "\n")
    os.replace(OUT + ".tmp", OUT)

if __name__ == "__main__":
    main()
