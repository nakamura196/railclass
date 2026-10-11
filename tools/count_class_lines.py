"""Count how far Wikidata alone takes the classes of the index to a line that OSM can draw (no geometry fetched).

1. Wikidata: every "vehicle normally used" (P3438) statement (tools/queries/wd-all-lines.rq), kept where the vehicle
   is a class of docs/search/index.json (the class itself only, no P279 step).
2. Wikidata: P31 of those line items, to see how many are lines (track) and how many are services.
3. OSM, through QLever's osm-planet endpoint (one SPARQL query per 500 lines instead of one Overpass call per line):
   relations that carry wikidata=<line>, with their route= tag.

Output (data/, not in git): wd-all-lines.csv, wd-index-lines.json, wd-index-lines-p31.csv, osm-index-lines.csv.
Usage: python3 tools/count_class_lines.py
"""
import collections, csv, json, os, urllib.parse, urllib.request

UA = "railclass/0.1 (https://github.com/nakamura196/railclass)"
HERE = os.path.dirname(__file__)
os.makedirs("data", exist_ok=True)

def sparql(url, q):
    r = urllib.request.Request(url, data=urllib.parse.urlencode({"query": q}).encode(),
                               headers={"Accept": "text/csv", "User-Agent": UA})
    return list(csv.DictReader(urllib.request.urlopen(r, timeout=300).read().decode().splitlines()))

def qid(u):
    return u.rsplit("/", 1)[-1]

def chunks(xs, n):
    return [xs[i:i + n] for i in range(0, len(xs), n)]

def main():
    ids = set(json.load(open("docs/search/index.json"))["id"])
    rows = sparql("https://query.wikidata.org/sparql", open(os.path.join(HERE, "queries", "wd-all-lines.rq")).read())
    with open("data/wd-all-lines.csv", "w") as f:
        w = csv.writer(f); w.writerow(["line", "c", "osm"])
        for r in rows: w.writerow([qid(r["line"]), qid(r["c"]), r["osm"]])
    pairs = {(qid(r["line"]), qid(r["c"])) for r in rows}
    hit = {(l, c) for l, c in pairs if c in ids}
    lines = sorted({l for l, c in hit})
    json.dump(lines, open("data/wd-index-lines.json", "w"))
    print("P3438 statements", len(pairs), "| in the index:", len({c for l, c in hit}), "classes,", len(lines), "lines")

    types = []
    for part in chunks(lines, 400):
        v = " ".join("wd:" + x for x in part)
        types += sparql("https://query.wikidata.org/sparql",
                        f'SELECT ?l ?t ?tl WHERE {{ VALUES ?l {{ {v} }} ?l wdt:P31 ?t . '
                        f'OPTIONAL {{ ?t rdfs:label ?tl FILTER(lang(?tl)="en") }} }}')
    with open("data/wd-index-lines-p31.csv", "w") as f:
        w = csv.writer(f); w.writerow(["line", "type", "typeLabel"])
        for r in types: w.writerow([qid(r["l"]), qid(r["t"]), r.get("tl", "")])
    for (t, tl), n in collections.Counter((qid(r["t"]), r.get("tl", "")) for r in types).most_common(10):
        print(" ", n, t, tl)

    rels = []
    for part in chunks(lines, 500):
        v = " ".join('"%s"' % x for x in part)    # QLever keeps the wikidata= tag as a plain string
        rels += sparql("https://qlever.dev/api/osm-planet",
                       "PREFIX osmkey: <https://www.openstreetmap.org/wiki/Key:>\n"
                       f"SELECT ?q ?rel ?route WHERE {{ VALUES ?q {{ {v} }} ?rel osmkey:wikidata ?q . "
                       'FILTER(STRSTARTS(STR(?rel), "https://www.openstreetmap.org/relation/")) '
                       "OPTIONAL { ?rel osmkey:route ?route } }")
    with open("data/osm-index-lines.csv", "w") as f:
        w = csv.writer(f); w.writerow(["line", "rel", "route"])
        for r in rels: w.writerow([r["q"], qid(r["rel"]), r.get("route", "")])
    tagged = {r["q"] for r in rels}
    print("OSM relations", len(rels), "| lines with one:", len(tagged), "| classes reaching one:",
          len({c for l, c in hit if l in tagged}))
    print(" ", collections.Counter(r.get("route", "") for r in rels).most_common(8))

if __name__ == "__main__":
    main()
