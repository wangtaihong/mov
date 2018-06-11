# coding:utf-8

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from collections import namedtuple
import sys
import json
import demjson
sys.path.append('../')
import config
sys.path.append('./')
from pymongo import MongoClient

import matplotlib.pyplot as plt
plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt


mongo = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata
mongo_youku_videos = mongo.youku_videos
mongo_youku_star = mongo.youku_star
mongo_letv_tvs = mongo.letv_tvs
mongo_letv_stars = mongo.letv_stars
mongo_douban_tvs = mongo.douban_tvs
mongo_douban_stars = mongo.douban_stars
mongo_stars = mongo.stars
mongo_contents = mongo.contents
mongo_posters = mongo.posters
mongo_categories = mongo.categories


categories = mongo_categories.find(no_cursor_timeout=True)
xticklabels = []
means = []
#for cat in categories:
#	count = mongo_contents.find({"category":cat['category']}).count()
#	xticklabels.append(cat['category'])
#	means.append(count)

#xticklabels.append(u"未知")
#means.append(mongo_contents.find({'category':{"$exists":False}}).count())
data = {}
#for x in mongo_posters.find(no_cursor_timeout=True):
	#index = str(int(str(x['width'])[0])*10**(len(str(x['width']))-1))+"x"+ str(int(str(x['height'])[0])*10**(len(str(x['height']))-1))
	#if data.get(index):
		#data[index] = int(data[index])+1
	#else:
		#data[index] = 1
	#print(data[index])

#with open("./posters-size.txt", "w") as myfile:
    #myfile.write(json.dumps(data))

with open("./posters-size.txt") as myfile:
    for line in myfile:
    	data = json.loads(line)
xticklabels = []
means = []
for x in data:
    if data[x] < 3000:
        continue
    xticklabels.append(x)
    means.append(data[x])


plt.rcdefaults()
fig, ax = plt.subplots()

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

y_pos = np.arange(len(xticklabels)) + 0.8
error = np.random.rand(len(xticklabels))
print(y_pos)
ax.barh(y_pos, means, xerr=error, align='center',
        color='green', ecolor='black')
ax.set_yticks(y_pos)
ax.set_yticklabels(xticklabels)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel("")
ax.set_title('Posters')

plt.show()