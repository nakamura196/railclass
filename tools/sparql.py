"""Run a SPARQL query (stdin) against the Wikidata Query Service and print the rows as TSV.
The first line is the header (the query's variable names); unbound variables print as empty cells.
Usage: python3 tools/sparql.py [endpoint] < tools/queries/<name>.rq > out.tsv
endpoint defaults to Wikidata; for the ERA ontology use https://graph.data.era.europa.eu/repositories/ERA-Onto
(ERA's server is GraphDB: queries go to /repositories/<id>, not to /sparql, which is only the web UI).
"""
import sys, json, urllib.request, urllib.parse
q = sys.stdin.read()
ep = sys.argv[1] if len(sys.argv) > 1 else "https://query.wikidata.org/sparql"
r = urllib.request.Request(ep,
    data=urllib.parse.urlencode({"query": q, "format": "json"}).encode(),
    headers={"Accept": "application/sparql-results+json", "User-Agent": "railclass/0.1 (nakamura.satoru@mail.u-tokyo.ac.jp)"})
d = json.load(urllib.request.urlopen(r, timeout=300))
cols = d["head"]["vars"]
print("\t".join(cols))
for b in d["results"]["bindings"]:
    print("\t".join(b[c]["value"].replace("http://www.wikidata.org/entity/", "").replace("http://data.europa.eu/949/concepts/", "").replace("\t", " ").replace("\n", " ")
                    if c in b else "" for c in cols))
