# TODO: train-bodies を「世界の鉄道車両の形式」のデータベースにする

2026-10-09 作成。取り決め（URI・担当のファイル）は `data-model.md` の「位置付けと並行作業の取り決め」。
各セッションは自分の節だけを書き換える（済んだら `[x]` と日付・コミット）。他の節は読むだけ。

## A. RDF（worktree `train-bodies.worktrees/rdf`）

2026-10-10 9:45 棚卸し: 済んでいたのに印が付いていなかった項目に [x] を付けた（根拠: `docs/rdf/` に facets.json・all.ttl・all.jsonld・vocab.ttl・class/・model/ があり、語彙の判断は data-model.md の「担当 A」）。
B は `docs/iiif/` の 14 本と `annotations/*.json`（yaml でなく json にした）・iiif.md の 2026-10-09。C の詳細ページは Astro の形式のページ。

- [x] `docs/rdf/facets.json` を出す（絞り込みの項目: URI・日本語と英語の名前・値の型）。**最初にやる。C が待っている**
- [x] 語彙を決める（Wikidata の属性・ERA の語彙・schema.org・SKOS のどれを使うか。理由をノートに）
- [x] 形式の RDF `docs/rdf/class/<cid>.ttl`・`.jsonld`（まずは 3D モデルのある形式、次に Wikidata の全形式）
- [x] モデルの RDF `docs/rdf/model/<model-id>.ttl`・`.jsonld`（形式・塗装・作者・ライセンス・IIIF Manifest への逆リンク）
- [x] 全件をまとめたファイル（`docs/rdf/all.ttl` など）を一括ダウンロード用に
- [x] ERATV と Wikidata の照合を改善（「ICE T BR 411 ETCS BL3」→ Q115612330 のように、版の付いた名前を形式に結ぶ。skos:narrowMatch）
      2026-10-10 10:30 名前を後ろから削る照合と「BR nnn」の引き当てを `tools/build_classes.py` に入れた。結べた型 134 → 629（data-model.md の同じ日）。RDF に入れるのは ERATV の公開の判断の後
- [x] ERATV の再利用条件を確かめる（ERA の Copyright Notice）。結果で `docs/` に入れるか決める
      2026-10-10 10:00 確かめた（data-model.md の同じ日）: 出典を示せば複製してよい、という ERA の一般の許可だけ。ERATV に個別の定めは無い。`docs/` に入れるかは本人の判断待ち（推奨: 出典つきで入れる）
      2026-10-10 11:00 本人の判断: 対応表だけ出す（元の一覧は出さない）。`docs/data/eratv-wikidata.tsv` と CSVW の説明ファイル（`tools/build_eratv_map.py`）。RDF には入れていない
- [x] 「RDF にする利点」をノートで実測で示す（例: 典拠の更新がそのまま反映される、外部と結べる件数）
      2026-10-10 10:10 外部と結べる件数は実測した（data-model.md の同じ日: 17 形式・Wikidata 111 項目・路線 42）。典拠の更新の反映はまだ。公開中の RDF が 17 形式だけで、索引の 14,325 形式には RDF が無い点も分かった
      2026-10-10 11:10 全形式を RDF にした（本人の判断）うえで数え直し、典拠の更新の速さも測った（data-model.md の同じ日）。残る限界: 1 年前の値との差は未

## B. IIIF v4・注釈・ダウンロード（worktree `train-bodies.worktrees/iiif`）

- [x] IIIF Presentation 4.0 の今の状態を確かめる（正式版か草案か、Scene・3D・navPlace・注釈の書き方、対応ビューア）
- [x] ICE T 411 の Manifest 1 つで試す: Scene に GLB、`seeAlso` で RDF、`rendering` でダウンロード、`navPlace` で運行地域
- [x] 部位と特徴の注釈の元データ `annotations/<model-id>.yaml`（部位の名前・説明・3D 上の位置）。ICE T 411 から
- [x] 14 モデル全部の Manifest と、全体の Collection `docs/iiif/collection.json`（2026-10-10 9:45 Collection を足した: `build_iiif.py --collection`。トップの「データ」の RDF と IIIF の「準備中」を外してリンクした。Manifest の homepage を `view.html#<模型>`（形式のページへ）に直した）
- [x] ダウンロード形式 `docs/downloads/<model-id>/`（GLB・STL・OBJ・3MF・STEP など）と `~/git/3d/skytrain/tools/export_formats.py`。
      STEP は面を貼っただけで、CAD で寸法を直せる立体ではないことを画面とノートに書く
      2026-10-10 10:45 本人の案で、形式ごとに別のファイル（GLB・STL・OBJ・MTL・USDZ）を形式のページとモデルのページから落とせるようにした。OBJ の zip はやめ、MTL を並べた。18 モデル 92 MB。STEP・3MF は作らない（面を貼っただけの立体になるため）。画面に「CAD で寸法を直せる立体ではない」と書いた
- [x] 「IIIF v4 の実例」としての位置付けをノート `docs/notes/iiif.md` に（先行例の有無も）（2026-10-10 10:05。先行例は MorphoSource・Smithsonian Voyager・TSG の例。MorphoSource の Manifest の中身は未確認）

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
- [x] 地図から探す: navPlace（B の Manifest）を読んで地図に出す → navPlace でなく路線の線で作った（2026-10-10 `map/`、「路線」の節）
- [x] 形式の詳細ページ（RDF の中身を人が読める形で。3D・注釈・ダウンロードへのリンク）
- [x] 画面の判断をノート `docs/notes/site.md` に（2026-10-09、続けて書き足す）
- トップページの項目（ヘッダ〜フッタ）は 2026-10-09 から別セッション D（worktree `top`）が担当。main へ取り込み済み（16d0db2）

## サイトを Astro に移す — 方針は `site.md` の「Astro に移す」

- [x] 前提: site（写真のクレジット・種類の大分類）と iiif の枝を main に入れる（site は 2026-10-09 に b6f8f3b の時点を astro 経由で）
- [x] Astro の雛形、レイアウト 1 つ（ヘッダ・フッタ）、GitHub Actions で Pages に出す（配る段は配信元の切り替えまで止めてある）
- [x] トップ・ビューア・検索・形式の詳細の 4 種類を移す（2026-10-09。モデルのページ `rdf/model/*.html` はまだ Python の HTML）
- [x] `build_rdf.py` から HTML を書く部分を外し、形式の詳細ページは Astro が JSON から作る（2026-10-10 9:50。モデルのページ `rdf/model/<id>.html` も Astro にした: 名前・形式・寸法・形式のページへの入口・Turtle／JSON-LD／IIIF／GLB。Python の HTML 35 件は消した。点検に足した）
- [x] 多言語（日本語は今の URL、英語は `/en/`）（4 種類とも済み。2026-10-10 9:50 モデルの英語は gallery.py が `models.json` に label_en・title_en・line_en として書くようにし、仮置きの models.en.json は消した。`gallery.py --data-only` で models.json だけ書き直せる）
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
- [x] 形式のページに地図を出す（上が決まってから）
      2026-10-10 7:50 コミット 1aa7372・push・公開済み（線は 2 本だけ: Gäubahn・Madrid–Seville）。点検 `npm test` も公開の手順に入った
- [x] 残りの線を足して公開し直す: 切り出しは会話から切り離して動いている（`pgrep -fl tools/osm_lines.py`、記録 data/osm_lines.log、2026-10-10 7:50 で 6/42）。
      2026-10-10 10:50 取れなかった 12 本を 1 本ずつ取り直した（記録 data/osm_retry.log）: 9 本取れて、線は 29/42。Q802606 は OSM に wikidata= の付いた relation が無かった。Q1201543・Q489609 はまた 504。Q559660（Fugleflugtslinjen）は道路とフェリーの relation も入っている
      2026-10-10 残りの 504 の 2 本を mail.ru のミラーで取り直した（記録 data/osm_retry.log）: Q1201543（Detroit People Mover）・Q489609（龍仁軽電鉄）とも取れて、線は 31/42。札の付いた路線 31 本はこれで全部
      終わったら、失敗した路線を `--only Q… --api https://maps.mail.ru/osm/tools/overpass/api/interpreter` で取り直す → `_osm.tsv` を全件で作り直す（`--count` 以外の全体の流し直しは取れた分を飛ばす）→ docs/lines をコミット → push → `zsh scripts/deploy-pages.zsh`
- [x] 地図を MapLibre GL JS に替える（2026-10-10 7:52 本人の決定。理由: 暗い表示・地球儀表示。背景は OpenFreeMap）。
      2026-10-10 8:00 替えた（maplibre-gl 5.6.0 を CDN から。背景は OpenFreeMap の positron／dark で、サイトの明暗の切り替えに追従。地球儀表示。線の名前は重ねると出る）。
      Leaflet だった 4 か所（`ClassPage.astro` の読み込み・`web/src/scripts/line-map.ts`・`class.css`・点検 `web/scripts/check-dist.mjs`）を替えた。
      手元で ETR400（Q370895）のページを確かめた: 暗・明の切り替えで線が消えない、引くと地球儀、コンソールのエラーなし。`npm test` 通過。公開は線がそろってから一緒に
      2026-10-10: ページ側は作った（未コミット: ClassPage.astro・lib/data.ts の classLines・scripts/line-map.ts・class.css・i18n・sync-public.mjs に lines/）。
      線の切り出しは Overpass の 504 で難航中（1 路線ずつやり直し、失敗は飛ばして続きから取れるようにした）。`python3 -u tools/osm_lines.py --api https://maps.mail.ru/osm/tools/overpass/api/interpreter`（記録は data/osm_lines.log）。出力は docs/lines/
- [x] 地図のページ `map/`（日・英）を作った（2026-10-10 8:05、本人の了承）。準備中だった見出しの「地図」とトップの「地図から探す」から飛ぶ。
      線を取り出せた路線を全部 1 枚の地球儀に重ね、横の一覧に各路線を走る形式（形式のページへのリンク）を出す。地図の動きは形式のページと同じ `line-map.ts`。
      限界: 載るのは路線を調べた 12 形式だけ（検索の約 1 万 4 千形式の大半は出ない）。路線を足すほど育つ入口として出す。点検 `npm test` に map/ の確認を足した。公開は線がそろってから
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
- [x] 本人に確かめる: フッターの「© 2026 中村 覚」と、IIIF の提供者（`tools/build_iiif.py` の PROVIDER）「中村 覚（東京大学）」を残すか
      2026-10-10 本人の指示「このサイトでは東京大学をあまり出さない」: IIIF の提供者を「中村 覚」「Satoru Nakamura」にした（build_iiif.py と 14 件の Manifest、未コミット）。フッターの © は未確認
      2026-10-10 本人の判断（お任せ）: フッターは「© 2026 中村 覚」「© 2026 Satoru Nakamura」のまま残す（名前だけ。東京大学は入れない）
- [x] 新しい 4 モデル（allegra・frecciarossa・maglev・vandebharat）は注釈が無いので、IIIF マニフェストとダウンロードがまだ無い（2026-10-10 10:05 注釈 15〜16 か所ずつと Manifest を作った。Collection は 18 本。推測は frecciarossa 2・maglev 1。ダウンロードはまだ無いので、Manifest の rendering は GLB だけ。navPlace は入れていない）
- [x] `docs/downloads/`（git の管理外）は穴なし版から 14 件作り直した。公開の置き場所（git か Releases か）は未定のまま
      2026-10-10 10:45 決めた: git の main には入れず、公開の手順（gh-pages、履歴なし）でそのまま配る。Releases は使わない。作り直しても履歴に溜まらない。ファイルが欠けていると npm test が落ちる。Manifest の rendering も作り直した（404 は解消）
      2026-10-10 気づいたこと: Manifest の rendering（ダウンロード 4 件）は downloads/ を指しているが、公開の手順で downloads/ を外すので、今は 404 になる。置き場所が決まったら Manifest を作り直す
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
  → 2026-10-10 9:50 411 形が正しい（車番 411 525、skytrain の models/icet_green.py と写真 411_horb_green_stripe_side.jpg）。build_rdf.py の MODELS と annotations/icet_green.json を直し、RDF・Manifest・索引を作り直した
- [x] 2026-10-10 0:35 印の手直し（Sketchfab にならう）: 小さく半透明に、裏側の印は薄く（向きは部位のカメラから逆算し、カメラが動くたびにページ側で判定。model-viewer の data-visible は付かなかった）、選んだ印は輪にして部位が見えるように、「部位の印」で全部隠せる、部位の一覧は箱の中で巻き取る（Mirador の注釈欄のように）、下の項目の見出しと文字を大きく
- [x] 2026-10-10 0:45 形式のページの右に「データと引用」のカード（ArchiveBase の項目ページの共有・エクスポートのカードにならう）: 引用文とコピー、エクスポート（Turtle・JSON-LD・IIIF Manifest（ロゴ付き）・GLB）。「つながり」の「データ」の行と、3D の下のロゴは外した。SNS の共有は付けていない
- [x] Sketchfab のような「前へ・次へ」で部位を順にたどるボタン（2026-10-10 9:50。部位の一覧の下に「‹ 前へ」「n / 全数」「次へ ›」。端で一周する。印を押しても番号が付いてくる）
- [x] 2026-10-10 0:12 コミット・push・公開（deb2e8e、索引 7e8b87e、gh-pages は 7e8b87e のビルド 193 MB）。部品の説明の IIIF リンクは IIIF のロゴにした（`web/src/assets/iiif-logo.svg`、本人の他のサイトと同じファイル）。公開後に、形式のページの 3D・`view.html` の振り分け・文言（作者の行・プラレールが消えた）・写真の写し・検索・英語を確かめた


## 路線を全形式に広げる（2026-10-10 午後。測り方と実数は data-model.md の同じ日の「路線の線を全形式に広げられるか」「20 路線で試した」）

- [x] 件数調べ（`tools/count_class_lines.py`）: P3438 で 899 形式・1,695 路線、OSM の札あり 923、線まで届く形式 561
- [x] 20 路線で試した: Overpass 14/20、QLever 20/20（形は同じ）
- [x] Wikidata の対応表 `tools/class_lines_wd.tsv`（`tools/wd_class_lines.py`。deprecated を除く。2,441 行・913 形式・1,694 路線・終了 173）。手の表が優先
- [x] `tools/osm_lines.py --qlever`（QLever で取る）と `docs/lines/_all.geojson`（地図のページ用に 1 つにまとめる）。試し用の qlever_lines.py は消した
- [x] サイト・点検・RDF が 2 つの表を読む（data.ts・check-dist.mjs・build_rdf.py。地図のページは _all.geojson を 1 つの層で描く）。build_rdf.py は手の 17 形式にしか路線を書いていなかった不具合も直した: tb:usedOn 12 → 2,490
- [x] 線の取り出し（`python3 -u tools/osm_lines.py --qlever`）: 1,733 路線のうち 935 本で線、失敗 0。558 形式に線（実数は data-model.md「全路線を取り出した」）
- [x] build・`npm test` 通過、map/ と Q432757 を目で確認（明暗の切り替えで線は残る。選んだ線が見分けにくかったので、ほかを薄くした）。ノートに記録
- [x] コミットと公開（main 4706d76、2026-10-10）
- [x] 小さな残り: 線の読み込み前に一覧を押すと地図が動かない（2026-10-11 直した。読み込み前に押した路線は、読み込み後に寄る。手元では速すぎて再現できず、コードで確かめた）

## 地図のページの見せ方（2026-10-11、本人の依頼）

- [x] 既定を平面の世界地図にし、バンクーバーを中心にした（地球儀だと半分しか映らず、欧州・アジアの線が裏に隠れる）。地球儀は右上のボタンで切り替え。形式のページは地球儀のまま
- [x] 地図のページだけホイールで拡大縮小（形式のページは縦に長いので切ったまま）
- [x] 「3D モデルのある形式の路線だけ（34）」の絞り込みと、一覧の形式名に「3D」の印
- [x] 線のファイル `_all.geojson` が 3.2 MB（gzip で約 1 MB）で、線が出るまで数秒かかる。困るようなら軽くする
      （2026-10-11 本人の了承で 2 段にした。`_all.geojson` は約 200 m 刻み・小数 3 桁・名前と ID だけ: 3.4 MB → 1.1 MB、gzip 1.0 → 0.24 MB。
      路線を選んだとき、または拡大 9 以上で画面内の路線（一度に 40 本まで）だけ `lines/<Q>.geojson` の詳しい線に差し替える。
      ODbL の表示は集まり全体に 1 回。`python3 tools/osm_lines.py --all` で作り直せる。間引きを約 1 km にすると gzip 0.12 MB だが都市の線が崩れるので取らなかった。
      目で確かめたのはヘッドレスの Chromium（Chrome 拡張のタブは裏に回って地図が描かれなかった））

## 新しいモデルを足す手順（2026-10-11、canadian で通した手順を書き起こした）

次の 6 両（gautrain・dubaimetro・trenmaya・tilttrain・ed250・class395）はこの順で足す。`<id>` は gallery の模型の名前、`<Q>` は Wikidata の形式。
始める前に、train-bodies で `git status` を見る。ほかのセッションが動いていたら（未コミットの変更、数分以内に書き換わったファイル、`pgrep -fl 'astro build'`）待つ。

1. skytrain で、台座なしの版を作る: `/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python build.py -- <id> --no-mount`（out/<id>/nomount/ に入る）
2. skytrain の `tools/gallery.py` の MODELS（日本語の名前・1 行・`<Q>`・足した日）と EN（英語の名前・1 行）に 1 行ずつ足す
3. skytrain で `python3 tools/gallery.py --no-mount --out ~/git/3d/train-bodies/docs` を走らせる（全模型を書き直す）
4. train-bodies で `git status --short docs/models docs/thumbs docs/data` を見る。変わるのは models.json と、新しい glb・jpg だけのはず
5. train-bodies の `tools/build_rdf.py` に 3 か所足す: CLASSES（`"<Q>": ("<Q>", None, None)`）、LIVERIES（塗装の名前 ja/en と、その塗装の運行会社の Q）、MODELS（`"<id>": ("<Q>", "<塗装>", None)`）
6. Wikidata に形式の日本語の名前が無ければ、LABEL_JA にも足す
   （2026-10-12 追記）Wikidata の名前が mul だけのとき（en も無い）は、CLASSES の 3 番目に en・ja の名前を入れる（trenmaya）。
   Wikidata に車両の形式の項目が無く、路線網の項目しか無いときは、形式 `tb-<短い英字>` を立てる（gautrain・dubaimetro）:
   CLASSES `"tb-x": (None, None, {"en": …, "ja": …})`、HAND（国・運行・製造・種類・開業年）と HAND_SOURCE、
   路線網は tools/class_lines.tsv に「走る路線」として 1 行（`tb-x	<Q>	<名前>	current	https://www.wikidata.org/wiki/<Q>	Wikidata (the system)	…`）。
   注釈の "class" は tb-x にし、"wikidata" は書かない（書くと IIIF で「上位の形式」と表示される）。コミットに docs/rdf/class/tb-x.* と tools/class_lines.tsv も入れる
7. 色: `python3 tools/extract_colors.py`（build_rdf.py の MODELS を読む。ほかの模型の行が変わっていないことを、出力の一覧と `git diff tools/livery_colors.json` で見る）
8. RDF: `python3 tools/build_rdf.py`（1 分半ほど。新しい形式だけを Wikidata から取る。`--refresh` は付けない。付けるとほかの形式の値も今の Wikidata に変わる）
9. 並び順だけ変わった .jsonld を戻す: `python3 tools/rdf_order_only.py`（「real」と出るのは all.jsonld・新しい形式・void.jsonld だけのはず）
10. 部位の注釈 `annotations/<id>.json` を書く（skytrain の models/<id>.py の座標と実験ノートから。14 か所前後。形は annotations/canadian.json を手本に）
11. `python3 tools/build_iiif.py <id>`（どの部位も、狙った色の面に当たったかが表に出る。外れると止まる）
12. ダウンロード: skytrain で `python3 tools/export_formats.py <id> ~/git/3d/train-bodies/docs/downloads/<id> --no-mount`（git には入らない。公開の手順でだけ配る）
13. Manifest をダウンロード込みで作り直す: `python3 tools/build_iiif.py <id>`（「5 downloads」と出る）、続けて `python3 tools/build_iiif.py --collection`
14. 検索の索引: `python3 tools/build_search.py`（変わるのは新しい形式の行だけのはず。stats.json の models が 1 つ増える）
15. データセットの説明: `python3 tools/build_void.py`（docs/rdf/void.* と docs/data/dataset.json）
16. 路線: 形式に Wikidata の P3438 が無ければ何もしない（地図には出ない）。手で足すなら tools/class_lines.tsv と `tools/osm_lines.py`
17. サイト: `cd web && npm run build && npm test`
18. コミット（ファイルを 1 つずつ `git add`）: train-bodies は annotations/<id>.json・docs/models/<id>.glb・docs/thumbs/<id>.jpg・docs/data/models.json・docs/data/dataset.json・docs/iiif/<id>/manifest.json・docs/iiif/collection.json・docs/rdf/all.*・docs/rdf/void.*・docs/rdf/class/<Q>.*・docs/rdf/model/<id>.*・docs/search/index.json・docs/search/stats.json・tools/build_rdf.py・tools/livery_colors.json。skytrain は tools/gallery.py
19. 本人の了承のあとで: train-bodies で `git push` と `zsh scripts/deploy-pages.zsh`（main で走らせる。中で build と npm test をもう一度走らせ、通ったときだけ gh-pages に出す）

## カナディアン（パーク・カー）を足した（2026-10-11）

- [x] 模型 canadian（skytrain の models/canadian.py、実験ノート skytrain/docs/notes/canadian.md）。形式 Q19877282（パーク・カー）、塗装 via-stainless（VIA鉄道 Q876720 の帯なしのステンレス）。gallery は skytrain 48faddc
- [x] 色は灰 98.4% だけ（地のステンレス）。ほかの 18 模型の色は変わらず
- [x] v2 の車体（skytrain ad74687、屋根 40・全高 48.1 mm）で作り直した。RDF: 形式 18 + 14,307、模型 19、251,043 トリプル。build_rdf.py は、キャッシュに無い形式だけを Wikidata から取るようにした（それまでは新しい形式があると止まり、`--refresh` で全部を取り直すしかなかった）
- [x] 注釈 14 か所（推測 1・模型の都合 1）、Manifest（ダウンロード 5 件）、Collection 19 本、索引（変わったのは Q19877282 の行だけ）、VoID
- 路線: Q19877282 に P3438 が無いので、地図には出ない。列車のカナディアン（Q1069301）の路線を形式に結ぶかは未決
- 2026-10-11 23:00 ごろ、別のセッション（OG 画像の作業）が同じチェックアウトで `astro build` を走らせ、こちらのビルドとぶつかって落ちた。向こうが終わってから作り直し、`npm run build && npm test` は通った（28,650 形式のページ・19 模型）。ビルドの前に `pgrep -fl 'astro build'` を見ること
- 注釈は v2 で高さが最大 2.5 mm 動いたので、狙う点を直した（尾の窓・VIA の板・帯・ドームの 3 か所）。14 か所とも狙った色に当たる
- [x] 2026-10-11 電気式ティルト・トレイン（tilttrain、Q23641827、塗装 qr-tilt）を足した。色は黄・灰、注釈 14 か所（推測 1・模型の都合 1）。npm test 通過。gallery は skytrain ce1a3a9
- [x] 2026-10-11 クラス395「ジャベリン」（class395、Q246841、塗装 southeastern-2025、運行 Southeastern Q1696490）を足した。色は青（紺）・橙・黄、注釈 15 か所（推測 1・模型の都合 1）。npm test 通過。gallery は skytrain 5db1e42
- [x] 2026-10-11 ED250 ペンドリーノ（ed250、Q18331751、塗装 pkp-ic-ed250、運行 PKP Intercity Q590406）を足した。Wikidata に日本語の名前が無いので LABEL_JA に「ED250 ペンドリーノ」。色は灰（銀）・青、注釈 13 か所（推測 1・模型の都合 1）。npm test 通過。gallery は skytrain 54e8d48
- [x] 2026-10-12 トレン・マヤ（trenmaya、Q140092296、塗装 tren-maya-xiinbal、事業 Q59806309）を足した。Wikidata の名前が mul だけ（en・ja が無い）なので、CLASSES に en・ja の名前を手で入れた。色は白（クリーム）・緑、注釈 15 か所（推測 1・模型の都合 2）。npm test 通過。gallery は skytrain d4606cb
- [x] 2026-10-12 ハウトレイン（gautrain、形式 tb-gautrain、塗装 gautrain）を足した。Q1476881 は路線網の項目なので形式にせず、tools/class_lines.tsv で「走る路線」（tb:usedOn）として結んだ。国・運行・製造・種類・開業年は HAND（出典は HAND_SOURCE）。Electrostar（Q841722）を skos:broader にしなかったのは、引き継ぐ値（電化方式など）が英国の系列のものになるため。build_rdf.py は HAND と塗装の運行会社の名前も取るようにした。色はシャンパンが「橙」に分けられた（87%）。注釈 16 か所（推測 1・模型の都合 1）。npm test 通過。gallery は skytrain 9951604
- [x] 2026-10-12 ドバイメトロ（dubaimetro、形式 tb-dubaimetro、塗装 dubai-metro は RTA Q22101985 のもの）を足した。ハウトレインと同じく、路線網 Q83787 は tools/class_lines.tsv で結んだ。色は灰（銀）・青、注釈 13 か所（推測 1・模型の都合 2）。npm test 通過（28,654 形式のページ・25 模型）。gallery は skytrain 0b14780。上の手順の 6 に、mul だけの名前と tb- の形式の足し方を書き足した
- [x] 2026-10-12 台湾鉄路 EMU3000型（emu3000、Q65054413、塗装 tr-emu3000-red、運行 Q697926）を足した。色は白だけ（黒い先頭部 13.4% は中立色の 20% に届かず、赤い帯は 1.5% 未満で落ちた）。注釈 16 か所（推測 1・模型の都合 1）。Q65054413 に P3438 が無いので地図には出ない。npm test 通過（28,654 形式のページ・26 模型）。gallery は skytrain 46fb38e
- [x] 2026-10-12 SRTレッドライン（srtred、形式 tb-srtred、塗装 srt-red-line、運行はタイ国鉄 Q2165702。実際の運行は子会社 SRTET で項目なし）を足した。路線網 Q2542280 は tools/class_lines.tsv で結んだ。HAND は国・運行・製造（日立 Q53238）・種類・開業 2021。A-train（Q1066003）は群が広いので skos:broader にしなかった。色は白・赤（黒い仮面 4.5% は落ちた）。注釈 16 か所（推測 1・模型の都合 1）。npm test 通過（28,656 形式のページ・27 模型）。gallery は skytrain 55fd5a3
- [x] 2026-10-12 SJ X2000 の動力車（x2000、Q853105、塗装 sj-x2000-2021、運行 SJ Q8301325）を足した。色は灰だけ（95.2%。濃い灰・明るい灰・ステンレスがすべて灰に入る。実車どおり）。注釈 15 か所（推測 1・模型の都合 1）。Q853105 に P3438 が無いので地図には出ない。npm test 通過（28,656 形式のページ・28 模型）。gallery は skytrain f3a8957
- [x] 2026-10-12 トランツアルパインの AK 形パノラマ客車（tranzalpine、Q7015181、塗装 kiwirail-ak-flames、運行 KiwiRail Scenic Journeys Q956508）を足した。色は白・灰・青。青は屋根の肩の窓（空の映り込みの色、4.4%）で、炎の黄・橙・赤はどれも 1.5% 未満で落ちた。実車の印象とずれる。注釈 15 か所（推測 1・模型の都合 1）。npm test 通過（28,656 形式のページ・29 模型）。gallery は skytrain 32969ce
- [x] 2026-10-12 ペルーレイルのビスタドーム気動車（vistadome、形式 tb-vistadome、塗装 perurail-vistadome、運行 PeruRail Q1407952）を足した。走る路線 Q100145062（クスコ〜マチュピチュ）は tools/class_lines.tsv で結んだ。HAND は国・運行・製造（Macosa、いまの Stadler Rail Valencia Q2729224）・種類（気動車 Q752392）。開業年は入れていない（製造 1984、ビスタドームでの使用開始は不明）。色は青・灰・黄。注釈 15 か所（推測 1・模型の都合 2）。npm test 通過（28,658 形式のページ・30 模型）。gallery は skytrain a13473b
- [x] 2026-10-12 ケニア SGR の DF8B 形（madaraka、Q10871152 は中国の DF8B の項目。ケニア向けの独立した項目が無いのでここに結んだ。塗装 kr-sgr-df8b、運行 Kenya Railways Q1663639）を足した。形式の国などは中国の DF8B の値のまま。色は赤・黄だけ（白い車体 13.2% は中立色の 20% に届かず落ちた。実車は赤と白）。注釈 15 か所（推測 1・模型の都合 1）。npm test 通過（28,658 形式のページ・31 模型）。gallery は skytrain 22e6737
- [x] 2026-10-12 ICNG（icng、Q26158722、塗装 ns-icng、運行 NS Q23076）を足した。Wikidata に日本語の名前が無いので LABEL_JA に「ICNG（新世代インターシティ）」。色は橙・青（NS の黄 #FFBF1F は色相 45 度の境目で「橙」に分けられた。実車は黄）。注釈 17 か所（推測 1・模型の都合 1）。npm test 通過（28,658 形式のページ・32 模型）。gallery は skytrain 055061b
- [x] 2026-10-12 タンザニア SGR の E6800 形電気機関車（tanzania、形式 tb-tanzania、塗装 trc-sgr、運行 TRC Q2393276）を足した。路線網 Q60744141 は tools/class_lines.tsv で結んだ。HAND は国・運行・製造（Hyundai Rotem Q152517）・種類（電気機関車 Q625151）・旅客営業 2024。設計の元の TCDD E68000（Q28444692）は別の形式なので skos:broader にしなかった。色は白（クリーム）・茶（えんじ）・橙。注釈 14 か所（推測 1・模型の都合 1）。npm test 通過（28,660 形式のページ・33 模型）。gallery は skytrain 8b20426
- [x] 2026-10-12 マルマライ（marmaray、Q20926238、塗装 tcdd-marmaray、運行 TCDD Taşımacılık Q28220824）を足した。Wikidata に日本語の名前が無いので LABEL_JA に「TCDD E32000形」。色は白・灰・青・赤。白が 56.5% でステンレスの灰（16%）より多く出た（模型の地の色が白のため）。青緑の帯は「青」。注釈 15 か所（推測 1・模型の都合 1）。npm test 通過（28,660 形式のページ・34 模型）。gallery は skytrain afaf6a8
- [x] 2026-10-12 KTX-이음（ktxeum、Q104216528、塗装 korail-ktx-eum、運行 韓国鉄道公社 Q18169）を足した。色は青だけ（窓帯の濃い灰 14% は中立色の 20% に届かず落ちた）。注釈 14 か所（推測 1・模型の都合 1）。npm test 通過（28,660 形式のページ・35 模型）。gallery は skytrain 91e2e45
- [x] 2026-10-12 リヤド・メトロ 1 号線（riyadh、Q2284320 は Siemens Inspiro の系列の項目。リヤド向けの項目が無いのでここに結んだ。塗装 riyadh-metro-line1、塗装の持ち主はリヤド市の王立委員会 Q12194736）を足した。色は青・白（黒い窓帯 11.5% は落ちた）。注釈 16 か所（推測 1・模型の都合 1）。npm test 通過（28,660 形式のページ・36 模型）。gallery は skytrain 0375e2c
- [x] 2026-10-12 IC3（ic3、Q706345、塗装 dsb-ic3、運行 DSB Q83824）を足した。色は灰・青（紺の窓帯 4.3%。黒いゴムの顔 9% は中立色の 20% に届かず落ちた）。注釈 17 か所（推測 1・模型の都合 1）。npm test 通過（28,660 形式のページ・37 模型）。gallery は skytrain 7a32411
- [x] 2026-10-12 ダージリン・ヒマラヤ鉄道 B 形 782 号機（darjeeling、Q18349836、塗装 dhr-blue、運行 DHR Q463874）を足した。Wikidata に日本語の名前が無いので LABEL_JA に「ダージリン・ヒマラヤ鉄道 B形」。蒸気機関車で高さ 46.3 mm。色は灰・青・赤。黒い煙室など（#2C2E32）は明るさ 0.18 で「黒」の境 0.15 を超え、「灰」75.9% に入った。注釈 16 か所（推測 1・模型の都合 1）。npm test 通過（28,660 形式のページ・38 模型）。gallery は skytrain f941d47
- [x] 2026-10-12 アセラ（アヴェリア・リバティ）動力車（acela、Q26724167、塗装 amtrak-acela-2025、運行 Amtrak Q23239）を足した。色は青・赤。実車の印象（白が主）とずれる。地の色の青（acela）が 69% と出た（車体の内側の面も地の色で数えられるためと見ている。marmaray の白 56% も同じ）。白 18% は中立色の 20% に届かず落ちた。注釈 17 か所（推測 1・模型の都合 1）。npm test 通過（28,660 形式のページ・39 模型）。gallery は skytrain 736b36e
- [x] 2026-10-12 インターシティ 125 の 43 形動力車（ic125、Q1080162、塗装 scotrail-inter7city、運行 ScotRail Trains Q107980329）を足した。色は青（紺）・灰・黄。注釈 16 か所（推測 1・模型の都合 1）。npm test 通過（28,660 形式のページ・40 模型）。gallery は skytrain c9e5c19
- [x] 2026-10-12 コルコバード登山電車 4 代目（corcovado、Q120801969、塗装 corcovado-2019、運行 コルコバード鉄道 Q1132053）を足した。Wikidata に日本語の名前が無いので LABEL_JA に「コルコバード登山鉄道 4 代目電車」。高さ 40 mm。色は赤だけ（黒い顔 6.9%・白い腰板 6.4% は中立色の 20% に届かず落ちた）。注釈 16 か所（推測 1・模型の都合 1）。npm test 通過（28,660 形式のページ・41 模型）。gallery は skytrain 723c434
- [x] 2026-10-12 リスボン市電 28 番線の Remodelado（lisbon28、形式 tb-lisbon28、塗装 carris-yellow、運行 Carris Q1045108）を足した。リスボン市電 Q149629 は tools/class_lines.tsv で結んだ。HAND は国・運行・種類（路面電車 Q3407658）・作り直しの 1995 年（製造者は入れていない）。高さ 46 mm。色は白・橙・茶。Carris の黄 #F2B200 は色相 44 度で「橙」に分けられた（実車は黄）。注釈 11 か所（模型の都合 1）。npm test 通過（28,662 形式のページ・42 模型）。gallery は skytrain 4b4353d
- [x] 2026-10-12 アディスアベバ・ライトレールの路面電車（addis、形式 tb-addis、塗装 aalrt-green、運行 エチオピア鉄道公社 Q55639671）を足した。路線網 Q16250141 は tools/class_lines.tsv で結んだ。HAND は国・運行・製造（CRRC 長春 Q848225）・種類（路面電車 Q3407658）・開業 2015。高さ 40 mm。色は白・緑。注釈 16 か所（推測 1・模型の都合 1）。npm test 通過（28,664 形式のページ・43 模型）。gallery は skytrain f5d6666
- [x] 2026-10-12 ジャカルタ MRT 1000 系（jakartamrt、Q56394168、塗装 mrtj-standard、運行 PT MRT Jakarta Q137969581）を足した。Wikidata に日本語の名前が無いので LABEL_JA に「ジャカルタ MRT 1000系」。色は灰・青（紺と青の顔は面積が小さく、青 3.6%）。注釈 14 か所（模型の都合 2）。npm test 通過（28,664 形式のページ・44 模型）。gallery は skytrain 1c7af4f
- [x] 2026-10-12 ワラタ（シドニー・トレインズ A 編成）の先頭車（waratah、Q5122977、塗装 sydney-trains-waratah、運行 Sydney Trains Q7660181）を足した。2 階建てで高さ 45.9 mm。色は灰・橙。ワラタの黄 #F4B400 も橙と一緒に「橙」に入った（実車は黄と橙）。注釈 14 か所（推測 1・模型の都合 1）。npm test 通過（28,664 形式のページ・45 模型）。gallery は skytrain 5c9d63d
- [x] 2026-10-12 サンティアゴ〜チジャン線の EFE SFB-500（santiago-chillan、Q117538222、塗装 efe-sfb500、運行 EFE Q679910）を足した。名前にハイフンがあるが、ビルド・検査・モデルのページ（rdf/model/santiago-chillan.html）とも問題なし。Wikidata に日本語の名前が無いので LABEL_JA に「チリ国鉄 SFB-500」。色は灰・赤・青。注釈 17 か所（推測 1・模型の都合 1）。npm test 通過（28,664 形式のページ・46 模型）。gallery は skytrain 9fe8efc
- [x] 2026-10-12 サンフランシスコのケーブルカー 1 号車（cablecar、形式 tb-cablecar、塗装 muni-cablecar、運行 Muni Q1140138）を足した。仕組み全体 Q374956 は tools/class_lines.tsv で結んだ。HAND は国・運行・種類（ケーブルカー Q5609555）だけ（製造者と年は車ごとに違うので入れていない）。高さ 44.8 mm。色は橙・茶・青。クリーム #ECE3C8 が彩度 0.14 で「橙」に分けられ 68% になった（実車の印象は栗色・クリーム・水色）。注釈 12 か所（模型の都合 1）。npm test 通過（28,666 形式のページ・47 模型）。gallery は skytrain 10d0934
- [x] 2026-10-12 カイロ地下鉄 2 号線の日本製の電車（cairo、形式 tb-cairo、塗装 cairo-line2）を足した。2 号線 Q5017773 は tools/class_lines.tsv で結んだ。HAND は国・運行（持ち主のトンネル庁 Q64744683）・製造（近畿車輛 Q1592306）・種類・開業 1996。色は灰・桃・赤（薄紫の帯は「桃」、サーモン色のオレンジの帯は「赤」に分けられた）。注釈 16 か所（推測 1・模型の都合 1）。npm test 通過（28,668 形式のページ・48 模型）。gallery は skytrain f3cad6f
- [x] 2026-10-12 ベトナム鉄道 D19E 形 923 号機（vietnam、Q423578、塗装 vnr-hanoi-skyblue、運行 ベトナム鉄道 Q501329）を足した。Wikidata に日本語の名前が無いので LABEL_JA に「ベトナム鉄道 D19E形」。高さ 41.4 mm。色は青・赤（クリーム色の運転室の正面 5.4% は落ちた）。注釈 16 か所（推測 1・模型の都合 1）。npm test 通過（28,668 形式のページ・49 模型）。gallery は skytrain 5e12ea5
- [x] 2026-10-12 ロンドン地下鉄 1973 形（lu1973、Q1814255、塗装 lu-corporate、運行 London Underground Q682520）を足した。高さ 40 mm。色は白・赤・青。注釈 12 か所（模型の都合 1）。npm test 通過（28,668 形式のページ・50 模型）。gallery は skytrain 83a3f61
- [x] 2026-10-12 ニューヨーク地下鉄 R211A（r211、Q7274448、塗装 mta-r211、運行 MTA ニューヨーク市交通局 Q1146109）を足した。色は灰・青。注釈 11 か所（模型の都合 1）。npm test 通過（28,668 形式のページ・51 模型）。gallery は skytrain a46ca51
- [x] 2026-10-13 ブルートレイン（南アフリカ）の展望車（bluetrain、形式 tb-bluetrain、塗装 bluetrain-royal、持ち主 Transnet Q820804）を足した。別のセッションが 2026-10-12 に RDF まで進めて止まっていたのを引き継ぎ、注釈 15 か所（推測 1・模型の都合 2）・IIIF・索引・VoID を足した。列車（サービス）Q885923 は tools/class_lines.tsv で結んだ。色は青・黄・橙（屋根の灰 18% は中立色の 20% に届かず落ちた）。gallery は skytrain f31c123
- [x] 2026-10-13 UBC サンダーバーズのシャトルバス（ubcshuttle、Q1436723 フォード E シリーズ、塗装 ubc-take-flight、持ち主 UBC Thunderbirds Q7863809）を足した。初めての「鉄道でも路線バスでもない」車両。資料は本人が撮った写真 6 枚（未公開）で、注釈の参考写真にも Commons の写真は無い。色は白・青。注釈 16 か所（推測 1・模型の都合 1）。Q1436723 に P3438 は無いので地図には出ない。gallery は skytrain f31c123
- [x] 2026-10-12 KTM ETS 93 形（ets、Q18619244、塗装 ktm-ets2、運行 KTM Q1187590）を足した。色は白・赤・黄・青。注釈 14 か所（推測 1・模型の都合 1）。npm test 通過（28,668 形式のページ・52 模型）。gallery は skytrain a904761
- [x] 2026-10-12 ナモ・バーラト（namobharat、Q119438293、塗装 ncrtc-namobharat、運行 NCRTC Q17077649）を足した。Q119438293 の P31 は Q870（列車）だが、車両そのものの項目なのでこれを形式にした（路線・サービスの Q119294099 と取り違えない）。色は灰・赤（94.1% が灰。実車どおり、ステンレスに赤い矢印）。注釈 15 か所（推測 1・模型の都合 2）。Q119438293 に P3438 が無いので地図には出ない。npm test 通過（28,670 形式のページ・53 模型）。gallery は skytrain f54f3ac
- [x] 2026-10-12 カナダ・ラインの現代ロテム製の電車（canadaline、Q55614147、塗装 translink-canadaline、運行 ProTrans BC Q141170779）を足した。形式は data/classes.tsv に既にあったものに結んだ。Wikidata に日本語の名前が無いので LABEL_JA に「カナダ・ライン（現代ロテム製）」。色は灰・青（緑の移りと白い流れ模様は面積が小さく、緑は 1.5% 未満で落ちた。白 2.4% は中立色の 20% に届かず落ちた）。注釈 17 か所（推測 1・模型の都合 2）。Q55614147 に P3438 が無いので地図には出ない（カナダ・ライン Q1031997 は結んでいない）。npm test 通過（28,670 形式のページ・54 模型）。gallery は skytrain ec9657f
- [x] 2026-10-12 ICE 4 の端の車（ice4、Q324870、塗装は既存の db、運行 DB Q9322）を足した。色は白・赤（青 1.5% は前面ガラスなど）。注釈 16 か所（推測 1・模型の都合 2）。Q324870 に P3438 が無いので地図には出ない。npm test 通過（28,670 形式のページ・55 模型）。gallery は skytrain a36ef1e
- [x] 2026-10-12 アル・ボラクの動力車 1210 号（alboraq、Q727577 は TGV 2N2（Euroduplex）の項目。アル・ボラクそのものの形式の項目は無く、Q60539878 は列車の名前（ブランド）なので結んでいない。塗装 oncf-alboraq、運行 ONCF Q1815809）を足した。Q727577 の運行に ONCF は入っていない。色は灰・赤・緑（緑 1.5%）。注釈 16 か所（推測 1・模型の都合 2）。Q727577 に P3438 が無いので地図には出ない。npm test 通過（28,670 形式のページ・56 模型）。gallery は skytrain ea4622e
- [x] 2026-10-12 ギルノ（giruno、Q16798908、塗装 sbb-giruno、運行 SBB Q83835）を足した。WESTbahn の Q138768194 は使っていない。色は白・黒・赤（実車どおり）。注釈 17 か所（推測 1・模型の都合 2）。Q16798908 に P3438 が無いので地図には出ない。npm test 通過（28,670 形式のページ・57 模型）。gallery は skytrain ff7bcba
- [x] 2026-10-12 ハラマイン高速鉄道の Talgo 350 SRO の動力車（haramain、Q6138251、塗装 sar-haramain、運行 サウジアラビア鉄道機構 Q843548）を足した。Wikidata の名前が es・mul だけなので、CLASSES に en・ja の名前を手で入れた。色は白・緑（金の線は 1.5% 未満で落ちた）。注釈 15 か所（推測 1・模型の都合 2）。Q6138251 に P3438 が無いので地図には出ない。npm test 通過（28,670 形式のページ・58 模型）。gallery は skytrain 65b5f4f
- [x] 2026-10-12 メルボルンの E 形路面電車の端の車体（melbourne-e、Q5321494、塗装 ptv-tram、運行 Yarra Trams Q16927551）を足した。名前にハイフンがあるが、ビルド・検査とも問題なし。高さ 45.5 mm。色は白・緑・黄（実車どおり）。注釈 16 か所（推測 1・模型の都合 2）。Q5321494 に P3438 が無いので地図には出ない。npm test 通過（28,670 形式のページ・59 模型）。gallery は skytrain 8a50921
- [x] 2026-10-12 ブライトラインの SCB-40 機関車 114 号（brightline、Q134533452、塗装 brightline-yellow、運行 Brightline Q27012668）を足した。Wikidata に日本語の名前が無いので LABEL_JA に「ブライトライン SCB-40」。色は白・灰・黄・茶（茶 2.8% は黄色の帯から透ける放熱器のよろい戸の色 #7A6422）。注釈 17 か所（推測 1・模型の都合 2）。Q134533452 に P3438 が無いので地図には出ない。npm test 通過（28,670 形式のページ・60 模型）。gallery は skytrain 5205569
- [x] 2026-10-12 シドニーメトロのメトロポリス（sydneymetro、Q96407257、塗装 sydney-metro、運行 Metro Trains Sydney Q20861549）を足した。形式は新しく足した（data/classes.tsv に無かった。P31 が Q4102249 のため）。Wikidata に日本語の名前が無いので LABEL_JA に「シドニーメトロ（アルストム メトロポリス）」。色は灰・青（白い車体 9.8% は中立色の 20% に届かず落ちた。実車は白が目立つ）。注釈 16 か所（推測 1・模型の都合 2）。P3438 が無いので地図には出ない。npm test 通過（28,671 形式のページ・61 模型）。gallery は skytrain 2f9765a
- [x] 2026-10-12 ウェストコースト・エクスプレスのバイレベル制御客車 104 号（wce、Q891775、塗装 wce-violet、運行 West Coast Express Q1675085）を足した。2 階建てで高さ 46 mm。色は白・青・橙（紫 #3D3B8C は「青」、金 #F0AE1E は「橙」に分けられた）。注釈 17 か所（推測 1・模型の都合 2）。Q891775 に P3438 が無いので地図には出ない。npm test 通過（28,672 形式のページ・62 模型）。gallery は skytrain 18d1cd8
- [x] 2026-10-12 レールジェット第 1 世代の制御客車（railjet、Q125350160、塗装 oebb-railjet、運行 ÖBB Q83822）を足した。形式は新しく足した（第 3 世代の Q125350627 とサービスの Q327051 は使っていない）。Wikidata の名前は en・mul だけなので LABEL_JA に「レールジェット（第1世代）」。色は赤・灰（模型の赤 #E82C34・#FF5A45 はどちらも「赤」、69%）。Q125350160 には P3438（Q1472045 ほか 3 本）があるが、路線の表（tools/class_lines.tsv）は作り直していないので地図にはまだ出ない。注釈 16 か所（推測 1・模型の都合 2）。npm test 通過（28,673 形式のページ・63 模型）。gallery は skytrain 00f5538
- [x] 2026-10-13 アヴァンティ・ウェスト・コーストの 390 形ペンドリーノ（avanti390、Q681896、塗装 avanti-teal、運行 Avanti West Coast Q68441695）を足した。色は青・橙・黄（青緑・紺は「青」。黄 1.8%）。注釈 18 か所（推測 1・模型の都合 2）。Q681896 に P3438 が無いので地図には出ない。extract_colors.py を走らせると mk1 の色の割合も変わった（skytrain の out/mk1 が別の作業で作り直されたため）。mk1 の値は元のまま戻した。npm test 通過（28,678 形式のページ・66 模型）。gallery は skytrain 361e828

## データセットのページと路線の色（2026-10-11 夜。main bc41944・公開済み）

- [x] データセットのページ `dataset.html`（日・英）と VoID・DCAT（`tools/build_void.py`）。ヘッダの「データ」はここへ飛ぶ
- [x] 地図の路線を 1 本ずつ色分け（Wikidata P465 の公式色、無ければ決まった色。`tools/line_colors.py`）
- [ ] 明るい地図の上で黄色の線（路線「4」など）がやや見えにくい。気になったら色を替える（本人の判断待ち）

## 次: LOD チャレンジ 2026 の応募 — 計画は `data-model.md` の「LOD チャレンジ 2026 の応募計画」

- [ ] 「決めていないこと（本人の判断）」の 5 点を本人に確かめる（2 作品で出すか・名義・所属欄・ライセンス・テーマ賞）
- [ ] w3id の PR（perma-id/w3id.org#6867）が通ったら RDF の URI を一度に差し替える
- [ ] 応募は 2026 年 12 月中（締切 2027-01-05）

## アイコンと共有画像（2026-10-13。2026-10-14 公開）

- [x] アイコン「R」（赤 #c8102e）と共有画像（日・英）を `~/git/tools/og-image` で作った。設定は `og-image.json`、出力は `docs/site/`（ビルドで `site/` にコピー）。全ページに og:* と twitter:card とアイコンのタグ
- [x] **公開する。** 2026-10-14 に公開（gh-pages 78bfc0b）。https://railclass.ldas.jp/ と /en/ の og:image（/site/og-ja.jpg・og-en.jpg）とアイコン（/site/icon.svg が 200）を確かめた
- [x] 形式のページの共有画像を、その形式の写真に替えた（2026-10-14、997786e、公開済み gh-pages 6ed1c17）。手元の写し `photos/<key>.webp`（330px）を使う。写真のある 10,402 形式が対象で、残り 3,944 形式はサイト全体の画像のまま。コモンズの 1280px を直接指す案は、Facebook の取得役が 403 で断られたのでやめた。12,195 枚を大きい JPEG にして置く案は、Pages の容量（1 GB）を超えるのでやめた
- [x] 公開して、Facebook・X などで形式のページを共有したときに写真が出るか確かめる（WebP を読めない SNS があれば、そこだけ考え直す）
  - 2026-10-14: 共有画面の見え方を試すサイト opengraph.xyz で、クリスタルムーバーのページ（https://railclass.ldas.jp/rdf/class/Q1685852.html）を確かめた。写真（photos/eb7d951052a6.webp、12 KB）は読み込めて、Facebook 風の表示に出た。指摘は 1 件で、画像が 330×247 と小さく、横長（1200×630、比 1.91:1）でないため、上下が切られるか余白が付くおそれがある。題名・説明が短いという注意 3 件は、そのままでよい
  - 2026-10-14: Facebook のシェアデバッガーでも確かめた。WebP の写真をそのまま取り込み、表示した。ただし大きな横長の画像ではなく、左に小さな正方形（158×158）が付く形になる。写真が 330px と小さいため。「fb:app_id がない」という警告は、Facebook アプリを使わないので無視してよい
  - これで完了とした（2026-10-14）。X での実表示は確かめていない。大きな画像で出したくなったら、そのとき 600px 以上（できれば 1200×630）の画像を用意する
