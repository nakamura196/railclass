"""The colour of each line on the maps (map/ and the class pages): Wikidata P465 (sRGB colour hex triplet, CC0) of the line
items that have a shape in docs/lines (tools/osm_lines.py). Lines without P465 get a colour from a fixed palette in the site
(web/src/lib/data.ts, lineColor), so that lines that run side by side (Vancouver's Expo and Millennium lines) can be told apart.
Out: docs/lines/_colors.json  {"Q736619": "#0060A9", ...}
Usage: python3 tools/line_colors.py
"""
import json, os, re, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINES = os.path.join(HERE, "docs", "lines")
OUT = os.path.join(LINES, "_colors.json")
UA = "railclass/0.1 (nakamura.satoru@mail.u-tokyo.ac.jp)"


def sparql(q):
    r = urllib.request.Request("https://query.wikidata.org/sparql", data=urllib.parse.urlencode({"query": q, "format": "json"}).encode(),
                               headers={"Accept": "application/sparql-results+json", "User-Agent": UA})
    return json.load(urllib.request.urlopen(r, timeout=300))["results"]["bindings"]


def main():
    ids = sorted(f[:-len(".geojson")] for f in os.listdir(LINES) if re.fullmatch(r"Q\d+\.geojson", f))
    out = {}
    for i in range(0, len(ids), 300):
        vals = " ".join("wd:" + q for q in ids[i:i + 300])
        for b in sparql(f"SELECT ?l ?c WHERE {{ VALUES ?l {{ {vals} }} ?l wdt:P465 ?c }}"):
            q, c = b["l"]["value"].rsplit("/", 1)[1], b["c"]["value"].strip().lstrip("#").upper()
            if re.fullmatch(r"[0-9A-F]{6}", c) and q not in out:   # a line with several colours: the first one
                out[q] = "#" + c
        time.sleep(1)
    json.dump(dict(sorted(out.items(), key=lambda kv: int(kv[0][1:]))), open(OUT, "w"), indent=0)
    print(f"{len(out)} of {len(ids)} lines have a colour in Wikidata -> {OUT}")


if __name__ == "__main__":
    main()
