"""Build the RDF of the classes (形式) and the 3D models into docs/rdf/.

Usage: python3 tools/build_rdf.py [--refresh]
  Values come from Wikidata (CC0) for the classes listed in CLASSES, plus the hand-entered values in HAND.
  Wikidata answers are cached in data/wikidata/rdf-cache.json (data/ is git-ignored); --refresh fetches again.
Writes:
  docs/rdf/class/<cid>.ttl|.jsonld|.html   one class each (URI https://nakamura196.github.io/train-bodies/rdf/class/<cid>)
  docs/rdf/model/<model-id>.ttl|.jsonld|.html   one 3D model each (URI .../rdf/model/<model-id>)
  docs/rdf/all.ttl|.jsonld   everything, plus rdfs:label @ja/@en of every Wikidata item used as a value
  docs/rdf/vocab.ttl   the few terms of our own (tb:)
The facet properties are the ones in docs/rdf/facets.json. No ERATV-derived data goes in here (reuse licence unconfirmed).
"""
import html, json, os, sys, time, urllib.parse, urllib.request
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, PROV, RDF, RDFS, SKOS, XSD

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(HERE, "docs", "rdf")
CACHE = os.path.join(HERE, "data", "wikidata", "rdf-cache.json")
BASE = "https://nakamura196.github.io/train-bodies/"
TB = Namespace(BASE + "vocab#")
WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")
SDO = Namespace("https://schema.org/")
CLS = Namespace(BASE + "rdf/class/")
MDL = Namespace(BASE + "rdf/model/")
SCHEME = URIRef(BASE + "rdf/")
UA = "train-bodies/0.1 (nakamura.satoru@mail.u-tokyo.ac.jp)"

FACETS = json.load(open(os.path.join(DOCS, "facets.json"), encoding="utf-8"))["facets"]
WD_FACETS = [f for f in FACETS if f["uri"].startswith(str(WDT))]

# cid: (Wikidata item or None, skos:broader cid in this dataset or None, labels for classes without a Wikidata item)
# Classes without their own Wikidata item get skos:broadMatch to the nearest item (the family).
CLASSES = {
    "Q4940487": ("Q4940487", None, None),                      # Innovia Metro (family incl. ART / SkyTrain Marks)
    "tb-skytrain-mk1": (None, "Q4940487", {"en": "SkyTrain Mark I", "ja": "スカイトレイン Mark I"}),
    "tb-skytrain-mk2": (None, "Q4940487", {"en": "SkyTrain Mark II", "ja": "スカイトレイン Mark II"}),
    "tb-skytrain-mk3": (None, "Q4940487", {"en": "SkyTrain Mark III", "ja": "スカイトレイン Mark III"}),
    "tb-skytrain-mk5": (None, "Q4940487", {"en": "SkyTrain Mark V", "ja": "スカイトレイン Mark V"}),
    "Q696668": ("Q696668", None, None),                         # ICE T
    "Q115612330": ("Q115612330", "Q696668", None),              # DBAG Class 411
    "Q137972762": ("Q137972762", "Q696668", None),              # DBAG Class 415
    "Q8078904": ("Q8078904", "Q696668", None),                  # ÖBB Class 4011
    "Q659660": ("Q659660", None, None),                         # ICE TD (DBAG Class 605)
    "Q140611223": ("Q140611223", None, None),                   # Amtrak Airo
    "Q1087710": ("Q1087710", None, None),                       # AVE Class 102
    "Q137921671": ("Q137921671", None, None),                   # New Flyer XD60 (a bus model, not rolling stock)
}

# Hand-entered values: cid -> {facet id: [values]}, with the source in HAND_SOURCE. Values are Wikidata Q ids or years.
SKYTRAIN = {"country": ["Q16"], "operator": ["Q141170526"]}   # Canada; British Columbia Rapid Transit Company (from SkyTrain Q876780)
HAND = {
    "tb-skytrain-mk1": {**SKYTRAIN, "manufacturer": ["Q3552199"], "serviceEntry": [1985]},   # UTDC; opening of SkyTrain 1985-12-11
    "tb-skytrain-mk2": {**SKYTRAIN, "manufacturer": ["Q688893"], "serviceEntry": [2002]},    # Bombardier Transportation
    "tb-skytrain-mk3": {**SKYTRAIN, "manufacturer": ["Q688893"], "serviceEntry": [2016]},
    "tb-skytrain-mk5": {**SKYTRAIN, "manufacturer": ["Q309084"]},                            # Alstom
}
HAND_SOURCE = {
    "tb-skytrain-mk1": "Country and operator from Wikidata Q876780 (SkyTrain (Vancouver)); manufacturer from English Wikipedia 'SkyTrain (Vancouver)' (rolling stock section, read 2026-10-09); service entry year from the train-bodies gallery text.",
}
for k in ("tb-skytrain-mk2", "tb-skytrain-mk3", "tb-skytrain-mk5"):
    HAND_SOURCE[k] = HAND_SOURCE["tb-skytrain-mk1"]

# Japanese labels for Wikidata classes that have none (hand-entered; Wikidata's own labels win when they exist)
LABEL_JA = {"Q115612330": "ICE T 411形", "Q137972762": "ICE T 415形", "Q8078904": "ÖBB 4011形",
            "Q140611223": "Amtrak Airo", "Q137921671": "New Flyer XD60"}

# Liveries: id -> (labels, operator Q id whose livery it is)
LIVERIES = {
    "translink": ({"en": "TransLink livery", "ja": "TransLink の塗装"}, "Q1142140"),
    "db": ({"en": "Deutsche Bahn livery (red stripe)", "ja": "DB の塗装（赤い帯）"}, "Q9322"),
    "db-green": ({"en": "Deutsche Bahn livery with green stripe (2019–2022)", "ja": "DB の塗装（緑の帯、2019〜2022年）"}, "Q9322"),
    "db-oebb": ({"en": "Deutsche Bahn livery with ÖBB marks", "ja": "DB の塗装に ÖBB の印"}, "Q83822"),
    "dsb": ({"en": "DSB livery", "ja": "DSB の塗装"}, "Q83824"),
    "amtrak-cascades": ({"en": "Amtrak Cascades livery", "ja": "Amtrak Cascades の塗装"}, "Q697217"),
    "renfe-ave": ({"en": "Renfe AVE livery", "ja": "Renfe AVE の塗装"}, "Q2476154"),
}

# model id (gallery) -> (class cid, livery id, part note or None). Titles and sizes come from docs/index.html.
MODELS = {
    "mk1": ("tb-skytrain-mk1", "translink", None),
    "mk2": ("tb-skytrain-mk2", "translink", None),
    "mk3": ("tb-skytrain-mk3", "translink", None),
    "mk5": ("tb-skytrain-mk5", "translink", None),
    "icet_411": ("Q115612330", "db", None),
    "icet_415": ("Q137972762", "db", None),
    "icet_green": ("Q696668", "db-green", None),
    "icet_oebb": ("Q8078904", "db-oebb", None),
    "icet_td": ("Q659660", "db", None),
    "icet_dsb": ("Q659660", "dsb", None),
    "airo": ("Q140611223", "amtrak-cascades", None),
    "ave102": ("Q1087710", "renfe-ave", None),
    "bus49_front": ("Q137921671", "translink", {"en": "front half of the articulated bus", "ja": "連節バスの前半分"}),
    "bus49_rear": ("Q137921671", "translink", {"en": "rear half of the articulated bus", "ja": "連節バスの後ろ半分"}),
}


def sparql(q):
    r = urllib.request.Request("https://query.wikidata.org/sparql",
                               data=urllib.parse.urlencode({"query": q, "format": "json"}).encode(),
                               headers={"Accept": "application/sparql-results+json", "User-Agent": UA})
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(r, timeout=120))["results"]["bindings"]
        except Exception as e:   # WDQS answers 429/504 now and then
            print("retry", e); time.sleep(5 * (i + 1))
    raise SystemExit("Wikidata did not answer")


def qid(u):
    return u.rsplit("/", 1)[-1]


def fetch(refresh):
    if os.path.exists(CACHE) and not refresh:
        return json.load(open(CACHE, encoding="utf-8"))
    items = [w for w, _, _ in CLASSES.values() if w]
    vals = " ".join("wd:" + q for q in items)
    out = {"fetched": time.strftime("%Y-%m-%d"), "classes": {q: {} for q in items}, "labels": {}}
    for f in WD_FACETS:
        p = qid(f["uri"])
        if f["datatype"] == "decimal":   # quantity: normalised to SI (m/s for speed), converted to km/h
            q = f"""SELECT ?i ?v WHERE {{ VALUES ?i {{ {vals} }} ?i p:{p}/psn:{p}/wikibase:quantityAmount ?v }}"""
        elif f["datatype"] == "gYear":
            q = f"""SELECT ?i (YEAR(MIN(?t)) AS ?v) WHERE {{ VALUES ?i {{ {vals} }} ?i wdt:{p} ?t }} GROUP BY ?i"""
        else:
            q = f"""SELECT ?i ?v WHERE {{ VALUES ?i {{ {vals} }} ?i wdt:{p} ?v FILTER(isIRI(?v)) }}"""
        for b in sparql(q):
            v = b["v"]["value"]
            if f["datatype"] == "decimal":
                v = round(float(v) * 3.6) if f.get("unit") == "km/h" else float(v)
            elif f["datatype"] == "gYear":
                v = int(v)
            else:
                v = qid(v)
            lst = out["classes"][qid(b["i"]["value"])].setdefault(f["id"], [])
            if v not in lst:
                lst.append(v)
        time.sleep(1)
    lab = f"""SELECT ?i ?l WHERE {{ VALUES ?i {{ {vals} }} ?i rdfs:label ?l FILTER(lang(?l) IN ("ja","en")) }}"""
    for b in sparql(lab):
        out["classes"][qid(b["i"]["value"])].setdefault("label", {})[b["l"]["xml:lang"]] = b["l"]["value"]
    # labels of every item used as a value (Wikidata values and hand-entered ones)
    used = set()
    for c in out["classes"].values():
        for f in WD_FACETS:
            if f["datatype"] == "iri":
                used.update(c.get(f["id"], []))
    for h in HAND.values():
        for k, vs in h.items():
            used.update(v for v in vs if isinstance(v, str))
    used.update(op for _, op in LIVERIES.values())
    used = sorted(used)
    for i in range(0, len(used), 200):
        vals2 = " ".join("wd:" + q for q in used[i:i + 200])
        for b in sparql(f"""SELECT ?i ?l WHERE {{ VALUES ?i {{ {vals2} }} ?i rdfs:label ?l FILTER(lang(?l) IN ("ja","en")) }}"""):
            out["labels"].setdefault(qid(b["i"]["value"]), {})[b["l"]["xml:lang"]] = b["l"]["value"]
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(out, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out


def gallery_items():
    s = open(os.path.join(HERE, "docs", "index.html"), encoding="utf-8").read()
    line = next(l for l in s.splitlines() if l.startswith("const DATA = "))
    return {i["id"]: i for i in json.loads(line[len("const DATA = "):].rstrip(";"))["items"]}


def new_graph():
    g = Graph()
    for p, ns in (("tb", TB), ("wd", WD), ("wdt", WDT), ("schema", SDO), ("skos", SKOS), ("dcterms", DCTERMS),
                  ("prov", PROV), ("owl", OWL), ("cls", CLS), ("mdl", MDL)):
        g.bind(p, ns)
    return g


def value_node(f, v):
    if f["datatype"] == "iri":
        return WD[v]
    if f["datatype"] == "decimal":
        return Literal(str(v), datatype=XSD.decimal)
    if f["datatype"] == "gYear":
        return Literal(f"{v:04d}", datatype=XSD.gYear)
    return Literal(v)


def add_class(g, cid, wd, models):
    wq, broader, labels = CLASSES[cid]
    s = CLS[cid]
    g.add((s, RDF.type, TB.VehicleClass)); g.add((s, RDF.type, SKOS.Concept)); g.add((s, SKOS.inScheme, SCHEME))
    labels = labels or dict(wd["classes"][wq].get("label", {}))
    if "ja" not in labels and cid in LABEL_JA:
        labels["ja"] = LABEL_JA[cid]
    for lang, l in labels.items():
        g.add((s, SKOS.prefLabel, Literal(l, lang=lang))); g.add((s, RDFS.label, Literal(l, lang=lang)))
    if wq:
        g.add((s, SKOS.exactMatch, WD[wq])); g.add((s, PROV.wasDerivedFrom, WD[wq]))
    if broader:
        g.add((s, SKOS.broader, CLS[broader]))
        if not wq:
            g.add((s, SKOS.broadMatch, WD[CLASSES[broader][0]]))
    vals = dict(wd["classes"].get(wq, {})) if wq else {}
    for k, vs in HAND.get(cid, {}).items():
        vals[k] = vs
        g.add((s, TB.handEntered, URIRef(next(f["uri"] for f in FACETS if f["id"] == k))))
    if cid in HAND_SOURCE:
        g.add((s, DCTERMS.source, Literal(HAND_SOURCE[cid], lang="en")))
    for f in WD_FACETS:
        for v in vals.get(f["id"], []):
            g.add((s, URIRef(f["uri"]), value_node(f, v)))
    g.add((s, TB.has3DModel, Literal(bool(models))))
    for m in models:
        g.add((s, SDO.subjectOf, MDL[m]))


def add_model(g, mid, item):
    cid, lid, part = MODELS[mid]
    s = MDL[mid]
    g.add((s, RDF.type, SDO["3DModel"]))
    g.add((s, SDO.name, Literal(item["title"], lang="ja")))
    g.add((s, SDO.description, Literal(item["line"], lang="ja")))
    g.add((s, SDO.about, CLS[cid]))
    g.add((s, SDO.contentUrl, URIRef(f"{BASE}models/{mid}.glb")))
    g.add((s, SDO.encodingFormat, Literal("model/gltf-binary")))
    g.add((s, SDO.thumbnailUrl, URIRef(f"{BASE}thumbs/{mid}.jpg")))
    g.add((s, SDO.subjectOf, URIRef(f"{BASE}iiif/{mid}/manifest.json")))   # IIIF Manifest (担当 B)
    g.add((s, SDO.url, URIRef(f"{BASE}#{mid}")))
    for prop, v in zip((SDO.depth, SDO.width, SDO.height), item["size"]):   # x = length, y = width, z = height, in mm
        q = BNode(f"{mid}-{prop.rsplit('/', 1)[-1]}")
        g.add((s, prop, q)); g.add((q, RDF.type, SDO.QuantitativeValue))
        g.add((q, SDO.value, Literal(str(v), datatype=XSD.decimal))); g.add((q, SDO.unitCode, Literal("MMT")))
    lv = URIRef(f"{MDL[mid]}#livery")
    g.add((s, TB.livery, lv)); g.add((lv, RDF.type, TB.Livery))
    labels, op = LIVERIES[lid]
    for lang, l in labels.items():
        g.add((lv, RDFS.label, Literal(l, lang=lang)))
    g.add((lv, TB.liveryOf, WD[op]))
    if part:
        for lang, l in part.items():
            g.add((s, TB.part, Literal(l, lang=lang)))
    g.add((s, TB.galleryGroup, Literal(item["group"])))


CONTEXT = {
    "@vocab": str(TB), "tb": str(TB), "wd": str(WD), "wdt": str(WDT), "schema": str(SDO), "skos": str(SKOS),
    "dcterms": str(DCTERMS), "prov": str(PROV), "rdfs": str(RDFS), "xsd": str(XSD),
}


def write(g, path, title, uri):
    g.serialize(path + ".ttl", format="turtle")
    g.serialize(path + ".jsonld", format="json-ld", context=CONTEXT, indent=1, auto_compact=True)
    name = os.path.basename(path)
    open(path + ".html", "w", encoding="utf-8").write(f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="alternate" type="text/turtle" href="{name}.ttl">
<link rel="alternate" type="application/ld+json" href="{name}.jsonld">
</head><body><h1>{html.escape(title)}</h1>
<p><code>{html.escape(uri)}</code></p>
<p><a href="{name}.ttl">Turtle</a> · <a href="{name}.jsonld">JSON-LD</a> · <a href="{BASE}">train-bodies</a></p>
<pre>{html.escape(open(path + ".ttl", encoding="utf-8").read())}</pre>
</body></html>
""")


def vocab():
    g = new_graph()
    terms = [
        (TB.VehicleClass, RDFS.Class, "Vehicle class", "形式", "A class (type) of railway vehicle or road vehicle; one record per class."),
        (TB.Livery, RDFS.Class, "Livery", "塗装", "A paint scheme that a 3D model reproduces."),
        (TB.has3DModel, RDF.Property, "has 3D model", "3D モデルあり", "True when at least one 3D model in train-bodies depicts this class."),
        (TB.handEntered, RDF.Property, "hand-entered property", "手入力の項目", "A property whose values on this class were entered by hand (see dcterms:source), not copied from Wikidata."),
        (TB.livery, RDF.Property, "livery", "塗装", "The livery a 3D model reproduces."),
        (TB.liveryOf, RDF.Property, "livery of", "塗装の持ち主", "The operator whose livery this is."),
        (TB.part, RDF.Property, "part", "部分", "Which part of the vehicle the model is, when one vehicle is split into several models."),
        (TB.galleryGroup, RDF.Property, "gallery group", "ギャラリーの区分", "Group id used on the gallery page."),
    ]
    for t, typ, en, ja, c in terms:
        g.add((t, RDF.type, typ)); g.add((t, RDFS.label, Literal(en, lang="en"))); g.add((t, RDFS.label, Literal(ja, lang="ja")))
        g.add((t, RDFS.comment, Literal(c, lang="en"))); g.add((t, RDFS.isDefinedBy, URIRef(BASE + "vocab")))
    g.add((SCHEME, RDF.type, SKOS.ConceptScheme))
    g.add((SCHEME, RDFS.label, Literal("train-bodies: vehicle classes", lang="en")))
    g.add((SCHEME, RDFS.label, Literal("train-bodies: 車両の形式", lang="ja")))
    return g


def main():
    wd = fetch("--refresh" in sys.argv)
    items = gallery_items()
    by_class = {}
    for mid, (cid, _, _) in MODELS.items():
        if mid in items:
            by_class.setdefault(cid, []).append(mid)
    for sub in ("class", "model"):
        d = os.path.join(DOCS, sub); os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
    allg = new_graph()
    allg += vocab()
    for cid in CLASSES:
        g = new_graph(); add_class(g, cid, wd, by_class.get(cid, []))
        title = str(g.value(CLS[cid], SKOS.prefLabel) or cid)
        for l in g.objects(CLS[cid], SKOS.prefLabel):
            if l.language == "ja":
                title = str(l)
        write(g, os.path.join(DOCS, "class", cid), title, str(CLS[cid])); allg += g
    for mid in MODELS:
        if mid not in items:
            print("skip (not in gallery):", mid); continue
        g = new_graph(); add_model(g, mid, items[mid])
        write(g, os.path.join(DOCS, "model", mid), items[mid]["title"], str(MDL[mid])); allg += g
    for q, ls in wd["labels"].items():
        for lang, l in ls.items():
            allg.add((WD[q], RDFS.label, Literal(l, lang=lang)))
    vocab().serialize(os.path.join(DOCS, "vocab.ttl"), format="turtle")
    allg.serialize(os.path.join(DOCS, "all.ttl"), format="turtle")
    allg.serialize(os.path.join(DOCS, "all.jsonld"), format="json-ld", context=CONTEXT, indent=1, auto_compact=True)
    print(f"{len(CLASSES)} classes, {len(by_class and [m for ms in by_class.values() for m in ms])} models, {len(allg)} triples -> {DOCS}"
          f" (Wikidata fetched {wd['fetched']})")


if __name__ == "__main__":
    main()
