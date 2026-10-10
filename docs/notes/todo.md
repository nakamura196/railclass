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
- [ ] `docs/` の古い `index.html`・`view.html`・`assets/`・`search/index.html`・`search.js`・`search.css` を消す（検索を触る別セッションが終わってから）
- [ ] Actions の残りが戻ったら `pages.yml` の push の起動を戻し、配信元を Actions にするか決める

## 路線（地図の線）— 担当は未定。方針は `data-model.md` の「路線の線データ」

- [ ] 形式 → 路線の Wikidata ID の対応表を作る（Wikidata の P3438 を逆にたどる。足りない分は GTFS・Wikipedia から手で、出典つき）
- [ ] 対応表を RDF に入れる（A の形式の RDF に、路線へのリンクとして）
- [ ] 対象の路線のうち、OSM の route relation に `wikidata=` 札が付いている数を数える
- [ ] OSM の線を地図に出す方法を決める（表示のたびに Overpass か、事前に切り出すか。後者ならライセンスの扱いも）
- [ ] 線の形は train-bodies のデータに入れない（ODbL に縛られないため）。これを崩す案が出たら本人に確かめる
