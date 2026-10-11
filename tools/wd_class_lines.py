"""The class -> line table taken from Wikidata alone: every "vehicle normally used" (P3438) statement whose vehicle is a
class of the search index (any rank but deprecated; the class itself, no P279 step: docs/notes/data-model.md, 2026-10-10).

Output: tools/class_lines_wd.tsv, the same columns as the hand-filled tools/class_lines.tsv (which wins where both have
a class and line). status: "historical <year>" when the statement has an end time (P582) or the line item was closed
(P576), otherwise "current". source_url points at the statement on the line's Wikidata page.
Usage: python3 tools/wd_class_lines.py
"""
import csv, json, os, urllib.parse, urllib.request

HERE = os.path.dirname(__file__)
UA = "railclass/0.1 (https://github.com/nakamura196/railclass)"
Q = """SELECT ?line ?c ?st (SAMPLE(?end) AS ?e) (SAMPLE(?closed) AS ?x) (SAMPLE(?en) AS ?le) (SAMPLE(?mul) AS ?lm) (SAMPLE(?any) AS ?la) WHERE {
  ?line p:P3438 ?st . ?st ps:P3438 ?c ; wikibase:rank ?rank . FILTER(?rank != wikibase:DeprecatedRank)
  OPTIONAL { ?st pq:P582 ?end }
  OPTIONAL { ?line wdt:P576 ?closed }
  OPTIONAL { ?line rdfs:label ?en FILTER(lang(?en) = "en") }
  OPTIONAL { ?line rdfs:label ?mul FILTER(lang(?mul) = "mul") }
  OPTIONAL { ?line rdfs:label ?any }
} GROUP BY ?line ?c ?st"""

def main():
    r = urllib.request.Request("https://query.wikidata.org/sparql", data=urllib.parse.urlencode({"query": Q}).encode(),
                               headers={"Accept": "text/csv", "User-Agent": UA})
    rows = list(csv.DictReader(urllib.request.urlopen(r, timeout=300).read().decode().splitlines()))
    ids = set(json.load(open(os.path.join(HERE, "..", "docs", "search", "index.json")))["id"])
    hand = {(r["class"], r["line"]) for r in csv.DictReader(open(os.path.join(HERE, "class_lines.tsv")), delimiter="\t")}
    qid = lambda u: u.rsplit("/", 1)[-1]
    out = {}
    for r in rows:    # one row per statement; a class and line can have several statements
        c, l = qid(r["c"]), qid(r["line"])
        if c not in ids or (c, l) in hand: continue
        year = (r["e"] or r["x"])[:4]
        status = f"historical {year}" if year.isdigit() else "current"
        prev = out.get((c, l))
        if prev and (prev["status"] == "current" or status != "current" and prev["status"] >= status): continue
        out[(c, l)] = dict(**{"class": c}, line=l, lineLabel=r["le"] or r["lm"] or r["la"] or l, status=status,
                           source_url=f"https://www.wikidata.org/wiki/{l}#P3438", source_section="P3438", note="wikidata")
    cols = ["class", "line", "lineLabel", "status", "source_url", "source_section", "note"]
    with open(os.path.join(HERE, "class_lines_wd.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for k in sorted(out):
            f.write("\t".join(out[k][c].replace("\t", " ") for c in cols) + "\n")
    print(len(out), "rows,", len({c for c, l in out}), "classes,", len({l for c, l in out}), "lines,",
          sum(v["status"] != "current" for v in out.values()), "historical")

if __name__ == "__main__":
    main()
