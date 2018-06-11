#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-01 18:50:52
# @Author  : taihong (wangtaihong1@gmail.com)
# @Link    : citybrain.top
# @Version : $Id$

def task_video():
    """
    """
    retry = 5
    i = 0
    while True:
        id = rd.spop(config.douban_tv_task)
        if id is None:
            print(u"task_page sleeping....20sec")
            time.sleep(task_wait)
            continue
        if rd.sismember(config.doubantv_ajax_task_failed, id) == True or rd.sismember(config.doubantv_ajax_task_done, id) == True:
            print(u"already done%s" % id)
            continue
        url = tv_url.format(id=id)
        r = requests_get(url=url, headers=douban_home_headers)
        if r == False or r == None:
            rd.sadd(config.douban_tv_failed, id)
            continue
        try:
            cb = check_block(r)
        except Exception as e:
            print("check_block:",str(e))
        data = parse_video(r)
        if u'检测到有异常请求从你的 IP 发出' in r:
            print("------spider ben block... break......")
            break
        if data.get("title") == None:
            rd.sadd(config.douban_tv_failed, id)
            time.sleep(task_wait)
            # update_session()
            print("------spider ben block...")
            break
            continue
        data['doubanid'] = id
        print(json.dumps(data))
        mongo_r = mongo_douban_tvs.insert(data, check_keys=False)  #
        photostask = json.dumps({"id": id, "mongoTVID": str(mongo_r)})
        if rd.sismember(config.douban_star_done, photostask) == False and rd.sismember(config.douban_photos_failed, photostask) == False:
            rd.sadd(config.douban_photos_task, photostask)
        print(photostask)
        # return True
        rd.sadd(config.douban_tv_done, id)
        # tv_after(id=id, url=url)
        i += 1
        if i % max_step == 0:
            bid = random_str(10)
            session.cookies.set('bid', bid, domain='.douban.com', path='/')
