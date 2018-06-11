git init
git add README.md
git commit -m "first commit"
git remote add origin https://github.com/wangtaihong/zydata.git
git push -u origin master


git remote add origin https://github.com/wangtaihong/zydata.git
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