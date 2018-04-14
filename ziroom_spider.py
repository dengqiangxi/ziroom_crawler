#!/usr/bin/env python
# -*- coding=utf8 -*-
# Created by dengqiangxi at 2018/4/8

from requests_html import HTMLSession
from path_calculate import calculate_path
from configurations import config
import re
from time import sleep
from jinja2 import Template
from mail_utils import sendmail

from fake_useragent import UserAgent

def get_page_info(url):
    page = session.get(url=url, headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, identity",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": ua.random,
        "Accept-Language": "zh-CN,zh;q=0.9,ja;q=0.8",
    })
    return page.html


# 解析列表页
def parse_page_summary(url):
    html = get_page_info(url)
    if not html:
        raise Exception('获取数据失败')
    lis = html.xpath('//*[@id="houseList"]/li')
    for i in lis:
        info = {}
        details = i.xpath('//div[@class="txt"]')[0]
        page_url = details.xpath('//h3/a/@href')[0]
        detail = details.xpath('//div[@class="detail"]/p/span/text()')
        price = i.xpath('//p[@class="price"]/text()')[0]
        price = number_re.findall(price)[0]
        info['url'] = 'http:' + page_url
        room_number = number_re.findall(info['url'])[0]
        if room_number in file_room_number or room_number in [item['room_number'] for item in suitable_info]:
            continue
        info['room_number'] = room_number
        info['price'] = int(price)
        info['area'] = float(number_re.findall(detail[0])[0])
        if info['area'] > 10 and config['max_price'] > info['price'] > 500:
            sleep(.5)
            parse_page_detail(info)

    next_pages = html.xpath('//div[@class="pages"]/a[@class="next"]/@href')
    if len(next_pages) > 0:
        next_page_url = 'http:' + next_pages[0]
        print(next_page_url)
        sleep(.5)
        parse_page_summary(next_page_url)


# 解析详情页
def parse_page_detail(page_detail_info):
    url = page_detail_info['url']
    html = get_page_info(url)
    if not page_detail_info:
        page_detail_info = {}
    detail_left = html.xpath('//div[@class="area clearfix"]/div[@class="room_detail_left"]')[0]

    # 获取坐标位置
    search_text = detail_left.xpath('//input[@id="mapsearchText"]')[0]
    lng = search_text.xpath('//input/@data-lng')[0]
    lat = search_text.xpath('//input/@data-lat')[0]
    location = {
        'lng': lng,
        'lat': lat
    }

    if 'latlng' in config:
        path = calculate_path(lat, lng)
        if path:
            page_detail_info['distance'] = path['distance']
            page_detail_info['duration'] = path['duration']
            if 'max_distance' in config and int(path['distance']) > config['max_distance']:
                print(page_detail_info['room_number'], "距离不符合")
                return
            if 'max_time' in config and int(path['duration']) > config['max_time']:
                print(page_detail_info['room_number'], "时间不符合")
                return

    page_detail_info['location'] = location
    # 图片
    imgs = detail_left.xpath('//ul[@class="lof-main-wapper"]/li//img/@src')
    if len(imgs) <= 2:
        return
    page_detail_info['imgs'] = [x.replace('v800x600_', 'v4000x4000_') for x in imgs]  # 替换参数，使图片最大
    page_detail_info['img_width'] = 100 / len(page_detail_info['imgs']) if len(page_detail_info['imgs']) <= 3 else 30

    # 房间编号
    sn = ''.join(detail_left.xpath('//div[contains(@class,"aboutRoom")]/h3[@class="fb"]/text()')).replace("\n", '')
    page_detail_info['sn'] = sn

    # 房间描述
    about_room = detail_left.xpath('//div[contains(@class,"aboutRoom")]/p/text()')
    description = about_room[0]
    traffic = about_room[1]
    page_detail_info['description'] = description
    page_detail_info['traffic'] = traffic

    # 房间内配置
    configuration = detail_left.xpath('//ul[contains(@class,"configuration")]/li/text()')
    page_detail_info['configuration'] = configuration

    # 好室友信息
    greatRoommates = detail_left.xpath('//div[@class="greatRoommate"]/ul/li')
    roommates = []
    for i in greatRoommates:
        sex = i.xpath('//li/@class')[0]
        if sex == 'current ':
            continue
        roommate = {}
        roommate['sex'] = sex
        room_location = ''.join(i.xpath('//li//div[contains(@class,"user_top")]/p/text()'))
        room_state = ''.join(i.xpath('//li//div[contains(@class,"user_top")]/span/text()'))
        room_job = i.xpath('//li//div[@class="user_center"]/p[@class="jobs"]/span/text()')[0]
        sign = ''.join(i.xpath('//li//div[@class="user_center"]/p[@class="sign"]/text()'))
        roommate['sign'] = sign
        room_time_interval = ''.join(i.xpath('//li//div[contains(@class,"user_bottom")]/p/text()')).replace(" ", '')
        roommate['room_location'] = room_location
        roommate['room_state'] = room_state
        if room_job != '…' and room_job != '...':
            roommate['room_job'] = room_job
        roommate['room_time_interval'] = room_time_interval
        roommates.append(roommate)
    page_detail_info['roommates'] = roommates

    detail_right = html.xpath('//div[@class="area clearfix"]/div[@class="room_detail_right"]')[0]
    # 标题
    title = ''.join(detail_right.xpath('//div[@class="room_name"]/h2/text()')).replace("\n", '').replace(" ", '')
    page_detail_info['title'] = title
    # tag
    ellipsis = ''.join(detail_right.xpath('//p[@class="pr"]/span[@class="ellipsis"]/text()'))
    page_detail_info['ellipsis'] = ellipsis
    # 价格
    price = ''.join(detail_right.xpath('//span[@class="room_price"]/text()'))
    page_detail_info['price'] = int(price.replace("￥", ''))
    # 标签
    room_tags = detail_right.xpath('//p[contains(@class,"room_tags")]//span/text()')
    page_detail_info['room_tags'] = room_tags

    # 详细信息
    infos_arr = detail_right.xpath('//ul[@class="detail_room"]/li/text()')
    detail_info = {}
    for i in enumerate(infos_arr):
        line = i[1].replace(' ', '').replace('\n', '')
        if not line:
            continue
        parts = line.split('：')
        detail_info[parts[0]] = parts[1]
    if "面积" in detail_info.keys():
        page_detail_info['area'] = float(detail_info['面积'].replace('约', '').replace('㎡', ''))
    if "朝向" in detail_info.keys():
        toward = detail_info['朝向']
        if 'toward' in config and toward != config['toward']:
            print(page_detail_info['room_number'], "朝向不符合")
            return
        if 'not_towards' in config and toward in config['not_towards']:
            print(page_detail_info['room_number'], "朝向不符合")
            return
        page_detail_info['toward'] = toward
    if "户型" in detail_info.keys():
        page_detail_info['house_type'] = detail_info['户型']
    if "楼层" in detail_info.keys():
        page_detail_info['floor'] = detail_info['楼层']

    suitable_info.append(page_detail_info)


def analyze_and_send_mail():
    global current_favor_rooms
    room_numbers = [x['room_number'] for x in suitable_info]
    new_room_info = [x for x in suitable_info if x['room_number'] in room_numbers]
    if new_room_info:
        current_favor_rooms = open("./misc/current_favor_rooms", "a+")
        str_new_info = '\n' + '\n'.join(room_numbers) if file_room_number else '\n'.join(room_numbers)
        current_favor_rooms.write(str_new_info)
        current_favor_rooms.close()
        with open("./templates/template.html", "r") as fd:
            template = Template(fd.read())
            res = template.render(new_room_info=new_room_info)  # 渲染
            sendmail("自如找到了{}个房源".format(len(new_room_info)), res)


if __name__ == '__main__':
    ua = UserAgent()
    # 只匹配数字
    number_re = re.compile("(\d+)")

    session = HTMLSession()

    current_favor_rooms = open("./misc/current_favor_rooms", "r+")

    file_room_number = set([x for x in current_favor_rooms.read().split("\n") if x])

    suitable_info = []

    start_urls = config['urls']
    for url in start_urls:
        parse_page_summary(url)
    analyze_and_send_mail()
