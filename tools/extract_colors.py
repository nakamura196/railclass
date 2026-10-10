"""Take the livery colours of each 3D model from its build in ~/git/3d/skytrain and name them (red, blue, ...).

Usage: python3 tools/extract_colors.py [--skytrain <path, default ~/git/3d/skytrain>]
  Reads skytrain/out/<model-id>/*.obj and its .mtl: every face carries the material (= named colour) of the cut
  that made it, so the area of each material is the area of that colour on the body.
  Materials that are not paint (glass, lamps, door seams, tyres, bellows) are left out; the rest is the painted area.
  Each colour is put under one basic colour name (a Wikidata item) by hue and lightness; a basic colour is kept
  when it covers at least MIN_SHARE of the painted area (smaller ones are logos, lamps and numbers).
Writes tools/livery_colors.json, which tools/build_rdf.py reads (so the RDF build does not need the skytrain checkout).
"""
import colorsys, glob, json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "tools", "livery_colors.json")
NOT_PAINT = {"glass", "lamp", "groove", "tyre", "bellows"}
MIN_SHARE = 0.015

# basic colour name -> Wikidata item (instances of colour Q1075; labels come from Wikidata in build_rdf.py)
BASIC = {"red": "Q3142", "orange": "Q39338", "yellow": "Q943", "green": "Q3133", "blue": "Q1088", "purple": "Q3257809",
         "pink": "Q429220", "brown": "Q47071", "white": "Q23444", "grey": "Q42519", "black": "Q23445"}


def basic_name(rgb):
    r, g, b = (c / 255 for c in rgb)
    h, l, _ = colorsys.rgb_to_hls(r, g, b)
    h *= 360
    chroma = max(r, g, b) - min(r, g, b)
    if chroma < 0.12:   # achromatic (body white, cream, charcoal, silver)
        return "white" if l > 0.85 else "black" if l < 0.15 else "grey"
    if l < 0.12:
        return "black"
    if (h < 50 or h >= 345) and chroma < 0.35 and l < 0.6:   # dull dark red-orange: brown stripes, gold trim
        return "brown"
    for top, name in ((15, "red"), (45, "orange"), (68, "yellow"), (180, "green"), (260, "blue")):
        if h < top:
            return name
    if h < 345:
        return "pink" if l > 0.6 else "purple"
    return "red"


def lin2srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def measure(obj):
    """Area per material of an OBJ (Blender exports it triangulated) and the sRGB of each material."""
    rgb, cur = {}, None
    for line in open(obj[:-4] + ".mtl", encoding="utf-8"):
        p = line.split()
        if p and p[0] == "newmtl":
            cur = p[1].split(".")[0]   # Blender adds .001 to names used by an earlier object
        elif p and p[0] == "Kd":
            rgb[cur] = tuple(round(lin2srgb(float(x)) * 255) for x in p[1:4])
    V, area, m = [], {}, None
    for line in open(obj, encoding="utf-8"):
        if line.startswith("v "):
            V.append(tuple(map(float, line.split()[1:4])))
        elif line.startswith("usemtl"):
            m = line.split()[1].split(".")[0]
        elif line.startswith("f "):
            i = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
            for k in range(1, len(i) - 1):
                a, b, c = V[i[0]], V[i[k]], V[i[k + 1]]
                u = [b[j] - a[j] for j in range(3)]; v = [c[j] - a[j] for j in range(3)]
                x = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
                area[m] = area.get(m, 0) + 0.5 * (x[0] ** 2 + x[1] ** 2 + x[2] ** 2) ** 0.5
    return area, rgb


def main():
    sky = sys.argv[sys.argv.index("--skytrain") + 1] if "--skytrain" in sys.argv else os.path.expanduser("~/git/3d/skytrain")
    sys.path.insert(0, os.path.join(HERE, "tools"))
    from build_rdf import MODELS
    out = {"note": __doc__.strip().splitlines()[0], "minShare": MIN_SHARE, "notPaint": sorted(NOT_PAINT),
           "basic": BASIC, "models": {}}
    for mid in MODELS:
        objs = glob.glob(os.path.join(sky, "out", mid, "*.obj"))
        if len(objs) != 1:
            print("skip (no single OBJ):", mid, objs); continue
        area, rgb = measure(objs[0])
        paint = {k: a for k, a in area.items() if k not in NOT_PAINT}
        total = sum(paint.values())
        samples = sorted(({"name": k, "hex": "#%02X%02X%02X" % rgb[k], "basic": basic_name(rgb[k]), "share": round(a / total, 4)}
                          for k, a in paint.items()), key=lambda s: -s["share"])
        by_basic = {}
        for s in samples:
            by_basic[s["basic"]] = by_basic.get(s["basic"], 0) + s["share"]
        colors = [n for n, sh in sorted(by_basic.items(), key=lambda x: -x[1]) if sh >= MIN_SHARE]
        out["models"][mid] = {"source": os.path.relpath(objs[0], os.path.dirname(sky)), "colors": colors,
                              "samples": [s for s in samples if s["basic"] in colors and s["share"] >= 0.005]}
        print(f"{mid:12s} " + ", ".join(f"{n} {by_basic[n]:.1%}" for n in colors))
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("->", OUT)


if __name__ == "__main__":
    main()
