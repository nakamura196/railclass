"""Draw each line of tools/class_lines.tsv from OpenStreetMap, found by its Wikidata ID (the OSM tag wikidata=Q…).
The geometry stays out of the dataset (docs/notes/data-model.md, "路線の線データ"): OSM data is ODbL, so it is
written to its own folder as a display layer, never into the RDF or the search index.

Input:  tools/class_lines.tsv            class, line, ... (one row per class and line; hand-filled with sources)
Output: data/lines/_osm.tsv              line, rel, type, route, name: every OSM relation that carries wikidata=<line>
        data/lines/<line>.geojson         one Feature, MultiLineString of the track (ways of the relations and of
                                          their child relations), simplified to ~TOL degrees, 5 decimals
--count only looks the relations up (tags, no geometry) and prints how many lines OSM can draw.
Overpass is asked once per line, 2 s apart, with retries on 429/504 (it is a shared, free service).
Needs shapely.
Usage: python3 tools/osm_lines.py [--count] [--only Q123] [--out data/lines]
"""
import csv, json, os, sys, time, urllib.parse, urllib.request
from shapely.geometry import LineString, MultiLineString, mapping
from shapely.ops import linemerge

ARGS = sys.argv[1:]
def opt(k, d):
    return ARGS[ARGS.index(k) + 1] if k in ARGS else d
SRC = os.path.join(os.path.dirname(__file__), "class_lines.tsv")
OUT = opt("--out", os.path.join("data", "lines"))
API = "https://overpass-api.de/api/interpreter"
UA = "train-bodies/0.1 (nakamura.satoru@mail.u-tokyo.ac.jp)"
TOL = 0.0003    # degrees, about 30 m: enough for a class page map, keeps a long line to some tens of KB
TRACK = {"rail", "light_rail", "subway", "monorail", "narrow_gauge", "tram", "funicular", "construction"}

def overpass(q):
    data = urllib.parse.urlencode({"data": q}).encode()
    for wait in (10, 60, 180, None):
        try:
            r = urllib.request.Request(API, data=data, headers={"User-Agent": UA})
            return json.load(urllib.request.urlopen(r, timeout=200))
        except Exception as e:
            if wait is None: raise
            print("  retry in", wait, "s:", e); time.sleep(wait)

def relations(q):
    d = overpass(f'[out:json][timeout:60];rel["wikidata"="{q}"];out tags;')
    return [dict(line=q, rel=e["id"], type=e["tags"].get("type", ""),
                 route=e["tags"].get("route") or e["tags"].get("route_master") or e["tags"].get("railway", ""),
                 name=e["tags"].get("name", "")) for e in d["elements"]]

def geometry(q):
    """The ways of every relation tagged wikidata=q and of their child relations (route_master -> routes)."""
    d = overpass(f'[out:json][timeout:180];rel["wikidata"="{q}"]->.r;(.r;rel(r.r);)->.a;way(r.a);out tags geom;')
    lines = []
    for e in d["elements"]:
        t, g = e.get("tags", {}), e.get("geometry", [])
        if len(g) < 2: continue
        if t.get("railway") in TRACK or "highway" in t:    # track (or road, for a bus route); not platforms
            if t.get("railway") == "platform" or t.get("public_transport") == "platform": continue
            lines.append(LineString([(p["lon"], p["lat"]) for p in g]))
    if not lines: return None
    m = linemerge(lines).simplify(TOL, preserve_topology=False)
    parts = list(m.geoms) if hasattr(m, "geoms") else [m]
    parts = [[(round(x, 5), round(y, 5)) for x, y in p.coords] for p in parts if p.length > 0]
    return MultiLineString(parts), len(lines)

def main():
    rows = list(csv.DictReader(open(SRC), delimiter="\t"))
    want = [opt("--only", "")] if "--only" in ARGS else sorted({r["line"] for r in rows if r["line"]})
    os.makedirs(OUT, exist_ok=True)
    found = []
    for n, q in enumerate(want, 1):
        rs = relations(q); found += rs
        print(f"{n}/{len(want)} {q}: {len(rs)} relation(s)", "; ".join(f"{r['rel']} {r['type']}/{r['route']} {r['name']}" for r in rs)[:200])
        time.sleep(2)
        if "--count" in ARGS or not rs: continue
        got = geometry(q)
        if not got: print("  no track ways"); continue
        geom, ways = got
        label = next((r["lineLabel"] for r in rows if r["line"] == q), "")
        f = {"type": "Feature", "id": q, "geometry": mapping(geom),
             "properties": {"wikidata": q, "label": label, "osm_relations": [r["rel"] for r in rs], "ways": ways,
                            "license": "ODbL-1.0", "attribution": "© OpenStreetMap contributors",
                            "source": "https://www.openstreetmap.org/relation/" + str(rs[0]["rel"])}}
        p = os.path.join(OUT, q + ".geojson")
        json.dump({"type": "FeatureCollection", "features": [f]}, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
        print(f"  {ways} ways -> {len(geom.geoms)} parts, {os.path.getsize(p) / 1e3:.0f} KB")
        time.sleep(2)
    with open(os.path.join(OUT, "_osm.tsv"), "w") as o:
        o.write("line\trel\ttype\troute\tname\n")
        for r in found:
            o.write("\t".join(str(r[c]).replace("\t", " ") for c in ("line", "rel", "type", "route", "name")) + "\n")
    hit = {r["line"] for r in found}
    print(f"lines: {len(want)} | with an OSM relation tagged wikidata=: {len(hit)} | missing: {' '.join(q for q in want if q not in hit)}")

if __name__ == "__main__":
    main()
