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
- [ ] `assets/site.js` のヘッダ・フッタ差し込みを消す
- [x] Dependabot（cooldown つき）、Actions の SHA 固定、`npm audit`
- [x] Pages の配信元を切り替える（2026-10-09、Actions の残りが 0 のため `gh-pages` ブランチに。`zsh scripts/deploy-pages.zsh` を main で走らせて配る）
- [x] `docs/` の古い `index.html`・`view.html`・`assets/`・`search/index.html`・`search.js`・`search.css` を消す（2026-10-09）
- [ ] Actions の残りが戻ったら `pages.yml` の push の起動を戻し、配信元を Actions にするか決める

## 路線（地図の線）— 担当は未定。方針は `data-model.md` の「路線の線データ」

- [ ] 形式 → 路線の Wikidata ID の対応表を作る（Wikidata の P3438 を逆にたどる。足りない分は GTFS・Wikipedia から手で、出典つき）
- [ ] 対応表を RDF に入れる（A の形式の RDF に、路線へのリンクとして）
- [ ] 対象の路線のうち、OSM の route relation に `wikidata=` 札が付いている数を数える
- [ ] OSM の線を地図に出す方法を決める（表示のたびに Overpass か、事前に切り出すか。後者ならライセンスの扱いも）
- [ ] 線の形は train-bodies のデータに入れない（ODbL に縛られないため）。これを崩す案が出たら本人に確かめる

## 写真の保存と公開待ちの変更（2026-10-09 夜）

写真の保存（`tools/fetch_photos.py`）が終わるまで、コミットも公開もしない。終わったら本人に確かめてから進める。

- [ ] 写真の保存が終わったか確かめる（2026-10-09 21:53 で約 600 / 12,195 枚、1 分に約 85 枚、0 時すぎに終わる見込み。
      記録ファイルは空のままなので、`ls data/photos | wc -l` で数える。`data/` は git の管理外）
- [ ] 未コミットの変更を 2 つに分けてコミットする
      (1) 写真・検索: `tools/fetch_photos.py`・`tools/build_search.py`・`docs/search/index.json`・`web/scripts/sync-public.mjs`・`web/src/scripts/search.js`・検索と形式のページ
      (2) 文言と台座なし: 「プラレール」を外した注釈 `annotations/*.json`・`web/src/i18n/*.json`・README、作者の行の削除、台座を外して書き出し直した `docs/models/*.glb`・`docs/data/models.json`
- [ ] 本人の了承を得てから push し、`zsh scripts/deploy-pages.zsh` を main で走らせて公開する（未 push の 1462dbb・322eb5c も一緒に出る）
- [ ] 公開後に `/`・`/view.html`・`/search/`・`/en/`・形式のページ 1 つが開くか確かめる
- [ ] (2) には次も含める: `docs/thumbs/*.jpg`、作り直した `docs/iiif/*/manifest.json`（14 件）、`web/src/components/SiteFooter.astro`（作者の行）。
      注釈は「爪の穴より上」を「印刷用の版で開ける爪の穴より上」に、ICE TD の屋根の穴の説明も印刷用の版の話に直してある
- [ ] skytrain 側も別にコミットする: `lib.py`（`NO_MOUNT` でネジ受けの柱・屋根の切り欠き・後ろの爪穴を省く）・`build.py`（`--no-mount`、出力は `out/<モデル>/nomount/`）・
      `tools/gallery.py` と `tools/export_formats.py`（どちらも `--no-mount`。2 つとも未追跡のファイル）。旗なしは今までどおり穴あり（印刷用）
- [ ] 本人に確かめる: フッターの「© 2026 中村 覚」と、IIIF の提供者（`tools/build_iiif.py` の PROVIDER）「中村 覚（東京大学）」を残すか
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
