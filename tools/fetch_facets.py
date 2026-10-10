"""Fetch, from Wikidata, the value of every search facet for every rolling stock class, so that the search page
can filter all ~14,000 classes (the class RDF in docs/rdf/ covers only the classes with a 3D model so far).

The facets are not listed here: they are read from docs/rdf/facets.json (made by the RDF work). Each facet whose
uri is a Wikidata property (http://www.wikidata.org/prop/direct/P...) is fetched with one query:
  iri      -> data/wikidata/facets/<id>.tsv  item, value, value label en, value label ja
  decimal  -> item, value (normalised to SI by Wikidata; converted to the facet's unit: km/h)
  gYear    -> item, year
Also data/wikidata/facets/_image.tsv (P18, for thumbnails), and for the type facet (kind) kind_broader.tsv:
  value, ancestor (wdt:P279*, the value itself included), so that tools/build_search.py can fold the ~700 type values
  into a few groups. Other facets (has3d...) come from the RDF.
Usage: python3 tools/fetch_facets.py [--facets docs/rdf/facets.json] [--data data] [--only id,id]
"""
import json, os, sys, time, urllib.request, urllib.parse

ARGS = sys.argv[1:]
def opt(k, d):
    return ARGS[ARGS.index(k) + 1] if k in ARGS else d
FACETS = opt("--facets", "docs/rdf/facets.json")
OUT = os.path.join(opt("--data", "data"), "wikidata", "facets")
ONLY = set(opt("--only", "").split(",")) - {""}
WDT = "http://www.wikidata.org/prop/direct/"
POP = "?item wdt:P31/wdt:P279* wd:Q811704."
BROADER = {"kind"}   # facets whose values tools/build_search.py folds into groups
UNIT = {"km/h": 3.6}   # Wikidata normalises speed to m/s

def run(q):
    r = urllib.request.Request("https://query.wikidata.org/sparql",
        data=urllib.parse.urlencode({"query": q, "format": "json"}).encode(),
        headers={"Accept": "application/sparql-results+json", "User-Agent": "train-bodies/0.1 (nakamura.satoru@mail.u-tokyo.ac.jp)"})
    d = json.load(urllib.request.urlopen(r, timeout=300))
    cols = d["head"]["vars"]
    for b in d["results"]["bindings"]:
        yield [b[c]["value"].replace("http://www.wikidata.org/entity/", "") if c in b else "" for c in cols]

def query(f):
    p = "wdt:" + f["uri"][len(WDT):]
    if f["datatype"] == "iri":
        return f"""SELECT ?item ?v ?en ?ja WHERE {{ {POP} ?item {p} ?v. FILTER(isIRI(?v))
 OPTIONAL {{ ?v rdfs:label ?en FILTER(LANG(?en)="en") }} OPTIONAL {{ ?v rdfs:label ?ja FILTER(LANG(?ja)="ja") }} }}"""
    if f["datatype"] in ("decimal", "integer"):
        pid = f["uri"][len(WDT):]
        return f"""SELECT ?item (MAX(?n) AS ?v) WHERE {{ {POP} ?item p:{pid}/psn:{pid}/wikibase:quantityAmount ?n. }} GROUP BY ?item"""
    if f["datatype"] == "gYear":
        return f"""SELECT ?item (MIN(YEAR(?d)) AS ?v) WHERE {{ {POP} ?item {p} ?d. }} GROUP BY ?item"""

def save(name, header, rows):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".tsv"), "w") as o:
        o.write("\t".join(header) + "\n")
        for r in rows:
            o.write("\t".join(c.replace("\t", " ").replace("\n", " ") for c in r) + "\n")
    print(name, len(rows))

def main():
    facets = json.load(open(FACETS))["facets"]
    for f in facets:
        # on="livery" (colour): the values are on the 3D models' liveries in the RDF, not on the classes in Wikidata
        if ONLY and f["id"] not in ONLY or not f["uri"].startswith(WDT) or f.get("on", "class") != "class":
            continue
        rows = list(run(query(f)))
        if f["datatype"] in ("decimal", "integer"):
            k = UNIT.get(f.get("unit"), 1)
            rows = [[i, f"{float(v) * k:.0f}"] for i, v in rows]
        save(f["id"], ["item", "value", "label_en", "label_ja"][:len(rows[0]) if rows else 2], rows)
        time.sleep(2)
        if f["id"] in BROADER:
            vals = " ".join(sorted({"wd:" + r[1] for r in rows if r[1].startswith("Q")}))
            save(f["id"] + "_broader", ["value", "ancestor"],
                 list(run(f"SELECT ?v ?a WHERE {{ VALUES ?v {{ {vals} }} ?v wdt:P279* ?a. }}")))
            time.sleep(2)
    if not ONLY or "_image" in ONLY:
        save("_image", ["item", "image"], list(run(f"SELECT ?item (SAMPLE(?i) AS ?img) WHERE {{ {POP} ?item wdt:P18 ?i. }} GROUP BY ?item")))

if __name__ == "__main__":
    main()
