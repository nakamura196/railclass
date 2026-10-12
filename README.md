# railclass

3Dプリントで作る、おもちゃの列車とバスの車体の一覧と3Dビューアです。
おもちゃの車台に載る大きさで作っています。

公開ページ: https://nakamura196.github.io/railclass/

- SkyTrain（バンクーバー）Mark I / II / III / V
- ICE T（ドイツ）411・415・緑の帯・ÖBB 4011・ICE TD（DB / DSB）
- Amtrak Cascades Airo、Renfe AVE 102
- TransLink 49番の連節バス（前・後ろ）

ページは Astro で作ります。`web/` が Astro のサイトで、
`cd web && npm ci && npm run dev` で手元に開けます（`docs/` の生成物を `web/public/` に写してから起動します）。
公開は main で `zsh scripts/deploy-pages.zsh` を走らせ、組み上がったものを `gh-pages` ブランチに置きます。

`docs/` には、スクリプトが書き出すデータと実験ノートを置きます。

- 手で書く: `data/news.json`（お知らせ）、`notes/`（実験ノート）
- 書き出す（手で編集しない）:
  - `models/`・`thumbs/`・`data/models.json` — 別の作業用リポジトリで、モデルを Blender のスクリプトで作り、
    `python3 ~/git/3d/skytrain/tools/gallery.py --out <this repo>/docs` で書き出す
  - `search/` の索引 — `tools/build_search.py`
  - `rdf/` — `tools/build_rdf.py`
  - `rdf/void.ttl`・`void.jsonld` と `data/dataset.json`（データセットの説明と件数） — `tools/build_void.py`。
    `build_rdf.py`・`build_eratv_map.py`・路線の線を作り直したあとに走らせる
  - `iiif/` — `tools/build_iiif.py`

個人が趣味で作った非公式のモデルです。タカラトミー、各鉄道会社・バス会社とは関係ありません。
塗装とロゴは Wikimedia Commons の写真を参考に再現しました。
