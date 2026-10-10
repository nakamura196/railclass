# TODO: train-bodies を「世界の鉄道車両の形式」のデータベースにする

2026-10-09 作成。取り決め（URI・担当のファイル）は `data-model.md` の「位置付けと並行作業の取り決め」。
各セッションは自分の節だけを書き換える（済んだら `[x]` と日付・コミット）。他の節は読むだけ。

## A. RDF（worktree `train-bodies.worktrees/rdf`）

- [ ] `docs/rdf/facets.json` を出す（絞り込みの項目: URI・日本語と英語の名前・値の型）。**最初にやる。C が待っている**
- [ ] 語彙を決める（Wikidata の属性・ERA の語彙・schema.org・SKOS のどれを使うか。理由をノートに）
- [ ] 形式の RDF `docs/rdf/class/<cid>.ttl`・`.jsonld`（まずは 3D モデルのある形式、次に Wikidata の全形式）
- [ ] モデルの RDF `docs/rdf/model/<model-id>.ttl`・`.jsonld`（形式・塗装・作者・ライセンス・IIIF Manifest への逆リンク）
- [ ] 全件をまとめたファイル（`docs/rdf/all.ttl` など）を一括ダウンロード用に
- [ ] ERATV と Wikidata の照合を改善（「ICE T BR 411 ETCS BL3」→ Q115612330 のように、版の付いた名前を形式に結ぶ。skos:narrowMatch）
- [ ] ERATV の再利用条件を確かめる（ERA の Copyright Notice）。結果で `docs/` に入れるか決める
- [ ] 「RDF にする利点」をノートで実測で示す（例: 典拠の更新がそのまま反映される、外部と結べる件数）

## B. IIIF v4・注釈・ダウンロード（worktree `train-bodies.worktrees/iiif`）

- [ ] IIIF Presentation 4.0 の今の状態を確かめる（正式版か草案か、Scene・3D・navPlace・注釈の書き方、対応ビューア）
- [ ] ICE T 411 の Manifest 1 つで試す: Scene に GLB、`seeAlso` で RDF、`rendering` でダウンロード、`navPlace` で運行地域
- [ ] 部位と特徴の注釈の元データ `annotations/<model-id>.yaml`（部位の名前・説明・3D 上の位置）。ICE T 411 から
- [ ] 14 モデル全部の Manifest と、全体の Collection `docs/iiif/collection.json`
- [ ] ダウンロード形式 `docs/downloads/<model-id>/`（GLB・STL・OBJ・3MF・STEP など）と `~/git/3d/skytrain/tools/export_formats.py`。
      STEP は面を貼っただけで、CAD で寸法を直せる立体ではないことを画面とノートに書く
- [ ] 「IIIF v4 の実例」としての位置付けをノート `docs/notes/iiif.md` に（先行例の有無も）

## C. トップページ・検索（worktree `train-bodies.worktrees/site`）

トップページの構成は ArchiveBase（https://ab.ldas.jp/）を手本にする。

- [x] ヘッダ: 探す・地図・データ（RDF / IIIF / ダウンロード）・このサイトについて・English
- [x] ヒーロー: サイト名と一言、3D モデルを 1 つ回して見せる、検索窓
- [x] 数字: 形式の数・3D モデルの数・国の数（RDF / 索引から生成し、手で書かない）
- [x] できること: 形式を探す・地図から探す・3D で見る（部位の説明つき）・ダウンロード・データとして使う（RDF・IIIF）
- [x] 新着モデル: カードで数件
- [x] お知らせ: 日付つきの一覧。元データ `content/news.yaml`（初回は公開・LOD チャレンジ向けの整備開始など）
- [x] このサイトについて・フッタ: 作者（中村 覚（東京大学））、ライセンス、非公式の注記（TOMY・DB・TransLink などの商標）
  （上の 7 項目は 2026-10-09 に D がブランチ `top` で。地図・English・ライセンスは未。site.md の「トップページ」）
- [x] 検索ページ: 絞り込み（項目は `docs/rdf/facets.json` から読む）、ページ送り、格子と一覧の切り替え、URL に条件を残す（2026-10-09、ブランチ site）
- [ ] 地図から探す: navPlace（B の Manifest）を読んで地図に出す
- [ ] 形式の詳細ページ（RDF の中身を人が読める形で。3D・注釈・ダウンロードへのリンク）
- [x] 画面の判断をノート `docs/notes/site.md` に（2026-10-09、続けて書き足す）
- トップページの項目（ヘッダ〜フッタ）は 2026-10-09 から別セッション D（worktree `top`）が担当。main へ取り込み済み（16d0db2）

## サイトを Astro に移す — 方針は `site.md` の「Astro に移す」

- [x] 前提: site（写真のクレジット・種類の大分類）と iiif の枝を main に入れる（site は 2026-10-09 に b6f8f3b の時点を astro 経由で）
- [x] Astro の雛形、レイアウト 1 つ（ヘッダ・フッタ）、GitHub Actions で Pages に出す（配る段は配信元の切り替えまで止めてある）
- [x] トップ・ビューア・検索・形式の詳細の 4 種類を移す（2026-10-09。モデルのページ `rdf/model/*.html` はまだ Python の HTML）
- [ ] `build_rdf.py` から HTML を書く部分を外し、形式の詳細ページは Astro が JSON から作る
- [ ] 多言語（日本語は今の URL、英語は `/en/`）（4 種類とも済み。モデルの英語は `web/src/i18n/models.en.json` に仮置き → gallery.py が出すようにする）
- [x] ライト・ダーク・OS に従う の切り替え（ヘッダのボタン、選択を覚える、開いた瞬間のちらつきなし）
- [x] `assets/site.js` のヘッダ・フッタ差し込みを消す（1462dbb で `docs/assets/` ごと削除）
- [x] Dependabot（cooldown つき）、Actions の SHA 固定、`npm audit`
- [x] Pages の配信元を切り替える（2026-10-09、Actions の残りが 0 のため `gh-pages` ブランチに。`zsh scripts/deploy-pages.zsh` を main で走らせて配る）
- [x] `docs/` の古い `index.html`・`view.html`・`assets/`・`search/index.html`・`search.js`・`search.css` を消す（2026-10-09）
- [ ] Actions の残りが戻ったら `pages.yml` の push の起動を戻し、配信元を Actions にするか決める

## 路線（地図の線）— 担当はこのセッション。方針は `data-model.md` の「路線の線データ」

- [x] 形式 → 路線の Wikidata ID の対応表を作る（Wikidata の P3438 を逆にたどる。足りない分は GTFS・Wikipedia から手で、出典つき）
      2026-10-09 23:45: 置き場所は `tools/class_lines.tsv`（git に入れる。列は class・line・lineLabel・status・source_url・source_section・note）。まだ作っていない。
      Wikidata だけでは 12 形式中 4 形式しか路線に届かない（`tools/queries/wd-class-lines.rq`、AVE 102・Frecciarossa 1000・Innovia Metro・S series 経由で Line 3）。
      1 段上の分類（P279）経由は「電車」「バス」などの広い分類を通る無関係な路線ばかりなので使わない。Q847141 は路線でなく運行会社なので除く。
      残りは Wikipedia の各形式の記事を出典に手で補う（サブエージェントに調べさせ中。結果が来たら表にする。来ていなければ調べ直す）
      2026-10-10 0:05 作った（未コミット）: 50 行・42 路線・12 形式。Wikipedia の記事（en/de/it）を出典に、Wikidata の P3438 の 4 件（Kelana Jaya 延伸・Córdoba–Málaga・Milan–Paris Frecciarossa ほか）を足した。
      ID はすべて Wikidata の API で照合済み。記事が運行区間（例: München–Berlin）しか書いていない所は路線を推定し、note に INFERRED と書いた（17 行）。
      「Expo Line」は英語版の記事名だと LA の路線（Q5421492）に当たる。SkyTrain は Q736619。
      ヴァンデ・バーラトと Milan–Paris は線路でなく列車の運行（サービス）の項目なので、OSM の線は無いはず。
      49 番バスは Wikidata に項目が無く、line は空（TransLink の GTFS から取るなら別の道）
- [x] 対応表を RDF に入れる（A の形式の RDF に、路線へのリンクとして）
      2026-10-10: `tb:usedOn` と `tb:LineUse`（状態・終わった年・出典）。49 件・42 路線。中身は data-model.md の 2026-10-10。未コミット
- [x] 対象の路線のうち、OSM の route relation に `wikidata=` 札が付いている数を数えた（2026-10-10 0:35）: 42 路線中 31。
      札が無い 11: サービスの項目 4（ヴァンデ・バーラト 2・Milan–Paris・Kelana Jaya 延伸）、Line 3 Scarborough（廃止）、オーストリア・ドイツの在来線 6（Q669665 Q694717 Q5873973 Q477258 Q100940666 Q802606）。
      在来線は OSM 側で札が別の関係（route=tracks など）に付いているか、Wikidata 側が別項目の可能性。Overpass は 429/504 が多く、`--only` で 1 路線ずつ 15 秒おきに流すと通った
      道具は `tools/osm_lines.py`（未コミット）。`--count` で数えるだけ、無しで線も取り出して `data/lines/<Q>.geojson`（git の管理外）に書く。
      2026-10-09 23:40 試運転: Expo Line・Millennium Line・上海リニアの 3 路線とも札があり、線が取れた（点を減らして 1 路線 2〜3 KB）
- [x] OSM の線を地図に出す方法を決める（表示のたびに Overpass か、事前に切り出すか。後者ならライセンスの扱いも）
      2026-10-10 本人の決定: 事前に切り出し、RDF とは別の表示用の層（例 `lines/<Q>.geojson`、ODbL と「© OpenStreetMap contributors」を明記）として公開する
- [ ] 形式のページに地図を出す（上が決まってから）
      2026-10-10: ページ側は作った（未コミット: ClassPage.astro・lib/data.ts の classLines・scripts/line-map.ts・class.css・i18n・sync-public.mjs に lines/）。
      線の切り出しは Overpass の 504 で難航中（1 路線ずつやり直し、失敗は飛ばして続きから取れるようにした）。`python3 -u tools/osm_lines.py --api https://maps.mail.ru/osm/tools/overpass/api/interpreter`（記録は data/osm_lines.log）。出力は docs/lines/
- [ ] 線の形は train-bodies のデータに入れない（ODbL に縛られないため）。これを崩す案が出たら本人に確かめる

## 写真の保存と公開待ちの変更（2026-10-09 夜）

2026-10-09 23:40 本人の指示で、train-bodies の作業はこのあと 1 つのセッションに一本化した。

写真の保存（`tools/fetch_photos.py`）が終わるまで、コミットも公開もしない。終わったら本人に確かめてから進める。

- [x] 写真の保存が終わったか確かめる（2026-10-10 1:00 完了: 12,194 枚・214.5 MB・失敗 0。索引を作り直し bc80dd3 でコミット・push・公開。2026-10-09 23:43 で 6,762 / 12,194 枚、1 分に約 65 枚、1:10 ごろ終わる見込み。
      2026-10-09 23:46 会話から切り離して動かし直した（PID 88172、記録は `data/photos_fetch.log`）。/clear しても止まらない。
      動いているかは `pgrep -fl tools/fetch_photos.py`。止まっていたら `python3 tools/fetch_photos.py` を流し直せば続きから取る。
      記録ファイルは空のままなので、`ls data/photos | wc -l` で数える。`data/` は git の管理外）
- [x] 未コミットの変更を分けてコミットする（2026-10-09 23:40: (1) のコードと記録 d736345、(2) 00e5c17、色 ef3aa31。索引 `docs/search/index.json` は写真の保存が終わってから）
      (1) 写真・検索: `tools/fetch_photos.py`・`tools/build_search.py`・`docs/search/index.json`・`web/scripts/sync-public.mjs`・`web/src/scripts/search.js`・検索と形式のページ
      (2) 文言と台座なし: 「プラレール」を外した注釈 `annotations/*.json`・`web/src/i18n/*.json`・README、作者の行の削除、台座を外して書き出し直した `docs/models/*.glb`・`docs/data/models.json`
- [x] push は本人の指示で 2026-10-09 23:40 に済み（origin/main = ef3aa31）。公開はまだ: `zsh scripts/deploy-pages.zsh` を main で走らせて公開する（未 push の 1462dbb・322eb5c も一緒に出る）
- [x] 公開後に `/`・`/view.html`・`/search/`・`/en/`・形式のページ 1 つが開くか確かめる（2026-10-10 1:05 bc80dd3 の公開で、いずれも 200。索引は 14,325 形式、写真も配信されている）
- [x] (2) には次も含める: `docs/thumbs/*.jpg`、作り直した `docs/iiif/*/manifest.json`（14 件）、`web/src/components/SiteFooter.astro`（作者の行）。
      注釈は「爪の穴より上」を「印刷用の版で開ける爪の穴より上」に、ICE TD の屋根の穴の説明も印刷用の版の話に直してある
- [x] skytrain 側も別にコミットした（299111d 台座なし、e37b7c3 印刷の道具とノート。skytrain は手元だけで push しない）: `lib.py`（`NO_MOUNT` でネジ受けの柱・屋根の切り欠き・後ろの爪穴を省く）・`build.py`（`--no-mount`、出力は `out/<モデル>/nomount/`）・
      `tools/gallery.py` と `tools/export_formats.py`（どちらも `--no-mount`。2 つとも未追跡のファイル）。旗なしは今までどおり穴あり（印刷用）
- [ ] 本人に確かめる: フッターの「© 2026 中村 覚」と、IIIF の提供者（`tools/build_iiif.py` の PROVIDER）「中村 覚（東京大学）」を残すか
      2026-10-10 本人の指示「このサイトでは東京大学をあまり出さない」: IIIF の提供者を「中村 覚」「Satoru Nakamura」にした（build_iiif.py と 14 件の Manifest、未コミット）。フッターの © は未確認
- [ ] 新しい 4 モデル（allegra・frecciarossa・maglev・vandebharat）は注釈が無いので、IIIF マニフェストとダウンロードがまだ無い
- [ ] `docs/downloads/`（git の管理外）は穴なし版から 14 件作り直した。公開の置き場所（git か Releases か）は未定のまま
- [x] 2026-10-09 新しい 4 モデルを `tools/build_rdf.py` の MODELS・CLASSES・LIVERIES に足し、RDF と検索の索引を作り直した（3D のある形式 12 → 16）。
      形式は gallery の wikidata 欄どおり（Q671805・Q370895・Q289090 = Transrapid 08・Q119775864）。上海リニアは運行会社の Wikidata 項目が無いので、塗装は路線 Q769591 に結んだ。
      ae15492 でコミット・push 済み（RDF だけ）。`docs/search/index.json` は (1) に入る（写真の保存が終わったら作り直す）
- [x] 2026-10-09 22:20 4 モデルの色を `tools/extract_colors.py` で `tools/livery_colors.json` に足した（allegra 赤・灰／frecciarossa 赤・青／maglev 白・青／vandebharat 橙・茶・青。既存 14 件は変化なし）。
      `tools/build_rdf.py` で `docs/rdf/` も作り直した（既存モデルの .jsonld の差分は並び順だけ）。未コミット。(1)(2) とは別の「色」コミットにする。`docs/search/index.json` への反映は (1) の索引の作り直しで入る
- [x] 2026-10-09 22:20 公開用の `docs/models/*.glb` 18 件が、skytrain の `out/<モデル>/nomount/*.glb` と同じファイル（穴なし版）であることを cmp で確かめた
- 2026-10-09 22:11 時点の写真の保存: 1,894 / 12,195 枚（PID 89664、1 分に約 76 枚、0 時半ごろ終わる見込み）。
  終わったら: `python3 tools/build_search.py` で索引を作り直す → web を組み立てて手元で確かめる → (1)(2)・色・skytrain の順にコミット → 本人の了承を得て push と `zsh scripts/deploy-pages.zsh`

## 形式のページで 3D を見せる（2026-10-09 夜に依頼。2026-10-10 0:12 コミット deb2e8e・公開済み）

- [x] 2026-10-09 23:59 公開中の模型 18 件が穴ありのままだった（公開 21:51、穴なし版のコミット 23:31、公開し直していなかった）。gh-pages に模型 18 件だけ差し替えるコミット 53a0675 を足し、公開中のファイル 18 件が `docs/models/*.glb` と一致することを確かめた。文言の変更（作者の行の削除・「プラレール」を外した文）は、まだ公開に入っていない。写真のあとの全体の公開で入る
- [x] 形式のページ（`rdf/class/<Q>.html`、`web/src/components/ClassPage.astro`）に 3D の表示を置く。注釈 `annotations/<id>.json`（14 件）を部位の印として重ねる。今は注釈は IIIF の Manifest にしか出ていない。1 つの形式に模型が複数あるとき（Innovia Metro の Mk1〜Mk5 など）は切り替え
- [x] `view.html` は振り分けだけのページにする（一覧は検索の「3D モデルあり」 `search/?has3d=1` と同じなので持たない）: `view.html#<模型>` は その模型の形式のページへ、`view.html` だけなら `search/?has3d=1` へ移す。見出しの「3D で見る」も `search/?has3d=1` に替える。URL は残す（外から張られている）
- [x] フッターが 2 重に見える件: `view.html` の注記（寸法・塗装の説明、`ja.json` の `view.note`）がサイトのフッターの真上に並んでいる。注記を 3D の表示の下（情報欄）に移す
- 作ったもの: `ClassPage.astro` の上に 3D の舞台（番号の印・模型の切り替え・向きのボタン・注記）と部位の一覧。部位を押すと、IIIF の Manifest に書いた部位ごとのカメラ（位置と注視点）に寄る。注釈は `lib/data.ts` の `modelParts` が Manifest から読む。区分（実車の特徴など）は Manifest に日本語しか無いので英語はページ側で訳す。Manifest の無い 4 件（allegra ほか）は印なし・リンクなしで、1 列の配置
- `view.html` は振り分けだけ（`lib/classes.ts` の `modelClasses`）。見出し・フッター・トップの「3D で見る」と新着は形式のページか `search/?has3d=1` へ。`styles/view.css` は消した
- 手元の確かめ（astro preview）: ICE TD で部位 1 を押すと前面ガラスに寄る、DSB への切り替えと `#icet_dsb`、英語のページ、Mk1、Allegra、`view.html` → `search/?has3d=1`、`view.html#icet_dsb` → ICE TD の DSB
- 気づいたこと: icet_green は models.json では Q115612330（411 形）だが、RDF では Q696668（ICE T）のページに載っている。どちらが正しいか未確認
- [x] 2026-10-10 0:35 印の手直し（Sketchfab にならう）: 小さく半透明に、裏側の印は薄く（向きは部位のカメラから逆算し、カメラが動くたびにページ側で判定。model-viewer の data-visible は付かなかった）、選んだ印は輪にして部位が見えるように、「部位の印」で全部隠せる、部位の一覧は箱の中で巻き取る（Mirador の注釈欄のように）、下の項目の見出しと文字を大きく
- [x] 2026-10-10 0:45 形式のページの右に「データと引用」のカード（ArchiveBase の項目ページの共有・エクスポートのカードにならう）: 引用文とコピー、エクスポート（Turtle・JSON-LD・IIIF Manifest（ロゴ付き）・GLB）。「つながり」の「データ」の行と、3D の下のロゴは外した。SNS の共有は付けていない
- [ ] Sketchfab のような「前へ・次へ」で部位を順にたどるボタン（未着手）
- [x] 2026-10-10 0:12 コミット・push・公開（deb2e8e、索引 7e8b87e、gh-pages は 7e8b87e のビルド 193 MB）。部品の説明の IIIF リンクは IIIF のロゴにした（`web/src/assets/iiif-logo.svg`、本人の他のサイトと同じファイル）。公開後に、形式のページの 3D・`view.html` の振り分け・文言（作者の行・プラレールが消えた）・写真の写し・検索・英語を確かめた

