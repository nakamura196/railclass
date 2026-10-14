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
- 2026-10-11 決定（未実施）: 「もの」の URI を w3id に移す。名前は `railclass`。
  `https://w3id.org/railclass/class/<cid>`・`/model/<id>`・`/vocab#<term>`、データセット全体は `https://w3id.org/railclass/`。
  w3id の転送で、求められた形式（Turtle / JSON-LD / HTML）に振り分ける。GitHub Pages ではこれができないのが移す理由。
  IIIF の Manifest の `id`（ファイルの置き場所）は変えない。ビューアが直接取りに行くので、転送と CORS を挟まない。
  - 却下した名前: `train-bodies`（中身の大半は 14,325 件の形式で、3D は 14 点。名前が中身を表さない）、
    `3d-train`（同じ理由）、`trains`・`rail`（一般的すぎて w3id で断られるおそれ）、`rail-cls`（1 文字短いだけで、`cls` が読めない）。
    候補はどれも w3id で未使用だった（GitHub の perma-id/w3id.org を 2026-10-11 に確認）
  - 今の公開状態で分かったこと: 形式の HTML は `rdf/class/<cid>`（末尾の `/` なし）。`vocab` と `rdf/`（概念体系の URI）は 404 で、
    今の URI は引けない。`vocab.jsonld` は無い
  - 全 28,650 ファイル（138MB）が書き換わるので、URI の差し替えは 1 回で済ませる
  - 同日の修正: `railclass/class/` は class が重なる（本人の指摘）。形式は名前の直下に置く。
    `https://w3id.org/railclass/<cid>`（例 `/Q1200438`）、モデルは `/model/<id>` のまま。
    形式の ID は `Q` 番号 14,321 件と `tb-` 4 件だけで、`era-` を含めても、`model`・`vocab` とも今のモデル ID とも重ならない。
    これからモデル ID を付けるときは、`Q` で始めない・`era-`/`tb-` を付けない
  - 同日実施: GitHub のリポジトリ名を `railclass` に変え、サイトは `https://nakamura196.github.io/railclass/` に移った（1ad8754）。
    表示名も「RailClass」に。IIIF の `id`・`annotations/` も新しいアドレスにした（build_iiif.py で作り直した結果と一致を確認）。
    旧アドレス `…/train-bodies/` は 404（GitHub Pages は転送しない）。RDF の URI は旧アドレスのままで、w3id への切り替えまで引けない。
    手元のフォルダ名は `~/git/3d/train-bodies` のまま
  - w3id の出し方が変わっていた（2026-10-11 に README で確認）: 置き場所が直下ではなく `ids/<名前>/.htaccess`。
    前回の申請（perma-id/w3id.org#6804、histact、2026-10-04）でも管理者から「`ids/` の下へ移して」と言われていた。
    PR には自動の点検が走る。手元でも `node tools/check/bin/w3id-check.js ids/<名前>` で同じ点検ができる。
    `.htaccess` の冒頭のコメントに連絡先と GitHub のユーザー名を書く決まり。`ids/railclass` も未使用だった
  - 同日、申請を出した: perma-id/w3id.org#6867（`ids/railclass/.htaccess` と `README.md`）。自動の点検は通過。
    手元の Apache（macOS 付属。w3id の Docker 環境はネットワークの空きが無く起動できなかった）で、
    形式・モデル・語彙・全体 × HTML/Turtle/JSON-LD の転送先を確認し、転送先がすべて 200 で正しい形式を返すことも確かめた。
    `run-server` を macOS の Apache で動かすには `W3ID_ALLOW_SYSTEM_HTTPD=1 W3ID_MODDIR=/usr/libexec/apache2 W3ID_MIMETYPES=/private/etc/apache2/mime.types` が要る。
    語彙は Turtle しか無いので、`/vocab` は常に Turtle を返す。取り込まれたら、RDF の URI を一括で差し替える

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

### 担当 A: 絞り込みの項目と、形式・モデルの RDF（この日）

- `docs/rdf/facets.json` を先に出した（C の提案した形をそのまま採用）。項目は 10: 種類 P279・国 P17・運行者 P137・製造者 P176・
  軌間 P1064・電化方式 P930・軸配置 P2978・最高速度 P2052（km/h）・営業開始年 P729（gYear）・3D モデルあり（自前の語彙）。
  - **述語は Wikidata の属性（wdt:）をそのまま使う。** 自前の属性を作って Wikidata に対応付ける案は却下。
    C が Wikidata から全 1.4 万形式の値を取るとき、同じ URI のまま突き合わせられるため。
  - 種類は P31 でなく P279。形式はどれも P31 が rolling stock class で、P31 では分かれない。
  - **`inherit`（上位の形式から値を借りる）を項目ごとに付けた。** Wikidata は下位の形式に値が無いことが多い
    （DBAG Class 411 に製造者が無く、ICE T にはある）。値は RDF に書き写さず、skos:broader をたどって索引側で補う。
    書き写すと「Wikidata に書いてあること」と「こちらが推した値」の区別が消えるため。運行者と営業開始年は下位で違うので借りない。
- 実測: Wikidata で P31 が rolling stock class とその下位クラスの項目のうち、各属性を持つ項目数（この日）。
  P279 14,451・P176 12,289・P137 12,107・P1064 10,428・P2978 7,624・P17 7,436・P729 4,883・P2052 3,922・P930 1,901・P571 357。
  → 製造年は P571（inception）ではなく P729（service entry）を使う。
- `tools/build_rdf.py` → `docs/rdf/`。形式 13（Wikidata 9・自前 4）、モデル 14、全体 731 トリプル。
  - 形式: `rdf/class/<cid>`（skos:Concept かつ tb:VehicleClass）。Wikidata の項目へは skos:exactMatch、
    SkyTrain Mark I〜V のように項目の無いものは skos:broadMatch（Innovia Metro Q4940487）と、データ内の skos:broader。
    Innovia Metro 自体もデータ内の形式として置いた（Mark I〜V が値を借りる先にするため）。
  - モデル: `rdf/model/<model-id>`（schema:3DModel）。schema:about で形式、tb:livery で塗装（`#livery`、持ち主は tb:liveryOf）、
    schema:subjectOf で IIIF Manifest（B の URI 取り決めどおり）、寸法は mm の QuantitativeValue。
    名前と説明はギャラリー（docs/index.html の DATA）から読む。
  - 各ファイルは .ttl・.jsonld・.html の 3 つ。GitHub Pages は拡張子なしの `/rdf/class/Q696668` に `.html` を返すので、
    URI を開くと人が読める頁が出る（内容の交渉はできないので、機械向けには `<link rel="alternate">` で .ttl と .jsonld を指す）。
  - `docs/rdf/all.ttl`・`all.jsonld` に全部と、値に使った Wikidata 項目の名前（ja・en）を入れた。C はここから値の名前を読む。
  - Wikidata の答えは `data/wikidata/rdf-cache.json` に取っておく（data/ は git 管理外）。`--refresh` で取り直す。
- 手入力した値（tb:handEntered でどの属性かを示し、dcterms:source に出典）: SkyTrain Mark I〜V の国・運行者（Wikidata Q876780 から）、
  製造者（英語版 Wikipedia「SkyTrain (Vancouver)」の車両の節: Mark I は UTDC、II・III は Bombardier、V は Alstom）、
  営業開始年（ギャラリーの説明文: 1985・2002・2016。Mark V は未確認なので入れていない）。
  日本語名の無い形式 5 つ（411・415・ÖBB 4011・Airo・XD60）は日本語名を手で付けた（Wikidata に付いたらそちらを使う）。
- 途中で分かったこと:
  - Wikidata の Q688893 のラベルは今「ALSTOM Transportation Germany」（旧 Bombardier Transportation）。英語版 Wikipedia の
    「Bombardier Transportation」もこの項目に結ばれている。Mark II・III の製造者はこの項目で表す。
  - ICE TD（Q659660）の製造者に Alstom が入っている（Siemens・Bombardier と並んで）。Wikidata の値のまま載せた。
  - Airo には国が無い（運行は米国とカナダ）。手で補っていない。
  - 速度は Wikidata の正規化値（m/s）× 3.6 で km/h に揃えた。マイル毎時で入った項目もこれで揃う。
  - rdflib で Turtle と JSON-LD を読み直すと 731 トリプルずつで、違いは小数の書き方（230.0 と 230）だけ。
- 決めていないこと: モデルと RDF の利用条件（ライセンス）。LOD チャレンジでは明記が要る（無ければパブリックドメイン扱い）。本人の判断。
- 主張の候補: 典拠（Wikidata）に無い値を写さず、skos:broader で上位の形式から借りる、と索引の側で明示すると、
  典拠の不足を補いつつ出所の区別を保てる。根拠: 上の 411 の製造者の例（数を測るのは C の索引ができてから）。

### 路線の線データ（この日、本人と決めた）

地図に「その形式が走る路線」を線で出したい。線の元を調べ、取り込み方を決めた。

- 実測（Wikidata Query Service、この日）: 手持ちのモデルの形式 10 件について、
  「この路線で使う車両」（P3438）でたどれる路線の数を数えた。
  AVE Class 102 が 2、Innovia Metro が 2、Siemens Venture が 1。ICE T・411・415・ÖBB 4011・ICE TD・Airo・XD60 は 0。
  そのうち路線の形（P3896、Commons の geoshape）を持つものは 0。
  → Wikidata は「どの路線か」をたどる元にはなるが、線を描く元にはならない。
- 候補にした線の元（どれも GeoJSON にできる）:
  - OpenStreetMap: 路線が route relation でまとまり、多くに `wikidata=Q…` の札が付いている。Overpass API で取り GeoJSON にする。
    網羅と精度はいちばん高い。ライセンスは ODbL（派生データベースは同じ条件で公開）。
  - 運行会社の GTFS: 中の shapes.txt に走る線の形がある。TransLink・Amtrak などが公開。どの路線をどの車両で運行するかが公式に分かる。ライセンスは会社ごと。
  - Natural Earth の鉄道: パブリックドメインだが大まかで、路線名も ID も無い。背景用。
  - ERA の RINF（EU の鉄道設備の登録簿、ERA KG の中）: EU の線路網と駅の位置。再利用条件は未確認。
- 決めたこと:
  - **線の形（座標）は train-bodies のデータに入れない。** 地図を出すときに OSM からその場で読む（または表示用に別に置く）。
    手元のデータが ODbL に縛られず、ライセンスを本人が自由に決められるようにするため。
  - **データに入れるのは「形式 → 路線の Wikidata ID」の対応だけ。** 土台は Wikidata の P3438（路線 → 車両）を逆にたどったもの。
    足りない分は GTFS・Wikipedia から手で補い、出典を付ける。路線から線へは OSM の `wikidata=` 札で結ぶ。
- 却下した案: OSM の線を GeoJSON にして docs/ に置く（ODbL がデータ全体の条件に関わる。OSM の更新にも追従できない）。
  Natural Earth だけで描く（路線を区別できない）。
- 確かめていないこと: 対象の路線に OSM で `wikidata=` 札がどれだけ付いているか（数えていない）。
  OSM の線をその場で読む方法（Overpass を表示のたびに叩くと重い・止められるおそれ。事前に切り出して置く場合のライセンスの扱い）。
  IIIF の navPlace に入れるのは運行地域の面か、路線の線か（B と相談）。

### 担当 A: 絞り込みに「色」を足す（この日、本人の指示を受けて）

- 指示: 色を、モデルの塗装ごとの値として、skytrain の各モデルの塗り分けの色から自動で取り出し、赤・青・黄などの名前に寄せる。
- `facets.json` に 11 番目の項目 `color`（色、wdt:P462 color、値は Wikidata の色の項目）を足し、version を `2026-10-09b` にした。
  - **全項目に `on` を付けた。** 今までの 10 項目は `class`（形式の RDF に値がある）、色だけ `livery`（各モデルの塗装に値がある）。
    同じ形式でも塗装で色が違う（ICE TD は DB の赤帯と DSB の紺）ので、形式に色を書くと区別が消える。
    検索では「形式のどれかのモデルが当てはまれば、その形式が当てはまる」とする（`schema:subjectOf` → `tb:livery` → `wdt:P462`）。
  - 述語は他の項目と同じく Wikidata の属性をそのまま使う（P462）。色の名前も Wikidata の項目（赤 Q3142・青 Q1088・黄 Q943・
    緑 Q3133・白 Q23444・黒 Q23445・灰 Q42519・茶 Q47071・紫 Q3257809・橙 Q39338・桃 Q429220）。名前（ja・en）は Wikidata から取る。
- `tools/extract_colors.py` → `tools/livery_colors.json`（git に入れる。RDF の生成に skytrain の作業ツリーを要らなくするため）。
  - 取り方: `skytrain/out/<model-id>/*.obj` と `.mtl`。面は、それを作った切り抜きの材質（= 名前付きの色）を持っているので、
    **材質ごとの面積が、そのまま車体の上の色の面積になる。** ガラス・灯火・扉の溝・タイヤ・幌は塗装ではないので除き、残りを塗装面とした。
  - 名前への寄せ方: sRGB の彩度の幅（最大−最小）が 0.12 未満なら白・灰・黒（明るさ 0.85 超が白、0.15 未満が黒）。
    それ以外は色相で赤・橙・黄・緑・青・紫・桃に分け、くすんだ暗い赤〜橙（色相 345〜50°、彩度の幅 0.35 未満、明るさ 0.6 未満）は茶。
  - 塗装面の 1.5% 以上を占める名前だけを残した（それより小さいのはロゴ・灯火・番号）。正確な色は `tb:colorSample`
    （`schema:color` の #RRGGBB と `tb:areaShare`）として塗装に付けた。
- 実測（塗装面に占める割合）: Mk I 灰 74.4・青 20.2・黒 4.1。Mk V 青 85.5・黒 12.6。ICE T 411 白 86.7・灰 5.5・黒 5.0・赤 2.8。
  ICE T 緑帯 白 86.7・灰 5.5・黒 5.0・緑 1.7。DSB 白 81.7・青 8.6・灰 5.1・黒 4.3。Airo 緑 67.8・灰 15.1・白 7.0・茶 5.9・黒 4.1。
  AVE 102 白 85.6・灰 6.7・紫 4.2・黒 3.3。バス 前 青 84.6・灰 7.1・黒 6.7。
  形式の数で数えると（モデルのある 12 形式、all.ttl に SPARQL）黒 12・灰 11・白 7・青 6・赤 4・緑 2・茶 1・紫 1。
- 途中で分かったこと:
  - 最初に三角形 1 枚分だけで面積を測ったら、Mk I の青が 7.5%（正しくは 20.2%）と出た。OBJ は三角形に分けて書き出す設定だが、
    四角以上の面が残っている。多角形は扇形に分けて足す。
  - Airo の「brown2」（#4A2C24）は色相 12° で、色相だけでは赤に入った。暗くくすんだ色を茶に寄せる条件を色相の前に置いた。
  - SkyTrain の黄（扉の縁など）は塗装面の 0.7〜1.1% で、1.5% の線で落ちる。「黄で探すと SkyTrain が出ない」のは、この線の結果。
  - main に入ったトップページの作り替えで、ギャラリーの DATA が `docs/index.html` から `docs/data/models.json` に移っていて、
    `build_rdf.py` が動かなくなっていた。読み先を直した。あわせてモデルの `schema:url` を `view.html#<model-id>` に直した。
- 確かめていないこと: 黒と灰は、窓まわりの黒や床下・屋根の灰が多く、ほとんどのモデルに付く。絞り込みとして効くのは
  「主な色」だけかもしれない。割合の大きい順に並べてあるので、C が「主な色（最大の割合）」だけで絞る使い方もできる。
- 主張の候補: 3D モデルの面の材質の面積から塗装の色を数値で取り出し、典拠の色の項目（Wikidata）に寄せると、
  「赤い帯の車両」のような見た目での検索が、人手で色を付けずにできる。根拠: 上の実測（14 モデル、手作業なし）。

### 色の絞り込みを画面で確かめ、白・灰・黒の扱いを決めた（この日、本人と）

- 検索ページの索引（`docs/search/index.json`）には、RDF に色を入れた後も色が入っていなかった。`build_search.py` が
  `on: livery` を知らなかったため。形式の色 = その形式のモデルの塗装の色を合わせたもの、として読むようにした。
- 画面で見ると（3D モデルのある 12 形式）黒 12・灰 11・白 7・青 6・赤 4・緑 2・紫 1・茶 1。黒・灰を選んでも絞れない。
- モデルごとの割合を並べると、白・灰・黒は 2 つの群にはっきり分かれた。車体の地の色として 69〜87%、
  窓まわり・床下・屋根として 3〜15%。16〜68% は 1 つも無い。帯の色（赤・緑・紫など）は 1.7〜8.6% だが、探したいのはこちら。
- 決めたこと: **白・灰・黒は塗装面の 20% 以上のときだけ色に入れる。** ほかの色は今までどおり 1.5% 以上。
  線は `extract_colors.py` に置いた（RDF の `wdt:P462` も検索も同じ値になる）。小さい白・灰・黒も、
  正確な色と割合は `tb:colorSample` に残す。
- 結果: 白 7・青 6・赤 4・灰 3（Mk I〜III）・緑 2・紫 1・茶 1、黒 0。赤を選ぶと ICE T の 4 形式が出る。
  変わったモデル: Mk V は青だけ（黒 12.6% が落ちる）、Airo は緑・茶（灰 15.1%・白 7.0% が落ちる）。
- 却下した案:
  - 主な色（最大の 1 色）だけ: 赤・緑・紫の帯がすべて消え、「赤い帯で探す」ができなくなる。
  - 「主な色」と「差し色」の 2 項目: 項目が増え、差し色の側に窓まわりの黒がまた全部に付く。
- 確かめていないこと: 20% の線は 14 モデルで決めた。灰の屋根が広い車両や、黒が地の色の車両が増えたら見直す。

### 訂正: 白の形式の数（この日、公開後に確かめて）

- 上の 2 か所で「白 7」と書いたが、正しくは **白 6**。公開した `search/index.json` で数え直した。
  ICE TD の形式には `icet_td` と `icet_dsb` の 2 モデルが付いており、形式としては 1 つに数える。
  数え直した結果（3D モデルのある 12 形式）: 白 6・青 6・赤 4・灰 3・緑 2・紫 1・茶 1。赤は ICE TD・ÖBB 4011・411・415 の 4 形式。

## 2026-10-10

### 路線の線: 事前に切り出して別の層で公開する（本人と決めた）

- 10-09 の「却下した案: OSM の線を GeoJSON にして docs/ に置く」を改めた。**線は事前に切り出し、`docs/lines/<Q>.geojson` として公開する。**
  ただしデータ（RDF・検索の索引・`tools/class_lines.tsv`）には座標を入れない。線は地図を描くための別の層とし、
  `docs/lines/README.md` と地図の下に「© OpenStreetMap contributors（ODbL）」を書く。データ全体が ODbL に縛られない、という 10-09 の狙いはこれで保てる。
- 表示のたびに Overpass を叩く案は、やめた。実際に 10-10 の昼、本家（overpass-api.de）は 504 が続き、1 本目の路線も取れなかった。
  閲覧者のたびにこれが起きると地図が出ない。道具に `--api` を足し、公開ミラー（maps.mail.ru）で切り出した。
- 形式のページの「走る路線」: 地図（Leaflet 1.9.4、背景は OSM のタイル）と一覧。線の無い路線は「地図なし」として一覧にだけ出す。
  運用を外れた路線は点線で薄く描く。

### 形式 → 路線を RDF に入れた

- 形は 2 段にした。`cls:<形式> tb:usedOn wd:<路線>`（ふつうの問い合わせ用の直のリンク）と、
  `tb:lineUse` → `tb:LineUse` の節点（`tb:line`・`tb:useStatus`（current / historical / unknown）・`tb:usedUntil`（xsd:gYear）・
  `dcterms:source`・`tb:sourceSection`・`tb:inferred`・`skos:note`）。状態と出典は路線ごとに違うので、直のリンクだけでは持てない。
- `tb:usedOn` は Wikidata の P3438（路線 → 使う車両）の逆向きだが、`owl:inverseOf wdt:P3438` とは書かなかった。
  こちらの主語は train-bodies の形式（Wikidata の項目とは `skos:exactMatch`）で、主語が同じではないため。説明文で逆向きと書くにとどめた。
- 却下した案: 1 本に行を潰して `tb:usedOn` だけにする（廃止の路線と今の路線が区別できない。INFERRED の 16 行も見えなくなる）。
- 実数: 50 行のうち路線のある 49 件が入った（49 番バスの 1 行は路線の項目が無い）。42 路線、全体で 2,100 トリプル。
  路線の英語名は表の lineLabel から `rdfs:label` として入れた（日本語名は無い）。

### デグレ: 路線の節点で形式のページが空になった（同じ日、本人の指摘で）

- 路線を RDF に入れたあと、形式のページから名前・Wikidata のリンク・3D のビューアが消えた（例: Allegra）。組み立ては通っていた。
- 原因: 形式の JSON-LD が 1 つの節点から `@graph`（形式と LineUse の節点）に変わり、ページ側（`web/src/lib/classes.ts`）が
  ファイル全体を形式の節点として読んでいた。形式の節点を `@graph` から `@id` で選ぶようにした（d816cc1）。
- 再発を防ぐため、組み立てた結果を元データと突き合わせる点検 `web/scripts/check-dist.mjs`（`npm test`）を足し、公開の手順に入れた（1ecd679）。
  正解はページと別の読み方で取る（3D モデルと名前は Turtle から、路線は `class_lines.tsv` と `docs/lines/` から）。
  直す前の `classes.ts` で組み立てると 97 件の失敗を出すことを確かめた。

### 訂正: 緑帯の ICE T の模型の形式（同じ日、9:50）

- 緑帯の模型 icet_green を、RDF では ICE T 全体（Q696668）に結んでいた。正しくは 411 形（Q115612330）。
- 根拠: 模型の車番は 411 525。skytrain の `models/icet_green.py` と、写真 `411_horb_green_stripe_side.jpg` も 411 形の先頭車。`docs/data/models.json` は初めから 411 形だった。
- 塗装（緑帯）は 411 形と 415 形の両方に塗られたので、「塗装の範囲」と「模型にした車両の形式」を取り違えたとみられる。
- `tools/build_rdf.py` の MODELS と `annotations/icet_green.json` を直した。Turtle の差分は icet_green の `schema:about` と、2 つの形式の `schema:subjectOf` だけ（all.jsonld などの差分は並び順）。

### ERATV の再利用条件を確かめた（同じ日、10:00）

- ERA の「Disclaimer and copyright notice」（https://www.era.europa.eu/content/disclaimer-and-copyright-notice、2026-10-10 に読んだ。版や日付の表示は無く、「Copyright European Union Agency for Railways, 2025」とだけある）は、
  「出典を示せば複製してよい。ただし別に定めがある場合を除く」という一般的な許可。データやデータベース、ERATV のような登録簿についての個別の定めは無い。
- ERATV の Terms of Use（V1.6、前に読んだもの）は登録する側の約束で、取り出したデータの再利用には触れていない。つまり「別の定め」には当たらない。
- ERA の刊行物（例: 2024 年の「20 years of ERA」）は CC BY 4.0 と明記しているが、これは文書についての表示で、ERATV に同じ表示は見つからなかった。
- 結論（解釈）: ERATV から取り出した型式の一覧は、出典（ERA・ERATV・取り出した日）を示せば公開してよいと読める。CC BY 4.0 と同じ扱いと言い切れる文言は無い。
- 確かめていないこと: ERA に問い合わせてはいない。ERATV の画面そのものに別の表示が無いかは、一覧と出力の画面だけ見た。

### 公開中の RDF の実測（同じ日、10:10。「RDF にする利点」の下地）

測り方: `docs/rdf/all.ttl`（コミット b39e4ff の時点）を rdflib で読み、数えた。

- 形式 17・3D モデル 18・トリプル 2,100。
- **公開中の RDF は 3D モデルのある形式（とその上位）だけ。** 検索の索引は 14,325 形式あるが、形式のページ（RDF）があるのは 17。残りは索引の中にしか無い。
- 外部の URI への参照: Wikidata の項目への参照 510 件、異なり 111 項目。`skos:exactMatch` で Wikidata に結んだ形式は 17 中 13（残り 4 は SkyTrain の Mark I〜V のように Wikidata に項目が無いもの）。
- 路線とのつながり: `tb:usedOn` 49 件（42 路線、すべて Wikidata の項目）。
- 色: 塗装の色見本 96 件、Wikidata の色の項目（wdt:P462）130 件。
- 確かめていないこと: 「典拠の更新がそのまま反映される」は、Wikidata を取り直して差分を出す実験をしていないので、まだ示せていない。


### ERATV と Wikidata の照合: 名前を後ろから削って結ぶ（同じ日、10:30）

これまでは、名前を正規化して完全に一致したものだけを結んでいた（3,295 型のうち 134）。
ERATV の型名には、製品名の後ろに版・編成・保安装置が付いている（「ICE T BR 415 Bremsbelagsubstitution」「TRAXX AC3 VR07 Var. F」）。
そこで、一致しなかった型は名前を語の単位で後ろから削り、長いほうから順に Wikidata の名前（ラベルと別名）と照らした。
当たったものは、ERATV の型が Wikidata の形式の一つの版にあたるので、skos:narrowMatch の候補として扱う（`data/classes.tsv` の match=prefix）。
その前に、名前の中のドイツの形式番号（「BR 411」「BR1440」）を「DB-Baureihe 411」として引く。製品名より細かいからである。

- 結果: 結べた型は 134 → 629（名前の一致 134、削って当たった 495）。当たった Wikidata の項目は 124 → 244。候補が 2 つ以上ある型は 132
- 測り方: `python3 tools/build_classes.py` の出力。削る規則を入れる前の当たり 445 件のうち、無作為に 60 件と、数字を含まない削り名 41 種の全部を目で見た
- 外した削り名（`NOT_PREFIX`）: 「Desiro」（Wikidata では MÁV 426 の別名）、「CRRC」（ŽRSM 711 の別名）、「RAIL-BUS」（GTW の 1 編成の別名）、
  「Electric multiple unit」「Schienenbus」（種類の名前で、形式ではない）。数字を含む削り名には、この表を当てない
- 却下した案: 数字を含まない削り名では、項目の英語ラベルにその語が入っていることを条件にする案。Desiro などは落とせるが、
  「EW IV」（ラベルは Einheitswagen IV）や「ICNG」（ラベルは Intercity Nieuwe Generatie）の正しい当たりまで落ちる
- 分かったこと: 「ICE T BR 411 ETCS BL3」は DBAG Class 411（Q115612330）と ICE T（Q696668）の両方に当たる。
  Wikidata の ICE T 自身に「DB Baureihe 411」「Baureihe 415」の別名が付いているためで、こちらでは選ばずに両方を候補として残した
- 限界: 当たりは手で確かめていない。削る単位は空白・「_」・「 - 」・「(」だけで、「BR189」と「ES64F4」のような別名どうしの関係は見ていない。
  ERATV のデータは再利用条件の判断待ちで `docs/` に出していないので、この照合はまだ RDF に入らない（入れるなら skos:narrowMatch）

### 本人の判断 3 つと、全形式の RDF（同じ日、11:00）

本人に聞いて決めた（3 つとも推奨どおり）。

1. **全形式を RDF にする。1 形式 1 ファイルで、どの URI も引けるようにする。**
   `tools/build_rdf.py` が、3D のある 17 形式に加えて `data/classes.tsv` の Wikidata の行（ERATV の行は除く）すべてを書く。
   値は `data/wikidata/facets/<id>.tsv`、名前は `classes.tsv` と `class-labels-ja.tsv` から。
   - 実測: 17 + 14,308 形式、トリプル 206,977、生成 28 秒。`docs/rdf/class/` は 28,650 ファイル・38 MB。all.ttl 7.1 MB、all.jsonld 15.4 MB
   - 検索の索引は、作り直しても値が 1 件も変わらなかった（形式ごと・項目ごとの値の集合で比べた）。
     変わったのは値の番号の振り順と、名前 8 件。後者は前の索引に `"South African ""Natal"" 0-4-0WT"` のような引用符の二重が残っていたのが直ったもの
   - 形式のページ（Astro）は 28,694 枚、組み立て 35〜44 秒。1 ページが全形式のファイルを読み直していたので（形式の数の 2 乗）、一度読んで覚えておく形に直した
   - **サイトの容量: 380 MB → 732 MB → 638 MB。** ページごとに 4 KB の CSS が埋め込まれていたのを共有の 1 ファイルにして、約 110 MB 減った。
     GitHub Pages の上限は 1 GB。残りの大きいものは写真 228 MB とダウンロード用ファイル 113 MB
   - 却下した案: 一括ファイルだけ全形式にして、1 形式のファイルは 17 のまま。URI を引けない形式が残るので取らなかった
2. **ERATV は、Wikidata との対応表だけ出す。** `docs/data/eratv-wikidata.tsv`（629 型 → 244 形式、775 行。候補が複数の型 132 は全候補を並べる）。
   出典と条件は W3C の CSVW の説明ファイル（`eratv-wikidata.tsv-metadata.json`）に書いた。元の一覧（eratv.tsv・XML）は出さない。RDF にはまだ入れていない
3. **利用条件: データ（RDF）は CC0、3D モデルとその画像は CC BY 4.0、形式の写真は Commons のそれぞれの条件。**
   フッターに書き、RDF（体系に `dcterms:license` CC0、各モデルに `schema:license` CC BY 4.0）と IIIF の Manifest（`rights`）にも入れた

### 「RDF にする利点」の実測（同じ日、11:10）

**外部と結べる件数（全形式の RDF で数え直した）**
- 測り方: `docs/rdf/all.ttl`（全形式にした後）を rdflib で読み、目的語が Wikidata の項目である三つ組を数えた
- 形式 14,325、トリプル 206,977。Wikidata の項目への参照 102,009 件、異なり 18,095 項目（17 形式のときは 510 件・111 項目）
- 属性ごと: 運行者 15,823、製造者 14,876、`skos:exactMatch` 14,321、`prov:wasDerivedFrom` 14,321、種類（P279）14,090、軌間 10,070、国 8,789、軸配置 7,545、電化 1,924、色 130、路線 49
- 名前を自分で持たずに項目へ結んでいるので、日本語名は Wikidata にある分だけ自動で付く: 形式の日本語名 2,959（20.7%）、絞り込みの値 4,252 のうち 2,308（54.3%）

**典拠の更新は、どのくらいの速さで起きるか**
- 測り方 1: 値を Wikidata から取り直し（`tools/fetch_facets.py --data <別の場所>`、10:59 開始、80 秒）、前日 21:03 に取った値と、形式ごと・項目ごとに比べた
  - 14 時間で変わったのは写真 2 件だけ（Q11742819 に追加、Q1114573 が差し替え）。種類・国・運行者などの値は 0 件
  - 種類の上下関係（P279*）は 23 の種類で祖先が増えた（+1,415 行・−179 行）。上位の体系（Q35120「もの」など）の編集による。検索の分類（kindGroup）は変わらなかった
- 測り方 2: 各形式の最終編集日時を WDQS の `schema:dateModified` で 1 回で取った（`tools/wd_modified.py`、`data/wikidata/modified.tsv`）
  - 直近 1 日 13 件（0.1%）、7 日 132（0.9%）、30 日 676（4.7%）、90 日 1,495（10.4%）、1 年 5,322（37.2%）、2 年 7,534（52.6%）。中央値 645 日前
  - 編集はどの言語の名前・サイトリンク・使っていない属性でも数えるので、**このサイトに届く変更の上限**。値の変化に絞った率は出せていない
- 取り直しから公開までは手作業が無い: 取得 80 秒 → RDF 28 秒 → 索引 9 秒 → サイト 44 秒
- 主張の候補: 形式を典拠の URI で持つと、1 年で 37% の形式に入る典拠側の編集を、手で書き写さずに約 3 分の作り直しで取り込める（根拠は上の 2 つの測り方）
- 確かめていないこと: 1 年前の値との差（版をさかのぼって比べていない）。そのためには、取得を定期的に残すか、版の履歴（`schema:version` の過去）を引く必要がある
- 途中で分かった不具合: `fetch_facets.py` は、3D のある形式だけが持つ種類（Amtrak Airo → Siemens Venture Q96106536）の上下関係を取っていなかった。
  前回の表にはなぜか入っていたが、取り直すと Airo が「その他」に落ちる。`data/wikidata/rdf-cache.json` の値も足すように直した（直した後の比較で分類の変化 0）
- API（wbgetentities）は最初の問い合わせから 429（多すぎる）を返したので、WDQS の 1 回の問い合わせに替えた（1.3 秒）


### 路線の線を全形式に広げられるか — Wikidata だけで数えた（12:00 ごろ）

地図に線が出るのは、手で路線を調べた 12 形式だけ。全形式に広げられるかを、取り出す前に件数だけ数えた。道具は `tools/count_class_lines.py`（出力は `data/` の 4 ファイル、git の管理外）。

- 測り方 1: Wikidata の「通常使用される車両」（P3438）を全件、1 回の問い合わせで取り（`tools/queries/wd-all-lines.rq`、4,043 件・相手 2,877 項目）、車両が検索の索引の形式そのものである分だけ残した（P279 の 1 段は通さない。12 形式で試したとき、広い分類を通って無関係な路線ばかり来たため）
  - 結べた形式 **899**（索引 14,325 の 6.3%）、相手の項目 1,695、組 2,400
  - 1 形式あたりの最多は Q432757 の 55 項目、Q729191 の 54
  - 手で調べた 12 形式のうち、この方法で直接届くのは 3 形式。手の表の 42 路線のうち、この 1,695 に入るのは 8
- 測り方 2: 相手 1,695 項目の P31（何の項目か）。多い順に railway line 300、train service 287、tram route 153、Regionalbahn 142、rapid transit line 115、S-Bahn service 99、passenger train service 99。路線（線路）と列車の運行がおよそ半々
  - 運行の項目でも、OSM の route relation は運行の単位で作られるので、線は取れる。12 形式のときに「運行の項目だから線は無い」とした判断（ヴァンデ・バーラトなど）は、項目ごとに確かめ直す余地がある
- 測り方 3: OSM の側で `wikidata=` の札が付いた relation を数えた。Overpass に 1 路線ずつ聞くと 1,695 × 15 秒 ≒ 7 時間かかるので、OSM 全体を SPARQL で引ける QLever（`https://qlever.dev/api/osm-planet`）に 500 項目ずつ 4 回で聞いた（数十秒）
  - relation 2,798、札の付いた相手 **923 / 1,695（54%）**、線まで届く形式 **561**（今の 12 の約 47 倍）
  - route= の内訳: train 994、札なし 737、subway 452、tram 317、railway 121、light_rail 113、monorail 31、tracks 27（ほかに foot・bicycle が 1 件ずつ混ざる）
  - 確かめ: 手の表の 8 路線のうち 6 に札があり、Overpass での結果（札あり）と食い違いは無かった
- 途中で分かったこと: QLever の osm-planet は `wikidata=` の値を IRI でなく文字列 "Q…" で持つ。`qlever.cs.uni-freiburg.de` は `qlever.dev` へ転送（308）され、Python の urllib は POST の転送を追わない
- 主張の候補: Wikidata の P3438 と OSM の `wikidata=` 札だけで、手作業なしに 561 形式（索引の 3.9%）を路線の線に結べる。手で出典を付けて調べた 12 形式とは、ほとんど重ならない（根拠は上の測り方 1 と 3）
- 確かめていないこと: 札が付いた relation が本当にその路線の線か（foot・bicycle のような取り違え、札なし route の中身）。1 つの項目に relation が多数あるとき（往復・支線）の扱い。線を取り出したときの容量

### 20 路線で線を試しに取り出した（13:00 ごろ）

上の 923 路線（札あり）から、手の表に無い 917 本のうち 20 本を無作為に選んだ（`random.seed(20261010)`、一覧 `data/lines-trial.txt`）。ベルリン S15・Heathrow Express・Caltrain・アルジェの路面電車・アディスアベバ–ジブチ鉄道・シンガポール南北線・ハーグの路面電車 1 系統と 12 系統など、8 か国以上に散った。

- 測り方 1: 既存の `tools/osm_lines.py --only <Q> --out data/lines-trial`（Overpass の mail.ru ミラー、10 秒おき）を 1 本ずつ。約 25 分
  - relation は 20 本とも見つかった。線まで取れたのは **14 本**。6 本は線を取る段で 504（時間切れ）が 4 回続いて落ちた
  - 全 923 本で同じ割合なら 3 割が落ち、取り直しが要る
- 測り方 2: 同じ「relation とその子 relation の、railway= が線路の way」を、QLever osm-planet に SPARQL で聞いた（`tools/qlever_lines.py`）。間引き・丸めは osm_lines.py と同じ（約 30 m、小数 5 桁）
  - **20 本とも取れた。1 本 1 秒前後**（最初の 1 本だけ 23 秒）、合計 50 秒ほど
  - 両方で取れた 14 本を比べた: way の数は同じか ±4、長さはすべて同じ（km 単位）、形のずれ（ハウスドルフ距離）は最大 30 m（間引きの幅と同じ）
  - QLever だけで取れた 6 本も、範囲と長さは実際の路線どおり（Heathrow Express 26 km、アディスアベバ–ジブチ 766 km など）
- 正しさ: 20 本とも、範囲は名前どおりの土地。徒歩道・自転車道の取り違えは 20 本には無かった（数えたときに混ざっていた foot・bicycle の 1 件ずつは、この 20 本に入っていない）
- 長さは、複線や往復の relation の線路をどちらも数えるので、実際の距離の 1〜2 倍になる（Caltrain 184 km、南北線 90 km）。地図に描くだけなら困らない。距離として出すなら使えない
- 容量: 20 本で約 100 KB、1 本あたり 0.5〜50 KB（長距離の Brisbane XPT が 49 KB）。923 本なら約 5 MB の見込み
- 主張の候補: OSM の線の取り出しは、Overpass に 1 本ずつ聞くより、OSM 全体を RDF にした QLever に聞くほうが速く（1 本 1 秒前後と約 75 秒）、落ちない（20/20 と 14/20）。取れる形は同じ（根拠は上の測り方 1 と 2）
- 確かめていないこと: QLever の OSM がいつの時点の写しか（メタデータに日付が見当たらなかった）。札なし route の 737 件の中身。1 つの路線に複数の形式が載るときの地図の見せ方

## 全路線を取り出した（2026-10-10 午後）

- 訂正: 上の「20 路線で試しに取り出した」の測り方 2 にある `tools/qlever_lines.py` は、そのあと `tools/osm_lines.py --qlever` に組み込んで消した。中身の問い合わせは同じ
- 測り方: `python3 -u tools/osm_lines.py --qlever`。対象は手の表と `tools/class_lines_wd.tsv` を合わせた 1,733 路線。記録は data/osm_lines_qlever.log（git の外）。1 本ずつ間を空けずに聞いた。所要は約 37 分（記録ファイルの作成と最終更新の時刻から）
- 結果: OSM に wikidata= の札がある relation を持つ路線 953、そのうち線が取れたもの 935、失敗 0。残りの 18 本は、relation はあるが線路の way が 1 本も引けなかった（停留所だけの relation など。中身は未確認）
- 形式で数えると: 2 つの表に出る 924 形式のうち、地図に線が出るのは 558 形式（20 路線の前に数えた見込みは 561）。それまでは 12 形式だった
- 容量: docs/lines 全体で 8.7 MB。地図のページ用にまとめた `_all.geojson` は 3.4 MB（gzip で 0.99 MB）。手元の preview で、ページを開いてから線が出るまで 2〜5 秒
- 偏り: 線の重心で大まかに分けると、ヨーロッパ 657、東アジア 94、北アメリカ 85、南アメリカ 21、その他 78。Wikidata の P3438 がヨーロッパの路線に多く付いているためと思われる（日本の路線にはほとんど付いていない。確かめたのは地図の見た目だけ）
- 見た目の手直し: 線を選んでも、ほかの線と同じ色で太さが 4 → 6 になるだけで、トロントのような路線の多い街では見分けにくかった。選んでいる間は、ほかの線を薄くする（不透明度 0.9 → 0.25、廃止は 0.45 → 0.15）ことにした
- 主張の候補: Wikidata の「通常使われる車両」（P3438）と OSM の wikidata= の札だけで、形式から路線の形までを手作業なしにたどれる。形式で 12 → 558、路線で 935 本（根拠は上の 2 行）。ただし地域の偏りは Wikidata の偏りをそのまま映す
- 確かめていないこと: 線が取れなかった 18 本の中身。地図のページを開いてすぐ（線の読み込み前）に一覧を押すと、地図がその路線へ動かない（読み込み後は動く）

## 2026-10-11

### 形式に写真を結んだ（foaf:depiction、本人の指示）

- `tools/build_rdf.py` が、形式ごとに Wikidata の P18（画像）を `foaf:depiction` で書く。値は既に取ってあった
  `data/wikidata/facets/_image.tsv`（`fetch_facets.py`、1 形式 1 枚の SAMPLE）。新しい問い合わせは無し
- 目的語の IRI は Wikidata の `wdt:P18` と同じ `http://commons.wikimedia.org/wiki/Special:FilePath/<ファイル名>` のまま。
  Wikidata 側と同じ IRI なので、連合検索でそのまま結び付く
  - 却下した案: `https://` に書き換える。表示には有利だが、Wikidata の値と一致しなくなる。
    ブラウザは画像の http を https に読み替えるので、表示はこれで足りる見込み（LD Browser での確認はまだ）
  - 却下した案: 写真ごとに作者と利用条件（`_image_credit.tsv`）も RDF に入れる。三つ組が数万増え、
    条件は Commons 側が正本で変わりうる。今回は入れていない。サイトのクレジット表示は従来どおり
- 実測: 写真が付いた形式 10,402 / 14,325（72.6%）。三つ組 228,306 → 238,708（差はちょうど 10,402）。生成 44 秒。
  3D のある 17 形式では 13 形式に付いた。付かないのは Amtrak Airo・New Flyer XD60・トランスラピッド 08（Wikidata に P18 が無い）と、
  Wikidata に項目の無い SkyTrain Mark I〜V（4 形式）。ファミリーの Innovia Metro（Q4940487）には付いた
- `_image.tsv` の 12,362 項目のうち残りの約 2,000 は、`classes.tsv` に入っていない項目（日本の形式など）
- 途中で分かったこと: 作者情報の表（`_image_credit.tsv`）に行が無いファイルが 5 つ。どれも名前に `"` を含む
  ニュージーランドの蒸気機関車（Q1961770 ほか）。Commons には実在する（API で確認）ので、写真の指し先は正しい。
  作者情報の取得（`fetch_image_credits.py`）がこの記号で漏らしている可能性。未修正
- JSON-LD は、変更の無いモデルのファイルも差分に出る。rdflib が書き出しのたびに要素の並びを変えるためで、中身は同じ

### LOD チャレンジ 2026 の応募計画（本人の指示）

**応募要項を確かめた（2026-10-11、https://2026.lodc.jp/entry.html ）。**
これまでのメモは 2025 年の要項を見て書いていたので、2026 年の要項で読み直した。

- 応募期間: 2026-09-01 〜 2027-01-05。結果発表 2027 年 2 月中旬、授賞式 2027-03-13（国立情報学研究所）
- 部門: データ作成部門（新しく作ったデータ、既存データを加工したデータ、データをつなぐデータ）と、
  データ活用部門（アプリ・サービス、データを使うための基盤的な道具、データ作成・公開を支える仕組み）
- 応募数・部門数は自由。**同じ作品を 2 つの部門に出すことはできない**（規定 4）
- ライセンスの指定が要る。無ければパブリックドメイン扱い（規定 9）
- **2027-03-31 まで**ネットから見られる・落とせる状態にしておく（規定 5）
- 既存の応募作品を使うときは、その作品の URL を応募書式に書く（規定 6）
- 締切後の追加・修正は審査されない（規定 8）
- 応募書式の細かい項目（概要の字数など）は要項に無い。Google フォームで確かめた（下の「応募フォームの項目」）

**応募フォームの項目（2026-10-11、フォームのページに埋め込まれた設問データを読んで確かめた）**

フォーム: https://docs.google.com/forms/d/e/1FAIpQLSd5wIhAgjSz-GggSMILTz8hxNu6lZVcBnVrfdKeIHMZAH5kcA/viewform
（entry.html の応募ボタンの先）。1 ページだけで、設問は 11 個。1 回の送信で 1 作品なので、2 作品なら 2 回送る。

| 設問 | 形式 | 必須 | 公開 | 備考 |
|---|---|---|---|---|
| 作品タイトル | 1 行 | ○ | ○ | |
| 作品の概要説明 | 複数行 | ○ | ○ | 字数の制限なし |
| 応募者名 | 1 行 | ○ | ○ | ニックネーム・団体名も可 |
| 応募者のご所属 | 1 行 | ○ | ○ | 会社名・学校名 |
| 応募者属性 | 択一 | ○ | | 社会人 / 学生 |
| エントリー部門 | 択一 | ○ | ○ | データ作成部門 / データ活用部門 |
| エントリー作品の URL | 1 行 | ○ | ○ | URL の形かどうかを検査する。1 つだけ |
| エントリー作品の権利指定 | 択一 | ○ | ○ | CC0 / CC BY 4.0 / CC BY-SA 4.0 / その他（自由記入） |
| 利用しているオープンデータ | 複数行 | | ○ | 名称・URL など |
| 利用しているパートナーリソース | 複数行 | | ○ | 書いていないとパートナー賞の対象外になりうる |
| 備考 | 複数行 | | | 事務局あて |

- **字数の制限はどの欄にも無い**（設問に入力の検査が付いているのは URL 欄だけ）。
  「【公開】」の欄はそのまま応募作品一覧に載るので、概要は一覧で読める長さにする（目安 400〜800 字。要項の指定ではなく、こちらの判断）
- **2027-01-05 までは送信後も直せる**（送信後の画面と確認メールの「回答を編集」から）。
  したがって 12 月中に一度送り、締切までに書き直す流れが取れる。締切後は直せない（規定 8）
- 確認メールが届くので、送信時にメールアドレスを入れる形と思われる（設定値からの推測。開いて確かめてはいない）

**フォームから分かった、計画への影響**

- **所属が必須で、しかも公開される。** サイトに所属を出さない方針（2026-10-10）とは別に、ここは何か書く必要がある。
  対外的な書き方の決まりでは「東京大学」まで。個人として出すなら「個人」と書く手もある（本人の判断）
- **権利指定は 1 つしか選べない。** RailClass はデータ CC0・3D モデルと画像 CC BY 4.0・写真は Commons の条件、と混在している。
  案: 「その他」を選び「データ CC0、3D モデル・画像 CC BY 4.0、写真は各ファイルの Commons の条件」と書く。
  CC0 を選んで概要で補う案もあるが、一覧では CC0 だけが見え、写真まで CC0 と誤解されるので推奨しない
- **LD Browser のリポジトリにはライセンスのファイルがまだ無い**（2026-10-11 に確かめた）。応募前に決めて置く必要がある。
  プログラムなので CC の選択肢は合わず、「その他」で MIT などを書くことになる（本人の判断）
- **URL は 1 つだけ。** RailClass はトップ（w3id が通れば `https://w3id.org/railclass/`、通らなければ github.io）を書き、
  RDF の一括ファイル・リポジトリ・データセットの説明は概要の中に書く。残り作業 3 のデータセットの説明は、トップから 1 クリックで行ける場所に置く
- **規定 6（既存の応募作品の URL）を書く専用の欄は無い。** LD Browser の書式では「利用しているオープンデータ」に
  RailClass の名前と URL を書く。RailClass 側は Wikidata・Wikimedia Commons・ERATV・OpenStreetMap をここに並べる
- パートナーリソース: 2026 年のパートナーと提供リソースの一覧はまだ見ていない。Wikidata などが入っていれば書く（下の「確かめていないこと」）

**応募する作品は 2 つ（案）。**

| 部門 | 作品 | 中身 |
|---|---|---|
| データ作成 | RailClass（このリポジトリ） | 日本を除く世界の鉄道車両の形式 14,325 件の RDF、3D モデル 18 体の RDF と IIIF Manifest、形式 → 路線の線、ERATV ↔ Wikidata の対応表 |
| データ活用 | LD Browser（browser.ldas.jp、`~/git/lod/ld-browser`） | ブラウザだけで動く Linked Data ブラウザ。RailClass に限らず、CORS を許す RDF なら何でも表と小さなグラフ図で見せる |

- 分け方の理由: RailClass は「データ」、LD Browser は「データを使うための道具」で、要項の部門の説明にそれぞれそのまま当てはまる。
  LD Browser は RailClass 専用ではなく、Wikidata など他のデータも開ける。これを応募書式に書けば「同じ作品」には当たらない
- LD Browser の応募書式には、使用データとして RailClass の応募作品の URL を書く（規定 6 の書き方に合わせる）。
  逆に RailClass の書式には「LD Browser で見られる」と 1 行添える。互いに相手を引き立てる形にする
- LD Browser は神崎正英さんの ld-browser（2014、サーバ型。現在は停止）に着想を得て、ブラウザだけで作り直したものだと明記する。
  神崎さんの作品として見せない（詳しくは ld-browser.md の先行事例）
- 却下した案: RailClass を 1 作品にまとめて活用部門に出す。サイト・地図・3D の見た目は目立つが、
  中心は 14,325 形式を典拠に結んだデータそのものなので、作成部門の観点（機械可読性・つながる可能性）のほうが強みを出せる
- 却下した案: 見せ方（地図・IIIF の 3D）を RailClass から切り出して、活用部門の 3 つ目の作品にする。
  同じサイトの中にあり、別の作品と言いにくい。RailClass の一部として出す

**データ作成部門の審査の観点と、出せる根拠（このノートの実測）**

- Accessibility（機械可読性）: 1 形式 1 ファイルの Turtle と JSON-LD、一括の all.ttl・all.jsonld（「本人の判断 3 つと、全形式の RDF」）
- Linkability（つながる可能性）: Wikidata の項目への参照 102,009 件・異なり 18,095 項目、`skos:exactMatch` 14,321（「RDF にする利点」の実測）。
  写真 10,402 形式（`foaf:depiction`、Wikidata と同じ IRI）。ERATV の型 629 → 形式 244 の対応表
- Openness（開放性）: データ CC0、3D モデルと画像 CC BY 4.0、写真は Commons の条件（決定済み、フッター・RDF・Manifest に記載）
- Sustainability（持続可能性）: 典拠を取り直して約 3 分で作り直せる（取得 80 秒 → RDF 28 秒 → 索引 9 秒 → サイト 44 秒）。
  URI を w3id.org/railclass に移せば、置き場所を変えても URI が残る（下の残り作業）
- Usefulness・Impact・Creativity: 形式 → 路線の線（形式で 12 → 558、路線 935 本、手作業なし）、IIIF v4 の 3D に部位のアノテーションを載せた交通分野の実例、
  ERA の知識グラフに型式がまだ無い（2026-10-09 の実測）ところを Wikidata との対応で補っている点

**データ活用部門の審査の観点と、出せる根拠（ld-browser.md の実測）**

- Operativity・Designability: 表とグラフ図、日英の切り替え、明暗の切り替え、画像の値を小さな絵で表示
- Feasibility・Sustainability: サーバを持たないので、神崎版を止めた「アクセス過多」が構造上起きない（ld-browser.md の主張の候補）
- Use of open data: RailClass・Wikidata を実際に開ける。RailClass の形式・モデルのページから直接リンク済み
- Completeness: RDF/XML・Turtle・JSON-LD・HTML に埋め込まれた RDF（JSON-LD・microdata・RDFa）を読める

**締切までの残り作業（応募に効く順）**

1. w3id の PR（perma-id/w3id.org#6867）が通ったら、RDF の URI を `https://w3id.org/railclass/...` に一度に差し替える。
   応募書式に書く URI はこれにする。PR が 12 月中に通らなければ、今の github.io の URI で出す
2. 応募書式の項目を Google フォームで確かめ、2 作品の概要を下書きする（日本語。英語は要るときだけ）
3. ~~データセットの説明を 1 か所にまとめる（VoID かそれに近いもの: 件数・ライセンス・一括ファイルの場所・SPARQL が無いこと）。審査員が最初に開く場所にする~~ → 2026-10-11 作った（下の「データセットの説明を 1 か所にまとめた」）
4. ~~LD Browser の使い方の動画を YouTube に上げ、トップに埋め込む（題名と公開範囲は上げる前に本人に確かめる）~~ → 2026-10-11 済み。日本語版 XNXKw03V55w（2026-10-12 19:00 JST に公開）、英語版 gIjU2KkaxAE（2026-10-13 9:00 ET に公開）を予約公開にし、browser.ldas.jp の日英トップに埋め込んで配った（ld-browser c1dde8c）。作り方は ld-browser の実験ノート
5. 応募は 2026 年 12 月中に済ませる（締切の 2027-01-05 は年始の休みに当たる。締切後は直せない）
6. 2027-03-31 まで、GitHub Pages と browser.ldas.jp を止めない。大きな作り替えは応募後に、URI を変えない範囲で

**決めていないこと（本人の判断）**

- 2 作品で出すか、RailClass だけにするか（推奨は 2 作品。部門が違えば別々に部門賞を狙える）
- 応募者の名義（個人名だけ。サイトに所属を出さない方針〔2026-10-10〕に合わせるのが自然）
- 所属の欄（必須・公開）に何を書くか: 「東京大学」か「個人」か
- LD Browser のライセンス（MIT など）と、RailClass の権利指定を「その他」で書くか
- テーマ賞のテーマ（2026 年分は要項のページに出ていない。発表されたら当てはまるものを選ぶ）

**確かめていないこと**

- 過去の LOD チャレンジで、鉄道車両や LD ブラウザそのものが入賞した例（lodc.jp の各年の結果で確かめる）
- ~~応募書式の字数・必須項目~~ → 確かめた（上の「応募フォームの項目」）
- 2026 年のパートナーと、提供しているリソース（パートナーリソースの欄に書けるものがあるか）

### 応募フォームの下書き（2 作品、全 11 設問）

上の「応募フォームの項目」の順に書いた。数字はこのノートと ld-browser.md の実測。
【要判断】は本人が決める箇所、【条件】は締切までの状況で書き換える箇所。概要はどちらも 600 字前後。

**作品 1: RailClass（データ作成部門）**

- 作品タイトル: RailClass — 世界の鉄道車両形式の Linked Data
- 作品の概要説明:

  > RailClass は、世界の鉄道車両の「形式」（ICE T や SkyTrain Mark II のように、同じ設計で作られた車両のまとまり）を集め、Linked Data として公開するデータセットです。
  > Wikidata から日本を除く 14,325 形式を取り出し、1 形式 1 ファイルの Turtle と JSON-LD、および一括ファイル（all.ttl・all.jsonld）にしました。
  > 各形式は skos:exactMatch で Wikidata の項目に結び、運営者・製造者などの値も Wikidata の IRI のまま持つので、他のデータとそのままつながります。
  > 写真は 10,402 形式に、Wikidata と同じ Wikimedia Commons の IRI で付けています。
  > 既存のデータを加工し、つないだデータとして、次の 3 つも含みます。
  > (1) 欧州鉄道庁の車両型式登録（ERATV）の型式 629 件を、Wikidata の 244 形式に結んだ対応表。
  > (2) 形式ごとの運用路線を Wikidata と OpenStreetMap から引いた線データ。558 形式・935 路線を地図で見られます。
  > (3) 制作した鉄道模型の車体の 3D モデル 18 体の RDF と、IIIF Presentation API 4.0 の Manifest。3D の上に部位の注記を載せています。
  > 典拠からの再生成は約 3 分で、手作業を挟みません。
  > データは CC0、3D モデルと画像は CC BY 4.0、路線の線データは OpenStreetMap に従い ODbL、写真は各ファイルの Commons の条件です。
  > 中身は、同時に応募する LD Browser（https://browser.ldas.jp/ ）でも見られます。
  > URI は https://w3id.org/railclass/ で、置き場所が変わっても残ります。
  > 件数・ファイル・ライセンスの一覧は https://railclass.ldas.jp/dataset.html にあります。

  URI の 1 文は、2026-10-13 に URI を w3id に移したので入れた（下の「RDF の URI を w3id に差し替えた」）。
  データセットの説明の頁は 2026-10-13 時点で https://railclass.ldas.jp/dataset.html で公開中。上の最後の 1 文に入れた
  （w3id の転送は dataset.html を扱わないので、railclass.ldas.jp の URL で書く）
- 応募者名: 中村 覚
- 応募者のご所属: 東京大学
- 応募者属性: 社会人
- エントリー部門: データ作成部門
- エントリー作品の URL: https://w3id.org/railclass/ （PR #6867 は 2026-10-12 にマージ。ブラウザで開くと https://railclass.ldas.jp/ に転送される）
- エントリー作品の権利指定: その他 →「データ CC0 1.0、3D モデル・画像 CC BY 4.0、路線の線データ ODbL（© OpenStreetMap contributors）、写真は各ファイルの Wikimedia Commons の利用条件」
- 利用しているオープンデータ:

  > Wikidata（CC0） https://www.wikidata.org/
  > Wikimedia Commons（各ファイルの条件） https://commons.wikimedia.org/
  > ERATV 欧州車両型式登録（© European Union Agency for Railways。ERA の著作権表示に従い出典を示して利用、2026 年 10 月取得） https://eratv.era.europa.eu/
  > OpenStreetMap（ODbL） https://www.openstreetmap.org/ （路線の線形。QLever の OSM 窓口で取得）

  OSM の線形は、2026-10-10 の決定どおり別の層として ODbL で出している（docs/lines/README.md）。権利指定と概要にもそう書いた
- 利用しているパートナーリソース: 【条件】2026-10-11 時点で 2026 年のパートナー一覧は空（ページは枠だけ）。
  一覧が出たら Wikidata・OSM・Wikimedia 関係があるか見て、あれば書く。無ければ空欄（任意の欄）
- 備考:

  > 同時にデータ活用部門へ「LD Browser」を応募しています。RailClass の各頁から LD Browser で RDF を開けます。

**作品 2: LD Browser（データ活用部門）**

- 作品タイトル: LD Browser — ブラウザだけで動く Linked Data ブラウザ
- 作品の概要説明:

  > LD Browser は、URI を入れると、その RDF をブラウザが直接取りに行き、表と小さなグラフ図で見せる Linked Data ブラウザです。
  > サーバを持たず、静的な頁だけで動きます。
  > Turtle・N-Triples・JSON-LD・RDF/XML に加え、HTML に埋め込まれた JSON-LD・microdata・RDFa も読めます。
  > 値の URI を押すと、その先の資源をその場で開き、リンクをたどっていけます。
  > ラベルは日本語・英語を優先し、Wikidata の属性名や値も名前で示します。
  > 画像の値（schema:image、foaf:depiction、Wikidata の P18 など）は小さな絵で見せます。
  > 着想は神崎正英さんの LD Browser（2014）です。
  > 神崎版はサーバ側で任意の URI を取りに行く作りで、アクセス過多のため現在は止まっています。
  > 本作はこれをブラウザだけで作り直したもので、サーバへの負荷の問題が構造上起きません。
  > 代わりに、相手が CORS を許可していないと読めません。
  > 読めなかったときは、「転送の途中で許可が切れた」のように理由を細かく出します。
  > 作る過程で、主要な語彙でも http から https への転送の段に許可が無く、ブラウザから読めないものがあると分かりました。
  > 公開する側への提言として、転送の応答にも Access-Control-Allow-Origin を付けることを勧めます。
  > 画面は日本語と英語、明暗を切り替えられます。
  > 同時に応募する RailClass の形式・モデルの頁から直接開けます。
  > 使い方の動画（5 分）: https://www.youtube.com/watch?v=XNXKw03V55w （英語版 4 分: https://www.youtube.com/watch?v=gIjU2KkaxAE ）
- 応募者名・ご所属・属性: 作品 1 と同じ
- エントリー部門: データ活用部門
- エントリー作品の URL: https://browser.ldas.jp/
- エントリー作品の権利指定: その他 →「MIT License」
- 利用しているオープンデータ:

  > RailClass（LOD チャレンジ 2026 データ作成部門への応募作品） 【条件】作品 1 と同じ URL
  > Wikidata（CC0） https://www.wikidata.org/
  > Wikimedia Commons（画像の表示） https://commons.wikimedia.org/
- 利用しているパートナーリソース: 【条件】作品 1 と同じ
- 備考:

  > ソースコード: https://github.com/nakamura196/ld-browser
  > 神崎正英さんの LD Browser（https://www.kanzaki.com/works/2014/pub/ld-browser ）に着想を得て、独自に作り直したものです。神崎さんのコードは使っていません。

  「コードは使っていない」は 2026-10-11 に確かめた: 神崎版はサーバ側の PHP（ARC2）で、そのソースは見ていない
  （見たのはアーカイブされた画面だけ。ソースが公開されているかは確かめていない）。本作はブラウザ側の JavaScript を一から書いた。ソース中の神崎版への言及は、
  「表ごとのグラフ図」「HTML からの抽出」という機能の着想を示すコメント 2 か所と、画面の謝辞だけ

**下書きで気づいたこと**

- 権利指定は 4 種類（CC0・CC BY 4.0・ODbL・Commons の条件）になる。「その他」を選ぶ理由がいっそう強い
- 概要は一覧にそのまま載るので、専門用語（skos:exactMatch、CORS）は残した。審査員は LOD の専門家なので、言い換えないほうが正確に伝わる

### 過去の受賞作を確かめた（応募計画の「確かめていないこと」の 1 つ目）

- 2011〜2025 の 15 回の受賞ページを見た。汎用の LD ブラウザの受賞作は無い（詳しくは ld-browser.md の同じ日の節。2012 年の「LOD Browser」は地図表示・編集で別物）
- 鉄道は多い: 2020「鉄道駅LOD」（uedayou、会社・路線・駅の LOD）、2025「電車から街を眺めてみよう」（uedayou）、2018 最優秀賞「鉄道地質」、
  2017「JITOZU 鉄道写真を楽しむプラットフォーム」など。**鉄道車両の形式を扱う受賞作は見つからなかった**（要約経由。一次確認は 2012 年分のみ）
- 応募書式への影響: RailClass の概要で「駅・路線の LOD はあるが、車両の形式は無かった」と位置付けられる。
  2020 の鉄道駅LOD は日本の駅、RailClass は日本以外の形式で、重ならない。つなぐ余地（路線）は今後の話として書ける

### 応募の名義・所属・LD Browser のライセンスを決めた（本人）

- 応募者名「中村 覚」、所属「東京大学」。下書きに反映した
- LD Browser のライセンスは「何でもよい」との指示で MIT にした（広く使われ、条件が著作権表示を残すことだけ）。
  リポジトリに LICENSE と README の License 節を置いた（ld-browser、未コミット）。下書きの権利指定は「その他 → MIT License」

### データセットの説明を 1 か所にまとめた（締切までの残り作業の 3）

- 人向けに `dataset.html`（英語 `en/dataset.html`）、機械向けに `rdf/void.ttl`・`rdf/void.jsonld`（VoID と DCAT）を作った。
  ヘッダーの「データ」、トップの「データ」の節、フッターから入れる。審査員にはこのページの URL を示す
- 件数は手で書かない。`tools/build_void.py` が `all.ttl`・ERATV の対応表・`lines/`・IIIF Collection から数え、
  VoID と `docs/data/dataset.json`（ページが読む）を同時に書く。ページと VoID が食い違わないようにするため。
  点検（`npm test`）で、ページの形式数が Turtle のファイル数と合うかを見る
- この日の実測: 形式 14,325（exactMatch 14,321）、写真 10,402、Wikidata の値 81,519、走る路線の分かる形式 923（路線 1,733、
  うち線のある 558 形式・935 路線）、3D モデル 18（15 形式）、ERATV 629 型 → 244 形式（775 行）、238,708 トリプル、
  主語になる資源 16,967、述語 54 種
- ページに書いたこと: 収録数、ファイルと大きさ、URI の形（.ttl/.jsonld を付けて取る。GitHub Pages はコンテントネゴシエーション
  をしない）、w3id.org に移す予定、**SPARQL エンドポイントは無い**こと（all.ttl を手元に読み込む。国ごとの形式数の問い合わせ例を
  rdflib で実行して確かめた）、部分ごとのライセンス、典拠と作り方、引用の書き方。schema.org の Dataset も埋め込んだ
  （Google Dataset Search 向け）
- VoID の書き方: データセット IRI は `<BASE>dataset`、void:uriSpace は `<BASE>rdf/`、void:dataDump は配信先（railclass）の
  all.ttl / all.jsonld。Wikidata（skos:exactMatch）と Commons（foaf:depiction）への void:Linkset。RDF 以外のファイル
  （ERATV の表・路線の線・IIIF）は dcat:Distribution として、それぞれのライセンスを付けた
- 却下: `/.well-known/void` に置く案。サイトは `nakamura196.github.io/railclass/` の下にあり、ドメインの根は別のリポジトリなので置けない。
  ページの `<link rel="alternate">` で VoID を指すことにした
- w3id に移るときは、`build_rdf.py` の BASE を替えて `build_rdf.py` → `build_void.py` の順に走らせれば VoID も揃う

### 応募フォームの下書きの【条件】【要確認】を片付けた（残り作業 2、2026-10-11）

- LD Browser の概要に、使い方の動画の URL（日英）を足した。動画は予約公開で、日本語版 2026-10-12 19:00 JST、英語版 2026-10-13 9:00 ET に一般公開になる
- **訂正:** 残り作業 4 で「予約公開にした」と書いたが、この日の夜に YouTube の API で確かめると、2 本とも限定公開のままで公開時刻が入っていなかった。
  非公開＋公開時刻（publishAt）に設定し直し、API で読み直して両方入っていることを確かめた。予約公開は「非公開」でないと効かない
- ERATV の利用条件の書き方を、2026-10-10 の「ERATV の再利用条件を確かめた」の結論（出典を示せば可）に合わせた
- 「神崎さんのコードは使っていない」を確かめた（下書きの備考の下に根拠）
- パートナーリソース: 2026.lodc.jp の「スポンサー・パートナー」は、2026-10-11 時点で項目が無い。一覧が出てから書く
- 残る【条件】は 3 つ: w3id の URI（PR #6867 待ち）、データセットの説明の頁の URL（配布待ち）、パートナー一覧（公開待ち）
- 下書きは 2 作品とも、この 3 つ以外はフォームにそのまま写せる状態


### 「運行国」を足した（本人の指摘から）

- きっかけ: イノヴィア・メトロ（Q4940487）の頁が「国: カナダ」なのに、写真と路線はクアラルンプール。見た人が戸惑う
- 最初は表示名を「製造国」に変える案を出したが、やめた。Wikidata で `wdt:P17` を持つ車両形式（P31 = Q811704）1,908 件を数えると、P17 が運行会社の国（P137/P17）と一致するのは 1,548 件（81%）、製造会社の国（P176/P17）と一致するのは 911 件（48%）。P17 は多くの形式で「走る国」を指し、製造国と呼ぶと半分ほどが誤りになる。イノヴィアが「カナダ」だけなのは、値が足りていないだけ
- 足したもの: `tb:operatingCountry`（運行国）。運行会社の国（P137/P17）と、走る路線の国（路線の P3438 → 路線の P17、手入力の路線表 `tools/class_lines.tsv` の路線も）を合わせる。「国」（P17）は Wikidata の値のまま残す
- 作り方: `docs/rdf/facets.json` に `wd`（SPARQL の型）を持つ「派生の項目」として書き、`tools/fetch_facets.py --only operatingCountry` で取る。14,719 行。イノヴィアは 5 か国（カナダ・アメリカ・中国・マレーシア・韓国）になった
- 下位の形式へは引き継がない（`inherit: false`）。スカイトレイン Mark I にマレーシアが付くと誤りになるため

### 地図の路線を 1 本ずつ色分けした（本人の指摘から）

- きっかけ: map/ の路線がすべて同じ色で、バンクーバーのように近くを走る別の路線が見分けられない
- 色は路線の公式の色（Wikidata P465）。地図に線のある 935 路線のうち 711 本（76%）にあった。エキスポ線 #0060A9（青）、ミレニアム線 #FFD520（黄）。`tools/line_colors.py` → `docs/lines/_colors.json`
- 公式の色が無い 224 本は、12 色の見本から Q 番号で決めて割り振る（`web/src/lib/data.ts` の lineColor）。どの頁でも同じ路線は同じ色になる
- 黄色が明るい地図で消えないよう、線の下に地図の背景色の縁取りを敷いた。一覧の見本の線も同じ色にした。形式の頁の地図も同じ扱い
- 確かめていないこと: 公式の色が同じ街の中で重なる例（同じ赤の路線が並ぶなど）

### 応募の下書きを最新の状態に合わせた（残り作業 2、2026-10-13）

- **w3id の PR #6867 は 2026-10-12 17:12 UTC にマージされた。** 転送の規則は `ids/railclass/.htaccess`。
  URI の形は `https://w3id.org/railclass/<cid>`（形式。`rdf/class/` は挟まない）、`.../model/<id>`、`.../vocab`、`.../`（データセット全体）。
  Accept で振り分け、text/turtle → `.ttl`、application/ld+json → `.jsonld`、それ以外 → HTML の頁（いずれも 303、railclass.ldas.jp へ）。
  形式 Q125966435・モデル railjet・vocab・トップで curl して、すべて期待どおりの転送先になり、転送先が 200 を返すことを確かめた
- **ただし RDF の中の URI はまだ古い。** `build_rdf.py` の BASE は `https://nakamura196.github.io/train-bodies/`、VoID も同じ。
  残り作業 1（URI の差し替え）は未着手。w3id の形は `rdf/class/` を挟まないので、BASE を替えるだけでは揃わない（形式の IRI の組み立てを変える必要がある）
- 使い方の動画は 2 本とも一般公開になった（2026-10-13 に YouTube の頁で isUnlisted・isPrivate がともに false を確かめた）
- 下書きに反映: データセットの説明の頁の URL（railclass.ldas.jp/dataset.html）を RailClass の概要の最後に足した。応募 URL を w3id に決めた
- 残る【条件】は 2 つ: 「URI は https://w3id.org/railclass/ で…」の 1 文（残り作業 1 が済んでから）、パートナーリソース（2026-10-13 時点でもパートナー一覧は空）


### RDF の URI を w3id に差し替えた（残り作業 1、2026-10-13）

- 形式 `https://w3id.org/railclass/<cid>`、モデル `.../model/<id>`、語彙 `.../vocab#<term>`、概念体系 `https://w3id.org/railclass/`。
  `build_rdf.py` の BASE を w3id にし、CLS を BASE の直下に（`rdf/class/` を挟まない）。
  3D ファイル・サムネイル・IIIF・閲覧頁へのリンク（schema:contentUrl など）は**置き場所なので w3id にしない**。新しく足した SITE（`https://railclass.ldas.jp/`）で書く。
  これまでは旧アドレス（github.io/train-bodies）のままで、開けなかった
- 合わせて直した所: `build_void.py`（uriSpace、説明文。`dataset.json` に classUri・modelUri・vocab・dataset を明示して持たせた）、
  `build_search.py`（URI から ID を取り出す所）、サイトの `classes.ts`・形式とモデルの頁・データセットの頁（「URI がまだ古い」という断り書きを外し、例は w3id の URI に直接結んだ）、`facets.json`、`build_eratv_map.py`
- 確かめたこと: docs/rdf に旧アドレスは 0 件。トリプル数は 255,154（前回 255,068 との差は同時に足されたモデル 1 両分）。
  検索の索引を値に戻して前回と比べ、違いは同時進行の作業の分（最高速度 2 件、sg-tel の 3 項目）だけ。
  サイトを手元で組み、形式の頁の上位・モデルの頁から形式への結びが生きていることを見た。
  w3id の URI を Turtle・JSON-LD・HTML で引き、形式・独自 ID の形式（tb-）・モデル・語彙・全体の行き先がすべて期待どおり
- **データセット自体の URI は `https://w3id.org/railclass/dataset` にした。w3id にこの転送はまだ無い**（引くと 404）。
  概念体系と同じ URI（ルート）にする案は、ルートを Turtle で引くと all.ttl が返り、VoID が入っていないのでやめた。
  w3id に `dataset` → `rdf/void.ttl`・`void.jsonld`・`dataset.html` の転送を足す PR を出した（perma-id/w3id.org#6896、2026-10-13。README も「`/` は概念体系、`/dataset` はデータセットの説明」に直した）
- 途中で見つけた別の不具合（未修正）: Wikidata の「値が不明」（`.well-known/genid/…`）が、`wd:` を前に付けた
  `http://www.wikidata.org/entity/http://www.wikidata.org/.well-known/genid/…` という IRI で 13 形式の電化方式などに入っている。
  検索の道具はこれを剥がして読んでいる（今回の書き換えで一度壊し、元に戻した）
- 進め方の記録: 別のセッションが同時に車両を足していた（avanti390、続いて sg-tel）。`build_rdf.py` と全 RDF が両方の作業で書き換わるため、
  avanti390 のコミットを待ってから始めた。sg-tel は途中で重なり、作り直した RDF に sg-tel の分も入っている
- コミット: sg-tel の追加（0814dcc。`build_rdf.py` は sg-tel の 3 行だけを先に入れた）→ URI の差し替えと RDF・検索の作り直し（c66ab5c）→ IIIF のコレクションに sg-tel（1f6add4）。
  sg-tel のダウンロード用ファイルは `skytrain/tools/export_formats.py sg-tel … --no-mount` で作った（公開前の検査に要る）
- 応募の下書きの RailClass の概要に「URI は https://w3id.org/railclass/ で…」の 1 文を入れた。残る【条件】はパートナーリソースだけ
