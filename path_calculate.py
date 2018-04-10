#!/usr/bin/env python
# -*- coding=utf8 -*-
# Created by dengqiangxi at 2018/4/9
import requests, json
from configurations import config


def calculate_path(lat, lng):
    try:
        response = requests.get(
            url="http://restapi.amap.com/v3/direction/walking",
            params={
                "origin": "{},{}".format(lng, lat),
                "destination": config['latlng'],
                "key": config['key'],
            },
        )
        if response.status_code == 200:
            detail = json.loads(response.text)['route']['paths']
            if len(detail) > 0:
                return detail[0]
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
