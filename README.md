This project aims to match DB-HAFAS-IDs to DELFI-GTFS-IDs for all train and bus/tram/etc. stations in Germany. [Jump to the results.](#Results)

## Terminology

__DB-HAFAS-IDs__ are the stop/station ids used by the DB-run HAFAS system. Other HAFAS instances most likely use different IDs. Depending on the context DB-HAFAS-IDs might also be called:

* EVA number. Usually only for DB/German train stations. See e.g. [here](https://data.deutschebahn.com/dataset/data-haltestellen.html)
* [IBNR](https://de.wikipedia.org/wiki/Interne_Bahnhofsnummer). Usually only for DB/German train stations.
* UIC number. Might be the same as IBNR for train stations (including the country prefix `80`), but often enough, it seems to differ, at least according to Wikidata (see e.g. [Frankfurt(Main) Hbf](https://www.wikidata.org/wiki/Q165368)). In OSM, there is a tag `uic_ref` which appears to sometimes contain the UIC number and sometimes the IBNR. There is also the very rare tag `ref:IBNR`. Also compare [this OSM discussion](https://community.openstreetmap.org/t/ibnr-nummern-taggen/50564).

However, DB-HAFAS also covers all German bus/tram stations, using IDs without the `80` prefix.

__DELFI-GTFS-IDs__ are the stop/station ids used by the [DELFI GTFS dataset](https://www.govdata.de/daten/-/details/deutschlandweite-sollfahrplandaten-gtfs). They might also be called:

* [DHID](https://www.delfi.de/de/strategie-technik/architektur/), issued/managed by [ZHV](https://zhv.wvigmbh.de/).
* [IFOPT](https://en.wikipedia.org/wiki/Identification_of_Fixed_Objects_in_Public_Transport)-ID, the standard according to which the DHIDs are built.

But, there is a difference between the IDs used in the GTFS dataset and the ZHV ones, see [this issue](https://github.com/mfdz/zhv-issues/issues/12) and below.

## Data sources

* [Official DB Haltestellendaten](https://data.deutschebahn.com/dataset/data-haltestellen.html), [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/), including DB-HAFAS-IDs and station-level IFOPT-IDs for train stations.
* [DELFI GTFS dataset](https://www.govdata.de/daten/-/details/deutschlandweite-sollfahrplandaten-gtfs), [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
* ([ZHV stations](https://zhv.wvigmbh.de/))
* ([OSM](http://download.geofabrik.de/), [ODbL](https://www.openstreetmap.org/copyright), for uic_ref/ref:IBNR-tagged stations and name matching)
* [db-hafas-stations](https://github.com/derhuerst/db-hafas-stations), a collection of about 300k stations from DB-HAFAS, some of which outside of Germany
* additional HAFAS stations not contained in db-hafas-stations obtained as a byproduct of [public-transport-statistics](https://github.com/traines-source/public-transport-statistics), currently about 10k

## Some insights

* IFOPT-IDs have a [hierarchical structure](https://wiki.openstreetmap.org/wiki/Key:ref:IFOPT) `country:admin_area:stop_place:level:quay`, the `stop_place` corresponding most closely to the notion of a station that might have multiple levels/areas/sections and quays.
* DB-HAFAS-IDs are just a number. They are assigned to stations/stops, there is no distinction for areas/quays.
* In the ZHV, a train station and its corresponding bus/tram station are usually identified by a common `stop_place` identifier, having different `level` identifiers.
* In DB-HAFAS, a train station and its corresponding bus/tram station will have two different IDs (though a common parent station, usually the train station).
* The DELFI GTFS and ZHV IDs diverge quite a lot. In particular (as of 2023), many train movements are not tied to the correct quays, but to a top-level `stop_place` postfixed with `_G` instead. E.g. all trains in Frankfurt(Main) Hbf depart from `de:06412:10_G`. Other stations have IDs that are not at all in IFOPT format. Also see [this issue](https://github.com/mfdz/zhv-issues/issues/12). So if you need a mapping from DB-HAFAS-IDs to ZHV-IDs instead of DELFI-GTFS-IDs, you should adjust the procedure below.
* I.e. it is not sufficient to map `stop_place` identifiers to DB-HAFAS-IDs, even though DB-HAFAS-IDs are not as fine-grained as to identify areas/quays.
* Train stations with an additional underground station ("tief") will usually be identified as two different stations by both DB-HAFAS and the ZHV. The corresponding bus/tram station will be assigned to one of the train stations in the ZHV.
* But there are also cases where two train stations with different DB-HAFAS-IDs correspond to a single station (and even quay, due to the `_G` quirk and others) in DELFI-GTFS, e.g. Berlin Ostkreuz [8011162, de:11000:900120003] and Berlin Ostkreuz (S-Bahn) [8089028, de:11000:900120003] or Berlin Hbf (oben) and Berlin Hbf (S-Bahn) (Berlin Hbf (tief) has separate IDs in both).
* There is an [alternative GTFS dataset](https://gtfs.de/de/feeds/) that might be easier to match, but does AFAIK not use IFOPT-IDs.

## Procedure

* Enrich [db-hafas-stations](https://github.com/derhuerst/db-hafas-stations) with additional stations and calling lines from [public-transport-statistics](https://github.com/traines-source/public-transport-statistics) and the known, manually assigned station-level IFOPT-IDs from the official [Official DB Haltestellendaten](https://data.deutschebahn.com/dataset/data-haltestellen.html). (Result below)
* Use an [adapted version](https://github.com/traines-source/nvbw-osm-stop-comparison) of [nvbw-osm-stop-comparison](https://github.com/mfdz/nvbw-osm-stop-comparison) to match DELFI-GTFS-IDS (and optionally ZHV stations) with the DB-HAFAS-stations (instead of OSM stations):
    * If only trains are calling at a given DELFI-GTFS-station/quay, and there exists a DB-HAFAS-station with a manually assigned IFOPT-ID being a prefix of the DELFI-GTFS-ID, then it is very likely a match
    * If things other than trains are calling at the station, it is most likely a bus/tram station that has a completely different DB-HAFAS-ID, i.e. it should not be matched even if the IFOPT-ID-prefixes match!
    * Then we can only rely on fuzzy location, name, mode and line name comparison (and, with enough HAFAS data, in the future possibly entire line routes)
* One fine-grained (quay-level) DELFI-GTFS-ID is usually mapped to one DB-HAFAS-ID (but may be mapped to multiple, see above). One DB-HAFAS-ID is typically mapped to many fine-grained DELFI-GTFS-IDS.
* We favor completeness over accuracy. We try to match every DB-HAFAS-ID to at least one DELFI-GTFS-ID and vice versa, if we have any candidate. However, DB-HAFAS-stations outside of Germany are obviously discarded and in both datasets, stations are missing!

If you want to match against ZHV-IDs instead of DELFI-GTFS-IDs, adjust the `-p` flag of the nvbw-osm-stop-comparison script from `GTFS` to `DELFI` and indicate the ZHV CSV source file using `-s` (see README). Beware that this will have an impact on the quality of the mapping.

## Results
* (Incomplete, best-effort) mapping between DB-HAFAS-IDs and DELFI-GTFS-IDs for all bus/tram/train/etc. stops/stations in Germany, including match rating, as SQL: [hafas-delfi-gtfs-stations-mapping.sql](http://mirror.traines.eu/hafas-ibnr-zhv-gtfs-osm-matching/hafas-delfi-gtfs-stations-mapping.sql)
* Same mapping as CSV: [hafas-delfi-gtfs-stations-mapping.csv](http://mirror.traines.eu/hafas-ibnr-zhv-gtfs-osm-matching/hafas-delfi-gtfs-stations-mapping.csv)
* Containing mappings for ~481000 DELFI-GTFS-IDs and ~258000 DB-HAFAS-IDs (and remember, it's a n:m mapping).
* There are currently ~8000 out of 489000 DELFI-GTFS-IDs not matched, mostly due to wrong coordinates and other issues
* There are currently ~100 out of 6500 train stations not matched, mostly because they are not contained in DELFI-GTFS
* (Incomplete) list of ~310000 DB-HAFAS stations including station-level IFOPT-IDs from [Official DB Haltestellendaten](https://data.deutschebahn.com/dataset/data-haltestellen.html) and (very incomplete) list of calling lines as [fptf](https://github.com/public-transport/friendly-public-transport-format)-[ndjson](http://ndjson.org/): [hafas-stations.ndjson](http://mirror.traines.eu/hafas-ibnr-zhv-gtfs-osm-matching/hafas-stations.ndjson)
* More source files: http://mirror.traines.eu/hafas-ibnr-zhv-gtfs-osm-matching/ and http://mirror.traines.eu/german-gtfs/delfi/

In order to obtain top-level IFOPT-IDs from quay-level ones (including quirks like `_G`), you might use a regex like that: `s/^([^:_]+:[^:_]+:[^:_]+)(_[^:]+)?(:.+)?$/\1/`. Beware, as stated above, that this will result in a fuzzy mapping, even more so than before.

## Related work

* [match-gtfs-rt-to-gtfs](https://github.com/derhuerst/match-gtfs-rt-to-gtfs) – maps HAFAS entites to GTFS entities (primarily lines, departures etc.)
* [nvbw-osm-stop-comparison](https://github.com/mfdz/nvbw-osm-stop-comparison) – maps GTFS to OSM