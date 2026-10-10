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
