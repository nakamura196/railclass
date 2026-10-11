"""When was each class last edited on Wikidata? (for the note "RDF にする利点": how fast the authority changes)

Asks the Wikidata Query Service (schema:dateModified, schema:version) for the last edit time and revision of every
source=wikidata class in data/classes.tsv, and writes data/wikidata/modified.tsv (item, modified, lastrevid).
The time is of the last edit of any kind (labels in any language, sitelinks, statements we do not use), so it is an
upper bound of the changes that reach this site.
Usage: python3 tools/wd_modified.py [--data data]
"""
import csv, json, os, sys, time, urllib.parse, urllib.request

ARGS = sys.argv[1:]
DATA = ARGS[ARGS.index("--data") + 1] if "--data" in ARGS else "data"
UA = "railclass/0.1 (nakamura.satoru@mail.u-tokyo.ac.jp)"

ids = {r["wikidata"] for r in csv.DictReader(open(os.path.join(DATA, "classes.tsv"), encoding="utf-8"), delimiter="\t")
       if r["source"] == "wikidata" and r["wikidata"]}
# One SPARQL query (schema:dateModified, schema:version) instead of ~290 API requests: the API answered 429 at once
# (2026-10-10). Same population as tools/fetch_facets.py; only the items in data/classes.tsv are kept.
q = """SELECT ?item ?m ?v WHERE { ?item wdt:P31/wdt:P279* wd:Q811704. ?item schema:dateModified ?m; schema:version ?v. }"""
req = urllib.request.Request("https://query.wikidata.org/sparql", data=urllib.parse.urlencode({"query": q, "format": "json"}).encode(),
                             headers={"Accept": "application/sparql-results+json", "User-Agent": UA})
for k in range(4):
    try:
        b = json.load(urllib.request.urlopen(req, timeout=300))["results"]["bindings"]; break
    except Exception as e:
        print("retry", e); time.sleep(10 * (k + 1))
else:
    raise SystemExit("Wikidata did not answer")
out = {}
for x in b:
    i = x["item"]["value"].rsplit("/", 1)[-1]
    if i in ids:
        out[i] = [i, x["m"]["value"], x["v"]["value"]]
with open(os.path.join(DATA, "wikidata", "modified.tsv"), "w", encoding="utf-8") as f:
    f.write("item\tmodified\tlastrevid\n" + "".join("\t".join(r) + "\n" for _, r in sorted(out.items())))
print(len(out), "of", len(ids), "items ->", os.path.join(DATA, "wikidata", "modified.tsv"))
