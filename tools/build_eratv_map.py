"""Write the ERATV type -> Wikidata class table that the site publishes (docs/data/eratv-wikidata.tsv) and its
CSVW metadata (docs/data/eratv-wikidata.tsv-metadata.json), which carries the source and the terms.

Only the mapping is published, not the ERATV list itself (decided 2026-10-10). ERA allows reproduction with the source
acknowledged (docs/notes/data-model.md, "ERATV の再利用条件を確かめた").
Input: data/classes.tsv (tools/build_classes.py), the source=eratv rows that have a Wikidata candidate.
One row per (ERATV type, Wikidata candidate); a type with several candidates has several rows (candidates > 1).
Usage: python3 tools/build_eratv_map.py [--exported YYYY-MM-DD]   (the day the ERATV list was exported; default: date of data/eratv/eratv.tsv)
"""
import csv, json, os, sys, time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "docs", "data")
NAME = "eratv-wikidata.tsv"
BASE = "https://nakamura196.github.io/train-bodies/"
ARGS = sys.argv[1:]
exported = ARGS[ARGS.index("--exported") + 1] if "--exported" in ARGS else \
    time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(os.path.join(HERE, "data", "eratv", "eratv.tsv"))))

rows = []
for r in csv.DictReader(open(os.path.join(HERE, "data", "classes.tsv"), encoding="utf-8"), delimiter="\t"):
    if r["source"] != "eratv" or not r["wikidata"]:
        continue
    cands = r["wikidata"].split("|")
    for q in cands:
        rows.append({"eratv_type": r["id"].removeprefix("era:"), "eratv_name": r["label"], "eratv_type_ids": r["eratv"].replace("|", " "),
                     "wikidata": q, "match": r["match"], "candidates": len(cands)})
rows.sort(key=lambda x: (x["eratv_type"], x["wikidata"]))
cols = list(rows[0])
with open(os.path.join(OUT, NAME), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, cols, delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(rows)

desc = {
    "eratv_type": "ERATV vehicle type: the first four groups of the ERATV Type ID (its versions folded together)",
    "eratv_name": "Name of the type in ERATV (of its first version)",
    "eratv_type_ids": "The full ERATV Type IDs (versions) folded into this row, space-separated",
    "wikidata": "Wikidata class this type was matched to",
    "match": "name: the normalised name equals a Wikidata label or alias (an exact match candidate); "
             "prefix: the ERATV name cut back from the end matches, so the type is a version of the class (a skos:narrowMatch candidate)",
    "candidates": "Number of Wikidata candidates for this type (more than 1: not decided, all are listed)",
}
meta = {
    "@context": ["http://www.w3.org/ns/csvw", {"@language": "en"}],
    "url": NAME,
    "dc:title": "ERATV vehicle types matched to Wikidata classes (train-bodies)",
    "dc:description": "Automatic matching of the vehicle types in the European Register of Authorised Types of Vehicles (ERATV) "
                      "to Wikidata rolling stock classes, by name. Not checked by hand. Made by tools/build_eratv_map.py from "
                      "tools/build_classes.py in https://github.com/nakamura196/train-bodies",
    "dc:source": {"@id": "https://eratv.era.europa.eu/Eratv/Home/List",
                  "dc:title": f"European Union Agency for Railways, ERATV (European Register of Authorised Types of Vehicles), list exported {exported}"},
    "dc:rights": "Type IDs and names: source European Union Agency for Railways (ERATV); reproduction is authorised provided the source is "
                 "acknowledged (https://www.era.europa.eu/content/disclaimer-and-copyright-notice). Wikidata identifiers: CC0.",
    "dc:modified": {"@value": time.strftime("%Y-%m-%d"), "@type": "xsd:date"},
    "dialect": {"delimiter": "\t", "header": True},
    "tableSchema": {
        "columns": [{"name": c, "titles": c, "dc:description": desc[c],
                     **({"datatype": "integer"} if c == "candidates" else {}),
                     **({"valueUrl": "http://www.wikidata.org/entity/{wikidata}"} if c == "wikidata" else {})} for c in cols],
        "primaryKey": ["eratv_type", "wikidata"],
    },
}
json.dump(meta, open(os.path.join(OUT, NAME + "-metadata.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len({r['eratv_type'] for r in rows})} ERATV types, {len({r['wikidata'] for r in rows})} Wikidata classes, "
      f"{len(rows)} rows -> {os.path.join(OUT, NAME)} (ERATV exported {exported})")
