#!/usr/bin/env zsh
# Point the site at https://railclass.ldas.jp/ (was https://nakamura196.github.io/railclass/).
#
# Before: main has no uncommitted work from other sessions (stops otherwise).
# Usage:  zsh scripts/setup/move-to-railclass-ldas.zsh
# Does:   rewrites the served-at URL in the Astro config, the IIIF/VoID builders,
#         the annotations and README; makes deploy-pages.zsh write web/dist/CNAME;
#         regenerates every IIIF manifest, the collection and VoID.
#         No commit, no deploy, no GitHub settings — those come after a look at the diff.
# Not:    the RDF URIs (tools/build_rdf.py, build_search) stay until w3id.org/railclass points here.
set -euo pipefail
cd "${0:A:h}/../.."

OLD="https://nakamura196.github.io/railclass/"
NEW="https://railclass.ldas.jp/"

dirty=$(git status --porcelain | grep -v -E ' (scripts/setup/|og-image.json$|docs/site/|web/scripts/sync-public.mjs$|web/src/layouts/Base.astro$)' || true)
if [[ -n $dirty ]]; then
  print "uncommitted changes on main — commit or wait first:"; print -- "$dirty" | head -20; exit 1
fi

sed -i '' -e 's|site: "https://nakamura196.github.io",|site: "https://railclass.ldas.jp",|' -e 's|base: "/railclass",|base: "/",|' web/astro.config.mjs
sed -i '' "s|$OLD|$NEW|g" tools/build_iiif.py tools/build_void.py README.md annotations/*.json
grep -q 'web/dist/CNAME' scripts/deploy-pages.zsh || perl -pi -e 's|^touch web/dist/\.nojekyll$|touch web/dist/.nojekyll\nprint railclass.ldas.jp > web/dist/CNAME   # custom domain; public/ is wiped by sync-public, so write it here|' scripts/deploy-pages.zsh

for d in docs/iiif/*/(N); do python3 tools/build_iiif.py ${d:t}; done
python3 tools/build_iiif.py --collection
python3 tools/build_void.py

print "\n--- left with the old URL (RDF URIs are expected until w3id moves):"
grep -rl "nakamura196.github.io/railclass" --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=.git . | grep -v '^./docs/rdf/\(all\|class\|model\)' || true
print "\n--- changed:"; git status --short | wc -l
