# mkdir -p $DIR/.tmp/gtfs/ $DIR/.tmp/zhv/
# 
# unzip $DIR/$D/*gtfs.zip -d $DIR/.tmp/gtfs/
# unzip $DIR/$D/zhv.zip -d $DIR/.tmp/zhv/
# python3 $SCRIPT_DIR/extend-delfi.py $DIR/.tmp/gtfs/stops.txt $DIR/.tmp/zhv/z*.csv $DIR/.tmp/zhv/vrr.csv && zip -j $DIR/delfi-gtfs-extended-zhv-evaNr.zip.tmp $DIR/.tmp/gtfs/* && mv $DIR/delfi-gtfs-extended-zhv-evaNr.zip{.tmp,}
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
stopstxt = sys.argv[1]
with open(stopstxt, mode ='r') as csvfile:
  stops = csv.DictReader(csvfile)
  for line in stops:
      existing[line['stop_id']] = line

  with open('/mnt/lfs3/traines-stc/mirror/hafas-ibnr-zhv-gtfs-osm-matching/full.ndjson') as f:
    for line in f:
      s = json.loads(line)
      if not s['id'] in existing:
        existing[s['id']] = {'stop_id': s['id'], 'stop_code':'', 'stop_name': s['name'], 'stop_desc': '', 'stop_lat': s['location']['latitude'], 'stop_lon': s['location']['longitude'], 'location_type': 0, 'parent_station': s['station']['id'] if 'station' in s else '', 'wheelchair_boarding': 0, 'platform_code': '', 'level_id': ''}
  
  with open(sys.argv[2], mode ='r', encoding='utf-8-sig') as zhvfile:
    zhv = csv.DictReader(zhvfile, delimiter=';')
    i = 0
    for s in zhv:
      if not s['DHID'] in existing:
        existing[s['DHID']] = {'stop_id': s['DHID'], 'stop_code':'', 'stop_name': '', 'stop_desc': '', 'stop_lat': gerfloat(s['Latitude']), 'stop_lon': gerfloat(s['Longitude']), 'location_type': 0, 'parent_station': s['Parent'], 'wheelchair_boarding': 0, 'platform_code': '', 'level_id': ''}
        i+=1
        #print(s['Parent'])
        #if i > 270000:
        #  break
    print(i)


  with open(sys.argv[3], mode ='r', encoding='iso-8859-1') as vrrfile:
    vrr = csv.DictReader(vrrfile, delimiter=';')
    i = 0
    for s in vrr:
      if not s['STOP_NR']+'_' in existing:
        existing[s['STOP_NR']+'_'] = {'stop_id': s['STOP_NR']+'_', 'stop_code':'', 'stop_name': '', 'stop_desc': '', 'stop_lat': s['STOP_POS_Y'], 'stop_lon': s['STOP_POS_X'], 'location_type': 0, 'parent_station': '', 'wheelchair_boarding': 0, 'platform_code': '', 'level_id': ''}
        i+=1
      if not s['GLOBAL_ID'] in existing:
        existing[s['GLOBAL_ID']] = {'stop_id': s['GLOBAL_ID'], 'stop_code':'', 'stop_name': '', 'stop_desc': '', 'stop_lat': s['STOP_POS_Y'], 'stop_lon': s['STOP_POS_X'], 'location_type': 0, 'parent_station': '', 'wheelchair_boarding': 0, 'platform_code': '', 'level_id': ''}


    print(i)

with open(stopstxt, 'w') as csvfile:
  writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=["stop_id","stop_code","stop_name","stop_desc","stop_lat","stop_lon","location_type","parent_station","wheelchair_boarding","platform_code","level_id"],
                            quotechar='"', quoting=csv.QUOTE_ALL)
  writer.writeheader()
  for s in existing:
    writer.writerow(existing[s])