# coding=utf-8
import threading
import time

from youku.tasks import spider_seed
from youku.tasks import get_category
from youku.tasks import task_category
from youku.tasks import task_types_fetch
from youku.tasks import task_page_fetch
from youku.tasks import get_detailurl_task
from youku.tasks import go_detail_list_task
from youku.tasks import task_star

# spider_seed.spider_seed()
# get_category.get_category()
# task_category.task_category()   #pass
# task_types_fetch.task_types_fetch()
# task_page_fetch.task_page_fetch()
# get_detailurl_task.get_detailurl_task()
# go_detail_list_task.go_detail_list_task()
# task_star.task_star()

# for i in range(1):
#     t = threading.Thread(target=spider_seed.spider_seed)
#     # t.setDaemon(True)
#     t.start()

# for i in range(1):
#     t = threading.Thread(target=get_category.get_category)
#     # t.setDaemon(True)
#     t.start()

#pass
# for i in range(5):
#     t = threading.Thread(target=task_category.task_category)
#     # t.setDaemon(True)
#     t.start()

# for i in range(20):
#     t = threading.Thread(target=task_types_fetch.task_types_fetch)
#     # t.setDaemon(True)
#     t.start()


# for i in range(20):
#     t = threading.Thread(target=task_page_fetch.task_page_fetch)
#     # t.setDaemon(True)
#     t.start()


for i in range(20):
    t = threading.Thread(target=get_detailurl_task.get_detailurl_task)
    # t.setDaemon(True)
    t.start()


# for i in range(5):
#     t = threading.Thread(target=go_detail_list_task.go_detail_list_task)
#     # t.setDaemon(True)
#     t.start()


# for i in range(5):
#     t = threading.Thread(target=task_star.task_star)
#     # t.setDaemon(True)
#     t.start()

