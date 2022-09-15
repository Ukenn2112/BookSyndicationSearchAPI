import logging
import re

from flask import Flask, request, jsonify
from waitress import serve
from get_info import GetBookInfo

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
@app.route('/info/<in_data>', methods=['get'])
def send_info(in_data):
    if len(in_data.split('-')) == 5:
        data = GetBookInfo().get_walker(in_data)
    elif len(in_data) == 10:
        data = GetBookInfo().get_amazon(in_data)
    elif len(in_data) == 12:
        data = GetBookInfo().get_google(in_data)
    else:
        data = None
    if data is None:
        resu = {'code': 404, 'message': f'{in_data} 获取数据失败'}
        return jsonify(resu), 404
    resu = {'code': 200, 'data': data.__dict__}
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
