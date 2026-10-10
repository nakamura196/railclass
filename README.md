# train-bodies

3Dプリントで作る、おもちゃの列車とバスの車体の一覧と3Dビューアです。
プラレール（タカラトミー）の車台に載る大きさで作っています。

公開ページ: https://nakamura196.github.io/train-bodies/

- SkyTrain（バンクーバー）Mark I / II / III / V
- ICE T（ドイツ）411・415・緑の帯・ÖBB 4011・ICE TD（DB / DSB）
- Amtrak Cascades Airo、Renfe AVE 102
- TransLink 49番の連節バス（前・後ろ）

`docs/` が公開されるページです。手で書くものと、スクリプトが書き出すものが混ざっています。

- 手で書く: `index.html`（トップ）、`view.html`（一覧と 3D ビューア）、`assets/`（CSS・JS。`site.css` は全ページ共通の見た目）、
  `data/news.json`（お知らせ）、`notes/`（実験ノート）
- 書き出す（手で編集しない）:
  - `models/`・`thumbs/`・`data/models.json` — 別の作業用リポジトリで、モデルを Blender のスクリプトで作り、
    `python3 ~/git/3d/skytrain/tools/gallery.py --out <this repo>/docs` で書き出す
  - `search/` の索引 — `tools/build_search.py`
  - `rdf/` — `tools/build_rdf.py`

ページは JSON を読み込んで描くので、手元で見るときは `python3 -m http.server -d docs 8000` で開きます（`file://` では読めません）。

個人が趣味で作った非公式のモデルです。タカラトミー、各鉄道会社・バス会社とは関係ありません。
塗装とロゴは Wikimedia Commons の写真を参考に再現しました。
