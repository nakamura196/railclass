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

- [ ] ヘッダ: 探す・地図・データ（RDF / IIIF / ダウンロード）・このサイトについて・English
- [ ] ヒーロー: サイト名と一言、3D モデルを 1 つ回して見せる、検索窓
- [ ] 数字: 形式の数・3D モデルの数・国の数（RDF / 索引から生成し、手で書かない）
- [ ] できること: 形式を探す・地図から探す・3D で見る（部位の説明つき）・ダウンロード・データとして使う（RDF・IIIF）
- [ ] 新着モデル: カードで数件
- [ ] お知らせ: 日付つきの一覧。元データ `content/news.yaml`（初回は公開・LOD チャレンジ向けの整備開始など）
- [ ] このサイトについて・フッタ: 作者（中村 覚（東京大学））、ライセンス、非公式の注記（TOMY・DB・TransLink などの商標）
- [ ] 検索ページ: 絞り込み（項目は `docs/rdf/facets.json` から読む）、ページ送り、格子と一覧の切り替え、URL に条件を残す
- [ ] 地図から探す: navPlace（B の Manifest）を読んで地図に出す
- [ ] 形式の詳細ページ（RDF の中身を人が読める形で。3D・注釈・ダウンロードへのリンク）
- [ ] 画面の判断をノート `docs/notes/site.md` に
