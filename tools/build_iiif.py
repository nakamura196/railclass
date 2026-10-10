"""Build IIIF Presentation 4.0 (draft) Manifests for the 3D models, with part annotations.

Run:
  python3 tools/build_iiif.py icet_411        -> docs/iiif/icet_411/manifest.json

Input: annotations/<model>.json (parts and their text), docs/models/<model>.glb,
docs/downloads/<model>/formats.json (written by ~/git/3d/skytrain/tools/export_formats.py).

Each part is aimed at in the model's own drawing coordinates (mm, x from the nose tip, z up from the rim,
as in skytrain/models/icet_base.py), on one face: side / farside / front / rear / roof. A ray is cast at the glb mesh
from outside that face, and the first surface hit becomes the PointSelector. The hit triangle's material
is checked against "expect", so a part that misses its feature (wrong colour) stops the build.

glTF axes: X = drawing x, Y = drawing z (up), Z = -drawing y. The "side" face is the one facing +Z.
"""
import json, os, re, struct, sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://nakamura196.github.io/train-bodies/"
CONTEXT = "http://iiif.io/api/presentation/4/context.json"
PROVIDER = {"id": "https://github.com/nakamura196", "type": "Agent",
            "label": {"ja": ["中村 覚"], "en": ["Satoru Nakamura"]}}
KIND = {"real": {"ja": "実車の特徴", "en": "Real car"},
        "toy": {"ja": "模型の都合", "en": "Toy adaptation"},
        "guess": {"ja": "推測", "en": "Inferred"}}
CAM_DIST = 55.0   # mm from the surface point to a part's camera
# Fixed views besides the hand-set oblique front (camera_default), as the gallery's view page orbits
# (web/src/components/ViewPage.astro): (azimuth from +Z towards +X, polar from +Y), in degrees.
# "Top" leans 1 degree off the pole so that a viewer's lookAt keeps a defined up direction.
VIEWS = [("side", {"ja": ["横"], "en": ["Side"]}, 0, 90),
         ("front", {"ja": ["正面"], "en": ["Front"]}, -90, 85),
         ("top", {"ja": ["上"], "en": ["Top"]}, 0, 1)]
VIEW_DIST = 2.9   # x the bounding-sphere radius; camera_default sits at about this distance on every model


def load_glb(path):
    """Triangles (n, 3, 3) and the material name of each triangle."""
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    bin0 = 20 + n + 8
    assert not any(k in nd for nd in j["nodes"] for k in ("matrix", "scale", "rotation", "translation")), \
        "node transforms are not handled"

    def acc(i):
        a = j["accessors"][i]
        v = j["bufferViews"][a["bufferView"]]
        dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16}[a["componentType"]]
        k = {"SCALAR": 1, "VEC3": 3}[a["type"]]
        off = bin0 + v.get("byteOffset", 0) + a.get("byteOffset", 0)
        return np.frombuffer(b, dt, a["count"] * k, off).reshape(-1, k) if k > 1 else \
            np.frombuffer(b, dt, a["count"], off)

    tris, mats = [], []
    for m in j["meshes"]:
        for p in m["primitives"]:
            pos = acc(p["attributes"]["POSITION"]).astype(np.float64)
            idx = acc(p["indices"]).reshape(-1, 3)
            tris.append(pos[idx])
            # Blender suffixes repeated material names (mk2 has "glass.001"); compare by the base name
            mats += [re.sub(r"\.\d{3}$", "", j["materials"][p["material"]]["name"])] * len(idx)
    return np.concatenate(tris), np.array(mats)


def raycast(tris, orig, d):
    """First hit of the ray orig + t*d (Moller-Trumbore over every triangle). Returns (point, normal, index)."""
    np.seterr(divide="ignore", over="ignore", invalid="ignore")   # axis-aligned rays give 0 * inf
    v0, e1, e2 = tris[:, 0], tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]
    p = np.cross(d, e2)
    det = np.einsum("ij,ij->i", e1, p)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1), 0)
    s = orig - v0
    u = np.einsum("ij,ij->i", s, p) * inv
    q = np.cross(s, e1)
    v = (q @ d) * inv
    t = np.einsum("ij,ij->i", e2, q) * inv
    hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6)
    if not hit.any():
        return None
    i = int(np.argmin(np.where(hit, t, np.inf)))
    nrm = np.cross(e1[i], e2[i])
    nrm /= np.linalg.norm(nrm)
    if nrm @ d > 0:
        nrm = -nrm
    return orig + t[i] * d, nrm, i


def aim(face, at):
    """Ray (origin, direction) in glTF axes for a point given in drawing coordinates on one face."""
    a, c = at
    if face == "side":    # (x, z) seen from the +Z side
        return np.array([a, c, 200.0]), np.array([0, 0, -1.0])
    if face == "farside":  # (x, z) seen from the -Z side (drawing +y; the kerb side of the bus, with its doors)
        return np.array([a, c, -200.0]), np.array([0, 0, 1.0])
    if face == "front":   # (drawing y, z) seen from the nose
        return np.array([-200.0, c, -a]), np.array([1.0, 0, 0])
    if face == "rear":
        return np.array([400.0, c, -a]), np.array([-1.0, 0, 0])
    if face == "roof":    # (x, drawing y) seen from above
        return np.array([a, 200.0, -c]), np.array([0, -1.0, 0])
    raise ValueError(face)


def pt(xyz, id_=None):
    s = {"type": "PointSelector", "x": round(float(xyz[0]), 2), "y": round(float(xyz[1]), 2), "z": round(float(xyz[2]), 2)}
    return {"id": id_, **s} if id_ else s


def camera(cid, scene_id, label, pos, look, hidden):
    a = {"id": cid, "type": "Annotation", "motivation": ["painting"],
         "body": {"id": cid + "/body", "type": "PerspectiveCamera", "label": label, "lookAt": pt(look)},
         "target": {"id": cid + "/target", "type": "SpecificResource",
                    "source": {"id": scene_id, "type": "Scene"}, "selector": [pt(pos)]}}
    if hidden:
        a["behavior"] = ["hidden"]
    return a


def build(model):
    src = json.load(open(os.path.join(ROOT, "annotations", model + ".json")))
    tris, mats = load_glb(os.path.join(ROOT, "docs", "models", model + ".glb"))
    formats = json.load(open(os.path.join(ROOT, "docs", "downloads", model, "formats.json")))

    mid = f"{BASE}iiif/{model}/manifest.json"
    scene = f"{BASE}iiif/{model}/scene"
    cid = src["class"]

    # The viewer has its own "fit the whole model" button, so the manifest's cameras are named by direction
    cams = [camera(f"{scene}/camera/default", scene, {"ja": ["斜め前"], "en": ["Oblique front"]},
                   src["camera_default"]["position"], src["camera_default"]["lookAt"], hidden=False)]
    pts = tris.reshape(-1, 3)
    lo, hi = pts.min(0), pts.max(0)
    ctr, dist = (lo + hi) / 2, np.linalg.norm(hi - lo) / 2 * VIEW_DIST
    for key, label, az, pol in VIEWS:
        a, p = np.radians(az), np.radians(pol)
        pos = ctr + dist * np.array([np.sin(p) * np.sin(a), np.cos(p), np.sin(p) * np.cos(a)])
        cams.append(camera(f"{scene}/camera/{key}", scene, label, pos, ctr, hidden=False))
    notes, bad = [], []
    for part in src["parts"]:
        r = raycast(tris, *aim(part["face"], part["at"]))
        if r is None:
            bad.append(f"{part['id']}: no hit")
            continue
        hit, nrm, i = r
        if mats[i] != part["expect"]:
            bad.append(f"{part['id']}: hit {mats[i]}, expected {part['expect']}")
        print(f"  {part['id']:18s} {mats[i]:8s} ({hit[0]:6.1f} {hit[1]:5.1f} {hit[2]:6.1f})")
        aid = f"{BASE}iiif/{model}/annotation/{part['id']}"
        up = np.array([0, 1.0, 0])
        cpos = hit + nrm * CAM_DIST + up * 12.0
        label = {k: [v] for k, v in part["label"].items()}
        cams.append(camera(aid + "/camera", scene, label, cpos, hit, hidden=True))
        body = [{"type": "TextualBody", "value": part["text"][lang], "language": lang, "format": "text/plain",
                 "purpose": "describing"} for lang in ("ja", "en")]
        k = KIND[part["kind"]]
        body.append({"type": "TextualBody", "value": k["ja"], "language": "ja", "purpose": "tagging",
                     "label": {"ja": ["区分"], "en": ["Category"]}})
        if part.get("wikidata"):
            body.append({"id": "http://www.wikidata.org/entity/" + part["wikidata"], "type": "Dataset",
                         "purpose": part.get("purpose", "linking")})
        notes.append({"id": aid, "type": "Annotation", "motivation": ["commenting"], "label": label,
                      "body": body,
                      "target": {"id": aid + "/target", "type": "SpecificResource",
                                 "source": {"id": scene, "type": "Scene"}, "selector": [pt(hit)]},
                      "scope": [{"id": aid + "/camera", "type": "Annotation"}]})
    if bad:
        sys.exit("parts off target:\n  " + "\n  ".join(bad))

    rendering = [{"id": f"{BASE}models/{model}.glb", "type": "Model", "format": "model/gltf-binary",
                  "label": {"ja": ["glTF（色つき）"], "en": ["glTF binary (colour)"]},
                  "fileSize": os.path.getsize(os.path.join(ROOT, "docs", "models", model + ".glb"))}]
    for f in formats["files"]:
        rendering.append({"id": f"{BASE}downloads/{model}/{f['file']}",
                          "type": "Model" if f["key"] != "obj" else "Dataset",
                          "format": f["format"], "label": f["label"], "fileSize": f["bytes"]})

    see_also = []
    for kind, key, ja, en in (("model", model, "このモデルの記述", "Description of this model"),
                              ("class", cid, "形式の記述", "Description of the class")):
        for ext, fmt in (("ttl", "text/turtle"), ("jsonld", "application/ld+json")):
            see_also.append({"id": f"{BASE}rdf/{kind}/{key}.{ext}", "type": "Dataset", "format": fmt,
                             "label": {"ja": [f"{ja}（RDF）"], "en": [f"{en} (RDF)"]}})
    # The class key is the one of docs/rdf/class/ (session A): a Wikidata QID, or tb-... for a class Wikidata lacks.
    # For a tb- class, "wikidata" in the source names the nearest item (SkyTrain marks -> the Innovia Metro family).
    wd = src.get("wikidata", cid if cid.startswith("Q") else None)
    if wd:
        same = wd == cid
        see_also.append({"id": f"https://www.wikidata.org/wiki/Special:EntityData/{wd}.jsonld", "type": "Dataset",
                         "format": "application/ld+json",
                         "label": {"ja": ["Wikidata の形式の項目" if same else "Wikidata の上位の項目"],
                                   "en": ["Wikidata item for the class" if same else "Wikidata item for the broader class"]}})

    manifest = {
        "@context": CONTEXT,
        "id": mid, "type": "Manifest",
        "label": src["label"], "summary": src["summary"], "metadata": src["metadata"],
        "provider": [PROVIDER],
        "homepage": [{"id": f"{BASE}#{model}", "type": "Text", "format": "text/html",
                      "label": {"ja": ["ギャラリーで見る"], "en": ["Open in the gallery"]}}],
        "thumbnail": [{"id": f"{BASE}thumbs/{model}.jpg", "type": "Image", "format": "image/jpeg"}],
        "seeAlso": see_also,
        "rendering": rendering,
        "items": [{
            "id": scene, "type": "Scene", "label": src["label"],
            "spatialScale": {"type": "Quantity", "quantityValue": 0.001, "unit": "m"},
            "items": [{"id": f"{scene}/page/1", "type": "AnnotationPage", "items": [
                {"id": f"{scene}/painting/model", "type": "Annotation", "motivation": ["painting"],
                 "body": {"id": f"{BASE}models/{model}.glb", "type": "Model", "format": "model/gltf-binary"},
                 "target": {"id": scene, "type": "Scene"}},
                *cams]}],
            "annotations": [{"id": f"{BASE}iiif/{model}/annotations/parts", "type": "AnnotationPage",
                             "label": {"ja": ["部位と特徴"], "en": ["Parts and features"]}, "items": notes}],
        }],
    }
    if src.get("navPlace"):
        manifest["navPlace"] = src["navPlace"]
    out = os.path.join(ROOT, "docs", "iiif", model, "manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{out}: {len(notes)} part annotations, {len(rendering)} downloads, {len(see_also)} seeAlso")


if __name__ == "__main__":
    for m in sys.argv[1:]:
        build(m)
