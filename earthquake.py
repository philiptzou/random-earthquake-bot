#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
import random
import requests


def fetch_earthquake(num):
    maxtime = int(time.time() * 1000)
    mintime = maxtime - 86400000 * 60
    resp = requests.get(
        'http://comcat.cr.usgs.gov/earthquakes/feed/search.php',
        params={
            'maxEventLatitude': 90.0,
            'minEventLatitude': -90.0,
            'minEventLongitude': -180.0,
            'maxEventLongitude': 180.0,
            'minEventTime': mintime,
            'maxEventTime': maxtime,
            'minEventMagnitude': 4.5,
            'maxEventMagnitude': 10,
            'minEventDepth': 0.0,
            'maxEventDepth': 100.0,
            'format': 'geojson'})
    data = resp.json()
    rand = random.sample(data['features'], num * 4)
    result = []
    for geo in rand:
        lon, lat, dpt = geo['geometry']['coordinates']
        place = geo['properties']['place']
        resp = requests.get(
            'http://maps.googleapis.com/maps/api/geocode/json',
            params={
                'address': '%s,%s' % (lat, lon),
                'sensor': 'false',
                'language': 'zh-CN'})
        results = resp.json()['results']
        if not results:
            continue
        country = province = city = ''
        for addr in results[0]['address_components']:
            type_ = addr['types'][0]
            if type_ == 'country':
                country = addr['long_name']
            elif type_ == 'administrative_area_level_1':
                province = addr['long_name']
            elif type_ == 'locality':
                city = addr['long_name']
        if country == u'中国':
            address = province + city
            is_china = True
        else:
            address = country + province
            is_china = False
        if not address or re.search('[A-Za-z]', address):
            continue
        result.append({
            'lat': lat,
            'lon': lon,
            'is_china': is_china,
            'place': address.replace(' ', '')})
        if len(result) > num - 1:
            break
    return result


TPL = [u'兰顿算法是有史以来靠谱的地震预测方法，其地位类似于隔壁三婶的二儿媳妇她同学认识的刘半仙真人。通过兰顿算法的精确计算，%(area)s附近可能会在未来%(hour).2f小时内发生地震。',
       u'兰顿算法是史上最牛逼的地震预测方法，由隔壁三百多位清廉的科学家为隔壁混小子拍胸脯保证其正确性，其重要程度堪比银河系搭车客们的毛巾。按照兰顿算法的精确运算，%(area)s附近可能会在未来%(hour).2f小时内发生地震。',
       u'兰顿预报中心提醒您：请准备好毛巾和泛银河系含漱爆破液。在未来%(hour).2f小时内，隐形粉红独角兽将在飞面大神的触手包裹下降临地球，并可能会在%(area)s附近为您提供震一震服务。']
ACCESS_TOKEN = [] # 这里填写一大堆用implicit流程搞来的access token就可以了


def weibo():
    num = random.randint(3, 6)
    eq = fetch_earthquake(num)
    if not eq:
        return
    places = list(set([e['place'] for e in eq]))
    area = u'、'.join(places[:-1])
    area += u'或' + places[-1]
    text = random.choice(TPL)
    text = text % {'area': area,
                  'hour': random.randrange(24, 80, int=float)}
    points = []
    alpha = 65
    center = '%s,%s' % (eq[0]['lat'], eq[0]['lon'])
    for e in eq:
        lat, lon = e['lat'], e['lon']
        points.append('color:red|label:%s|%s,%s' % (chr(alpha), lat, lon))
        alpha += 1
        if e['is_china']:
            center = '%s,%s' % (lat, lon)
    resp = requests.get(
        'http://maps.googleapis.com/maps/api/staticmap',
        params={'center': center,
                'zoom': 2,
                'size': '800x800',
                'maptype': 'terrain',
                'markers': points,
                'sensor': 'false',
                'language': 'zh-CN'})
    resp = requests.post(
        'https://upload.api.weibo.com/2/statuses/upload.json',
        data={'access_token': random.choice(ACCESS_TOKEN),
              'status': text.encode('U8')},
        files={b'pic': ('test.png', resp.content)})
    print text
    print resp.status_code


if __name__ == '__main__':
    weibo()
    #for r in fetch_earthquake():
    #    print r['lat'], r['lon'], r['place']
