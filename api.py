import json
import logging
import re
import requests
from lxml import etree

from flask import Flask, request, jsonify
from waitress import serve

logging.getLogger().setLevel(logging.INFO)
# logging.basicConfig(
#     format='%(asctime)s %(message)s',
#     handlers=[
#         logging.FileHandler("oauth.log", encoding="UTF-8"),
#         logging.StreamHandler(),
#     ],
# )

app = Flask(__name__)

# 查询/取消订阅 API
@app.route('/info/<walker_id>', methods=['get'])
def send_info(walker_id):
    if len(walker_id.split('-')) != 5:
        resu = {'code': 400, 'message': 'ID 格式错误'}
        return jsonify(resu), 400
    url = f'https://bookwalker.jp/{walker_id}/'
    result = requests.get(url=url, timeout=10)
    html = etree.HTML(result.text, parser = etree.HTMLParser(encoding='utf-8'))
    try:
        _data = html.xpath('/html/head/script[@type="application/ld+json"][1]/text()')[0].replace('\u3000', ' ')
        _dataa = ''.join(html.xpath('/html/body/script[7]/text()')[0].split())
        _dataa = re.findall(r'window.bwDataLayer.push\((.*)\);', _dataa)[0]
        data = json.loads(_data)
        dataa = json.loads(_dataa)['ecommerce']['items'][0]
    except:
        resu = {'code': 404, 'message': f'ID {walker_id} 获取数据失败'}
        return jsonify(resu), 404
    resu = {
        "code": 200,
        "walker_id": dataa['item_id'],
        "data": {
            "name": data['name'],
            "author": dataa['item_author'].split('\t'),
            "image": data['image'],
            "description": data['description'],
            "brand": dataa['item_brand'],
            "category": dataa['item_category'],
            "publisher": dataa['item_publisher'],
            "series": dataa['item_series'],
            "date": dataa['item_date'],
            }
    }
    return jsonify(resu), 200


@app.before_request
def before():
    """中间件拦截器"""
    url = request.path  # 读取到当前接口的地址
    if re.findall(r'info', url):
        pass
    else:
        logging.error(f'[E] before: 拦截访问 {request.remote_addr} -> {url}')
        resu = {'code': 403, 'message': '你没有访问权限！'}
        return jsonify(resu), 200


if __name__ == '__main__':
    serve(app, host="127.0.0.1", port=8800)
