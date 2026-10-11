"""Draw each line of tools/class_lines.tsv and tools/class_lines_wd.tsv from OpenStreetMap, found by its Wikidata ID (the OSM tag wikidata=Q…).
The geometry stays out of the dataset (docs/notes/data-model.md, "路線の線データ"): OSM data is ODbL, so it is
written to its own folder as a display layer, never into the RDF or the search index.

Input:  tools/class_lines.tsv            class, line, ... (one row per class and line; hand-filled with sources)
        tools/class_lines_wd.tsv         the same columns, from Wikidata P3438 alone (tools/wd_class_lines.py)
Output: docs/lines/_osm.tsv              line, rel, type, route, name: every OSM relation that carries wikidata=<line>
        docs/lines/<line>.geojson         one Feature, MultiLineString of the track (ways of the relations and of
                                          their child relations), simplified to ~TOL degrees, 5 decimals
        docs/lines/_all.geojson           every <line>.geojson in one FeatureCollection, for the map page
--qlever asks QLever's OSM endpoint (SPARQL, about 1 s a line) instead of Overpass; the same relations and track ways
(compared on 14 lines: same ways, at most 30 m apart; docs/notes/data-model.md, 2026-10-10). It knows no route_master
tag, so a route_master's route column is empty in _osm.tsv.
--count only looks the relations up (tags, no geometry) and prints how many lines OSM can draw.
Overpass is asked once per line, GAP s apart, with retries on 429/504 (it is a shared, free service). A line that
still fails is reported and skipped; lines that already have a .geojson are not asked again unless --redo (so a run
that was cut short can be started again and goes on where it stopped). _osm.tsv keeps the rows of lines not asked.
Needs shapely.
Usage: python3 tools/osm_lines.py [--count] [--only Q123] [--out docs/lines] [--qlever] [--api URL] [--gap 15] [--redo]
"""
import csv, json, os, sys, time, urllib.parse, urllib.request
from shapely.geometry import LineString, MultiLineString, mapping
from shapely.ops import linemerge
from shapely import wkt

ARGS = sys.argv[1:]
def opt(k, d):
    return ARGS[ARGS.index(k) + 1] if k in ARGS else d
SRC = [os.path.join(os.path.dirname(__file__), f) for f in ("class_lines.tsv", "class_lines_wd.tsv")]
QLEVER = "--qlever" in ARGS
OUT = opt("--out", os.path.join("docs", "lines"))
API = opt("--api", "https://overpass-api.de/api/interpreter")    # mirror when busy: https://maps.mail.ru/osm/tools/overpass/api/interpreter
UA = "railclass/0.1 (nakamura.satoru@mail.u-tokyo.ac.jp)"
GAP = float(opt("--gap", "0" if QLEVER else "15"))
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

def qlever(q):
    data = urllib.parse.urlencode({"query": "PREFIX osmkey: <https://www.openstreetmap.org/wiki/Key:>\n"
        "PREFIX osmrel: <https://www.openstreetmap.org/relation/>\nPREFIX geo: <http://www.opengis.net/ont/geosparql#>\n" + q}).encode()
    for wait in (10, 60, None):
        try:
            r = urllib.request.Request("https://qlever.dev/api/osm-planet", data=data, headers={"User-Agent": UA, "Accept": "text/csv"})
            return list(csv.DictReader(urllib.request.urlopen(r, timeout=300).read().decode().splitlines()))
        except Exception as e:
            if wait is None: raise
            print("  retry in", wait, "s:", e); time.sleep(wait)

def relations(q):
    if QLEVER:    # QLever keeps the wikidata= tag as a plain string
        return [dict(line=q, rel=r["rel"].rsplit("/", 1)[-1], type=r["type"], route=r["route"] or r["railway"], name=r["name"])
                for r in qlever(f'SELECT ?rel ?type ?route ?railway ?name WHERE {{ ?rel osmkey:wikidata "{q}" . '
                                'FILTER(STRSTARTS(STR(?rel), "https://www.openstreetmap.org/relation/")) '
                                "OPTIONAL { ?rel osmkey:type ?type } OPTIONAL { ?rel osmkey:route ?route } "
                                "OPTIONAL { ?rel osmkey:railway ?railway } OPTIONAL { ?rel osmkey:name ?name } }")]
    d = overpass(f'[out:json][timeout:60];rel["wikidata"="{q}"];out tags;')
    return [dict(line=q, rel=e["id"], type=e["tags"].get("type", ""),
                 route=e["tags"].get("route") or e["tags"].get("route_master") or e["tags"].get("railway", ""),
                 name=e["tags"].get("name", "")) for e in d["elements"]]

def geometry(q):
    """The ways of every relation tagged wikidata=q and of their child relations (route_master -> routes)."""
    if QLEVER:
        rows = qlever(f'SELECT DISTINCT ?way ?rw ?wkt WHERE {{ ?rel osmkey:wikidata "{q}" . '
                      "?rel (osmrel:member/osmrel:member_id)? ?r . ?r osmrel:member/osmrel:member_id ?way . "
                      "?way osmkey:railway ?rw . ?way geo:hasGeometry/geo:asWKT ?wkt }")
        lines = [wkt.loads(r["wkt"]) for r in rows if r["rw"] in TRACK and r["way"].startswith("https://www.openstreetmap.org/way/")]
        return merge([l for l in lines if l.geom_type == "LineString"])
    d = overpass(f'[out:json][timeout:180];rel["wikidata"="{q}"]->.r;(.r;rel(r.r);)->.a;way(r.a);out tags geom;')
    lines = []
    for e in d["elements"]:
        t, g = e.get("tags", {}), e.get("geometry", [])
        if len(g) < 2: continue
        if t.get("railway") in TRACK or "highway" in t:    # track (or road, for a bus route); not platforms
            if t.get("railway") == "platform" or t.get("public_transport") == "platform": continue
            lines.append(LineString([(p["lon"], p["lat"]) for p in g]))
    return merge(lines)

def merge(lines):
    if not lines: return None
    m = linemerge(lines).simplify(TOL, preserve_topology=False)
    parts = list(m.geoms) if hasattr(m, "geoms") else [m]
    parts = [[(round(x, 5), round(y, 5)) for x, y in p.coords] for p in parts if p.length > 0]
    return MultiLineString(parts), len(lines)

def main():
    rows = [r for p in SRC if os.path.exists(p) for r in csv.DictReader(open(p), delimiter="\t")]
    want = [opt("--only", "")] if "--only" in ARGS else sorted({r["line"] for r in rows if r["line"]})
    os.makedirs(OUT, exist_ok=True)
    tsv = os.path.join(OUT, "_osm.tsv")
    old = list(csv.DictReader(open(tsv), delimiter="\t")) if os.path.exists(tsv) else []
    done = {q for q in want if os.path.exists(os.path.join(OUT, q + ".geojson"))} if "--redo" not in ARGS and "--count" not in ARGS else set()
    asked, found, failed = set(), [], []
    for n, q in enumerate(want, 1):
        if q in done: continue
        try:
            rs = relations(q)
            asked.add(q); found += rs
            print(f"{n}/{len(want)} {q}: {len(rs)} relation(s)", "; ".join(f"{r['rel']} {r['type']}/{r['route']} {r['name']}" for r in rs)[:200])
            time.sleep(GAP)
            if "--count" in ARGS or not rs: continue
            got = geometry(q)
        except Exception as e:
            print(f"{n}/{len(want)} {q}: failed ({e}); skipped"); failed.append(q); time.sleep(GAP); continue
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
        time.sleep(GAP)
    keep = [r for r in old if r["line"] not in asked]
    with open(tsv, "w") as o:
        o.write("line\trel\ttype\troute\tname\n")
        for r in sorted(keep + found, key=lambda r: (r["line"], str(r["rel"]))):
            o.write("\t".join(str(r[c]).replace("\t", " ") for c in ("line", "rel", "type", "route", "name")) + "\n")
    if "--count" not in ARGS and "--only" not in ARGS:    # the map page draws them all from one file
        allf = [json.load(open(os.path.join(OUT, q + ".geojson")))["features"][0] for q in sorted({r["line"] for r in rows if r["line"]})
                if os.path.exists(os.path.join(OUT, q + ".geojson"))]
        json.dump({"type": "FeatureCollection", "features": allf}, open(os.path.join(OUT, "_all.geojson"), "w"),
                  ensure_ascii=False, separators=(",", ":"))
        print(f"_all.geojson: {len(allf)} lines, {os.path.getsize(os.path.join(OUT, '_all.geojson')) / 1e6:.1f} MB")
    hit = {r["line"] for r in keep + found}
    print(f"lines: {len(want)} | with an OSM relation tagged wikidata=: {len(hit & set(want))} | shapes: "
          f"{sum(os.path.exists(os.path.join(OUT, q + '.geojson')) for q in want)} | failed this run: {' '.join(failed) or '-'}")
    print("missing:", " ".join(q for q in want if q not in hit and q not in failed))

if __name__ == "__main__":
    main()
