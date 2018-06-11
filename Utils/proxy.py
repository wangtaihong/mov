# coding:utf-8
import requests
import config


def get_proxy():
    return requests.get(url='%sget/' % config.PROXY_HOST).content


def delete_proxy(proxy):
    return requests.get(url='%sdelete/?proxy=%s' % (config.PROXY_HOST, proxy))
