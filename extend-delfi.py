# mkdir -p $DIR/.tmp/gtfs/ $DIR/.tmp/zhv/
# 
# unzip $DIR/$D/*gtfs.zip -d $DIR/.tmp/gtfs/
# unzip $DIR/$D/zhv.zip -d $DIR/.tmp/zhv/
# python3 extend-delfi.py $DIR/.tmp/gtfs/stops.txt $DIR/.tmp/zhv/z*.csv $DIR/.tmp/zhv/vrr.csv
# zip -j $DIR/delfi-gtfs-extended-zhv-evaNr.zip $DIR/.tmp/gtfs/*
# rm -r $DIR/.tmp/




import json
import csv
import sys
# "stop_id","stop_code","stop_name","stop_desc","stop_lat","stop_lon","location_type","parent_station","wheelchair_boarding","platform_code","level_id"
#"de:06413:8041:2:2","","Offenbach (Main)-Rumpenheim Kurhessenplatz","NRumpenheim","50.129675000000","8.797545000000",0,,0,"","2"

#"SeqNo";"Type";"DHID";"Parent";"Name";"Latitude";"Longitude";"MunicipalityCode";"Municipality";"DistrictCode";"District";"Description";"Authority";"DelfiName";"THID";"TariffProvider";"LastOperationDate";"SEV"
#"0";"Q";"de:07334:1723:3:311";"de:07334:1723:3";"B>RWRT";"49,038597";"8,291136";"00000000";"-";"-";"-";"";"NVBW";"-";"-";"-";"";"nein"
def gerfloat(gf):
  return float(gf.replace(',','.'))

existing = {}
header = None
stopstxt = sys.argv[1]
with open(stopstxt, mode ='r') as csvfile:
  stops = csv.reader(csvfile)
  for line in stops:
    if header is None:
      header = line
      print(line)
    else:    
      existing[line[0]] = line

  with open('/mnt/lfs3/traines-stc/mirror/hafas-ibnr-zhv-gtfs-osm-matching/full.ndjson') as f:
    for line in f:
      s = json.loads(line)
      if not s['id'] in existing:
        existing[s['id']] = [s['id'], '', s['name'], '', s['location']['latitude'], s['location']['longitude'], 0, s['station']['id'] if 'station' in s else '', 0, '', '']
  
  with open(sys.argv[2], mode ='r', encoding='utf-8-sig') as zhvfile:
    zhv = csv.DictReader(zhvfile, delimiter=';')
    i = 0
    for s in zhv:
      if not s['DHID'] in existing:
        existing[s['DHID']] = [s['DHID'], '', '', '', gerfloat(s['Latitude']), gerfloat(s['Longitude']), 0, s['Parent'], 0, '', '']
        i+=1
        #print(s['Parent'])
        #if i > 270000:
        #  break
    print(i)

#VERSION	STOP_NR	STOP_TYPE	STOP_NAME	STOP_NAME_WITHOUT_LOCALITY	STOP_SHORTNAME	STOP_POS_X	STOP_POS_Y	PLACE	OCC	FARE_ZONE1_NR	FARE_ZONE2_NR	FARE_ZONE3_NR	FARE_ZONE4_NR	FARE_ZONE5_NR	FARE_ZONE6_NR	GLOBAL_ID	VALID_FROM	VALID_TO	PLACE_ID	GIS_MOT_FLAG	IS_CENTRAL_STOP	IS_RESPONSIBLE_STOP	INTERCHANGE_TYPE	INTERCHANGE_QUALITY
#57	77	0	Dortmund Oberdelle	Oberdelle	ObDel	7.3228685	51.5160517	Dortmund	5913000	374	-1	-1	-1	-1	-1	de:05913:77	19781001	25001231	c5e35586-2e68-4b9d-b9fd-6c86135feeda	0	0	0	2	0

  with open(sys.argv[3], mode ='r', encoding='iso-8859-1') as vrrfile:
    vrr = csv.DictReader(vrrfile, delimiter=';')
    i = 0
    for s in vrr:
      if not s['STOP_NR']+'_' in existing:
        existing[s['STOP_NR']+'_'] = [s['STOP_NR']+'_', '', '', '', s['STOP_POS_Y'], s['STOP_POS_X'], 0, s['GLOBAL_ID'], 0, '', '']
        i+=1
      if not s['GLOBAL_ID'] in existing:
        existing[s['GLOBAL_ID']] = [s['GLOBAL_ID'], '', '', '', s['STOP_POS_Y'], s['STOP_POS_X'], 0, '', 0, '', '']

 
    print(i)

with open(stopstxt, 'w') as csvfile:
  writer = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
      
  writer.writerow(header)
  for s in existing:    
    writer.writerow(existing[s])
