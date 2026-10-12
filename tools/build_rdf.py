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
UA = "railclass-build/1.0 (https://github.com/nakamura196/railclass)"

FACETS = json.load(open(os.path.join(DOCS, "facets.json"), encoding="utf-8"))["facets"]
# with the derived facets ("wd": a SPARQL pattern, e.g. operatingCountry), which come from the facet tables only
WD_FACETS = [f for f in FACETS if (f["uri"].startswith(str(WDT)) or "wd" in f) and f.get("on", "class") == "class"]
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
    "Q19877282": ("Q19877282", None, None),                     # Park series (Budd dome-observation sleepers of The Canadian)
    "Q23641827": ("Q23641827", None, None),                     # Electric Tilt Train (Queensland Rail)
    "Q246841": ("Q246841", None, None),                         # British Rail Class 395 (Javelin)
    "Q18331751": ("Q18331751", None, None),                     # PKP class ED250 (Alstom New Pendolino)
    # Wikidata has only a "mul" label for this class (none in en / ja), so the labels are given here
    "Q140092296": ("Q140092296", None, {"en": "Alstom X'Trapolis Tsíimin K'áak (Tren Maya)", "ja": "トレン・マヤの電車（X'Trapolis Tsíimin K'áak）"}),
    # Gautrain: Wikidata has no item for the rolling stock (Q1476881 is the system), so a class of our own; the system
    # is linked as the line it runs on (tools/class_lines.tsv). No skos:broader: Electrostar (Q841722) is the UK series
    # item, and the facets marked "inherit" would carry its values over.
    "tb-gautrain": (None, None, {"en": "Gautrain Electrostar", "ja": "ハウトレインの電車（Electrostar）"}),
    # Dubai Metro: as for the Gautrain, Wikidata has no item for the Kinki Sharyo rolling stock (Q83787 is the system)
    "tb-dubaimetro": (None, None, {"en": "Dubai Metro Kinki Sharyo train", "ja": "ドバイメトロの電車（近畿車輛）"}),
    "Q65054413": ("Q65054413", None, None),                     # Taiwan Railway EMU3000 (Hitachi)
    # SRT Red Lines (Bangkok): Wikidata has no item for the Hitachi AT100 rolling stock (Q2542280 is the line system), so a class
    # of our own; the system is linked as the line it runs on (tools/class_lines.tsv). Not under Hitachi A-train (Q1066003): too broad a family.
    "tb-srtred": (None, None, {"en": "SRT Red Lines Hitachi AT100", "ja": "SRTレッドラインの電車（日立 AT100）"}),
    "Q853105": ("Q853105", None, None),                       # SJ X2 (X2000 power car)
    "Q7015181": ("Q7015181", None, None),                     # New Zealand AK class carriage (TranzAlpine)
    # PeruRail Vistadome railcar (Macosa/MAN 1984, 220-225): Wikidata has no item for it, so a class of our own; the line it
    # runs on (Q100145062, Cusco - Machu Picchu) is linked in tools/class_lines.tsv.
    "tb-vistadome": (None, None, {"en": "PeruRail Vistadome railcar (Macosa/MAN)", "ja": "ペルーレイルのビスタドーム気動車（Macosa/MAN）"}),
    "Q10871152": ("Q10871152", None, None),                    # China Railway DF8B (the Kenyan SGR export version has no item of its own)
    "Q26158722": ("Q26158722", None, None),                    # Intercity Nieuwe Generatie (NS ICNG, Alstom Coradia Stream)
    # Tanzania SGR E6800: Wikidata has no item for the Hyundai Rotem locomotive (Q60744141 is the railway), so a class of our
    # own; the railway is linked in tools/class_lines.tsv. Not under TCDD E68000 (Q28444692), its design ancestor: another class.
    "tb-tanzania": (None, None, {"en": "Tanzania SGR class E6800 electric locomotive", "ja": "タンザニア SGR E6800 形電気機関車"}),
    "Q20926238": ("Q20926238", None, None),                    # TCDD E32000 (Marmaray, Hyundai Rotem)
    "Q104216528": ("Q104216528", None, None),                   # KTX-Eum (Korail EMU-260, Hyundai Rotem)
    "Q2284320": ("Q2284320", None, None),                     # Siemens Inspiro (family; no item for the Riyadh trains)
    "Q706345": ("Q706345", None, None),                       # IC3 (DSB MF, ABB Scandia)
    "Q18349836": ("Q18349836", None, None),                    # DHR B class (0-4-0ST steam)
    "Q26724167": ("Q26724167", None, None),                    # Avelia Liberty (new Acela, Alstom)
    "Q1080162": ("Q1080162", None, None),                     # British Rail Class 43 (HST power car)
    "Q120801969": ("Q120801969", None, None),                   # Corcovado rack railcars, 4th generation (Stadler Bhe 4/8)
    # Lisbon 'Remodelado' trams (Carris 541-585): Wikidata has no item for them (Q149629 is the tram system), so a class of
    # our own; the system is linked in tools/class_lines.tsv. Route 28 itself is Q63034669 (a line, not a vehicle).
    "tb-lisbon28": (None, None, {"en": "Lisbon Remodelado tram (Carris 541-585)", "ja": "リスボン市電の Remodelado（Carris 541〜585）"}),
    # Addis Ababa Light Rail: Wikidata has no item for the CNR Changchun trams (Q16250141 is the system), so a class of our
    # own; the system is linked in tools/class_lines.tsv.
    "tb-addis": (None, None, {"en": "Addis Ababa Light Rail tram (CNR Changchun)", "ja": "アディスアベバ・ライトレールの路面電車（CNR 長春）"}),
    "Q56394168": ("Q56394168", None, None),                    # MRTJ 1000 series (Jakarta MRT, Nippon Sharyo)
    "Q5122977": ("Q5122977", None, None),                     # Sydney Trains A & B sets (Waratah)
    "Q117538222": ("Q117538222", None, None),                   # EFE SFB-500 (CRRC Sifang bimodal)
    # San Francisco cable cars: Wikidata has no item for the cars (Q374956 is the cable car system), so a class of our own;
    # the system is linked in tools/class_lines.tsv. Route items: Powell-Hyde Q121410548, Powell-Mason Q113367771.
    "tb-cablecar": (None, None, {"en": "San Francisco cable car (Powell Street single-ended type)", "ja": "サンフランシスコのケーブルカー（パウエル線の片運転台の車）"}),
    # Cairo Metro Line 2: Wikidata has no item for its Japanese-built cars (Q5017773 is the line), so a class of our own;
    # the line is linked in tools/class_lines.tsv.
    "tb-cairo": (None, None, {"en": "Cairo Metro Line 2 Japanese-built car", "ja": "カイロ地下鉄 2 号線の日本製の電車"}),
    "Q423578": ("Q423578", None, None),                       # Vietnam Railways D19E
    "Q1814255": ("Q1814255", None, None),                     # London Underground 1973 Stock (Piccadilly line)
    "Q7274448": ("Q7274448", None, None),                     # R211 (New York City Subway, Kawasaki)
    "Q18619244": ("Q18619244", None, None),                    # KTM Class 93 (ETS, CRRC Zhuzhou)
    "Q119438293": ("Q119438293", None, None),                  # Namo Bharat (NCRTC RRTS trainset; P31 is Q870 train)
    "Q55614147": ("Q55614147", None, None),                   # Hyundai Rotem EMU (SkyTrain Canada Line)
    "Q324870": ("Q324870", None, None),                       # ICE 4 (DB Class 412)
    "Q727577": ("Q727577", None, None),                       # SNCF TGV 2N2 (Euroduplex; Al Boraq is the ONCF service Q60539878)
    "Q16798908": ("Q16798908", None, None),                   # SBB RABe 501 Giruno (Stadler SMILE)
    "Q6138251": ("Q6138251", None, {"en": "Talgo 350 SRO (Haramain High Speed Railway)", "ja": "ハラマイン高速鉄道 Talgo 350 SRO"}),  # Talgo 350 SRO (Haramain High Speed Railway; Wikidata has es/mul labels only)
    "Q5321494": ("Q5321494", None, None),                     # Melbourne E-class tram (Bombardier Flexity Swift)
    "Q134533452": ("Q134533452", None, None),                 # Siemens SCB-40 (Brightline)
    "Q96407257": ("Q96407257", None, None),                   # Sydney Metro Metropolis Stock (Alstom)
    "Q891775": ("Q891775", None, None),                       # Bombardier BiLevel Coach (West Coast Express cab car)
}

# Hand-entered values: cid -> {facet id: [values]}, with the source in HAND_SOURCE. Values are Wikidata Q ids or years.
SKYTRAIN = {"country": ["Q16"], "operator": ["Q141170526"]}   # Canada; British Columbia Rapid Transit Company (from SkyTrain Q876780)
HAND = {
    "tb-skytrain-mk1": {**SKYTRAIN, "manufacturer": ["Q3552199"], "serviceEntry": [1985]},   # UTDC; opening of SkyTrain 1985-12-11
    "tb-skytrain-mk2": {**SKYTRAIN, "manufacturer": ["Q688893"], "serviceEntry": [2002]},    # Bombardier Transportation
    "tb-skytrain-mk3": {**SKYTRAIN, "manufacturer": ["Q688893"], "serviceEntry": [2016]},
    "tb-skytrain-mk5": {**SKYTRAIN, "manufacturer": ["Q309084"]},                            # Alstom
    # South Africa; Gautrain Management Agency; Bombardier Transportation; EMU; opening 2010
    "tb-gautrain": {"country": ["Q258"], "operator": ["Q84945092"], "manufacturer": ["Q688893"], "kind": ["Q483373"], "serviceEntry": [2010]},
    # United Arab Emirates; Serco (Wikidata P137 of Q83787); Kinki Sharyo; EMU; opening 2009
    "tb-dubaimetro": {"country": ["Q878"], "operator": ["Q499104"], "manufacturer": ["Q1592306"], "kind": ["Q483373"], "serviceEntry": [2009]},
    # Thailand; State Railway of Thailand (its subsidiary SRTET runs the line and has no item); Hitachi; EMU; opening 2021
    "tb-srtred": {"country": ["Q869"], "operator": ["Q2165702"], "manufacturer": ["Q53238"], "kind": ["Q483373"], "serviceEntry": [2021]},
    # Peru; PeruRail (P137 of Q100145062); Macosa (today Stadler Rail Valencia); railcar. No service-entry year: built 1984, Vistadome use not dated
    "tb-vistadome": {"country": ["Q419"], "operator": ["Q1407952"], "manufacturer": ["Q2729224"], "kind": ["Q752392"]},
    # Tanzania; Tanzania Railways Corporation (P137 of Q60744141); Hyundai Rotem; electric locomotive; passenger service from 2024
    "tb-tanzania": {"country": ["Q924"], "operator": ["Q2393276"], "manufacturer": ["Q152517"], "kind": ["Q625151"], "serviceEntry": [2024]},
    # Portugal; Carris; tram; rebuilt 1995-96 (no manufacturer: 1930s bodies rebuilt with new running gear and electrics)
    "tb-lisbon28": {"country": ["Q45"], "operator": ["Q1045108"], "kind": ["Q3407658"], "serviceEntry": [1995]},
    # Ethiopia; Ethiopian Railway Corporation; CRRC Changchun (then CNR Changchun); tram; opening 2015
    "tb-addis": {"country": ["Q115"], "operator": ["Q55639671"], "manufacturer": ["Q848225"], "kind": ["Q3407658"], "serviceEntry": [2015]},
    # United States; San Francisco Municipal Railway (P137 of Q374956); cable car. No maker or year: the cars were built over many decades
    "tb-cablecar": {"country": ["Q30"], "operator": ["Q1140138"], "kind": ["Q5609555"]},
    # Egypt; National Authority for Tunnels (owner); Kinki Sharyo (with Mitsubishi Corporation and Toshiba); EMU; opening 1996
    "tb-cairo": {"country": ["Q79"], "operator": ["Q64744683"], "manufacturer": ["Q1592306"], "kind": ["Q483373"], "serviceEntry": [1996]},
}
HAND_SOURCE = {
    "tb-skytrain-mk1": "Country and operator from Wikidata Q876780 (SkyTrain (Vancouver)); manufacturer from English Wikipedia 'SkyTrain (Vancouver)' (rolling stock section, read 2026-10-09); service entry year from the train-bodies gallery text.",
    "tb-gautrain": "Country, operator and opening date (2010-06-08) from Wikidata Q1476881 (Gautrain, the system); manufacturer and type (Bombardier Electrostar EMU) from the skytrain lab note docs/notes/gautrain.md (photos and en.wikipedia 'Gautrain', read 2026-10-11).",
    "tb-dubaimetro": "Country, operator and opening date (2009-09-09) from Wikidata Q83787 (Dubai Metro, the system); manufacturer (Kinki Sharyo, cars 5001-5079) from en.wikipedia 'Dubai Metro' (rolling stock, read 2026-10-11) via the skytrain lab note docs/notes/dubaimetro.md.",
    "tb-srtred": "Country from Wikidata Q2542280 (SRT Red Lines, the system); operator (State Railway of Thailand, through its subsidiary SRT Electrified Train), manufacturer and type (Hitachi AT100 EMU) and opening year (2021) from en.wikipedia and ja.wikipedia (read 2026-10-12) via the skytrain lab note docs/notes/srtred.md.",
    "tb-vistadome": "Country and operator from Wikidata Q100145062 (Tramo Sur Oriente del Ferrocarril del Sur, the line); builder (Macosa/MAN, 1984, cars 220-225; Macosa is today Stadler Rail Valencia, Q2729224) and type (single-cab diesel railcar) from en.wikipedia 'List of stock used by PeruRail' (read 2026-10-12) via the skytrain lab note docs/notes/vistadome.md.",
    "tb-tanzania": "Country and operator from Wikidata Q60744141 (Tanzania Standard Gauge Railway); manufacturer and type (Hyundai Rotem electric locomotive, class E6800) from Railvolution 'New locomotives for Tanzania'; passenger service from 2024-06-14 (Railway Journal, The Citizen), read 2026-10-12 via the skytrain lab note docs/notes/tanzania.md.",
    "tb-lisbon28": "Country and operator (Carris) from Wikidata Q149629 (trams in Lisbon); type and the 1995-96 rebuild of the 1930s standard bodies (cars 541-585) from the skytrain lab note docs/notes/lisbon28.md.",
    "tb-addis": "Country and opening date (2015-09-21) from Wikidata Q16250141 (Addis Ababa Light Rail, the system); operator (Ethiopian Railway Corporation), manufacturer (CNR Changchun, now CRRC Changchun) and type (three-section 70 % low-floor tram) from the skytrain lab note docs/notes/addis.md (2026-10-12).",
    "tb-cablecar": "Country, operator and type (cable car) from Wikidata Q374956 (San Francisco cable car system); the Powell Street single-ended car and its dimensions from streetcar.org via the skytrain lab note docs/notes/cablecar.md (2026-10-12).",
    "tb-cairo": "Country and opening year (1996) from Wikidata Q5017773 (Cairo Metro Line 2); builders (Mitsubishi Corporation, Kinki Sharyo and Toshiba) and type from the skytrain lab note docs/notes/cairo.md (2026-10-12); operator entered as the National Authority for Tunnels, the owner of the Cairo Metro.",
}
for k in ("tb-skytrain-mk2", "tb-skytrain-mk3", "tb-skytrain-mk5"):
    HAND_SOURCE[k] = HAND_SOURCE["tb-skytrain-mk1"]

# Japanese labels for Wikidata classes that have none (hand-entered; Wikidata's own labels win when they exist)
LABEL_JA = {"Q115612330": "ICE T 411形", "Q137972762": "ICE T 415形", "Q8078904": "ÖBB 4011形",
            "Q140611223": "Amtrak Airo", "Q137921671": "New Flyer XD60",
            "Q289090": "トランスラピッド 08", "Q18331751": "ED250 ペンドリーノ",
            "Q26158722": "ICNG（新世代インターシティ）",
            "Q20926238": "TCDD E32000形",
            "Q18349836": "ダージリン・ヒマラヤ鉄道 B形",
            "Q120801969": "コルコバード登山鉄道 4 代目電車",
            "Q56394168": "ジャカルタ MRT 1000系",
            "Q117538222": "チリ国鉄 SFB-500",
            "Q423578": "ベトナム鉄道 D19E形",
            "Q55614147": "カナダ・ライン（現代ロテム製）",
            "Q134533452": "ブライトライン SCB-40",
            "Q96407257": "シドニーメトロ（アルストム メトロポリス）"}

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
    "via-stainless": ({"en": "VIA Rail livery (bare stainless steel, unstriped)", "ja": "VIA鉄道の塗装（帯なしのステンレス）"}, "Q876720"),
    "qr-tilt": ({"en": "Queensland Rail Tilt Train livery (yellow cab end and stainless, since the 2015–17 refurbishment)", "ja": "クイーンズランド鉄道のティルト・トレインの塗装（黄色の先頭部とステンレス、2015〜17年の更新から）"}, "Q379439"),
    "southeastern-2025": ({"en": "Southeastern high-speed livery (2025: grey doors and swoosh)", "ja": "Southeastern の高速電車の塗装（2025年から、灰色の扉と弧）"}, "Q1696490"),
    "pkp-ic-ed250": ({"en": "PKP Intercity Pendolino livery (silver with sky blue and cobalt)", "ja": "PKP インターシティのペンドリーノの塗装（銀に空色と紺）"}, "Q590406"),
    "tren-maya-xiinbal": ({"en": "Tren Maya Xiinbal livery (cream, dark teal and green)", "ja": "トレン・マヤ Xiinbal の塗装（クリーム、濃い青緑と緑）"}, "Q59806309"),
    "gautrain": ({"en": "Gautrain livery (champagne gold, from the 2010 opening)", "ja": "ハウトレインの塗装（シャンパンゴールド、2010年の開業から）"}, "Q84945092"),
    "dubai-metro": ({"en": "Dubai Metro livery (silver and light blue)", "ja": "ドバイメトロの塗装（銀と水色）"}, "Q22101985"),   # RTA (Roads and Transport Authority, Dubai)
    "tr-emu3000-red": ({"en": "Taiwan Railway EMU3000 livery (white with a black nose, red stripe at the coupled end)", "ja": "台湾鉄路 EMU3000型の塗装（白い車体に黒い先頭部、連結側に赤い帯）"}, "Q697926"),
    "srt-red-line": ({"en": "SRT Red Lines livery (white with a red band, black front mask)", "ja": "SRTレッドラインの塗装（白に赤い帯、黒い前面）"}, "Q2165702"),
    "sj-x2000-2021": ({"en": "SJ X2000 refurbished livery (dark grey nose and swoosh, light grey, stainless; from 2021)", "ja": "SJ X2000 の更新車の塗装（濃い灰の前頭部と帯、明るい灰、ステンレス。2021年から）"}, "Q8301325"),
    "kiwirail-ak-flames": ({"en": "KiwiRail Great Journeys AK carriage livery (silver with a grey line and yellow, orange and red flames)", "ja": "キウイレイルの AK 形客車の塗装（銀に灰色の線と黄・橙・赤の炎の帯）"}, "Q956508"),
    "perurail-vistadome": ({"en": "PeruRail livery (blue with yellow stripes, silver roof; seen in photos up to 2023)", "ja": "ペルーレイルの塗装（青に黄の線、銀の屋根。2023年の写真まで確認）"}, "Q1407952"),
    "kr-sgr-df8b": ({"en": "Kenya Railways SGR livery (red cabs and roof, white body, orange and yellow lines, Kenyan flag)", "ja": "ケニア鉄道 SGR の塗装（赤い運転室と屋根、白い車体、オレンジと黄色の線、ケニアの国旗）"}, "Q1663639"),
    "ns-icng": ({"en": "NS livery (yellow and blue, dark grey round the cab)", "ja": "オランダ鉄道の塗装（黄と青、運転室のまわりは濃い灰）"}, "Q23076"),
    "trc-sgr": ({"en": "Tanzania Railways Corporation SGR livery (cream with orange arches, maroon lower body)", "ja": "タンザニア鉄道公社 SGR の塗装（クリームにオレンジの弧、えんじの裾）"}, "Q2393276"),
    "tcdd-marmaray": ({"en": "Marmaray livery (white cab front with a black face, stainless with teal and red lines; 2024-)", "ja": "マルマライの塗装（白い前頭部に黒い顔、ステンレスに青緑と赤の線。2024年以降の写真）"}, "Q28220824"),
    "korail-ktx-eum": ({"en": "KTX-Eum livery (steel blue with a charcoal window band and a champagne line)", "ja": "KTX-이음の塗装（青い車体に濃い灰の窓帯と金色の細い線）"}, "Q18169"),
    "riyadh-metro-line1": ({"en": "Riyadh Metro Line 1 (Blue Line) livery (white lower side, black window band, blue band)", "ja": "リヤド・メトロ 1 号線（ブルーライン）の塗装（白い下回り、黒い窓帯、青い帯）"}, "Q12194736"),   # Royal Commission for Riyadh City (owner)
    "dsb-ic3": ({"en": "DSB livery (silver aluminium with a navy window band)", "ja": "デンマーク国鉄の塗装（銀のアルミに紺の窓帯）"}, "Q83824"),
    "dhr-blue": ({"en": "Darjeeling Himalayan Railway blue livery (blue tank, bunker and cab with white lining)", "ja": "ダージリン・ヒマラヤ鉄道の青の塗装（青いタンク・炭庫・運転室に白線）"}, "Q463874"),
    "amtrak-acela-2025": ({"en": "Acela livery (white and silver with Acela blue and a red band; 2025-)", "ja": "アセラの塗装（白と銀にアセラの青と赤い帯。2025年から）"}, "Q23239"),
    "scotrail-inter7city": ({"en": "ScotRail Inter7City livery (navy with a yellow front and a city skyline)", "ja": "スコットレールの Inter7City の塗装（紺に黄色の顔、町並みの絵）"}, "Q107980329"),
    "corcovado-2019": ({"en": "Trem do Corcovado livery (red with a black front mask, white lower panel; 2019-)", "ja": "コルコバード登山鉄道の塗装（赤に黒い顔、白い腰板。2019年から）"}, "Q1132053"),
    "carris-yellow": ({"en": "Carris tram livery (yellow and white)", "ja": "Carris の路面電車の塗装（黄と白）"}, "Q1045108"),
    "aalrt-green": ({"en": "Addis Ababa Light Rail East-West (green) line livery (white and green)", "ja": "アディスアベバ・ライトレール東西線（緑線）の塗装（白と緑）"}, "Q55639671"),
    "mrtj-standard": ({"en": "Jakarta MRT standard livery (navy and blue face, stainless with a sky-blue line; 2019-)", "ja": "ジャカルタ MRT の標準の塗装（紺と青の顔、ステンレスに水色の線。2019年から）"}, "Q137969581"),
    "sydney-trains-waratah": ({"en": "Sydney Trains Waratah livery (yellow face, orange cab sides, bare stainless, yellow doors)", "ja": "シドニー・トレインズのワラタの塗装（黄色の顔、橙色の運転室、ステンレス、黄色の扉）"}, "Q7660181"),
    "efe-sfb500": ({"en": "EFE SFB-500 livery (silver with a red-and-black nose and a blue stripe; 2024-)", "ja": "EFE SFB-500 の塗装（銀に赤と黒の顔、青い線。2024年から）"}, "Q679910"),
    "muni-cablecar": ({"en": "Muni cable car livery (maroon, cream and light blue)", "ja": "Muni のケーブルカーの塗装（栗色・クリーム・水色）"}, "Q1140138"),
    "cairo-line2": ({"en": "Cairo Metro Line 2 livery (stainless with orange and lilac bands)", "ja": "カイロ地下鉄 2 号線の塗装（ステンレスにオレンジと薄紫の帯）"}, "Q64744683"),
    "vnr-hanoi-skyblue": ({"en": "Vietnam Railways Hanoi depot livery (sky blue, cream cab front, red band)", "ja": "ベトナム鉄道ハノイ機関区の塗装（空色、クリーム色の運転室の正面、赤い帯）"}, "Q501329"),
    "lu-corporate": ({"en": "London Underground corporate livery (red cab end and doors, white sides, blue skirt)", "ja": "ロンドン地下鉄の塗装（赤い運転室の端と扉、白い側面、青い裾）"}, "Q682520"),
    "mta-r211": ({"en": "MTA R211 livery (blue face, stainless with a diagonal blue band)", "ja": "MTA の R211 の塗装（青い顔、ステンレスに斜めの青い帯）"}, "Q1146109"),
    "ktm-ets2": ({"en": "KTM ETS2 livery (yellow nose, silver with a red band)", "ja": "KTM の ETS2 の塗装（黄色の鼻、銀に赤い帯）"}, "Q1187590"),
    "ncrtc-namobharat": ({"en": "NCRTC Namo Bharat livery (bare stainless with a red arrow on the cab)", "ja": "NCRTC のナモ・バーラトの塗装（ステンレスの地に、運転室の赤い矢印）"}, "Q17077649"),
    "translink-canadaline": ({"en": "Canada Line livery (stainless, blue cab with a black shield face, white and blue swooshes, blue fading to green)", "ja": "カナダ・ラインの塗装（ステンレス、黒い盾形の顔の青い運転台、白と青の流れ模様、青から緑への移り）"}, "Q141170779"),
    "oncf-alboraq": ({"en": "ONCF Al Boraq livery (silver with Moroccan red and green)", "ja": "ONCF のアル・ボラクの塗装（銀地に、モロッコの赤と緑）"}, "Q1815809"),
    "sbb-giruno": ({"en": "SBB Giruno livery (white body, red nose, black roof)", "ja": "スイス国鉄のギルノの塗装（白い車体、赤い鼻、黒い屋根）"}, "Q83835"),
    "sar-haramain": ({"en": "Haramain High Speed Railway livery (white with gold and green lines)", "ja": "ハラマイン高速鉄道の塗装（白地に金と緑の線）"}, "Q843548"),
    "ptv-tram": ({"en": "PTV tram livery (green facets, white, yellow doors)", "ja": "PTV の路面電車の塗装（緑の三角形の面、白、黄色の扉）"}, "Q16927551"),
    "brightline-yellow": ({"en": "Brightline yellow livery (since 2022)", "ja": "ブライトラインの黄色の塗装（2022 年から）"}, "Q27012668"),
    "sydney-metro": ({"en": "Sydney Metro livery (charcoal front with teal corner wings, white body, navy window band)", "ja": "シドニーメトロの塗装（濃い灰の前面に青緑の翼、白い車体、紺の窓帯）"}, "Q20861549"),
    "wce-violet": ({"en": "West Coast Express livery (white and violet with gold lines)", "ja": "ウェストコースト・エクスプレスの塗装（白と紫に金の線）"}, "Q1675085"),
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
    "canadian": ("Q19877282", "via-stainless", None),
    "tilttrain": ("Q23641827", "qr-tilt", None),
    "class395": ("Q246841", "southeastern-2025", None),
    "ed250": ("Q18331751", "pkp-ic-ed250", None),
    "trenmaya": ("Q140092296", "tren-maya-xiinbal", None),
    "gautrain": ("tb-gautrain", "gautrain", None),
    "dubaimetro": ("tb-dubaimetro", "dubai-metro", None),
    "emu3000": ("Q65054413", "tr-emu3000-red", None),
    "srtred": ("tb-srtred", "srt-red-line", None),
    "x2000": ("Q853105", "sj-x2000-2021", None),
    "tranzalpine": ("Q7015181", "kiwirail-ak-flames", None),
    "vistadome": ("tb-vistadome", "perurail-vistadome", None),
    "madaraka": ("Q10871152", "kr-sgr-df8b", None),
    "icng": ("Q26158722", "ns-icng", None),
    "tanzania": ("tb-tanzania", "trc-sgr", None),
    "marmaray": ("Q20926238", "tcdd-marmaray", None),
    "ktxeum": ("Q104216528", "korail-ktx-eum", None),
    "riyadh": ("Q2284320", "riyadh-metro-line1", None),
    "ic3": ("Q706345", "dsb-ic3", None),
    "darjeeling": ("Q18349836", "dhr-blue", None),
    "acela": ("Q26724167", "amtrak-acela-2025", None),
    "ic125": ("Q1080162", "scotrail-inter7city", None),
    "corcovado": ("Q120801969", "corcovado-2019", None),
    "lisbon28": ("tb-lisbon28", "carris-yellow", None),
    "addis": ("tb-addis", "aalrt-green", None),
    "jakartamrt": ("Q56394168", "mrtj-standard", None),
    "waratah": ("Q5122977", "sydney-trains-waratah", None),
    "santiago-chillan": ("Q117538222", "efe-sfb500", None),
    "cablecar": ("tb-cablecar", "muni-cablecar", None),
    "cairo": ("tb-cairo", "cairo-line2", None),
    "vietnam": ("Q423578", "vnr-hanoi-skyblue", None),
    "lu1973": ("Q1814255", "lu-corporate", None),
    "r211": ("Q7274448", "mta-r211", None),
    "ets": ("Q18619244", "ktm-ets2", None),
    "namobharat": ("Q119438293", "ncrtc-namobharat", None),
    "canadaline": ("Q55614147", "translink-canadaline", None),
    "ice4": ("Q324870", "db", None),
    "alboraq": ("Q727577", "oncf-alboraq", None),
    "giruno": ("Q16798908", "sbb-giruno", None),
    "haramain": ("Q6138251", "sar-haramain", None),
    "melbourne-e": ("Q5321494", "ptv-tram", None),
    "brightline": ("Q134533452", "brightline-yellow", None),
    "sydneymetro": ("Q96407257", "sydney-metro", None),
    "wce": ("Q891775", "wce-violet", None),
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
    items = [w for w, _, _ in CLASSES.values() if w]
    if os.path.exists(CACHE) and not refresh:
        out = json.load(open(CACHE, encoding="utf-8"))
        # A class added to CLASSES after the last fetch (a new model): fetch only that one, so the values of the
        # other classes stay as cached (a --refresh would also take every change made on Wikidata since)
        items = [q for q in items if q not in out["classes"]]
        if not items:
            return out
        print("fetch: new classes", " ".join(items))
        out["classes"].update({q: {} for q in items})
    else:
        out = {"fetched": time.strftime("%Y-%m-%d"), "classes": {q: {} for q in items}, "labels": {}}
    vals = " ".join("wd:" + q for q in items)
    for f in WD_FACETS:
        if "wd" in f:   # derived: added from the facet table in main(), not cached
            continue
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
    used = sorted(u for u in used if u not in out["labels"])   # all of them on a fresh fetch; only new ones otherwise
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
        (TB.operatingCountry, RDF.Property, "operating country", "運行国", "A country where this class runs or ran: the countries (Wikidata P17) of its operators (P137) and of the lines it runs on (P3438 on the line, and the hand-filled line table). Added because P17 on a class is sometimes only the country it was built in."),
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


def add_derived(wd):
    """The derived facets (operatingCountry) for the classes with a page: from data/wikidata/facets/<id>.tsv
    (tools/fetch_facets.py), since the cache (fetch) only holds single Wikidata properties."""
    for f in (f for f in WD_FACETS if "wd" in f):
        for r in read_tsv(f"wikidata/facets/{f['id']}.tsv"):
            c = wd["classes"].get(r["item"])
            if c is None or not r["value"]:
                continue
            lst = c.setdefault(f["id"], [])
            if r["value"] not in lst:
                lst.append(r["value"])
            if r["value"] not in wd["labels"]:
                ls = {k: r[f"label_{k}"] for k in ("ja", "en") if r.get(f"label_{k}")}
                if ls:
                    wd["labels"][r["value"]] = ls


def main():
    wd = fetch("--refresh" in sys.argv)
    add_derived(wd)
    add_labels(wd, COLORS["basic"].values())
    # hand-entered values and livery operators: a class without a Wikidata item (tb-) triggers no fetch, so its labels
    # would be missing otherwise
    add_labels(wd, [v for h in HAND.values() for vs in h.values() for v in vs if isinstance(v, str)]
               + [op for _, op in LIVERIES.values()])
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
