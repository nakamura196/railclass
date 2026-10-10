"""Download the full list of vehicle types from ERATV (European Register of Authorised Types of Vehicles).

The ERA knowledge graph (graph.data.era.europa.eu) does not hold era:VehicleType instances yet
("Migration ongoing", checked 2026-10-09), so this uses the register's own "Export list" button:
open the list page to get a session cookie and the anti-forgery token, then post the search form
to /Eratv/Home/Export?exportTo=2 (XML). Two legal regimes are listed separately:
Directive (EU) 2016/797 (Is2016Directive=true) and the earlier regime (false).
Only the list is exported; detail pages are behind a CAPTCHA and are not fetched.

Usage: python3 tools/eratv_export.py [outdir]   (default data/eratv)
Writes eratv-2016.xml, eratv-pre2016.xml and eratv.tsv (both merged, with a regime column).
"""
import sys, os, re, http.cookiejar, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

BASE = "https://eratv.era.europa.eu"
out = sys.argv[1] if len(sys.argv) > 1 else "data/eratv"
os.makedirs(out, exist_ok=True)
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
opener.addheaders = [("User-Agent", "train-bodies/0.1 (nakamura.satoru@mail.u-tokyo.ac.jp)")]

page = opener.open(BASE + "/Eratv/Home/List", timeout=60).read().decode()
token = re.search(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"', page).group(1)

rows = []
for regime, flag in [("2016", "true"), ("pre2016", "false")]:
    form = urllib.parse.urlencode({"__RequestVerificationToken": token,
                                   "RegistrationRegimeModeViewModel.Is2016Directive": flag,
                                   "SelectedAuthorisationStatus": "Unknown",
                                   "PagedGrid.PageSize": "15"}).encode()
    req = urllib.request.Request(BASE + "/Eratv/Home/Export?exportTo=2", data=form,
                                 headers={"Referer": BASE + "/Eratv/Home/List"})
    body = opener.open(req, timeout=120).read()
    open(os.path.join(out, f"eratv-{regime}.xml"), "wb").write(body)
    for r in ET.fromstring(body.decode("utf-8-sig")):
        a = r.attrib
        rows.append([a["Type_ID"], a["Type_Name"].strip(), a["Authorisation_document_reference__x0028_EIN_x0029_"],
                     a["Authorisation_Status"], a["Last_Update"], regime])
    print(regime, sum(1 for x in rows if x[5] == regime), file=sys.stderr)

with open(os.path.join(out, "eratv.tsv"), "w") as f:
    f.write("type_id\ttype_name\tein\tstatus\tlast_update\tregime\n")
    for x in rows:
        f.write("\t".join(v.replace("\t", " ") for v in x) + "\n")
