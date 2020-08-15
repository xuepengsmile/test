#!/usr/bin/env python3
# encoding: utf8
# author: veelion
# file: bee_server.py

from sanic import Sanic
from sanic import response  #生成发给client的响应数据

from urlpool import UrlPool


"""
sanic 异步web框架，可以利用这个web框架进一步开发爬虫前端的监控界面，控制界面等
async def cache_urlpool(app, loop)
    服务停止后，将urlpool删除，并将必要数据（url等）存到硬盘
async def task_get(request)
    客户端传入要提取的url的数量，默认为10个url
    构造有count个的url的json并返回
async def task_post(request) #post方法
    传入数据包括url，status，real_url（重定向后的url），newurls（传入的新的url的队列）
    urlpool根据这些参数对自身进行更新修改
"""


urlpool = UrlPool(__file__)

# 初始化urlpool，根据你的需要进行修改
hub_urls = []
urlpool.set_hubs(hub_urls, 300)
urlpool.add('https://news.sina.com.cn/')

# init
app = Sanic(__name__)   #对sanic生成对象


@app.listener('after_server_stop')  #sanic稍微高级点的，比较少用到的属性
async def cache_urlpool(app, loop):
    global urlpool
    print('caching urlpool after_server_stop')
    del urlpool
    print('bye!')


@app.route('/task') # 路径，默认是get方法
async def task_get(request):
    count = request.args.get('count', 10)
    try:
        count = int(count)
    except:
        count = 10
    urls = urlpool.pop(count)
    return response.json(urls)


@app.route('/task', methods=['POST', ])
async def task_post(request):
    result = request.json
    urlpool.set_status(result['url'], result['status'])
    if result['url_real'] != result['url']:
        urlpool.set_status(result['url_real'], result['status'])
    if result['newurls']:
        print('receive URLs:', len(result['newurls']))
        for url in result['newurls']:
            urlpool.add(url)
    return response.text('ok')


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False,
        access_log=False,
        workers=1)

