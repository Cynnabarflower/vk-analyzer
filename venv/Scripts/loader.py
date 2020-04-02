import vk_caller
import codecs
import json
import time


def getUniversities():
    RUSSIA_ID = 1
    unis = dict()
    admin_api = vk_caller.VKFA('+79629884898', '9841b7a33831ef01')
    admin_api.auth()
    regions = admin_api.database.getRegions(country_id=1)['items']
    mapDataFile = codecs.open('mapData.js', 'r', "utf-8").read()
    mapdata = json.loads(mapDataFile)
    try:
        skip = True
        for region in regions:
            if region['title'] == 'Московская область':
                skip = False
            if skip:
                continue
            unis = dict()
            print(region['title'])
            time.sleep(0.5)
            cities_resp = admin_api.database.getCities(country_id=1, region_id=region['id'], count=1000, need_all=0)
            cities = cities_resp['items']
            while cities_resp['count'] > len(cities):
                off =  len(cities)
                time.sleep(0.5)
                cities_resp = admin_api.database.getCities(country_id=1, region_id=region['id'], count=1000,need_all=0, offset=off)
                cities += cities_resp['items']

            i = 1
            all = str(len(cities))
            for city in cities:
                print('  '+str(i)+'/'+all + ' '+city['title'])
                i = i + 1
                time.sleep(0.3)
                city_unis = admin_api.database.getUniversities(country_id=1, city_id=city['id'])['items']
                if len(city_unis) > 0:
                    unis.update({city['id'] : {'city' : city, 'unis' : city_unis}})
            if len(unis) > 0:
                regionFoud = False
                for regionMapData in mapdata.items():
                    if regionMapData[1]['name'] == region['title']:
                        regionFoud = True
                        mapdata[regionMapData[0]].update({'unis' : unis})
                        break
                if not regionFoud:
                    regId = input('regId '+region['title'])
                    mapdata[regId].update({'unis' : unis})

    except Exception as e:
        print('err:'+region['title'])
        f = open('123unis.txt', "w+", True, 'UTF-8')
        f.write(json.dumps(mapdata))
        f.close()
    f = open('456unis.txt', "w   +", True, 'UTF-8')
    f.write(json.dumps(mapdata))
    f.close()
    return unis


unis = getUniversities()
