# データモデルと収録範囲: 世界の鉄道車両の形式を集めるサイト

## 2026-10-09

### 目標

LODチャレンジ2026（締切 2027-01-05、データ作成部門を想定）に向けて、train-bodies を
「世界の鉄道車両の形式の情報を集めたサイト」に育て、そこへ自作の 3D モデルを足していく。
本人の指示: Wikipedia・Wikidata に無い形式も網羅する。日本は除く。

### 設計の骨組み（叩き台）

- 記録を 4 種類に分ける: 形式（class、Wikidata の Q か自前の ID）、塗装（livery、自前の ID）、
  3D モデル（形式 1 つ × 塗装 1 つ）、写真（Commons のファイル名。形式・塗装を写すものとして結ぶ）。
- Wikidata に形式の項目が無いとき（SkyTrain Mark I〜V）は、近い項目に「より広い」と明示して結ぶ
  （skos:broadMatch 相当）。ラベル・説明・写真の作者とライセンスは手で写さず、生成時に API から取る。
- 理由: 1 つの形式に複数の塗装のモデルがある（ICE TD の DB と DSB）。1 両を 2 体に分けたモデルもある（49 番バス）。

### 実測（Wikidata Query Service、この日）

- P31 = rolling stock class（Q811704）は 6,820 項目。うち P18（画像）あり 5,103、P373（Commons カテゴリ）あり 4,058、
  日本語版 Wikipedia あり 3,179、P17（国）あり 1,907、P137（運行者）あり 4,873。
- P279 の上位: electric multiple unit 2,169、diesel multiple unit 634、tank car 275、passenger railroad car 253、
  subway car 222、tram 207、high-speed train 74。
- P17 の上位: Japan 376、Germany 203、United States 119、United Kingdom 109、Switzerland 106、France 99。
- P17 の無い 4,913 項目のうち、Wikipedia の記事が日本語版だけのものが 1,576（ほぼ日本の車両とみられる）、
  どの言語の Wikipedia にも記事が無いものが 165。
  → 「日本を除く」は P17 だけでは決められない。運行者の国と、記事の言語も使う必要がある。
- 既存モデルの形式の分類: ICE T・ICE TD・AVE 102・Innovia Metro は Q811704 の実例。
  Airo（Q140611223）は railway rake（Q3418429）の実例で、Q811704 ではない。XD60 は bus model。
  → Q811704 だけで集めると Airo が漏れる。

### Wikipedia・Wikidata に無い形式の出典

- 第一候補: EU 鉄道庁（ERA）の車両型式登録（ERATV）。ERA の知識グラフとして公開され、2,000 型式以上を収める
  （ERA vocabulary https://github.com/Interoperable-data/ERA_vocabulary、
  data.europa.eu の解説 https://data.europa.eu/sl/publications/datastories/linking-data-route-compatibility-check）。
- https://graph.data.era.europa.eu/sparql は応答するが、GET は Accept をどう指定しても 406、POST は 405。
  正しい使い方（または一括ダウンロード）は未確認。
- 欧州以外（北米など）は、事業者の車両一覧から自前の記録を起こす見込み。

### 主張の候補

- 人文情報学の目録・典拠の技法（記述の粒度の階層、近いだけの一致の明示、出所の記録）は、
  鉄道車両という分野違いの対象でも設計の骨組みになる。根拠にする実測: Wikidata で国の無い 4,913 件のうち
  他の出典で何件補えたか、形式の段に項目の無い車両の件数（未測）。

### 決めていないこと

- 機関車と客車を範囲に入れるか（入れることを推奨。Airo が客車のため）。

### ERA の車両型式を取り出す（この日、続き）

- **ERA の知識グラフには、車両型式（era:VehicleType）の実体がまだ無い。** graph.data.era.europa.eu は
  GraphDB（RDF データベース製品）で、`/sparql` は画面だけ。問い合わせ先は `/repositories/<名前>`。
  公開されている 4 つ（rinf-plus・ERA-Onto・era-lex・OCR-KG）のどれにも era:VehicleType の実体は 0 件。
  era:VehicleType はオントロジー（ERA-Onto）に「クラス」として定義があるだけ。
  ERA の説明ページ（https://www.era.europa.eu/domains/registers/era-knowledge-graph）でも、
  ERATV は「Migration ongoing」（移行中）。→ 前回の 406・405 は使い方の誤りで、使い方を直しても型式は取れない。
- **代わりに、ERATV の画面の「Export list」で全件が取れる。** 一覧の画面（https://eratv.era.europa.eu/ERATV/Home/List）を開いて
  cookie と送信用の合言葉（__RequestVerificationToken）を受け取り、検索フォームを `/Eratv/Home/Export?exportTo=2`（XML）に送る。
  法令の区分ごとに別の一覧になっている: 指令 2016/797 の下で 2,603 件、それより前の区分で 1,816 件、重なり 0、計 4,419 件。
  取れる項目は 型式 ID・型式名・認可文書番号（EIN）・認可の状態・最終更新日 の 5 つだけ。
- **詳細ページは取らない。** 2 件目から CAPTCHA（人間かどうかの確認）が出る。製造者・別名・区分・プラットフォーム
  （例: Flirt LEX → 別名 RABe 522、Stadler、プラットフォーム FLIRT）は詳細ページにしか無い。
- **型式 ID の先頭 2 桁が区分（subcategory）。** 対応表は ERA-Onto の SKOS（用語集）にある
  （`vehicle-types/SubCategories`、26 区分）。一覧にある 23 種の先頭 2 桁のうち、`37` だけ表に無い（1 件）。
  ID の 5・6 番目の組は版（version）と枝番。先頭 4 組を「型式」とみなすと 3,295 型式になる。
- **Wikidata には ERATV の型式 ID を入れる属性が無い。** 近いのは P14109（European Vehicle Number）だが、これは 1 両ごとの番号。
  → 結び付けは名前の照合に頼るしかない。
- 区分別（3,295 型式）: 旅客用の動力分散編成 873、機関車 797、貨車 605、自走の保守用車 342、客車 316、牽引される保守用車 163、
  軌道作業機械 119、入換機 21、ほか。
- **ERATV の再利用条件は未確認。** Terms of Use（https://www.era.europa.eu/system/files/2022-11/eratv_terms_of_use_en.pdf、V1.6）は
  登録する側の約束だけで、取り出したデータの再利用には触れていない。公開前に ERA の Copyright Notice を確かめる。
  それまで `data/` はコミットしない。

### Wikidata と合わせた一覧（この日）

- Wikidata の母集団を「P31 が rolling stock class（Q811704）**またはその下位クラス**」に広げた。6,820 → 17,193 項目。
  増えた分の大半は locomotive class（Q19832486）8,593 と tram model（Q76154857）1,049。
  機関車を範囲に入れる既定（「決めていないこと」）に合わせた。
- 日本の除き方: 国（P17）と運行者の国（P137 → P17）のうち、分かっているものが全部日本なら除く（2,522）。
  国が 1 つも分からず、Wikipedia の記事が日本語版だけなら除く（353）。残り 14,318。
- ERATV の型式名と、Wikidata のラベル・別名（欧州の 23 言語と mul）を、大小文字・記号・空白を無視した完全一致で照合した。
  一致は 134 型式（3,295 の 4%）、複数の項目に当たったもの 15。当たった Wikidata 項目は 124。
  見た範囲では当たりは正しい（例: RABe 501 → Q16798908、ETR 470 → Q668075、TEM2 は 2 項目に当たる）。
- **完全一致では、既存モデルの形式が 1 つも結べなかった。** ICE T は ERATV に「ICE T BR 411 ETCS BL3」
  「ICE T BR 415 ETCS BL3」、ICE TD は「BR 605 ETCS Guardia」、AVE 102 は「Serie 102」で載っている。
  ERATV の名前は改造・装置の版（ETCS BL3 など）を付けた「認可の単位」で、Wikidata の「形式」より細かい。
  → 型式と形式は 1 対 1 ではなく、多対 1（skos:narrowMatch 相当）として結ぶのが筋。照合の改善は次の課題。
- 一覧は `data/classes.tsv`（17,613 行 = Wikidata 14,318 + ERATV 3,295）。ERATV だけの行（名前で Wikidata に当たらないもの）は 3,161。
  この 3,161 が「Wikidata に無い形式」の上限の目安。名前の照合が粗いので、本当に無いものはこれより少ない。

### データ作成の流れ（申請書に使う。手順が増えたら書き足す）

1. **範囲を決める**（この日）: 日本を除く世界の鉄道車両の形式。Wikipedia・Wikidata に無い形式も含める。
2. **Wikidata から形式の母集団を数える**（この日）: `python3 tools/sparql.py < tools/queries/<name>.rq`。
   使った問い合わせ: `wd-class-counts.rq`（総数と各属性の充足）、`wd-class-by-type.rq`（種類別）、
   `wd-class-by-country.rq`（国別）、`wd-class-no-country.rq`（国の無い項目の内訳）。結果は上の「実測」。
3. **Wikidata に無い形式の出典を探す**（この日、途中）: ERA の知識グラフ。取り出し方は未確認。
   → 結論（この日）: ERA の知識グラフには型式がまだ無い。ERATV の画面の一覧出力で取る（下の 4）。
4. **ERATV から型式の一覧を取る**（この日）: `python3 tools/eratv_export.py` → `data/eratv/eratv-2016.xml`・`eratv-pre2016.xml`・`eratv.tsv`。
   区分の対応表: `python3 tools/sparql.py https://graph.data.era.europa.eu/repositories/ERA-Onto < tools/queries/era-subcategories.rq > data/eratv/subcategories.tsv`。
5. **Wikidata の形式の一覧を取る**（この日）: `python3 tools/sparql.py < tools/queries/wd-classes.rq > data/wikidata/classes.tsv`（項目・種類・国・運行者の国・記事の言語）、
   `python3 tools/sparql.py < tools/queries/wd-class-names.rq > data/wikidata/class-names.tsv`（照合用のラベルと別名）。
   この日に `tools/sparql.py` を直した: 1 行目に列名を出し、値の無い列を空欄で残す（以前は空の列が詰まって列がずれた）。接続先を引数で替えられる。
6. **合わせて日本を除く**（この日）: `python3 tools/build_classes.py` → `data/classes.tsv`。日本の除き方と照合の仕方はスクリプト冒頭と上の「Wikidata と合わせた一覧」。

### 位置付けと並行作業の取り決め（この日、本人の指示を受けて）

本人の指示: データベースとしてトップページと検索ページを充実させる。各モデルを IIIF Presentation 4.0 で記述し、
`seeAlso` で RDF に結ぶ。navPlace で地図からも探せるようにする。アノテーションで部位と特徴を説明する。
位置付けは 2 つ: (a) 鉄道車両の形式のデータベースを RDF にする利点を示す、(b) IIIF v4（3D 対応）の実例にする。

- 主張の候補: 3D の IIIF Manifest（見せる層）と形式の RDF（記述する層）を `seeAlso` で分けて結ぶと、
  形式の典拠（Wikidata・ERATV）を Manifest に書き写さずに済み、典拠側の更新がそのまま生きる。根拠の実測は未。
- 主張の候補: IIIF v4 の 3D シーンに部位のアノテーションと navPlace を載せた、文化財以外（工業製品・交通）の実例。
  先行例の有無は未調査（prior-art.md に足す）。

URI の取り決め（3 つのセッションで共有する。変えるときはこの節に日付付きで書き足す）:

- 基点: `https://nakamura196.github.io/train-bodies/`（リポジトリの `docs/` が公開される）
- 形式の RDF: `docs/rdf/class/<cid>.ttl` と `.jsonld`。`<cid>` は Wikidata にある形式なら Q 番号、
  ERATV の型式なら `era-<型式 ID の先頭 4 組>`、どちらにも無いもの（SkyTrain Mark I など）は `tb-<短い英字>`
- モデルの RDF: `docs/rdf/model/<model-id>.ttl` と `.jsonld`。`<model-id>` は今のギャラリーの ID（`mk1`・`icet_411`・`bus49_front` など 14 個）
- IIIF Manifest: `docs/iiif/<model-id>/manifest.json`。`seeAlso` でモデルの RDF と形式の RDF を指す
- 検索用の索引: `docs/search/` の下（中身の形は検索の担当が決める）
- **ERATV 由来のデータは、再利用条件を確かめるまで `docs/` に入れない。** Wikidata は CC0 なので入れてよい

担当（触るファイルが重ならないように分ける）:

- A. RDF: `tools/build_rdf.py`、`docs/rdf/**`、この `data-model.md`
- B. IIIF: `tools/build_iiif.py`、`docs/iiif/**`、`annotations/**`（部位・特徴の説明の元データ）、`docs/notes/iiif.md`
- C. 画面: `~/git/3d/skytrain/tools/gallery.py`・`gallery_template.html`（トップページを生成する）、`docs/search/**`、`docs/notes/site.md`
- 追加の指示（同じ日）: CAD を含むいろいろな形式でダウンロードできるようにする。
  → B の担当に `docs/downloads/<model-id>/`（形式ごとのファイル）と、それを作る `~/git/3d/skytrain/tools/export_formats.py` を足す。
  Manifest からは `rendering` で指す。注意: 今のモデルは Blender のメッシュ（面の集まり）なので、STEP に入れても
  「面を貼っただけの STEP」で、CAD で寸法を直せる立体にはならない。正直に書き分ける。
- 似た先行例（本人の指摘）: ArchiveBase の「軍艦3D復元アーカイブ」（https://ab.ldas.jp/、17 点）。
  平賀譲の線図から主要目と中央断面の実測値を入力に、パラメトリックに艦の 3D を復元し、GLB で公開している。
  共通点: 資料から寸法を取り、手続き的に立体を起こし、データベースとして公開する。
  違い: 軍艦は 1 隻ごとに一次資料（線図）に結ぶ。train-bodies は形式の典拠（Wikidata・ERATV）に結び、
  1 つの形式に塗装ごとのモデルが付く。玩具の車台に合わせて形を変えている（実物の縮尺模型ではない）。
- 追加の指示（同じ日）: 検索ページは、RDF で定義した項目に基づいて、いろいろな観点で絞り込めるようにする。
  → 順番の取り決め: **A が最初に、形式の RDF で使う項目（属性）の一覧を `docs/rdf/facets.json` に出す**
  （項目の URI・日本語と英語の名前・値の型。候補は種類・国・運行者・製造者・軌間・電化方式・最高速度・製造年・軸配置）。
  C はこれを読んで絞り込みの項目を作り、手で項目を書き並べない。A が出すまで、C は画面の作りと索引の仕組みを先に進める。
- 追加の指示（同じ日）: 検索結果にページ送りと、格子表示（grid）・一覧表示（list）の切り替えを付ける。→ C の担当。
