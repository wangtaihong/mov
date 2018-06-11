# coding=utf-8
"""
douban首页headers
"""
import user_agent
ua = user_agent.generate_navigator(os=None, navigator=None, platform=None, device_type=None)

douban_home_headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate, br',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Cache-Control': 'max-age=0',
	'Connection': 'keep-alive',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': ua["user_agent"]
}

'''douban ajax拉取电影列表'''
douban_referer_tag_headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'movie.douban.com',
    'Referer': 'https://movie.douban.com/tag/',
    'User-Agent': ua["user_agent"]
}

'''douban movies search headers'''
douban_ajax_search_headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'movie.douban.com',
    'Referer': 'https://movie.douban.com/',
    'User-Agent': ua["user_agent"],
    'X-Requested-With': 'XMLHttpRequest'
}

douban_appjs_headers = {
	'authority':'img3.doubanio.com',
	'method':'GET',
	'scheme':'https',
	'accept':'*/*',
	'accept-encoding':'gzip, deflate, br',
	'accept-language':'zh-CN,zh;q=0.9',
	'cache-control':'no-cache',
	'pragma':'no-cache',
	'referer':'https://movie.douban.com/tag/',
	'user-agent':ua["user_agent"]
}

youku_home_headers = {
	'authority': 'www.youku.com',
	'method': 'GET',
	'path': '/',
	'scheme': 'https',
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'accept-encoding': 'gzip, deflate, br',
	'accept-language': 'zh-CN,zh;q=0.9',
	'upgrade-insecure-requests': '1',
	'user-agent': ua["user_agent"],
}



leshi_headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Cache-Control': 'max-age=0',
	'Connection': 'keep-alive',
	'Host': 'list.le.com',
	'Referer': 'http://tv.le.com/',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': ua["user_agent"],
}


leshi_ajax_headers = {
	'Accept': '*/*',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Connection': 'keep-alive',
	'Referer': 'http://list.le.com/listn/c2_t-1_a-1_y-1_s1_md_o20_d1_p.html',
	'User-Agent': ua["user_agent"],
	'X-Requested-With': 'XMLHttpRequest',
}

leso_headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Cache-Control': 'max-age=0',
	'Connection': 'keep-alive',
	'Referer': 'http://www.leso.cn/',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': ua["user_agent"],
}

baidu_headers = {
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
	"Accept-Encoding": "gzip, deflate, br",
	"Accept-Language": "zh-CN,zh;q=0.9",
	"Connection": "keep-alive",
	"Upgrade-Insecure-Requests": "1",
	"User-Agent": ua["user_agent"],
}

headers = {
	'Accept': '*/*',
	"Accept-Encoding": "gzip, deflate, br",
	"Accept-Language": "zh-CN,zh;q=0.9",
	"Connection": "keep-alive",
	# "Upgrade-Insecure-Requests": "1",
	"User-Agent": ua["user_agent"],
}
