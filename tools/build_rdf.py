"""Build the RDF of the classes (形式) and the 3D models into docs/rdf/.

Usage: python3 tools/build_rdf.py [--refresh]
  Values come from Wikidata (CC0) for the classes listed in CLASSES, plus the hand-entered values in HAND.
  Wikidata answers are cached in data/wikidata/rdf-cache.json (data/ is git-ignored); --refresh fetches again.
  Every other class of the search (data/classes.tsv, source=wikidata rows only) gets a file too, with its values from
  the facet tables data/wikidata/facets/<id>.tsv (tools/fetch_facets.py) and the labels from data/classes.tsv and
  data/wikidata/class-labels-ja.tsv, so every class URI resolves (decided 2026-10-10).
Writes:
  docs/rdf/class/<cid>.ttl|.jsonld        one class each (URI https://nakamura196.github.io/train-bodies/rdf/class/<cid>)
  docs/rdf/model/<model-id>.ttl|.jsonld        one 3D model each (URI .../rdf/model/<model-id>)
  docs/rdf/all.ttl|.jsonld   everything, plus rdfs:label @ja/@en of every Wikidata item used as a value
  docs/rdf/vocab.ttl   the few terms of our own (tb:)
The facet properties are the ones in docs/rdf/facets.json. Livery colours come from tools/livery_colors.json
(made by tools/extract_colors.py from the skytrain builds). No ERATV-derived data goes in here (only the mapping table is published, by tools/build_eratv_map.py).
Class photos: foaf:depiction to the Commons file of Wikidata P18 (data/wikidata/facets/_image.tsv, tools/fetch_facets.py;
one photo per class), with the same IRI as Wikidata's wdt:P18 (Special:FilePath) so the two join. Each photo keeps its own
Commons licence; the credit lines are on the site (decided 2026-10-11).
Terms (decided 2026-10-10): the data CC0 (dcterms:license on the scheme), the 3D models CC BY 4.0 (schema:license on each).
"""
import csv, json, os, sys, time, urllib.parse, urllib.request
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, FOAF, OWL, PROV, RDF, RDFS, SKOS, XSD

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
CC0 = URIRef("https://creativecommons.org/publicdomain/zero/1.0/")
CC_BY = URIRef("https://creativecommons.org/licenses/by/4.0/")
UA = "railclass/0.1 (nakamura.satoru@mail.u-tokyo.ac.jp)"

FACETS = json.load(open(os.path.join(DOCS, "facets.json"), encoding="utf-8"))["facets"]
WD_FACETS = [f for f in FACETS if f["uri"].startswith(str(WDT)) and f.get("on", "class") == "class"]
COLOR_URI = URIRef(next(f["uri"] for f in FACETS if f["id"] == "color"))
COLORS = json.load(open(os.path.join(HERE, "tools", "livery_colors.json"), encoding="utf-8"))
# class -> line (Wikidata items), hand-filled with sources (docs/notes/todo.md, 路線). Only the IDs come into the RDF:
# the line shapes are OSM data (ODbL) and stay in docs/lines, outside the dataset.
# Then the Wikidata P3438 rows (tools/class_lines_wd.tsv); the hand table wins on the same (class, line).
LINES, _seen = [], set()
for _f in ("class_lines.tsv", "class_lines_wd.tsv"):
    _p = os.path.join(HERE, "tools", _f)
    if not os.path.exists(_p): continue
    for r in csv.DictReader(open(_p, encoding="utf-8"), delimiter="\t"):
        if r["line"] and (r["class"], r["line"]) not in _seen:
            _seen.add((r["class"], r["line"])); LINES.append(r)

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
    "Q671805": ("Q671805", None, None),                         # Rhaetian Railway ABe 8/12 (Allegra)
    "Q370895": ("Q370895", None, None),                         # FS ETR 400 (Frecciarossa 1000)
    "Q289090": ("Q289090", None, None),                         # Transrapid 08 (Shanghai Maglev vehicles)
    "Q119775864": ("Q119775864", None, None),                   # Vande Bharat
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
            "Q140611223": "Amtrak Airo", "Q137921671": "New Flyer XD60",
            "Q289090": "トランスラピッド 08"}

# Liveries: id -> (labels, operator Q id whose livery it is)
LIVERIES = {
    "translink": ({"en": "TransLink livery", "ja": "TransLink の塗装"}, "Q1142140"),
    "db": ({"en": "Deutsche Bahn livery (red stripe)", "ja": "DB の塗装（赤い帯）"}, "Q9322"),
    "db-green": ({"en": "Deutsche Bahn livery with green stripe (2019–2022)", "ja": "DB の塗装（緑の帯、2019〜2022年）"}, "Q9322"),
    "db-oebb": ({"en": "Deutsche Bahn livery with ÖBB marks", "ja": "DB の塗装に ÖBB の印"}, "Q83822"),
    "dsb": ({"en": "DSB livery", "ja": "DSB の塗装"}, "Q83824"),
    "amtrak-cascades": ({"en": "Amtrak Cascades livery", "ja": "Amtrak Cascades の塗装"}, "Q697217"),
    "renfe-ave": ({"en": "Renfe AVE livery", "ja": "Renfe AVE の塗装"}, "Q2476154"),
    "rhb": ({"en": "Rhaetian Railway livery", "ja": "レーティッシュ鉄道の塗装"}, "Q177598"),
    "trenitalia-fr": ({"en": "Trenitalia Frecciarossa livery (red to the bottom, from 2022)", "ja": "Trenitalia フレッチャロッサの塗装（下まで赤、2022年から）"}, "Q286650"),
    # Wikidata has no item for the operating company, so the livery points to the line (Shanghai maglev train)
    "shanghai-maglev": ({"en": "Shanghai Maglev livery", "ja": "上海リニアの塗装"}, "Q769591"),
    "ir-vande-bharat": ({"en": "Vande Bharat livery (saffron and grey, from 2023)", "ja": "ヴァンデ・バーラトの塗装（サフランと灰、2023年から）"}, "Q819425"),
}

# model id (gallery) -> (class cid, livery id, part note or None). Titles and sizes come from docs/data/models.json.
MODELS = {
    "mk1": ("tb-skytrain-mk1", "translink", None),
    "mk2": ("tb-skytrain-mk2", "translink", None),
    "mk3": ("tb-skytrain-mk3", "translink", None),
    "mk5": ("tb-skytrain-mk5", "translink", None),
    "icet_411": ("Q115612330", "db", None),
    "icet_415": ("Q137972762", "db", None),
    "icet_green": ("Q115612330", "db-green", None),    # car 411 525 (skytrain models/icet_green.py)
    "icet_oebb": ("Q8078904", "db-oebb", None),
    "icet_td": ("Q659660", "db", None),
    "icet_dsb": ("Q659660", "dsb", None),
    "airo": ("Q140611223", "amtrak-cascades", None),
    "ave102": ("Q1087710", "renfe-ave", None),
    "bus49_front": ("Q137921671", "translink", {"en": "front half of the articulated bus", "ja": "連節バスの前半分"}),
    "bus49_rear": ("Q137921671", "translink", {"en": "rear half of the articulated bus", "ja": "連節バスの後ろ半分"}),
    "allegra": ("Q671805", "rhb", None),
    "frecciarossa": ("Q370895", "trenitalia-fr", None),
    "maglev": ("Q289090", "shanghai-maglev", None),
    "vandebharat": ("Q119775864", "ir-vande-bharat", None),
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


def add_labels(wd, qs):
    """Fetch Wikidata labels for items not in the cache yet (e.g. colours added after the last --refresh)."""
    missing = sorted(q for q in qs if q not in wd["labels"])
    if not missing:
        return
    vals = " ".join("wd:" + q for q in missing)
    for b in sparql(f"""SELECT ?i ?l WHERE {{ VALUES ?i {{ {vals} }} ?i rdfs:label ?l FILTER(lang(?l) IN ("ja","en")) }}"""):
        wd["labels"].setdefault(qid(b["i"]["value"]), {})[b["l"]["xml:lang"]] = b["l"]["value"]
    json.dump(wd, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def read_tsv(name):
    p = os.path.join(HERE, "data", name)
    return list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t")) if os.path.exists(p) else []


def tsv_classes(wd):
    """The classes of data/classes.tsv not in CLASSES: cid -> {"label": {lang: text}, <facet id>: [values]}.
    The labels of the values (in the facet tables) go into wd["labels"] for all.ttl, without touching the cache."""
    out = {}
    for r in read_tsv("classes.tsv"):
        if r["source"] == "wikidata" and r["wikidata"] and r["wikidata"] not in CLASSES:
            out[r["wikidata"]] = {"label": {"en": r["label"]} if r["label"] else {}}
    for r in read_tsv("wikidata/class-labels-ja.tsv"):
        if r["item"] in out and r["label_ja"]:
            out[r["item"]]["label"]["ja"] = r["label_ja"]
    for f in WD_FACETS:
        for r in read_tsv(f"wikidata/facets/{f['id']}.tsv"):
            c = out.get(r["item"])
            if c is None or not r["value"]:
                continue
            v = r["value"]
            if f["datatype"] == "decimal":
                v = float(v); v = int(v) if v.is_integer() else v
            elif f["datatype"] == "gYear":
                v = int(v)
            lst = c.setdefault(f["id"], [])
            if v not in lst:
                lst.append(v)
            if f["datatype"] == "iri" and v not in wd["labels"]:
                ls = {k: r[f"label_{k}"] for k in ("ja", "en") if r.get(f"label_{k}")}
                if ls:
                    wd["labels"][v] = ls
    return out


def add_tsv_class(g, cid, rec):
    s = CLS[cid]
    g.add((s, RDF.type, TB.VehicleClass)); g.add((s, RDF.type, SKOS.Concept)); g.add((s, SKOS.inScheme, SCHEME))
    for lang, l in rec["label"].items():
        g.add((s, SKOS.prefLabel, Literal(l, lang=lang))); g.add((s, RDFS.label, Literal(l, lang=lang)))
    g.add((s, SKOS.exactMatch, WD[cid])); g.add((s, PROV.wasDerivedFrom, WD[cid]))
    for f in WD_FACETS:
        for v in rec.get(f["id"], []):
            g.add((s, URIRef(f["uri"]), value_node(f, v)))
    add_depiction(g, s, cid)
    for k, r in enumerate((r for r in LINES if r["class"] == cid), 1):
        add_line(g, s, k, r)
    g.add((s, TB.has3DModel, Literal(False)))


IMAGES = {}   # Wikidata item -> Commons file IRI (P18), filled in main()


def add_depiction(g, s, q):
    if q in IMAGES:
        g.add((s, FOAF.depiction, URIRef(IMAGES[q])))


def gallery_items():
    d = json.load(open(os.path.join(HERE, "docs", "data", "models.json"), encoding="utf-8"))   # written by skytrain/tools/gallery.py
    return {i["id"]: i for i in d["items"]}


def new_graph():
    g = Graph()
    for p, ns in (("tb", TB), ("wd", WD), ("wdt", WDT), ("schema", SDO), ("skos", SKOS), ("dcterms", DCTERMS),
                  ("prov", PROV), ("foaf", FOAF), ("owl", OWL), ("cls", CLS), ("mdl", MDL)):
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
    if wq:
        add_depiction(g, s, wq)
    for k, r in enumerate((r for r in LINES if r["class"] == cid), 1):
        add_line(g, s, k, r)
    g.add((s, TB.has3DModel, Literal(bool(models))))
    for m in models:
        g.add((s, SDO.subjectOf, MDL[m]))


def add_line(g, s, k, r):
    """cls:<cid> tb:usedOn wd:<line> (the plain link, for simple queries), and a tb:LineUse node that carries how we know:
    current or historical (with the year it ended when known), the source and its section, and whether the line was
    inferred from a service (e.g. "München–Berlin") rather than named in the source."""
    line = WD[r["line"]]
    g.add((s, TB.usedOn, line))
    if r["lineLabel"]:
        g.add((line, RDFS.label, Literal(r["lineLabel"], lang="en")))
    u = URIRef(f"{s}#line{k}")
    g.add((s, TB.lineUse, u)); g.add((u, RDF.type, TB.LineUse)); g.add((u, TB.line, line))
    status, _, until = r["status"].partition(" ")
    g.add((u, TB.useStatus, Literal(status)))
    if until.isdigit():
        g.add((u, TB.usedUntil, Literal(until, datatype=XSD.gYear)))
    if r["source_url"]:
        g.add((u, DCTERMS.source, URIRef(r["source_url"])))
    if r["source_section"]:
        g.add((u, TB.sourceSection, Literal(r["source_section"])))
    if "INFERRED" in r["note"]:
        g.add((u, TB.inferred, Literal(True)))
    if r["note"]:
        g.add((u, SKOS.note, Literal(r["note"], lang="en")))


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
    g.add((s, SDO.url, URIRef(f"{BASE}view.html#{mid}")))
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
    c = COLORS["models"].get(mid)
    if c:
        for name in c["colors"]:
            g.add((lv, COLOR_URI, WD[COLORS["basic"][name]]))
        for k, smp in enumerate(c["samples"], 1):
            n = URIRef(f"{MDL[mid]}#color{k}")
            g.add((lv, TB.colorSample, n)); g.add((n, RDF.type, TB.ColorSample))
            g.add((n, RDFS.label, Literal(smp["name"]))); g.add((n, SDO.color, Literal(smp["hex"])))
            g.add((n, TB.areaShare, Literal(f"{smp['share']:.4f}", datatype=XSD.decimal)))
            g.add((n, COLOR_URI, WD[COLORS["basic"][smp["basic"]]]))
        g.add((lv, DCTERMS.source, Literal(f"Colours taken automatically from the face materials of {c['source']} "
                                          f"(area share of the painted surface, kept when >= {COLORS['minShare']:.1%}, white/grey/black when >= {COLORS['minShareNeutral']:.0%}; "
                                          f"the colour samples keep them all; tools/extract_colors.py)", lang="en")))
    if part:
        for lang, l in part.items():
            g.add((s, TB.part, Literal(l, lang=lang)))
    g.add((s, TB.galleryGroup, Literal(item["group"])))
    g.add((s, SDO.license, CC_BY))


CONTEXT = {
    "@vocab": str(TB), "tb": str(TB), "wd": str(WD), "wdt": str(WDT), "schema": str(SDO), "skos": str(SKOS),
    "dcterms": str(DCTERMS), "prov": str(PROV), "foaf": str(FOAF), "rdfs": str(RDFS), "xsd": str(XSD),
}


def write(g, path, title, uri):
    """Turtle and JSON-LD. The human page for the URI (<path>.html) is made by the site (web/, Astro), not here."""
    g.serialize(path + ".ttl", format="turtle")
    g.serialize(path + ".jsonld", format="json-ld", context=CONTEXT, indent=1, auto_compact=True)


def vocab():
    g = new_graph()
    terms = [
        (TB.VehicleClass, RDFS.Class, "Vehicle class", "形式", "A class (type) of railway vehicle or road vehicle; one record per class."),
        (TB.Livery, RDFS.Class, "Livery", "塗装", "A paint scheme that a 3D model reproduces."),
        (TB.has3DModel, RDF.Property, "has 3D model", "3D モデルあり", "True when at least one 3D model in train-bodies depicts this class."),
        (TB.handEntered, RDF.Property, "hand-entered property", "手入力の項目", "A property whose values on this class were entered by hand (see dcterms:source), not copied from Wikidata."),
        (TB.livery, RDF.Property, "livery", "塗装", "The livery a 3D model reproduces."),
        (TB.liveryOf, RDF.Property, "livery of", "塗装の持ち主", "The operator whose livery this is."),
        (TB.ColorSample, RDFS.Class, "Colour sample", "色見本", "One colour of a livery as painted on the 3D model, with its share of the painted surface."),
        (TB.colorSample, RDF.Property, "colour sample", "色見本", "A colour of this livery, taken from the 3D model's faces."),
        (TB.areaShare, RDF.Property, "area share", "面積の割合", "Share (0-1) of the painted surface of the 3D model that has this colour (glass, lamps, seams left out)."),
        (TB.part, RDF.Property, "part", "部分", "Which part of the vehicle the model is, when one vehicle is split into several models."),
        (TB.usedOn, RDF.Property, "used on line", "走る路線", "A line (a Wikidata item) this class runs or ran on: the inverse direction of Wikidata P3438 (vehicle normally used), from the hand-filled table with sources, and from Wikidata P3438 statements (the source is the statement). See tb:lineUse for the status and the source."),
        (TB.lineUse, RDF.Property, "line use", "路線での運用", "How this class is (was) used on one line, with the source: a tb:LineUse."),
        (TB.LineUse, RDFS.Class, "Line use", "路線での運用", "One class on one line: tb:line, tb:useStatus, tb:usedUntil, dcterms:source."),
        (TB.line, RDF.Property, "line", "路線", "The line (a Wikidata item)."),
        (TB.useStatus, RDF.Property, "status", "運用の状態", "\"current\", \"historical\" or \"unknown\"."),
        (TB.usedUntil, RDF.Property, "used until", "運用の終わり", "The year the class stopped running on the line, when known (the last year the source mentions it, if no end is stated)."),
        (TB.sourceSection, RDF.Property, "source section", "出典の節", "The section of the source (dcterms:source) that names the line."),
        (TB.inferred, RDF.Property, "inferred", "推定", "True when the source names a service (e.g. a city pair) and the line was inferred from it."),
        (TB.galleryGroup, RDF.Property, "gallery group", "ギャラリーの区分", "Group id used on the gallery page."),
    ]
    for t, typ, en, ja, c in terms:
        g.add((t, RDF.type, typ)); g.add((t, RDFS.label, Literal(en, lang="en"))); g.add((t, RDFS.label, Literal(ja, lang="ja")))
        g.add((t, RDFS.comment, Literal(c, lang="en"))); g.add((t, RDFS.isDefinedBy, URIRef(BASE + "vocab")))
    g.add((SCHEME, RDF.type, SKOS.ConceptScheme))
    g.add((SCHEME, DCTERMS.license, CC0))
    g.add((SCHEME, RDFS.label, Literal("train-bodies: vehicle classes", lang="en")))
    g.add((SCHEME, RDFS.label, Literal("train-bodies: 車両の形式", lang="ja")))
    return g


def main():
    wd = fetch("--refresh" in sys.argv)
    add_labels(wd, COLORS["basic"].values())
    IMAGES.update((r["item"], r["image"]) for r in read_tsv("wikidata/facets/_image.tsv") if r["image"])
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
    more = tsv_classes(wd)
    for cid, rec in more.items():
        g = new_graph(); add_tsv_class(g, cid, rec)
        write(g, os.path.join(DOCS, "class", cid), rec["label"].get("ja") or rec["label"].get("en") or cid, str(CLS[cid])); allg += g
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
    print(f"{len(CLASSES)} + {len(more)} classes, {len(by_class and [m for ms in by_class.values() for m in ms])} models, {len(allg)} triples -> {DOCS}"
          f" (Wikidata fetched {wd['fetched']})")


if __name__ == "__main__":
    main()
