#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-01 18:51:50
# @Author  : taihong (wangtaihong1@gmail.com)
# @Link    : citybrain.top
# @Version : $Id$

def task_star():
    """
    """
    retry = 5
    i = 0
    while True:
        task = rd.spop(config.douban_star_task)
        if task is None:
            print(u"task_page sleeping....20sec")
            time.sleep(task_wait)
            continue
        if rd.sismember(config.douban_star_failed, task) == True or rd.sismember(config.douban_star_done, task) == True:
            print(u"already done%s" % task)
            continue
        print(task)
        url = star_url.format(id=task)
        # url = u'https://movie.douban.com/subject/1292052/photos?type=R'
        print(url)
        r = requests_get(url=url)
        data = parse_star(r)
        if data == False or data == None or data.get("name") == None:
            rd.sadd(config.douban_star_failed, task)
            update_session()
            time.sleep(20)
            print("------spider ben sleep 20 sec...")
            continue
        data['doubanid'] = task
        print(json.dumps(data))
        result = mongo_douban_stars.insert(data, check_keys=False)
        print('done.', result)
        i += 1
        rd.sadd(config.douban_star_done, task)
        if i % max_step == 0:
            bid = random_str(10)
            session.cookies.set('bid', bid, domain='.douban.com', path='/')
