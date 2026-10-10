# 先行事例の調査: 鉄道車両の 3D モデルを Wikidata・Commons とつないだ集まり

## 2026-10-09

### 問い

鉄道車両（形式）の 3D モデルを、Wikidata の項目や Commons の写真と結びつけて集めたサイトは既にあるか。
あわせて、プラレール互換の車体を作るための台車・動力車の寸法が公開されていないか
（公開されていれば、実測は要らなかったか）。

### 測り方と結果

**Wikidata の P4896（3D model、Commons の STL ファイルを値に取る）**

- SPARQL（query.wikidata.org）で全件を数えた: 5,686 文、5,464 項目。
- 項目の P31/P279 の英語ラベルで分類。多い順に Unicode 文字 4,038、多面体 287、Johnson solid 181、
  考古遺物 171、彫刻 168、分類群 112 ……。
- ラベルに rail / train / locomotive / tram / wagon / carriage / multiple unit / railcar / shinkansen /
  metro / rolling stock を含むものを抜き出すと、**鉄道車両は 0 件**。
  当たったのは「railway track（線路）」1 件（`Eisenbahnschiene 20220828.stl`）と guard rail、clock だけ。

**Wikidata の Sketchfab 関連の属性**

- 3D モデル系の属性名を検索すると P4896 のほかに P14097（Sketchfab model ID）・P14098（channel）・
  P14099（user）がある。Thingiverse・Printables・MyMiniFactory の属性は無い。
- P14097 は 449 項目。城 145、砦 52、遺跡 46、考古遺物 29 など文化遺産が中心。**鉄道車両は 0 件**。

**Commons の STL ファイル**

- 検索 API（`filemime:application/sla`、名前空間 6）で総数 11,687 件。
- `train` 9 件、`locomotive` 21 件、`tram` 0、`railway` 0 件。
  当たったものは説明文の語に引っかかった骨格・彫刻・Wright Flyer などで、**鉄道車両の STL は見当たらない**
  （全文検索なので取りこぼしはありうる。カテゴリでの確認はしていない）。

**3D データの配布サイト（Web 検索経由。サイト内検索は JavaScript が要るため直接は叩いていない）**

- Thingiverse: プラレールの「きかんしゃトーマス」系の殻が数件（Duck を Percy の台車に載せる殻、Henry の部品、
  Gordon/James の炭水車の蓋など）。集約サイト stlfinder / yeggi 経由で見えただけで、個々の頁は未確認。
  外部の典拠（Wikipedia・Wikidata）への結びつけは見当たらない。
- MakerWorld: プラレール互換の**レール**は多い（1/4 直線、クロスなど）。車体は検索では出なかった。
- Printables: プラレール車体は検索で出なかった。
- 3D モデラボ（modelabo.net）: RX-44 氏「プラレール用 通勤型電車」1〜3 号車
  （https://modelabo.net/gallery/1841）。「プラレールの台車に乗せられる」とあるが、
  対応する台車の型・寸法・ライセンスの記載は無く、ダウンロードはログインが要る。
- Sketchfab: 鉄道車両のモデルは利用者の投稿として多数あるが、頁に Wikidata への結びつけは無い。
  カタルーニャ鉄道博物館の運転台を Sketchfab に載せた事例はある
  （UPC「An interactive museum, bringing railway heritage closer」
  https://upcommons.upc.edu/entities/publication/563f9bb2-06c8-4c0e-a91d-9e0698ecf5e1）。
- 日本の個人サイト: 「Plare Search」（http://plare.stlmaker.com/new/class.php）は改造・自作プラレールの
  リンク集（4WD 自作車、人車鉄道、関電トンネルトロリーバスなど）。STL や寸法の配布ではない。
- 個人ブログ: 3D プリントで連結器・レール・踏切を自作した記録は多い
  （temcee.hatenablog.com、jinsei-diy.com、mikiyoko.hatenablog.com、shibatano.jp など）。
  いずれも既存部品をノギスで測って作っており、**動力車・台車の取り付け寸法を公開した記事は見つからない**。
  2015 年に英国 Class 60 の車体を EF65 の台車に載せる企画（jnsforum.com）があったが、ファイルの公開は確認できない。
- タカラトミーの FAQ: 動力車のモーター単体は販売していない
  （https://faq.takaratomy.co.jp/detail.aspx?id=21578）。寸法の公式資料も見当たらない。

### 分かったこと

- 主張の候補: 鉄道車両の形式を Wikidata の項目に結びつけた 3D モデルの公開集は、調べた範囲では無い。
  Wikidata の 3D 系の属性（P4896・P14097、計 5,900 項目余り）に鉄道車両は 0 件
  （根拠: この日の SPARQL 集計）。
- 主張の候補: プラレール互換の車体を作るための台車・動力車の寸法は公開されておらず、
  個人の制作は手元の実物を測ることに依っている。写真からの採寸（skytrain の `tools/photo_measure/`）は、
  この空白を埋める手段として書ける。
- 配布サイトの互換車体は、キャラクター物（トーマス）の殻と、台車を特定しない通勤車が少数。
  寸法も、どの動力車に合うかも書いていない。仮に落として測っても、手元の動力車に合うかは結局確かめる必要がある。
- Commons は STL を受け付け、P4896 で項目に結べる。自前の車体を Commons に上げて P4896 に入れれば、
  鉄道車両で最初の例になる（意匠・商標の扱いは未確認）。

### 確かめていないこと（限界）

- Thingiverse・Printables・MakerWorld・Cults3D をサイト内検索で網羅していない（検索エンジン経由のみ）。
- Commons はカテゴリ（Category:STL files など）からの確認をしていない。glTF など STL 以外の形式も見ていない。
- 鉄道の塗装・編成のデータベース（Railcolor、vagonweb）、Europeana・Smithsonian の 3D 公開は未調査。
- 自分の既存リポジトリ（iiif-3d-viewer / iiif-3d-gallery）との関係は、データ設計のときに見る。
