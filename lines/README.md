# Line shapes (display layer)

`<Q>.geojson` is the track of the line with that Wikidata ID, cut out of OpenStreetMap by `tools/osm_lines.py`
(the OSM route relations tagged `wikidata=<Q>`, their ways, simplified to about 30 m). The class pages draw them on a map.

**Licence: these files are © OpenStreetMap contributors, available under the
[Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/).** See https://www.openstreetmap.org/copyright.
If you publish a database made from them, it must be offered under the ODbL as well.

They are a separate display layer, not part of the train-bodies dataset: the RDF, the search index and the class → line
table (`tools/class_lines.tsv`) contain no coordinates and are not under the ODbL.

`_osm.tsv` lists the OSM relations found for each line (line, relation ID, type, route, name).
