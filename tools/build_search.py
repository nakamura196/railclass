"""Build the search index (docs/search/index.json) and the site counts (docs/search/stats.json).

The page docs/search/index.html (static, with search.js) loads index.json; nothing is generated into the HTML.
Inputs:
  docs/rdf/facets.json                  the facets (made by the RDF work; read, not listed here)
  data/classes.tsv                      the class list, Japan excluded (tools/build_classes.py); only source=wikidata
                                        rows are used: ERATV data stays out of docs/ until its reuse terms are known
  data/wikidata/class-labels-ja.tsv     Japanese labels (tools/queries/wd-class-labels-ja.rq)
  data/wikidata/facets/<id>.tsv         facet values per class (tools/fetch_facets.py)
  data/wikidata/facets/_image_credit.tsv  author, licence and thumbnail of each photo (tools/fetch_image_credits.py), if present
  data/photos/_photos.tsv               the local copies of the photos (tools/fetch_photos.py), if present; the site
                                        serves them from photos/<key>.webp instead of Wikimedia
  docs/rdf/all.jsonld                   the class and model RDF (made by the RDF work), if present. For the classes in it:
                                        its values replace the Wikidata ones (facets with on=livery take the values of the
                                        liveries of its models), facets marked "inherit" take the value of the
                                        skos:broader class when the class has none, the 3D models come from schema:subjectOf,
                                        and classes outside the Wikidata list (SkyTrain Mark I, Airo, XD60...) are added
index.json is column-wise to stay small:
  {"facets":[{id,label,datatype,unit,values:[[id,en,ja],...]}], "n":N, "id":[...], "en":[...], "ja":[...],
   "img":[file name or ""], "photo":[local copy key (photos/<key>.webp) | ""],
   "thumb":[hash dir "f/f3" | full thumbnail URL | "" (use Special:FilePath)] (only used when there is no local copy),
   "credit":[[artist index, licence index] | 0], "artists":[text], "licenses":[[short name, url]],
   a group facet {id:"<facet id>Group", of:"<facet id>", ...} just before each facet listed in GROUPS, "models":[[model id,...]], "page":[1 if docs/rdf/class/<id>.html exists else 0], "<facet id>":[[value index,...] | number | null]}
Usage: python3 tools/build_search.py [--data data] [--facets docs/rdf/facets.json] [--out docs/search]
"""
import csv, collections, json, os, sys, urllib.parse

ARGS = sys.argv[1:]
def opt(k, d):
    return ARGS[ARGS.index(k) + 1] if k in ARGS else d
DATA = opt("--data", "data")
FACETS = opt("--facets", "docs/rdf/facets.json")
OUT = opt("--out", "docs/search")
RDF = opt("--rdf", "docs/rdf/all.jsonld")
BASE = "https://nakamura196.github.io/train-bodies/rdf/"
FP = "http://commons.wikimedia.org/wiki/Special:FilePath/"
THUMB = "https://thumb.wikimedia.org/wikipedia/commons/thumb/"   # search.js builds THUMB + h + "/" + f + "/330px-" + f
# The type facet (kind) has ~700 values, many used once. They are folded into these groups, shown as a facet of their
# own ("kindGroup", just above it). A value goes to the first group it is a subclass of (wdt:P279*,
# data/wikidata/facets/kind_broader.tsv); several ancestors in one entry are one group. The list is a choice of this
# site, not Wikidata's: picked on 2026-10-09 from the ancestors that cover the most classes, plus the values most often left in "other"
# (diesel railcar Q10915943 and Q7132141 have no subclass link to the railcar classes).
GROUPS = {"kind": [
    (["Q171043"], "steam locomotive", "蒸気機関車"),
    (["Q625151"], "electric locomotive", "電気機関車"),
    (["Q34336"], "diesel locomotive", "ディーゼル機関車"),
    (["Q93301"], "other locomotive", "その他の機関車"),
    (["Q15825863", "Q3407658"], "tram / light rail vehicle", "路面電車・LRV"),
    (["Q4102249"], "subway car", "地下鉄車両"),
    (["Q483373"], "electric multiple unit", "電車"),
    (["Q116951672", "Q1567915", "Q10915943", "Q7132141"], "diesel multiple unit / railcar", "気動車"),
    (["Q3959904", "Q752392", "Q640040", "Q50398146", "Q3707399"], "other multiple unit / railcar", "その他の動力車"),
    (["Q11504498", "Q753779"], "passenger car", "客車"),
    (["Q9166501"], "freight car", "貨車"),
    (["Q1117277", "Q800342"], "service vehicle", "事業用車"),
    ([], "other", "その他"),
]}

def read(p):
    return list(csv.DictReader(open(p), delimiter="\t", quoting=csv.QUOTE_NONE))

def load_rdf():
    """Classes in docs/rdf/all.jsonld: {cid: {en, ja, models, broader, values: {property uri: [values]}}}, and value labels."""
    out = dict(classes={}, labels={})
    if not os.path.exists(RDF):
        return out
    d = json.load(open(RDF))
    ctx = d["@context"]
    def expand(k):
        if k.startswith("@"): return k
        pre, _, rest = k.partition(":")
        if rest and pre in ctx and isinstance(ctx[pre], str): return ctx[pre] + rest
        return k if ":" in k else ctx.get("@vocab", "") + k
    def short(v):
        v = v["@id"] if isinstance(v, dict) and "@id" in v else v["@value"] if isinstance(v, dict) else v
        v = expand(v) if isinstance(v, str) and ":" in v and not v.startswith("http") else v
        if isinstance(v, str):
            for pre in ("http://www.wikidata.org/entity/", BASE + "class/", BASE + "model/"):
                if v.startswith(pre): return v[len(pre):]
        return v
    def many(v):
        return v if isinstance(v, list) else [v]
    def lang(v):
        return {x["@language"]: x["@value"] for x in many(v or []) if isinstance(x, dict) and "@language" in x}
    def props(n):
        return {expand(k): [short(x) for x in many(v)] for k, v in n.items()
                if expand(k).startswith("http://www.wikidata.org/prop/direct/") or expand(k).startswith(ctx.get("@vocab", "-"))}
    byid = {n["@id"]: n for n in d["@graph"]}
    livery = {}                                      # model id -> {property uri: [values]} of its livery
    for n in d["@graph"]:
        if "livery" in n and "@id" in n["livery"] and n["livery"]["@id"] in byid:
            livery[short(n["@id"])] = props(byid[n["livery"]["@id"]])
    for n in d["@graph"]:
        types = [expand(t) for t in many(n.get("@type", []))]
        nid = short(n["@id"])
        if "rdfs:label" in n and not any(t.endswith("VehicleClass") for t in types):
            l = lang(n["rdfs:label"]); out["labels"][nid] = [l.get("en", ""), l.get("ja", "")]
        if not any(t.endswith("VehicleClass") for t in types):
            continue
        l = lang(n.get("skos:prefLabel") or n.get("rdfs:label"))
        c = dict(en=l.get("en", ""), ja=l.get("ja", ""), models=sorted(short(m) for m in many(n.get("schema:subjectOf", []))),
                 broader=short(n["skos:broader"]) if "skos:broader" in n else None, values=props(n), livery={})
        for m in c["models"]:                        # a class has a livery value when any of its models has it
            for u, vs in livery.get(m, {}).items():
                c["livery"].setdefault(u, [])
                c["livery"][u] += [v for v in vs if v not in c["livery"][u]]
        out["classes"][nid] = c
    return out

def credits(idx, fdir):
    """Author and licence of each photo, and its thumbnail address (to skip the Special:FilePath redirect)."""
    p = os.path.join(fdir, "_image_credit.tsv")
    if not os.path.exists(p):
        print("no photo credits yet: run tools/fetch_image_credits.py"); return
    cr = {r["file"]: r for r in read(p)}
    lp = os.path.join(DATA, "photos", "_photos.tsv")
    local = {r["file"]: r["key"] for r in read(lp)} if os.path.exists(lp) else {}
    artists, apos, lics, lpos = [], {}, [], {}
    idx["photo"], idx["thumb"], idx["credit"] = [], [], []
    for f in idx["img"]:
        r = cr.get(f)
        if not r or not r["thumb"]:
            idx["photo"].append(""); idx["thumb"].append(""); idx["credit"].append(0); continue
        idx["photo"].append(local.get(f, ""))
        u = f.replace(" ", "_")
        t = urllib.parse.unquote(r["thumb"])
        if t.startswith(THUMB) and t.endswith("/" + u + "/330px-" + u) and t[len(THUMB) + 4] == "/":
            t = t[len(THUMB):len(THUMB) + 4]
        else:
            t = r["thumb"]
        idx["thumb"].append("" if f in local else t)
        a, l = r["artist"][:200], (r["license"], r["license_url"])
        if a not in apos: apos[a] = len(artists); artists.append(a)
        if l not in lpos: lpos[l] = len(lics); lics.append(list(l))
        idx["credit"].append([apos[a], lpos[l]])
    idx["artists"], idx["licenses"] = artists, lics
    print("photos with credit:", sum(1 for c in idx["credit"] if c), "of", sum(1 for f in idx["img"] if f),
          "| local copy:", sum(1 for k in idx["photo"] if k), "| short thumb:", sum(1 for t in idx["thumb"] if len(t) == 4), "| other thumb:", sum(1 for t in idx["thumb"] if len(t) > 4))

def group(fid, values, col, fdir):
    """The group facet of an iri facet: (facet, column). Each class gets the groups of its values."""
    anc = {}
    p = os.path.join(fdir, fid + "_broader.tsv")
    if os.path.exists(p):
        for r in read(p): anc.setdefault(r["value"], set()).add(r["ancestor"])
    gs = GROUPS[fid]
    def which(v):
        a = anc.get(v, set()) | {v}
        return next(k for k, (ids, _, _) in enumerate(gs) if not ids or a & set(ids))
    of = [which(v[0]) for v in values]
    gcol = [sorted({of[k] for k in c}) for c in col]
    g = dict(id=fid + "Group", label=dict(ja="種類（大分類）", en="Type (group)"), datatype="iri", of=fid,
             values=[[ids[0] if ids else "other", en, ja] for ids, en, ja in gs])
    return g, gcol


def main():
    rows = [r for r in read(os.path.join(DATA, "classes.tsv")) if r["source"] == "wikidata"]
    ja = {r["item"]: r["label_ja"] for r in read(os.path.join(DATA, "wikidata", "class-labels-ja.tsv"))}
    fdir = os.path.join(DATA, "wikidata", "facets")
    img = {r["item"]: urllib.parse.unquote(r["image"][len(FP):]) for r in read(os.path.join(fdir, "_image.tsv"))}
    rdf = load_rdf()
    ids = [r["id"] for r in rows] + [c for c in rdf["classes"] if c not in {r["id"] for r in rows}]
    pos = {q: i for i, q in enumerate(ids)}
    en = {r["id"]: r["label"] for r in rows}
    idx = dict(n=len(ids), id=ids, facets=[],
               en=[rdf["classes"].get(q, {}).get("en") or en.get(q, "") for q in ids],
               ja=[rdf["classes"].get(q, {}).get("ja") or ja.get(q, "") for q in ids],
               img=[img.get(q, "") for q in ids],
               models=[rdf["classes"].get(q, {}).get("models", []) for q in ids],
               page=[1 if q in rdf["classes"] else 0 for q in ids])
    credits(idx, fdir)
    for f in json.load(open(FACETS))["facets"]:
        d = dict(id=f["id"], label=f["label"], datatype=f["datatype"])
        if f.get("unit"): d["unit"] = f["unit"]
        p = os.path.join(fdir, f["id"] + ".tsv")
        got = {}                                     # item -> [values] (iri) or value
        if f["datatype"] == "iri" and os.path.exists(p):
            for r in read(p):
                got.setdefault(r["item"], []).append(r["value"])
                rdf["labels"].setdefault(r["value"], [r["label_en"], r["label_ja"]])
        elif f["datatype"] in ("decimal", "integer", "gYear") and os.path.exists(p):
            got = {r["item"]: int(float(r["value"])) for r in read(p) if r["value"]}
        for q, c in rdf["classes"].items():          # the RDF wins for its classes
            v = c["livery" if f.get("on") == "livery" else "values"].get(f["uri"])
            if v is None and f.get("inherit"):
                v = rdf["classes"].get(c.get("broader"), {}).get("values", {}).get(f["uri"])
            if v is not None:
                got[q] = v if f["datatype"] == "iri" else v[0]
            elif q in got and f["datatype"] == "boolean":
                del got[q]
        if not got and f["datatype"] != "boolean":
            print("no values yet:", f["id"]); continue
        if f["datatype"] == "iri":
            vals, vpos, col = [], {}, [[] for _ in ids]
            for q, vs in got.items():
                i = pos.get(q)
                if i is None: continue
                for v in vs:
                    if v not in vpos:
                        vpos[v] = len(vals); vals.append([v] + rdf["labels"].get(v, ["", ""]))
                    if vpos[v] not in col[i]: col[i].append(vpos[v])
            d["values"] = vals
        elif f["datatype"] == "boolean":
            col = [1 if got.get(q) in (True, "true", 1) else 0 for q in ids]
        else:
            col = [None] * len(ids)
            for q, v in got.items():
                if q in pos: col[pos[q]] = int(float(v))
        if f["id"] in GROUPS and f["datatype"] == "iri":
            g, gcol = group(f["id"], d["values"], col, fdir)
            idx["facets"].append(g); idx[g["id"]] = gcol
        idx["facets"].append(d); idx[f["id"]] = col
    os.makedirs(OUT, exist_ok=True)
    json.dump(idx, open(os.path.join(OUT, "index.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    countries = set()
    if "country" in idx:
        countries = {v for c in idx["country"] for v in c}
    stats = dict(classes=len(ids), models=sum(len(v) for v in idx["models"]), countries=len(countries))
    json.dump(stats, open(os.path.join(OUT, "stats.json"), "w"))
    print(stats, round(os.path.getsize(os.path.join(OUT, "index.json")) / 1024), "KB")

if __name__ == "__main__":
    main()
