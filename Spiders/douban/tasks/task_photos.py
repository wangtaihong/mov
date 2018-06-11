#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-01 18:51:16
# @Author  : taihong (wangtaihong1@gmail.com)
# @Link    : citybrain.top
# @Version : $Id$

def task_photos():
    """
    """
    retry = 5
    i = 0
    photos_url = u'https://movie.douban.com/subject/{id}/photos?type=R'
    while True:
        task = rd.spop(config.douban_photos_task)
        if task is None:
            print(u"task_page sleeping....20sec")
            time.sleep(task_wait)
            continue
        if rd.sismember(config.douban_photos_failed, task) == True or rd.sismember(config.douban_photos_done, task) == True:
            print(u"already done%s" % task)
            continue
        T = json.loads(task)
        print(task)
        url = photos_url.format(id=T['id'])
        # url = u'https://movie.douban.com/subject/1292052/photos?type=R'
        print(url)
        data = []
        for x in get_photos(url=url, id=T['id']):
            if x == False or len(x) == 0:
                rd.sadd(config.douban_photos_failed, task)
                update_session()
                time.sleep(20)
                print("------spider ben sleep 20 sec...")
                break
            data = x
        result = mongo_douban_tvs.update_one(
            {'_id': ObjectId(T['mongoTVID'])}, {'$set': {'poster': data}})
        print('done.', result.modified_count)
        if result.modified_count == 0:
            rd.sadd(config.douban_photos_failed, task)
        i += 1
        if i % max_step == 0:
            bid = random_str(10)
            session.cookies.set('bid', bid, domain='.douban.com', path='/')
