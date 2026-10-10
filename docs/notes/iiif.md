# IIIF Presentation 4.0 で 3D モデルを記述する — 実験ノート

担当 B（IIIF・注釈・ダウンロード）。取り決めは data-model.md の「位置付けと並行作業の取り決め」。

## 2026-10-09

### IIIF Presentation 4.0 の今の状態（この日に確かめた）

- **正式版ではなく草案。** https://iiif.io/api/presentation/4.0/ の表記は「4.0.0-draft」。最新の安定版は 3.0.0。
  2025-08-11 の IIIF のロードマップ（https://iiif.io/news/2025/08/11/roadmap/）は「v4 Alpha を公開し、
  次の 1 年で正式版へ進める」としていた。正式版の公開日は見つからなかった。→ 書き方は今後変わりうる。
- **`@context` は `http://iiif.io/api/presentation/4/context.json`。ただし、この URL は今 `{}`（空の JSON）を返す。**
  JSON-LD として RDF に展開すると何も残らない。RDF への橋渡しは Manifest ではなく `seeAlso` の先（担当 A）に任せる理由の 1 つになる。
- 3D の書き方（仕様の本文と、IIIF 3D TSG の例 https://github.com/IIIF/3d の manifests/9_commenting_annotations、
  10_activating_annotations、最終更新 2026-07-09）:
  - 入れ物は `Scene`（無限に広い 3 次元空間、右手系、y が上）。glb は `painting` の注釈の body に
    `"type": "Model", "format": "model/gltf-binary"` で置く。
  - 部位の注釈は `commenting`。target は `SpecificResource`（source = Scene）に `PointSelector`（x, y, z）。
    領域なら `WktSelector`（`POLYGON Z (...)`）。
  - 視点はカメラの注釈（body が `PerspectiveCamera`、`lookAt` に注視点、target の PointSelector が位置）。
    部位の注釈とカメラは `scope` で結ぶ（「この注釈を選んだら、このカメラに切り替える」の略記）。
    最初の、`hidden` でないカメラが既定の視点になる。
  - `navPlace` は v3 では拡張だったが、v4 では本体の仕様に入った。GeoJSON の FeatureCollection。
  - `spatialScale`（Scene の 1 単位が何 m か）、`fileSize`（rendering のファイルの大きさ）が新しく使える。
- v4 を読めるビューア（IIIF 公式の 3D の例のページが挙げているもの）: Kompakkt、Smithsonian Voyager の開発版。
  ほかに、本人の iiif-3d-viewer（~/git/ogawa/iiif-3d-viewer、https://3d.ldas.jp/）が v4 の Scene を読む。

### ICE T 411 の Manifest 1 つで試した

- 作ったもの:
  - `annotations/icet_411.json` — 部位 16 か所の元データ（名前・説明 ja/en・区分・Wikidata の項目・位置）
  - `tools/build_iiif.py` — 元データと glb から `docs/iiif/icet_411/manifest.json` を作る
  - `~/git/3d/skytrain/tools/export_formats.py` — ダウンロード用のファイルを `docs/downloads/icet_411/` に作る
- **部位の位置は、模型の図面の座標（skytrain/models/icet_base.py と同じ、鼻の先から x、縁から高さ z）で書き、
  glb の面に光線を当てて表面の点を求める。** 当たった三角形の色（材質名）を「その部位の色」と照らし合わせ、
  違えば生成を止める。最初の試しで 16 か所中 3 か所（「ICE」の文字、1 等の黄色い線、連結面の灰色の桟）が外れていたのを、
  これで見つけた。文字は x 44 を左端と思っていたが中央だった（実際は x 40〜48.5、高さ 8.5〜12.5）。
  - 手で表面の座標を書くと、模型を作り直したときに点が宙に浮くか埋もれる。図面の座標なら作り直しに付いてくる。
- 注釈の body は 4 つまで: 説明（日本語・英語、purpose = describing）、区分（purpose = tagging、
  「実車の特徴」12・「模型の都合」3・「推測」1）、Wikidata の項目（前照灯 Q869713 などは identifying、
  DB のマーク → Deutsche Bahn Q9322、連結器のカバー → 連結器 Q1501648 のように「それそのものではない」ものは linking）。
  - 「模型の都合」を分けたのは、この模型が実物の縮尺模型ではないため（長さ 1/183、幅と高さは車台に合わせた、
    下の灰色の帯は実車に無い）。注釈で実車の記述と模型の改変を混ぜないため。
- `seeAlso`: モデルの RDF（`rdf/model/icet_411.ttl`・`.jsonld`）、形式の RDF（`rdf/class/Q696668.ttl`・`.jsonld`）、
  Wikidata の Q696668。ICE T の形式は Wikidata の Q696668（ICE TD は Q659660）。RDF のファイルは担当 A が作り、main に入った（2026-10-09 に 4 つとも在ることを確認。この worktree はその前の main から分けたので、まだ入っていない）。
- `rendering`: glb（`models/` にあるものを指す。二重に置かない）、STL、OBJ + MTL（zip）、USDZ。
  各ファイルに `fileSize` を付けた。1 モデルあたり 4.9 MB（STL 1.71、OBJ zip 0.59、USDZ 2.84）。
- **STEP は作らなかった。** 今のモデルは三角形の集まりなので、STEP に入れても平らな面を貼り合わせた殻になり、
  CAD で寸法を直せる立体にはならない。「CAD 形式あり」と書くと実際より多くを約束してしまう。
  FreeCAD もこの端末に入っていない。作るなら、Blender のスクリプトの段階で立体の形を持つ必要がある（未着手）。
- `navPlace`: 車番を取った写真（Commons「Dresden_DB_411525_01.JPG」、Ad Meskens、CC BY-SA 4.0、2015-06-02）の
  撮影地（ドレスデン中央駅、Commons に記録された位置）を 1 点。ほかの 2 枚には位置の記録が無かった。
  - 形式の Manifest の navPlace に「何の場所」を置くかは決めていない。今回は「記述の根拠にした写真の撮影地」とした。
    形式の運行範囲（線や国）を出すなら RDF 側（担当 A）から取るほうが筋がよい。
- `rights` は空けた。モデルのライセンスがまだ決まっていない。

### ビューアで確かめた

- 公開中の https://3d.ldas.jp/ から手元のサーバ（http://127.0.0.1）の Manifest を読ませると、
  ブラウザが取りに行かない（https のページから手元の http への読み込みを Chrome が止める）。
  iiif-3d-viewer の書き出し済みファイル（out/、2026-09-28）を手元で配って試した。
- 表示できたもの: 模型、メタデータ、サムネイル、提供者、ダウンロード 4 つ、関連リンク 5 つ、注釈 16 件（日本語の説明）、
  区分のタグでの絞り込み、模型の上の注釈の印。印を押すと該当の場所が強調される（連結器のカバーで確認）。
- 表示されなかったもの（ビューアの側の作りによる。Manifest は仕様と IIIF/3d の例に合わせたまま）:
  1. **注釈の見出し**（Annotation の `label`）。ビューアは body の `label` を見出しに使う
  2. **カメラ**。ビューアはカメラを独自の形（body が SpecificResource で source に PerspectiveCamera）で探し、
     カメラを `scope` ではなく独自の `cameraAnnotation` か「注釈の id + /camera」で結ぶ。
     今回のカメラの id は「注釈の id + /camera」にしてあるので、body の形さえ読めれば効く
  3. 参考写真の 2 つ目以降（metadata の値が複数のとき、最初の 1 つだけ出る）
- Kompakkt・Voyager では試していない（https のページなので、Manifest を公開してからでないと試せない）。

### 決めていないこと

- モデルのライセンス（`rights`）。
- ダウンロードのファイルを git に入れるか。14 モデルで約 70 MB、作り直すたびに履歴が増える。
  GitHub の Releases に置き、Manifest からはそちらを指す案がある。
- iiif-3d-viewer を仕様の書き方（Annotation の label、PerspectiveCamera の body、scope）も読めるように直すか。
  直せば、このサイトの Manifest を 3d.ldas.jp でそのまま見せられる。

- 主張の候補: 部位の注釈の位置を、表面の座標ではなく「生成スクリプトの図面座標 + 光線」で持つと、
  手続き的に作り直すモデルでも注釈が外れない。外れたら色の照合で機械的に分かる。根拠: 上の 16 か所中 3 か所の検出。

### 残り 13 モデルに広げた（同じ日の続き）

- 14 モデルすべての Manifest ができた（`docs/iiif/<model>/manifest.json`）。部位の注釈は計 220 件
  （実車の特徴 174・模型の都合 36・推測 10）。1 モデル 14〜16 件。navPlace の点は計 21（Commons に位置の記録がある写真だけ）。
  SkyTrain の 4 形式は写真の位置の記録が多く、各 4 点。ICE T は icet_411 と icet_dsb（コペンハーゲン）だけ。Airo は 0。
- 注釈の文は、系列ごとに作業を分けて書いた（ICE T 5 種・SkyTrain 4 種・Airo/AVE/バス 4 種）。どれも生成スクリプトと
  実験ノート（skytrain/docs/notes/）と参考写真から読める範囲に限り、確かめていないことは文中に「確かめていない」と書いた。
- 光線と色の照合は 14 モデルとも追加の手直しなしで通った。ただし次の 2 か所は細い線の上で、模型を少し直すと外れうる:
  icet_oebb の車番（x 109.2, z 6.8）、icet_dsb の DSB のマーク（x 58.75, z 8.1）。外れたら点を打ち直す（expect は変えない）。
- 道具の手直し:
  - `build_iiif.py`: 材質名の末尾の「.001」（Blender が重複名に付ける。mk2・mk3）を落として照合する。
  - `build_iiif.py`: 面「farside」（図面の +y 側、glTF の −Z から）を足した。バスの乗降扉は歩道側にしか無く、
    これまでの「side」（−y 側）からは狙えなかった。
  - `build_iiif.py`: 形式の鍵を担当 A の `docs/rdf/class/` に合わせた。SkyTrain は Wikidata に Mark ごとの項目が無く
    `tb-skytrain-mk1` などの独自の鍵なので、seeAlso の Wikidata は元データの `wikidata`（系列 Innovia Metro Q4940487）を
    「上位の項目」として出す。
  - **訂正: icet_411 の形式は Q696668（ICE T 全体）ではなく Q115612330（DB 411 形）にした。** 担当 A がモデルの RDF で
    411 形を Q115612330 に結んでいたので、それに合わせた。
  - `skytrain/tools/export_formats.py`: out/ のファイル名がモデル名と違う（`skytrain_mk2.glb`、`translink_bus49_rear.glb` など）
    ので、out/<model>/ の glb の名前から元の名前を取るようにした。OBJ の zip の中は元の名前のまま（.obj が .mtl を名前で探すため）。
- 推測で振った車番（415 001・605 001、緑帯の車に流用した 411 525）は、区分を「推測」にした。根拠の無い Wikidata の結び付け
  （バスの扉 → プラグドア）は外した。
- ダウンロードのファイルは 14 モデルで 54 MB（前の見積もり 70 MB より小さい）。git に入れるか Releases にするかは、まだ決めていない。
- 確かめていないこと: 13 モデル分はビューアで見ていない。SkyTrain の写真の位置は、Commons の記録が撮影者の位置か被写体の位置か
  混ざっている。Mk2 の車番は前面 326・側面 323 で食い違う（前面だけを使い、メタデータに書いた）。

## 2026-10-10

### 公開中の 14 本を iiif-3d-viewer で表示した

- 見方: iiif-3d-viewer の書き出し済みファイル（out/、2026-09-28、f22a0f7）を手元（http://127.0.0.1:8790）で配り、
  `/ja/viewer/?manifest=<公開中の Manifest の URL>` で開いた。GitHub Pages は `Access-Control-Allow-Origin: *` を返すので、
  手元の http のページから https の Manifest を読める（逆向きの、https のページから手元の http は止められる）。
- 先に、Manifest が指す先を機械的に確かめた（`id` を持つ Model・Image・Dataset・Text をすべて HEAD で取得）。
  取れないのはダウンロード 42 件（14 本 × STL・OBJ zip・USDZ、`docs/downloads/` が git に無いため）だけ。
  模型（glb）・サムネイル・RDF・Wikidata への参照はすべて 200。
- 14 本とも、模型・メタデータ・サムネイル・注釈の一覧・区分のタグが出た。注釈の件数はビューアの表示と Manifest が一致
  （計 220。実車の特徴 174 は区分のタグの件数の合計でも一致）。ブラウザのコンソールにビューア側のエラーは無し。
- **初めの視点が模型の鼻先に寄りすぎる（14 本とも同じ）。** ビューアは最初のカメラを固定の位置（0, 2, 5）に置き、
  模型の大きさに合わせて引かない。床の格子も 10 単位で、1 単位 = 1 m の模型を前提にしている。
  こちらの glb は 1 単位 = 1 mm（`spatialScale` 0.001 m、長さ 130〜152）なので、カメラが鼻のすぐ前に来る。
  Manifest のカメラ（PerspectiveCamera の注釈）を読めば解決するが、前回書いたとおり、このビューアは仕様の書き方のカメラを読まない。
  - glb を m 単位に縮める手はとらない。`spatialScale` で単位を宣言するのが仕様の書き方で、注釈の座標もすべて mm で書いてある。
- 読み込みに 10〜30 秒かかることがあった。glb と環境光の画像（hdr）の取得は数ミリ秒で終わっており、
  遅いのは描画の側（自動操作のタブが裏に回っていたためと思われる。確かめていない）。Manifest の問題ではない。
- 確かめていないこと: navPlace の地図表示（ビューアの georef ページ）、注釈を押したときの視点の移動（前回 icet_411 の 1 か所だけ）、
  Kompakkt・Voyager での表示（Manifest は公開済みなので試せるようになった）。

### 「IIIF v4 の実例」としての位置付けと先行例（同じ日、10:05）

調べ方: ウェブ検索（2026-10-10）と、IIIF 3D TSG のリポジトリ（https://github.com/IIIF/3d）の例を読んだ。網羅的な調査ではない。

先行例:
- MorphoSource（デューク大学の 3D データの公開基盤）。全件のプレビューが IIIF 4 の Manifest で動いているという。
  出典: Thomas Flynn「Interoperable, Accessible, Portable 3D Data」2025-06-30（https://nebulousflynn.substack.com/p/interoperable-accesible-portable）。
  同じ記事は、部位へのコメントの注釈があるとだけ書き、点の位置・注釈ごとのカメラ・navPlace には触れていない。Manifest そのものは見ていない。
- Smithsonian Voyager（https://3d.si.edu/iiif-support）。v4 への対応は開発中で、試験用の Manifest がある、という段階。
- IIIF 3D TSG の例（MorphoSource のゴリラの頭骨、Royal Pavilion & Museums の鳥の剥製、British Library の書き物机ほか）。
  仕様を詰めるための例で、古い書き方のものも混じる。
- 仕様の本文の例（チェスの駒の Scene など）。

このサイトの Manifest で、上の先行例に見当たらなかった点（「無い」とは言い切れない。見つからなかった、という意味）:
- 部位ごとの `commenting` 注釈と、その部位を見せるカメラを `scope` で結んだ実データが、1 モデルに 10〜16 件ずつ、14 モデルある
  （公開しているページで、注釈を選ぶとカメラが寄るところまで動く）。
- 注釈に「実車の特徴／模型の都合／推測」の区分を持たせ、実車の特徴には Wikidata の項目を付けている。
- Manifest の `seeAlso` から、形式の RDF（Wikidata・ERATV と結んだもの）に渡れる。`navPlace` に運行地域を入れている。
- 注釈の位置を、生成スクリプトの図面座標から光線で求めている（前の主張の候補）。

- 主張の候補: 「文化財の 3D」でなく「量産品の形式（鉄道車両の形式）」を単位にして、IIIF v4 の 3D Manifest と Linked Data を結んだ実例。
  根拠: 上の先行例はいずれも 1 点ものの資料（標本・美術品）。形式の RDF への seeAlso は iiif/<モデル>/manifest.json にある。
- 限界: MorphoSource の Manifest の中身を見ていない。点の注釈とカメラの組み合わせがそこにあるかは未確認。次に確かめるなら、MorphoSource の公開データ 1 件の Manifest を取って読む。

