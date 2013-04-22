#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import time
import random
import requests


def fetch_earthquake():
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
    rand = random.sample(data['features'], 20)
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
        if country == '中国':
            address = province + city
        else:
            address = country + province
        if not address or re.search('[A-Za-z]', address):
            continue
        result.append({
            'lat': lat,
            'lon': lon,
            'place': address.replace(' ', '')})
        if len(result) > 7:
            break
    return result


if __name__ == '__main__':
    for r in fetch_earthquake():
        print r['lat'], r['lon'], r['place']
