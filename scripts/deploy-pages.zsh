#!/usr/bin/env zsh
# Builds the site locally and publishes it to the gh-pages branch, which GitHub Pages serves
# (Settings → Pages → Deploy from a branch: gh-pages, /). Used instead of the Actions workflow
# while the account has no Actions minutes; publishing from a branch does not use them.
#
# Prerequisites: run from the main checkout with main up to date and docs/ regenerated; npm ci done in web/.
# Usage: zsh scripts/deploy-pages.zsh
# What it does: npm run build in web/, checks the result (npm test; nothing is published when it fails), leaves the 3D files (GLB and the download
# files) out of the Pages build — since 2026-10-14 they are served only by the login-protected Worker railclass-models.ldas.jp
# (nakamura196/iiif-auth-cf-access; deploy them there with its scripts/deploy.zsh);
# npm test fails when a model's files are missing),
# adds .nojekyll (so _astro/ is served), and force-pushes web/dist as one commit to origin/gh-pages.
# The branch keeps no history: it is a build output, and the GLBs would otherwise pile up in the repository.
set -euo pipefail

root=${0:A:h:h}
cd "$root"
branch=$(git rev-parse --abbrev-ref HEAD)
if [[ $branch != main ]]; then print -u2 "deploy-pages: run on main (now on $branch)"; exit 1; fi
rev=$(git rev-parse --short HEAD)
remote=$(git remote get-url origin)

(cd web && npm run build && npm test)   # npm test: the built pages against the data (web/scripts/check-dist.mjs); stops here on a failure
touch web/dist/.nojekyll
rm -rf web/dist/downloads web/dist/models   # not public: on the auth Worker; sync-public still copies them for local previews
if find web/dist -name "*.glb" -o -name "*.usdz" -o -name "*.stl" | grep -q .; then print -u2 "deploy-pages: 3D files left in web/dist"; exit 1; fi
print railclass.ldas.jp > web/dist/CNAME   # custom domain; public/ is wiped by sync-public, so write it here

tmp=$(mktemp -d)
cp -R web/dist/. "$tmp"
cd "$tmp"
git init -q -b gh-pages
git add -A
git -c user.name="$(git -C "$root" config user.name)" -c user.email="$(git -C "$root" config user.email)" commit -q -m "Build of main $rev"
git push -q --force "$remote" gh-pages
cd "$root"
rm -rf "$tmp"
print "deploy-pages: pushed the build of $rev to gh-pages ($(du -sh web/dist | cut -f1))"
