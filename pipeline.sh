set -xe

DATE=$(date --iso-8601)

echo "Downloading GTFS data..."
wget https://data.public-transport.earth/gtfs/de -N -O ${DATA_DIR_GTFS}/gtfs_${DATE}.zip

if [ "$USE_PTS_DB" = true ] ; then
    echo "Downloading DB Haltestellendaten..."
    wget https://download-data.deutschebahn.com/static/datasets/haltestellen/D_Bahnhof_2020_alle.CSV -N -P ${DATA_DIR_STORE}

    echo "Dumping HAFAS stations... (This might take some minutes)"
    # Docker image built from https://github.com/traines-source/public-transport-statistics
    docker run --rm -it $DOCKER_EXTRA_FLAGS \
   -v ${DATA_DIR_STORE}:/data/ \
    traines-source/public-transport-stats node ingest/stations/dump.js
else
    echo "Downloading HAFAS station dataset..."
    wget http://mirror.traines.eu/hafas-ibnr-zhv-gtfs-osm-matching/hafas-stations.ndjson -N -P ${DATA_DIR_STORE}

echo "Matching stations... (This might take an hour or two)"
# Docker image built from https://github.com/traines-source/nvbw-osm-stop-comparison
docker run --rm -it $DOCKER_EXTRA_FLAGS \
    -v ${DATA_DIR_GTFS}:/usr/src/app/gtfs:ro \
    -v ${DATA_DIR_STORE}:/usr/src/app/data:ro \
    -v ${DATA_DIR_WORKING}:/usr/src/app/out \
    mfdz/gtfs-osm-stops-matcher \
    python compare_stops.py -g gtfs/gtfs_${DATE}.zip -f data/hafas-stations.ndjson -p GTFS -d out/stops.db

echo "Exporting mapping..."
docker run --rm -it $DOCKER_EXTRA_FLAGS \
    -v ${DATA_DIR_STORE}:/usr/src/app/data \
    -v ${DATA_DIR_WORKING}:/usr/src/app/out \
    mfdz/gtfs-osm-stops-matcher sqlite3 out/stops.db \
'DROP TABLE IF EXISTS station_mapping;' \
'CREATE TABLE station_mapping AS SELECT m.ifopt_id, m.osm_id AS ibnr, ROUND(m.rating, 2) AS rating, h.Haltestelle_lang AS delfi_name, f.name AS db_name FROM matches m JOIN fptf_stops f ON m.osm_id = f.ibnr JOIN haltestellen_unified h ON m.ifopt_id = h.globaleid;' \
'.output /usr/src/app/data/hafas-delfi-gtfs-stations-mapping.sql' '.dump station_mapping' \
'.headers on' '.mode csv' '.output /usr/src/app/data/hafas-delfi-gtfs-stations-mapping.csv' 'select * from station_mapping;' \
'.quit'


echo "Done."



