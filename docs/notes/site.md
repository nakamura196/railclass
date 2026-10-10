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
