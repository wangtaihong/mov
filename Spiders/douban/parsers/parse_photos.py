#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-01 18:47:33
# @Author  : taihong (wangtaihong1@gmail.com)
# @Link    : citybrain.top
# @Version : $Id$

def parse_photos(r, data=[]):
    page = etree.HTML(r)
    lis = page.xpath(
        u'//div[@class="article"]/ul[@class="poster-col3 clearfix"]/li')
    # <a href="https://movie.douban.com/subject/1292052/photos?type=R&amp;start=30&amp;sortby=like&amp;size=a&amp;subtype=a">后页&gt;</a>
    if len(lis) > 0:
        for x in lis:
            temp = {}
            temp['doubanid'] = x.get('data-id')
            name_el = x.find('div[@class="name"]')
            prop_el = x.find('div[@class="prop"]')
            cover = x.find('div[@class="cover"]/a')
            if name_el != None:
                temp['name'] = name_el.text.replace(u'\n', '')
                temp['name'] = temp['name'].strip(u' ')
            if prop_el != None:
                temp['prop'] = prop_el.text.replace(u'\n', '')
                temp['prop'] = temp['prop'].strip(u' ')
            if cover != None:
                temp['photos_page'] = cover.get("href")
                temp['url'] = cover.find('img').get("src")
            data.append(temp)
    nextpage = page.xpath(u'//a[contains(text(),"后页")]')
    if len(nextpage) > 0:
        return {"data": data, "next": nextpage[0].get("href")}
    return {"data": data}
