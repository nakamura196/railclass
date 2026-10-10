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
