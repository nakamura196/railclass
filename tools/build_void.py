"""Describe the dataset in one place: docs/rdf/void.ttl|.jsonld (VoID + DCAT) and docs/data/dataset.json (the same counts
for the dataset page of the site, web/src/components/DatasetPage.astro).

Usage: python3 tools/build_void.py        (after tools/build_rdf.py, build_eratv_map.py and osm_lines.py)
  Every number is counted from the published files, not written by hand: docs/rdf/all.ttl (triples, entities, classes,
  properties, links to Wikidata and Commons), docs/data/eratv-wikidata.tsv, docs/lines/*.geojson, docs/iiif/collection.json.
  The description says there is no SPARQL endpoint (GitHub Pages serves files only) and where the dumps are.
Terms are the ones decided 2026-10-10 (data CC0, 3D models CC BY 4.0; models changed to individual permission 2026-10-14); the files outside the RDF keep their own terms
(line shapes ODbL from OpenStreetMap, ERATV type IDs and names reproduced with acknowledgement, photos per Commons file).
"""
import csv, datetime, json, os, sys
from collections import Counter
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, RDFS, SKOS, XSD

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_rdf import BASE, SITE, CC0, CLS, DOCS as RDF_DIR, MDL, SCHEME, SDO, TB, WD, WDT
CC_BY = URIRef("https://creativecommons.org/licenses/by/4.0/")   # the IIIF Collection and the model list (descriptions, not the 3D files)

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(HERE, "docs")
VOID = Namespace("http://rdfs.org/ns/void#")
ODBL = URIRef("https://opendatacommons.org/licenses/odbl/1-0/")
DS = URIRef(BASE + "dataset")   # w3id has no rule for dataset yet (ids/railclass/.htaccess); the file is rdf/void.ttl
COMMONS = "http://commons.wikimedia.org/wiki/Special:FilePath/"


def size(rel):
    return os.path.getsize(os.path.join(DOCS, rel))


def count():
    g = Graph(); g.parse(os.path.join(RDF_DIR, "all.ttl"))
    types = Counter(g.objects(None, RDF.type))
    preds = Counter(g.predicates())
    n = {
        "triples": len(g),
        "entities": len({s for s in g.subjects() if isinstance(s, URIRef) and str(s).startswith(BASE)}),
        "properties": len(preds),
        "vocabularies": sorted({str(p).rsplit("#", 1)[0] + "#" if "#" in str(p) else str(p).rsplit("/", 1)[0] + "/" for p in preds}),
        "classes": types[TB.VehicleClass],
        "models": types[SDO["3DModel"]],
        "liveries": types[TB.Livery],
        "lineUses": types[TB.LineUse],
        "withPhoto": len(set(g.subjects(FOAF.depiction, None))),
        "withLines": len(set(g.subjects(TB.usedOn, None))),
        "lines": len(set(g.objects(None, TB.usedOn))),
        "withModel": len(set(g.subjects(TB.has3DModel, Literal(True)))),
        "exactMatch": sum(1 for _, _, o in g.triples((None, SKOS.exactMatch, None)) if str(o).startswith(str(WD))),
        "depiction": sum(1 for _, _, o in g.triples((None, FOAF.depiction, None)) if str(o).startswith(COMMONS)),
        "wikidataValues": sum(c for p, c in preds.items() if str(p).startswith(str(WDT))),
    }
    n["topProperties"] = [[str(p), c] for p, c in preds.most_common()]
    n["typeCounts"] = [[str(t), c] for t, c in types.most_common()]
    with open(os.path.join(DOCS, "data", "eratv-wikidata.tsv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    n["eratvRows"] = len(rows)   # a type matched to several candidate classes has one row per candidate
    n["eratvTypes"] = len({r["eratv_type"] for r in rows if r["wikidata"]})
    n["eratvClasses"] = len({r["wikidata"] for r in rows if r["wikidata"]})
    shapes = {f[:-8] for f in os.listdir(os.path.join(DOCS, "lines")) if f.startswith("Q") and f.endswith(".geojson")}
    n["lineShapes"] = len(shapes)
    n["withLineShape"] = len({s for s, o in g.subject_objects(TB.usedOn) if str(o).removeprefix(str(WD)) in shapes})   # on the map
    n["iiifManifests"] = len(json.load(open(os.path.join(DOCS, "iiif", "collection.json"), encoding="utf-8"))["items"])
    return n


# The files, in the order the page lists them: key, path under docs/, media type, licence, title en / ja
FILES = [
    ("allTtl", "rdf/all.ttl", "text/turtle", CC0, "All classes and models (Turtle)", "全形式と 3D モデル（Turtle）"),
    ("allJsonld", "rdf/all.jsonld", "application/ld+json", CC0, "All classes and models (JSON-LD)", "全形式と 3D モデル（JSON-LD）"),
    ("vocab", "rdf/vocab.ttl", "text/turtle", CC0, "Terms of our own (tb:)", "独自の語彙（tb:）"),
    ("eratv", "data/eratv-wikidata.tsv", "text/tab-separated-values", None, "ERATV types matched to Wikidata classes (TSV + CSVW)", "ERATV の型式と Wikidata の形式の対応表（TSV と CSVW）"),
    ("lines", "lines/_all.geojson", "application/geo+json", ODBL, "Line shapes from OpenStreetMap (GeoJSON, one file per line)", "路線の線（OpenStreetMap、GeoJSON、路線ごとのファイル）"),
    ("iiif", "iiif/collection.json", "application/ld+json", CC_BY, "IIIF Presentation 4.0 Collection of the 3D models", "3D モデルの IIIF Collection（Presentation 4.0）"),
    ("models", "data/models.json", "application/json", CC_BY, "List of the 3D models (JSON)", "3D モデルの一覧（JSON）"),
]


def build(n, modified):
    g = Graph()
    for p, ns in (("void", VOID), ("dcat", DCAT), ("dcterms", DCTERMS), ("foaf", FOAF), ("skos", SKOS), ("schema", SDO),
                  ("tb", TB), ("cls", CLS), ("mdl", MDL), ("wd", WD)):
        g.bind(p, ns)
    g.add((DS, RDF.type, VOID.Dataset)); g.add((DS, RDF.type, DCAT.Dataset))
    g.add((DS, DCTERMS.title, Literal("RailClass: railway vehicle classes of the world", lang="en")))
    g.add((DS, DCTERMS.title, Literal("RailClass: 世界の鉄道車両の形式", lang="ja")))
    g.add((DS, DCTERMS.description, Literal(
        f"{n['classes']:,} railway vehicle classes outside Japan, taken from Wikidata and linked to it (skos:exactMatch), "
        f"with operator, manufacturer and other values as Wikidata IRIs, photos for {n['withPhoto']:,} classes (Wikimedia Commons), "
        f"the lines {n['withLines']:,} classes run on, and {n['models']} 3D-printed vehicle bodies with their liveries. "
        "No SPARQL endpoint: every resource is a static file (Turtle and JSON-LD), and the whole dataset is in one dump file.", lang="en")))
    g.add((DS, DCTERMS.description, Literal(
        f"日本を除く世界の鉄道車両の形式 {n['classes']:,} 件。Wikidata から取り出し、skos:exactMatch で結んでいる。"
        f"運行者・製造者などの値は Wikidata の IRI のまま持つ。写真 {n['withPhoto']:,} 形式（Wikimedia Commons）、"
        f"走る路線 {n['withLines']:,} 形式、3D プリントで作った車体 {n['models']} 件とその塗装を含む。"
        "SPARQL エンドポイントは無い。資源はすべて静的なファイル（Turtle と JSON-LD）で、全体は一括ファイル 1 つにまとめてある。", lang="ja")))
    g.add((DS, DCTERMS.license, CC0))
    g.add((DS, DCTERMS.rights, Literal(
        "Class data CC0. 3D models (schema:3DModel and their files): individual permission required (In Copyright), stated on each model with schema:license; the files are behind a login. "
        "Photos: the licence of each Wikimedia Commons file.", lang="en")))
    me = BNode(); g.add((DS, DCTERMS.creator, me)); g.add((DS, DCTERMS.publisher, me))
    g.add((me, RDF.type, FOAF.Person)); g.add((me, FOAF.name, Literal("中村 覚", lang="ja"))); g.add((me, FOAF.name, Literal("Satoru Nakamura", lang="en")))
    g.add((DS, DCTERMS.modified, Literal(modified, datatype=XSD.date)))
    g.add((DS, DCTERMS.source, WD.Q2013))   # Wikidata
    g.add((DS, FOAF.homepage, URIRef(SITE)))
    g.add((DS, DCAT.landingPage, URIRef(SITE + "dataset.html")))
    g.add((DS, DCTERMS.isReferencedBy, URIRef("https://github.com/nakamura196/railclass")))
    for kw in ("railway", "rolling stock", "vehicle class", "Wikidata", "3D model", "鉄道車両", "形式"):
        g.add((DS, DCAT.keyword, Literal(kw)))
    # VoID: what is in the RDF, and how to get it
    g.add((DS, VOID.uriSpace, Literal(BASE)))
    g.add((DS, VOID.rootResource, SCHEME))
    for r in (CLS.Q696668, CLS.Q115612330, CLS["tb-skytrain-mk2"], MDL.icet_411):
        g.add((DS, VOID.exampleResource, r))
    for k in ("allTtl", "allJsonld"):
        g.add((DS, VOID.dataDump, URIRef(SITE + next(f[1] for f in FILES if f[0] == k))))
    g.add((DS, RDFS.comment, Literal(
        "There is no SPARQL endpoint. Load the dump (void:dataDump) into a triple store, or read single resources: "
        "each URI (a class <https://w3id.org/railclass/{id}>, a model <https://w3id.org/railclass/model/{id}>) is sent by "
        "w3id.org to its Turtle file, JSON-LD file or human page by the Accept header (text/turtle, application/ld+json, "
        "anything else).", lang="en")))
    g.add((DS, VOID.feature, URIRef("http://www.w3.org/ns/formats/Turtle")))
    g.add((DS, VOID.feature, URIRef("http://www.w3.org/ns/formats/JSON-LD")))
    for v in n["vocabularies"]:
        g.add((DS, VOID.vocabulary, URIRef(v)))
    for k, p in (("triples", VOID.triples), ("entities", VOID.entities), ("properties", VOID.properties)):
        g.add((DS, p, Literal(n[k])))
    g.add((DS, VOID.distinctSubjects, Literal(n["entities"])))
    for t, c in n["typeCounts"]:
        part = BNode(); g.add((DS, VOID.classPartition, part)); g.add((part, VOID["class"], URIRef(t))); g.add((part, VOID.entities, Literal(c)))
    for p, c in n["topProperties"]:
        part = BNode(); g.add((DS, VOID.propertyPartition, part)); g.add((part, VOID.property, URIRef(p))); g.add((part, VOID.triples, Literal(c)))
    # Linksets to Wikidata and to Wikimedia Commons
    for key, pred, target, triples in (("wikidata", SKOS.exactMatch, URIRef("http://www.wikidata.org/"), n["exactMatch"]),
                                       ("commons", FOAF.depiction, URIRef("http://commons.wikimedia.org/"), n["depiction"])):
        ls = URIRef(BASE + "dataset#links-" + key)
        g.add((ls, RDF.type, VOID.Linkset)); g.add((ls, VOID.subjectsTarget, DS)); g.add((ls, VOID.objectsTarget, target))
        g.add((ls, VOID.linkPredicate, pred)); g.add((ls, VOID.triples, Literal(triples))); g.add((DS, VOID.subset, ls))
    # Every published file as a DCAT distribution, with its own licence
    for key, rel, mt, lic, en, ja in FILES:
        d = URIRef(BASE + "dataset#" + key)
        g.add((DS, DCAT.distribution, d)); g.add((d, RDF.type, DCAT.Distribution))
        g.add((d, DCTERMS.title, Literal(en, lang="en"))); g.add((d, DCTERMS.title, Literal(ja, lang="ja")))
        g.add((d, DCAT.downloadURL, URIRef(SITE + rel))); g.add((d, DCAT.mediaType, Literal(mt)))
        g.add((d, DCAT.byteSize, Literal(size(rel), datatype=XSD.nonNegativeInteger)))
        if lic is not None:
            g.add((d, DCTERMS.license, lic))
        if key == "eratv":
            g.add((d, DCTERMS.rights, Literal(
                "Type IDs and names: source European Union Agency for Railways (ERATV); reproduction is authorised provided the "
                "source is acknowledged (https://www.era.europa.eu/content/disclaimer-and-copyright-notice). Wikidata identifiers: CC0.", lang="en")))
            g.add((d, DCTERMS.conformsTo, URIRef("http://www.w3.org/ns/csvw")))
        if key == "lines":
            g.add((d, DCTERMS.rights, Literal("© OpenStreetMap contributors, ODbL. Only the line IDs (Wikidata items) are in the RDF.", lang="en")))
    return g


def main():
    n = count()
    modified = datetime.date.fromtimestamp(os.path.getmtime(os.path.join(RDF_DIR, "all.ttl"))).isoformat()
    g = build(n, modified)
    g.serialize(os.path.join(RDF_DIR, "void.ttl"), format="turtle")
    g.serialize(os.path.join(RDF_DIR, "void.jsonld"), format="json-ld", indent=1, auto_compact=True,
                context={"void": str(VOID), "dcat": str(DCAT), "dcterms": str(DCTERMS), "foaf": str(FOAF), "skos": str(SKOS), "xsd": str(XSD)})
    files = [{"key": k, "path": rel, "type": mt, "bytes": size(rel)} for k, rel, mt, *_ in FILES]
    out = {k: v for k, v in n.items() if k not in ("topProperties", "typeCounts", "vocabularies")}
    out.update(modified=modified, uriSpace=BASE, classUri=str(CLS), modelUri=str(MDL), vocab=str(TB), dataset=str(DS), site=SITE, files=files,
               void=[{"key": "voidTtl", "path": "rdf/void.ttl", "bytes": os.path.getsize(os.path.join(RDF_DIR, "void.ttl"))},
                     {"key": "voidJsonld", "path": "rdf/void.jsonld", "bytes": os.path.getsize(os.path.join(RDF_DIR, "void.jsonld"))}])
    with open(os.path.join(DOCS, "data", "dataset.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"{len(g)} triples -> docs/rdf/void.ttl|.jsonld; counts -> docs/data/dataset.json")
    print({k: v for k, v in out.items() if isinstance(v, int)})


if __name__ == "__main__":
    main()
