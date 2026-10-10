# サイトの画面: トップページ・検索

担当 C（取り決めは `data-model.md` の「位置付けと並行作業の取り決め」）。トップページのデザインは
2026-10-09 から別セッション（D、worktree `train-bodies.worktrees/top`）が受け持ち、判断はこのノートの「トップページ」の節に書く。

## 2026-10-09

### 作り方の方針（本人と決めた）

- Python は JSON だけを出す。HTML・JS・CSS は `docs/` に置いた静的ファイルで、開いたときに JSON を読み込んで描く。
  見た目を直すのに Python を走らせ直さずに済み、HTML・JS・CSS が train-bodies の git に入る（履歴が残る）。
  欠点は JS が無いと中身が出ないこと。今のギャラリーも同じなので受け入れた。
- 共通の見た目（色の変数・ヘッダ・フッタ）は D が `docs/assets/site.css` に出す。検索ページの CSS は色の変数を
  `:where(:root)`（優先度 0）で持ち、`site.css` があればそちらが必ず勝つようにした。読み込み順に頼らない。

### 検索ページ（`docs/search/`）

- 対象は Wikidata の形式 14,318（日本を除く。`data/classes.tsv` の source=wikidata）に、A の RDF だけにある形式 6
  （SkyTrain Mark I・II・III・V、Airo、XD60）を足した **14,324 件**。ERATV 由来は再利用条件が分かるまで入れない。
- 絞り込みの項目は A の `docs/rdf/facets.json`（10 項目）をそのまま使い、手で書き並べない。
  値は 2 つの出どころを重ねる:
  1. **Wikidata から一括で**: `tools/fetch_facets.py` が facets.json の項目ごとに 1 回ずつ問い合わせる
     （Wikidata の属性を述語にしている項目だけ。属性を足せば自動で取りに行く）。
  2. **A の RDF（`docs/rdf/all.jsonld`）で上書き**: RDF にある形式（今は 13）は RDF の値を使う。手入力の値
     （SkyTrain の国・製造者など）、`inherit` の項目は上位の形式（skos:broader）から受け継ぐ、3D モデルの有無。
  A の RDF が全形式に広がれば 1 は要らなくなる。それまでの橋渡し。
- 実測（この日、Wikidata Query Service）: 値のある組の数は 種類 16,566・国 9,330・運行者 19,008・製造者 16,336・
  軌間 10,641・電化方式 2,260・軸配置 7,726・最高速度 3,922・営業開始年 4,883・写真（P18）12,362。
  国の分かる形式は全体の約半分なので、絞り込みに「（値なし）」も選べるようにした。
- 索引 `docs/search/index.json` は列ごとの配列（値は番号で引く）。1.86 MB、gzip で 530 KB。
  GitHub Pages は圧縮して送るので、最初の読み込みは 0.5 MB 程度。件数が 10 倍になったら分割を考える。
- トップページの数字は `docs/search/stats.json`（形式・3D モデル・国の数）。索引と同じ処理で作るので手で書かない。
- 絞り込みの件数は「その項目以外の条件を満たすもの」で数える（同じ項目の中は「または」、項目どうしは「かつ」）。
  1 回のなめで、どの条件にも外れない形式は全項目に、1 つだけ外れる形式はその項目にだけ数える。1.4 万件で体感の遅れは無い。
- 名前の検索: 英字は語の頭から合わせる。最初は部分一致にしたが「ice」で Service・Office・Automotrice まで当たった（28 件 → 15 件）。
  漢字・かなを含む語は部分一致のまま（語の切れ目が無いため）。空白を詰めた形でも引ける（「icet」で ICE T）。
- 並べ方は「おすすめ（3D あり → 写真あり → 名前）」「名前」と、数値の項目ごとの大きい順・小さい順。数値の項目も facets.json から作る。
- 格子と一覧の切り替え、1 ページの件数（24・48・96）、ページ送り。条件はすべて URL に残す（`?country=Q183&has3d=1&view=list`）。
- 結果の行き先: RDF のある形式は A の `docs/rdf/class/<id>.html`、それ以外は Wikidata の項目。形式の詳細ページを
  C で別に作るかは、A の .html を見てから決める。
- 写真は Wikidata の P18 を Commons の Special:FilePath（幅 330）で直接表示している。著作者表示はカードに出していない。
  クリック先の Wikidata・Commons で確かめられる形。公開前に、作者・ライセンスをカードかツールチップに出すか決める（未決）。

確かめていないこと:
- 写真の読み込みは Commons 側の速度に左右される。大量に開いたときの負荷・制限は見ていない。
- 「種類」（P279）の値は 1,000 を超え、英語のままの値も多い。上位の種類にまとめる（階層で畳む）かは未決。

### トップページ（D、worktree `train-bodies.worktrees/top`、ブランチ `top`）

手本は ArchiveBase のトップ（https://ab.ldas.jp/）。2026-10-09 に読んだ並び: ヘッダ（ライブラリ・API・ツール・English）、
サイト名と一言、公開中のサイトのカード（点数つき）、お知らせ 5 件、「ArchiveBase について」、フッタ。
ArchiveBase のトップには検索窓と収録数の欄が無い。ここでは TODO のとおり両方を足した（形式を探すのが主な入口なので）。

ファイルの分け方:

- `index.html`（トップ）・`view.html`（一覧＋3D のビューア）・`assets/` は手で書く静的ファイル。
  `data/models.json` だけを `~/git/3d/skytrain/tools/gallery.py` が書く（id・群・名前・一言・寸法・Wikidata の形式 ID・追加日・KB）。
  `gallery_template.html` は廃止し、中身を `view.html`・`assets/view.css`・`assets/view.js` に移した。
- `data/news.json` は手で書く。TODO にあった `content/news.yaml` はやめた。`docs/` の外に元データを置くと、
  JSON に変える処理がもう 1 つ要るため。1 件は `date`・`title`・`body`（任意）・`url`（任意）。
- 共通の見た目は `assets/site.css`（色の変数・地の文字・ヘッダ・フッタ・カッティングマットの `.mat`・「準備中」の印 `.soon`）。
  ヘッダとフッタの中身は `assets/site.js` が 1 か所で描く。ページには空の
  `<header class="site-header" data-base="../" data-current="search"></header>` と `<footer class="site-footer" data-base="../"></footer>` を置き、
  `<script src="../assets/site.js" defer></script>` を読む。`data-base` はそのページから `docs/` への道筋、`data-current` はナビのどれを太くするか。
  → 検索ページ（C）は今のところ自前のヘッダ。揃えるなら上の 2 行に置き換える。
- `.gitignore` の `data/` が `docs/data/` まで除外していたので、`/data/`（ルートだけ）に直した。ERATV 由来のルートの `data/` は今までどおり入らない。

判断:

- ヘッダ: 探す（`search/`）・3D で見る（`view.html`）・地図・データ（トップの `#data`）・このサイトについて（`#about`）・English。
  地図と English はまだ無いので、リンクにせず「準備中」の印を付けた。隠すより、何を作る予定かが見えるほうがよいと考えた。
  TODO に無い「3D で見る」を足した。ビューアへの入口がヘッダに無いと、トップの新着カードからしか行けないため。
- ヒーロー: いちばん新しいモデルを回して見せる。ただしバスは飛ばす（鉄道車両のサイトなので）。今は AVE 102。
  検索窓は `search/?q=...` に送る（C の `search.js` が `q` を読むことを確かめた）。
- 数字: `search/stats.json` の `classes`・`models`・`countries` をそのまま出す。読めないときは「—」のまま。手で書いた数字は置かない。
  手元で C の `stats.json` を借りて表示を確かめた時点の値は 14,324・14・159。
- できること: 5 枚のカード。まだ無いもの（地図・ダウンロード）は枠を点線にして「準備中」。
- 新着モデル: `added` の新しい順に 6 件。同じ日のものは `models.json` で後ろにあるほうを新しいとみなす。
- 追加日: SkyTrain 4 両は 2026-10-08、ほかは 2026-10-09（skytrain の `models/<name>.py` を最初にコミットした日）。
- Wikidata の形式 ID: SkyTrain は Mark ごとの項目が無いので、4 両とも Innovia Metro の家族（Q4940487）を入れた。
  ICE T の緑の帯は 411 の編成なので Q115612330、ICE TD は DB・DSB とも Q659660、49 番バスは前後とも XD60（Q137921671）。
- 古いリンク: `index.html#mk1` のように、トップに無い id の `#` が付いていたら `view.html#mk1` へ送る（`location.replace`）。
  トップの節の id（`features`・`new`・`news`・`about`・`data`）はモデルの id と重ならない。
- フッタ: 作者「中村 覚（東京大学）」、非公式の注記（タカラトミー・各社の商標）、形式の情報は Wikidata（CC0）。
  **3D モデルと画像のライセンスは未定なので「整備中」と書いた。** LOD チャレンジはライセンスの明記が要るので、決める必要がある。
- 確かめたこと: 幅 1568px と 500px で表示し、横にはみ出さない（`scrollWidth` 485 ≤ 幅 500）。`#icet_oebb` で開くとビューアに移る。

残り:

- ライセンスを決めてフッタと「このサイトについて」に書く
- 地図（B の navPlace）、データ（A の RDF、B の IIIF・ダウンロード）が出たら、「準備中」を外してリンクにする
- English 版

### Astro に移す（2026-10-09、本人と決めた）

上の「Python は JSON だけ、HTML・JS・CSS は `docs/` の静的ファイル」を一段進め、HTML は Astro で作る。
Python が JSON・RDF・IIIF を出し、Astro がそれを読んでページを作る、という分け方は変えない。

移す理由:

- 共通のヘッダ・フッタは、今は `assets/site.js` が開いたあとに差し込んでいる。表示が一瞬遅れ、
  JS を動かさない検索エンジンや LOD の収集ツールからは見えない。Astro ならレイアウト 1 つから全ページに組み込んだ HTML が出る。
- 形式の詳細ページは `tools/build_rdf.py` が HTML を直接書いている（2026-10-09 時点で 13 ページ、ヘッダ・フッタなし）。
  共通の見た目を JS と Python の 2 か所で持つことになる。世界の形式を載せていくと数百〜数千ページになるので、
  型を 1 か所で決めてデータから量産する仕組みが要る。
- 検索ページにヘッダ・フッタを `site.js` で入れる作業は、移行で片付くのでやらない。

引き換えに増えるもの: ビルドが要る（GitHub Actions でビルドして Pages に出す。公開リポジトリなので無料）、
npm の依存（`package-lock.json` をコミット、Dependabot の cooldown、Actions の SHA 固定を同時に入れる）、
A・B・C の担当ファイルの分け方の見直し。

時期: 動いている枝（site のクレジット取得、iiif）を main に入れてから、別セッションで行う。

移すときに守ること:

- 公開中の URL を変えない。`index.html`・`view.html#<model>`・`search/?q=...`・`rdf/class/<id>.html`・
  `rdf/` と `iiif/` の ttl・jsonld・manifest・`models/`・`thumbs/`。生成物は Astro の `public/` に置いて加工せず配る
- 最初は今と同じ見た目・同じ URL の 4 種類（トップ・ビューア・検索・形式の詳細）だけ。新しい画面は足さない
- 移行と同時に、次の 2 つを入れる（本人の指示、2026-10-09）:
  - 多言語（日本語・英語）。日本語は今の URL のまま、英語は `/en/` の下に同じ構成で置く。
    表示の文言は言語ごとのファイル 1 か所にまとめる。形式名などのデータは、索引にある `ja`・`en` を言語で選ぶ
  - ライト・ダークの切り替え。既定は OS の設定に従い（今の CSS は `prefers-color-scheme` で OS にだけ従っている）、
    ヘッダのボタンで「ライト・ダーク・OS に従う」を選べるようにする。選んだものはブラウザに覚えさせる。
    ページを開いた瞬間に色がちらつかないよう、色の決定は HTML の頭で行う
- ノート `docs/notes/` の置き場所は変えない（Pages の配信元が `docs/` から Actions に移るので、配信からは外れる）

#### 移行の一段目（2026-10-09、worktree `train-bodies.worktrees/astro`、ブランチ `astro`）

site と iiif が main に入る前なので、検索・形式の詳細・IIIF には触れず、雛形・レイアウト・日英・ライトとダーク・Actions・トップとビューアまでを行った。

- 置き場所は `web/`（Astro 7.3.5。公開から 2 週間たった版を選んだ。`package-lock.json` をコミット、`npm audit` 0 件）。
  Python の出力は `docs/` のまま。`web/scripts/sync-public.mjs` がビルドの前に `docs/` の
  `data`・`models`・`thumbs`・`rdf`・`search`・`iiif`・`downloads`（あるものだけ）を `web/public/` に写し、加工せず配る。
  `public/` は git に入れない。手書きの `index.html`・`view.html`・`assets/`・`notes/` は写さない。
- URL: `build.format: "preserve"` で `view.astro` → `view.html` になり、今の URL のまま出る。英語は `/en/`・`/en/view.html`。
  まだ Astro で作っていない検索は、英語のページからも日本語の `search/` へ送る。
- トップとビューアは、数字・新着・お知らせ・一覧をビルドの時に HTML に書き込むようにした。
  JS が無くても中身が出る（移す理由の 1 つ）。JS はビューアのモデルの切り替えと色のボタンだけ。
  トップの `top.js` に当たるものは無くなった。
- 文言は `web/src/i18n/ja.json`・`en.json`。モデルの英語の名前と説明は `models.json` に無いので、
  `web/src/i18n/models.en.json` に仮に置いた（無い項目は日本語のまま出る）。`models.json` を書く `skytrain/tools/gallery.py` は
  別の作業が未コミットのまま動いていたので触らなかった。gallery.py が `en` を出すようになったら、この仮置きは消す。
  お知らせは `news.json` の各件に `en: {title, body}` を足す形にした（無ければ日本語）。
- 色: `<head>` の中の短いスクリプトが `localStorage` の選択を読んで `<html data-theme>` を付けてから描くので、開いた瞬間のちらつきは無い。
  ボタンは 1 つで「OS に従う → ライト → ダーク」と巡る。`site.css` はもともと `data-theme` を受ける形だったので、変数はそのまま使えた。
  ライトを選んだのに OS がダークのとき、入力欄などがダークの見た目にならないよう `:root` に `color-scheme: light` を足した。
- Actions（`.github/workflows/pages.yml`）: main への push と PR で `npm ci`・`npm audit`・ビルドまで行う。配る段は、
  リポジトリの変数 `PAGES_SOURCE=actions` が無い間は動かない。今は Pages の配信元が `docs/`（API で `legacy /docs` を確認）なので、
  配ろうとすると失敗するため。切り替えは「Settings → Pages → Source を GitHub Actions」と「変数を足す」を同時に行う。
  Actions はすべて SHA で固定。Dependabot（npm は `web/`、Actions も、cooldown つき）を足した。
- 確かめたこと（手元の `astro preview`）: 4 ページが出る。色のボタンで 3 段が巡り、選択が再読み込み後も残る（ダークを覚えさせて
  英語のビューアを開くとダークのまま）。`index.html#icet_oebb` で開くと `view.html#icet_oebb` に移り、ÖBB 4011 が選ばれる。
  幅 390px で 4 ページとも横にはみ出さない。

確かめていないこと:
- Actions の実行（push していない）。
- `docs/` の古い `index.html`・`view.html`・`assets/` は、配信元を切り替えるまで公開に使われるので残した。切り替えたら消す。

#### 2026-10-09 追記: main の取り込みと push

- 一段目をコミットし、main（iiif の取り込み cccfb8d と色の絞り込み 298ea8d を含む）をマージした。衝突なし。
  `npm run build` で 4 ページが出て、`dist/iiif/` に 14 形式分の Manifest が写ることを確かめた。
- ブランチ `astro` を push した。main には入れていない（Actions は main への push と PR でしか動かない）。
- site の枝（写真の出典・形式のまとまり 47967bb）はまだ main に入っていないので、検索と形式の詳細ページの移行は待つ。

#### 2026-10-09 移行の二段目: 検索と形式の詳細、手元でビルドして gh-pages から配る

- site の枝は main に入る前だったが、本人の了承を得て、その時点の site（b6f8f3b）を astro に直接マージした。
  `tools/build_search.py` が衝突した。色の絞り込みを main と site が別々に書いていたためで、main の書き方（形式ごとに `livery` を集める）を残し、
  site 側の `liveries` を消した。索引を作り直し、色の値を持つ形式は 12 件。写真の出典は、別セッションの取得の途中の分まで入っている（10,402 枚中 8,633 枚）。
- 検索: `web/src/components/SearchPage.astro` と `web/src/scripts/search.js`（`docs/search/search.js` を移したもの）。
  日本語の文言は `ja.json`・`en.json` の `search.js` に出した。名前・値の名前・項目名は、ページの言語を先に、無ければもう一方を出す。
  英語の検索は `/en/search/`。結果から開く形式のページも、その言語のもの（`/en/rdf/class/<id>.html`）。
- 形式の詳細: `web/src/pages/rdf/class/[id].astro`。`docs/rdf/class/*.jsonld` 1 つにつき 1 ページ（今は 17）。
  表示する値は検索の索引から取る。索引には両言語の値の名前、上位の形式から受け継いだ値、模型の塗装の色が既に入っているので、
  検索とページで値が食い違わない。RDF からは、Wikidata・上位と下位の形式・3D モデルへのつながりと、Turtle の本文を取る。
  値を押すと、その値で絞った検索に移る（ICE T の「高速列車」→ 60 件）。
- `sync-public.mjs` は、Astro が作るようになった `search/index.html`・`search.js`・`search.css`・`rdf/class/*.html` を写さない。
  `rdf/model/*.html` はまだ Python が書いたものを配る。
- **配り方を変えた。** 本人から「Actions の残りが 0 なので、手元でビルドしてデプロイする」と指示があった。
  ブランチから配る Pages（「pages build and deployment」）は今も成功しているので、`scripts/deploy-pages.zsh` で `web/dist` を
  `gh-pages` ブランチに 1 コミットで強制 push し、Pages の配信元を `gh-pages` の `/` に切り替える。
  履歴を残さないのは、ビルドの出力で、GLB が積み重なるとリポジトリが太るため。
  `downloads/`（git に入れていない、置き場所は未定）は出さない。`_astro/` を配るため `.nojekyll` を置く。
  `pages.yml` は手で動かすときだけにした（main への push で動くと、残りが 0 のため失敗する）。
- 確かめたこと（手元の `astro preview`）: 32 ページが出る。英語の検索で「ice」が 14 件、結果が `/en/rdf/class/` に向く。
  ICE T のページに 7 項目・下位の形式 3 つ・模型 1 つ・写真と出典が出る。

確かめていないこと:
- 幅 390px での検索と形式のページ。
- `docs/` の古い `index.html`・`view.html`・`assets/`・`search/index.html` などは、配信元を切り替えたあとは使われない。
  別のセッションがまだ `docs/search/search.js` を触っている可能性があるので、今回は消さない。
