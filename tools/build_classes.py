"""Merge the Wikidata rolling stock classes (Japan excluded) and the ERATV vehicle types into one list.

Inputs (made by tools/sparql.py and tools/eratv_export.py):
  data/wikidata/classes.tsv, data/wikidata/class-names.tsv, data/eratv/eratv.tsv, data/eratv/subcategories.tsv
Output: data/classes.tsv, one row per class:
  - source=wikidata: one Wikidata item (id = Q number)
  - source=eratv: one ERATV type (id = era:<first four groups of the Type ID>; versions folded in)
ERATV types are linked to Wikidata by exact match of normalised names (match=name). Types left over are tried again
with the name cut back word by word from the end, longest first ("ICE T BR 415 Bremsbelagsubstitution" -> "ICE T"):
the ERATV type is then a version of the Wikidata class, skos:narrowMatch (match=prefix). A cut name without a digit
must not be in NOT_PREFIX (generic words, or aliases that point at one operator's class). Before that, a German
series number in the name ("BR 411", "BR1440") is looked up as "DB-Baureihe 411", which is narrower than the
product name in front of it ("ICE T BR 411 ETCS BL3" -> DBAG Class 411, not ICE T).
Such links are candidates, not checked by hand. A name that hits several items is listed with all of them.

Japan rule for Wikidata items: excluded when every country we know of (P17, and P17 of the operators) is Japan;
when no country is known, excluded when the only Wikipedia edition with an article is Japanese.
"""
import csv, re, sys, unicodedata, collections

JP = "Q17"
TYPE_LABEL = {"Q19832486": "locomotive class", "Q811704": "rolling stock class", "Q76154857": "tram model",
              "Q63040754": "multiple unit class", "Q77814805": "train type series", "Q50319430": "tender class",
              "Q63040753": "rail motor coach class", "Q2392395": "Amsterdam tram model", "Q1495859": "Gattung"}

def read(p):
    return list(csv.DictReader(open(p), delimiter="\t", quoting=csv.QUOTE_NONE))

def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold()
    return re.sub(r"[\W_]+", "", s)

# Cut names that hit the wrong item (checked 2026-10-10 against the 445 prefix hits): "Desiro" is an alias of MÁV 426,
# "CRRC" of ŽRSM 711, "RAIL-BUS" of one GTW; "Electric multiple unit" and "Schienenbus" are kinds, not classes
NOT_PREFIX = {"desiro", "crrc", "railbus", "electricmultipleunit", "schienenbus"}

def prefixes(n):
    toks = [t for t in re.split(r"[\s_]+|\s-\s|\(", n) if t]
    for k in range(len(toks) - 1, 0, -1):
        p = norm(" ".join(toks[:k]))
        if len(p) >= 4 and (re.search(r"\d", p) or p not in NOT_PREFIX):
            yield p

def series(n):
    for m in re.finditer(r"\bBR ?(\d{3,4})\b", n):
        yield norm("DB-Baureihe " + m.group(1))

def split(v):
    return [x for x in v.split("|") if x]

# --- Wikidata, Japan excluded
wd, jp_reason = {}, collections.Counter()
for r in read("data/wikidata/classes.tsv"):
    cos = set(split(r["country"])) | set(split(r["operator_country"]))
    wikis = set(split(r["wikis"]))
    if cos:
        if cos == {JP}:
            jp_reason["country"] += 1; continue
    elif wikis == {"ja"}:
        jp_reason["jawiki-only"] += 1; continue
    wd[r["item"]] = r

names = collections.defaultdict(set)
for r in read("data/wikidata/class-names.tsv"):
    if r["item"] in wd and len(norm(r["name"])) >= 4:
        names[norm(r["name"])].add(r["item"])

# --- ERATV, folded to type level
sub = {r["code"]: r["label"] for r in read("data/eratv/subcategories.tsv")}
types = collections.OrderedDict()
for r in read("data/eratv/eratv.tsv"):
    key = "-".join(r["type_id"].split("-")[:4])
    t = types.setdefault(key, {"names": [], "ids": [], "status": set(), "regime": r["regime"]})
    if r["type_name"] not in t["names"]:
        t["names"].append(r["type_name"])
    t["ids"].append(r["type_id"])
    t["status"].add(r["status"].split(" ")[0])

rows, wd_hits, wd_how = [], collections.defaultdict(set), collections.defaultdict(set)
for key, t in types.items():
    cand = set()
    for n in t["names"]:
        cand |= names.get(norm(n), set())
    how = "name" if cand else ""
    if not cand:    # a series number in any of the names, else the longest cut of the first name that hits
        cand = {q for n in t["names"] for p in series(n) for q in names.get(p, ())}
        if not cand:
            cand = next((set(names[p]) for n in t["names"] for p in prefixes(n) if p in names), set())
        how = "prefix" if cand else ""
    for q in cand:
        wd_hits[q].add("era:" + key); wd_how[q].add(how)
    rows.append({"id": "era:" + key, "source": "eratv", "label": t["names"][0],
                 "alt_labels": "|".join(t["names"][1:]), "kind": sub.get(key[:2], "code " + key[:2]),
                 "country": "", "wikidata": "|".join(sorted(cand)), "eratv": "|".join(t["ids"]),
                 "match": how, "status": "|".join(sorted(t["status"])), "regime": t["regime"]})

wd_rows = [{"id": q, "source": "wikidata", "label": r["label_en"], "alt_labels": "",
            "kind": TYPE_LABEL.get(r["type"], r["type"]), "country": "|".join(split(r["country"])),
            "wikidata": q, "eratv": "|".join(sorted(wd_hits.get(q, ()))), "match": "name" if "name" in wd_how[q] else "prefix" if q in wd_hits else "",
            "status": "", "regime": ""} for q, r in wd.items()]

cols = ["id", "source", "label", "alt_labels", "kind", "country", "wikidata", "eratv", "match", "status", "regime"]
with open("data/classes.tsv", "w") as f:
    w = csv.DictWriter(f, cols, delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(wd_rows + rows)

# --- summary for the lab note
era_matched = sum(1 for r in rows if r["wikidata"])
era_how = collections.Counter(r["match"] for r in rows if r["wikidata"])
era_multi = sum(1 for r in rows if "|" in r["wikidata"])
print(f"wikidata items: {len(wd) + sum(jp_reason.values())}, Japan excluded: {dict(jp_reason)}, kept: {len(wd)}")
print(f"eratv records: {sum(len(t['ids']) for t in types.values())}, types: {len(types)}")
print(f"eratv types with a name match: {era_matched} (several items: {era_multi}); wikidata items hit: {len(wd_hits)}")
print("  by how:", dict(era_how))
print(f"merged list rows: {len(wd_rows) + len(rows)}; classes not in Wikidata by name (eratv only): {len(rows) - era_matched}")
print("eratv types by kind:", collections.Counter(r["kind"] for r in rows).most_common())
print("eratv matched by kind:", collections.Counter(r["kind"] for r in rows if r["wikidata"]).most_common())
