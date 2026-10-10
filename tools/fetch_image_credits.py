"""Fetch, from Wikimedia Commons, the author and licence of every class photo (P18) used by the search page,
so that each photo can be shown with its credit (Commons asks for author, licence and a link to the file page).

Input:  data/wikidata/facets/_image.tsv          item, image (Special:FilePath URL; tools/fetch_facets.py)
Output: data/wikidata/facets/_image_credit.tsv   file, artist (text), license, license_url, attribution, thumb
  file         the file name as in _image.tsv (spaces, not underscores)
  artist       extmetadata Artist with the HTML removed ("" when the page gives none)
  license      LicenseShortName (e.g. "CC BY-SA 4.0", "Public domain")
  attribution  AttributionRequired ("true" / "false" / "")
  thumb        the 330 px thumbnail URL from the API, without the tracking query string; "" if the file is missing
One API call per 50 files (the API's limit). Files already in the output are skipped, so the script can be re-run
after an interruption; --all fetches everything again.
Usage: python3 tools/fetch_image_credits.py [--data data] [--all]
"""
import csv, html, json, os, re, sys, time, urllib.parse, urllib.request

ARGS = sys.argv[1:]
def opt(k, d):
    return ARGS[ARGS.index(k) + 1] if k in ARGS else d
FDIR = os.path.join(opt("--data", "data"), "wikidata", "facets")
SRC, OUT = os.path.join(FDIR, "_image.tsv"), os.path.join(FDIR, "_image_credit.tsv")
FP = "http://commons.wikimedia.org/wiki/Special:FilePath/"
API = "https://commons.wikimedia.org/w/api.php"
UA = "train-bodies/0.1 (nakamura.satoru@mail.u-tokyo.ac.jp)"
COLS = ["file", "artist", "license", "license_url", "attribution", "thumb"]

def text(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

def call(files):
    q = dict(action="query", format="json", formatversion="2", prop="imageinfo", iiprop="url|extmetadata",
             iiurlwidth="330", iiextmetadatafilter="Artist|LicenseShortName|LicenseUrl|AttributionRequired",
             titles="|".join("File:" + f for f in files), maxlag="5")
    r = urllib.request.Request(API, data=urllib.parse.urlencode(q).encode(), headers={"User-Agent": UA})
    for wait in (5, 20, 60, None):
        try:
            d = json.load(urllib.request.urlopen(r, timeout=120))
            if d.get("error", {}).get("code") == "maxlag":
                raise IOError("maxlag")
            break
        except Exception as e:
            if wait is None: raise
            print("retry in", wait, "s:", e); time.sleep(wait)
    back = {n["to"]: n["from"] for n in d["query"].get("normalized", [])}
    for p in d["query"]["pages"]:
        f = back.get(p["title"], p["title"])[len("File:"):]
        ii = (p.get("imageinfo") or [{}])[0]
        m = {k: v.get("value", "") for k, v in ii.get("extmetadata", {}).items()}
        yield [f, text(m.get("Artist")), text(m.get("LicenseShortName")), m.get("LicenseUrl", ""),
               m.get("AttributionRequired", ""), ii.get("thumburl", "").split("?")[0]]

def main():
    files = sorted({urllib.parse.unquote(r["image"][len(FP):]) for r in
                    csv.DictReader(open(SRC), delimiter="\t", quoting=csv.QUOTE_NONE)})
    done = set()
    if os.path.exists(OUT) and "--all" not in ARGS:
        done = {r["file"] for r in csv.DictReader(open(OUT), delimiter="\t", quoting=csv.QUOTE_NONE)}
    else:
        with open(OUT, "w") as o: o.write("\t".join(COLS) + "\n")
    todo = [f for f in files if f not in done]
    print(len(files), "files,", len(todo), "to fetch")
    with open(OUT, "a") as o:
        for k in range(0, len(todo), 50):
            for row in call(todo[k:k + 50]):
                o.write("\t".join(c.replace("\t", " ").replace("\n", " ") for c in row) + "\n")
            o.flush()
            if k // 50 % 20 == 0: print(k + 50, "/", len(todo))
            time.sleep(1)

if __name__ == "__main__":
    main()
