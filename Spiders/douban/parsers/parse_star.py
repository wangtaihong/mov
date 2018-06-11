#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-01 18:46:52
# @Author  : taihong (wangtaihong1@gmail.com)
# @Link    : citybrain.top
# @Version : $Id$

def parse_star(r):
    if r == False or r == None:
        return False
    page = etree.HTML(r)
    data = {}
    name = page.xpath(u'//div[@id="content"]/h1')
    if len(name) > 0:
        data['name'] = name[0].text
    imgUrl = page.xpath(u'//div[@class="pic"]/a[@class="nbg"]')
    if len(imgUrl) > 0:
        data['imgUrl'] = imgUrl[0].get("href")
    gender = page.xpath(u'//span[contains(text(),"性别")]/following::text()[1]')
    if len(gender):
        gender = re.sub('\n', '', gender[0])
        gender = gender.strip(':')
        data['gender'] = gender.strip(' ')

    constellation = page.xpath(
        u'//span[contains(text(),"星座")]/following::text()[1]')
    if len(constellation) > 0:
        constellation = re.sub('\n', '', constellation[0])
        constellation = constellation.strip(':')
        data['constellation'] = constellation.strip(' ')

    date_birth = page.xpath(
        u'//span[contains(text(),"出生日期")]/following::text()[1]')
    if len(date_birth) > 0:
        date_birth = re.sub('\n', '', date_birth[0])
        date_birth = date_birth.strip(':')
        date_birth = date_birth.strip(' ')
        data['date_birth'] = date_birth.strip(' ')
    birthplace = page.xpath(
        u'//span[contains(text(),"出生地")]/following::text()[1]')
    if len(birthplace) > 0:
        birthplace = re.sub(u'\n', "", birthplace[0])
        birthplace = birthplace.strip(':')
        data['birthplace'] = birthplace.strip(' ')

    occupation = page.xpath(
        u'//span[contains(text(),"职业")]/following::text()[1]')
    if len(occupation) > 0:
        occupation = re.sub('\n', '', occupation[0])
        occupation = occupation.strip(':')
        data['occupation'] = occupation.strip(' ')

    foreign_names = page.xpath(
        u'//span[contains(text(),"更多外文名")]/following::text()[1]')
    if len(foreign_names) > 0:
        foreign_names = re.sub('\n', '', foreign_names[0])
        foreign_names = foreign_names.strip(':')
        data['foreign_names'] = foreign_names.strip(' ')

    zh_names = page.xpath(
        u'//span[contains(text(),"更多中文名")]/following::text()[1]')
    if len(zh_names) > 0:
        zh_names = re.sub('\n', '', zh_names[0])
        zh_names = zh_names.strip('\n')
        data['zh_names'] = zh_names.strip(' ')

    family_member = page.xpath(
        u'//span[contains(text(),"家庭成员")]/following::text()[1]')
    if len(family_member) > 0:
        family_member = re.sub('\n', '', family_member[0])
        family_member = family_member.strip(':')
        data['family_member'] = family_member.strip(' ')

    imdb = page.xpath(u'//span[contains(text(),"imdb编号")]')
    if len(imdb) > 0:
        if imdb[0].getnext() is not None:
            data['imdb'] = imdb[0].getnext().text

    intro = page.xpath(u'//span[@class="all hidden"]/text()')
    _intro = page.xpath(u'//div[@id="intro"]/div[@class="bd"]/text()')
    if len(intro):
        data['intro'] = "".join(intro)
    else:
        data['intro'] = "".join(_intro)
    return data