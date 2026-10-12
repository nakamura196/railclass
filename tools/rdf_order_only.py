"""Put back the docs/rdf .jsonld files whose only change since HEAD is the order (same graph).

tools/build_rdf.py rewrites every .jsonld, and rdflib's JSON-LD output does not keep a stable order, so one new model
leaves hundreds of files changed with the same triples. This compares each changed .jsonld with its HEAD version as
graphs (rdflib isomorphic) and runs `git checkout` on those that are equal, so the commit shows only real changes.
Files with a real change, and new files, are left as they are and listed.

Usage: python3 tools/rdf_order_only.py            (list, then put back)
       python3 tools/rdf_order_only.py --dry-run  (list only)
"""
import os, subprocess, sys
from rdflib import Graph
from rdflib.compare import isomorphic

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*a, **kw):
    return subprocess.run(["git", "-C", HERE, *a], check=True, capture_output=True, **kw).stdout


def main():
    changed = [f for f in git("diff", "--name-only", "--", "docs/rdf").decode().split() if f.endswith(".jsonld")]
    same, real = [], []
    for f in changed:
        old = Graph().parse(data=git("show", "HEAD:" + f), format="json-ld")
        new = Graph().parse(os.path.join(HERE, f), format="json-ld")
        (same if isomorphic(old, new) else real).append(f)
    print(f"{len(changed)} changed .jsonld: {len(same)} order only, {len(real)} with a real change")
    for f in real:
        print("  real:", f)
    if same and "--dry-run" not in sys.argv:
        for i in range(0, len(same), 200):
            git("checkout", "--", *same[i:i + 200])
        print(f"put back {len(same)} files")


if __name__ == "__main__":
    main()
