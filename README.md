git init
git add README.md
git commit -m "first commit"
git remote add origin https://github.com/wangtaihong/mov.git
git push -u origin master


cd /Utils/python-bloomfilter
python setup.py install

mongodb导出表：
mongoexport -d zydata -c douban_tvs -o /home/jon/root/py/zydata/dumpdata/douban_tvs.bat
#mongoexport -d dbname -c tbname -o outputfile

导入:
mongoimport -d zydata -c douban_tvs --upsert /home/jon/root/py/zydata/dumpdata/douban_tvs.bat
#mongoimport -d dbname -c tbname --upsert filename

<!-- windows启动: -->
net start MongoDB

redis-cli --raw dump mykey | head -c-1 > myfile
#导出mykey到文件myfile中

cat myfile | redis-cli -x restore mynewkey 0
myfile内容导入到mynewkey  数据库0

pip install setuptools cffi 'cython>=0.28' git+git://github.com/gevent/gevent.git#egg=gevent



\Program Files\Redis
redis-server.exe redis.windows.conf


sudo pip install virtualenv

# sudo pip3 install virtualenv

mkdir ~/myproject
cd ~/myproject

virtualenv venv

source venv/bin/activate

deactivate it:
deactivate


import requests, requests.utils, pickle
session = requests.session()
# Make some calls
with open('somefile', 'w') as f:
    pickle.dump(requests.utils.dict_from_cookiejar(session.cookies), f)

with open('somefile') as f:
    cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
    session = requests.session()
    session.cookies = cookies


db.getCollection('contents').find({"source":"IPTV","category":{"$in":["电影","电视剧","动漫","动画片","综艺","少儿","剧集",null]},"$or":["directors":{"$ne":null},"starring":{"$nin":[null,1]]}})


yum install -y p7zip
7za x iptvcms.zip -o/home/Ameeting/iptvcms2/
7za x sx_posters.zip -o/web/data/test/EPG_Picture
cp -frp iptvcms/* iptvcms2/iptvcms/
\cp -frp iptvcms/* iptvcms2/iptvcms/
