import json
import re

import requests
from lxml import etree

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}

gbook_key = "" # https://console.cloud.google.com/marketplace/product/google/books.googleapis.com

class GetBookInfo:
    def __init__(self):
        self.name = None # 书名
        self.authors = None # 作者
        self.image = None # 封面
        self.description = None # 简介
        self.brand = None # 出版社
        self.category = None # 分类
        self.publisher = None # 出版商
        self.series = None # 系列
        self.date = None # 出版日期
        self.isbn = None # ISBN-10
        self.asin = None # ASIN
    
    def get_walker(self, walker_id):
        url = f'https://bookwalker.jp/{walker_id}/'
        result = requests.get(url=url, timeout=10, headers=headers)
        html = etree.HTML(result.text, parser = etree.HTMLParser(encoding='utf-8'))
        try:
            _data = html.xpath('/html/head/script[@type="application/ld+json"][1]/text()')[0].replace('\u3000', ' ')
            _dataa = ''.join(html.xpath('/html/body/script[7]/text()')[0].split())
            _dataa = re.findall(r'window.bwDataLayer.push\((.*)\);', _dataa)[0]
            data = json.loads(_data)
            dataa = json.loads(_dataa)['ecommerce']['items'][0]
        except:
            return None
        self.name = data['name']
        self.authors = dataa['item_author'].split('\t')
        self.image = data['image']
        self.description = data['description']
        self.brand = dataa['item_brand']
        self.category = dataa['item_category']
        self.publisher = dataa['item_publisher']
        self.series = dataa['item_series']
        self.date = dataa['item_date']
        return self
        
    def get_amazon(self, asin):
        url = f'https://www.amazon.co.jp/dp/{asin}/'
        result = requests.get(url=url, timeout=10, headers=headers)
        html = etree.HTML(result.text, parser = etree.HTMLParser(encoding='utf-8'))
        try:
            self.asin = html.xpath('//*[@id="ASIN"]/@value')[0]
            if self.asin.isdecimal():
                self.isbn = self.asin
            self.name = html.xpath('//*[@id="productTitle"]/text()')[0].strip()
            self.authors = html.xpath('//*[@class="a-size-base a-link-normal a-text-normal"]/text()')
            _image = html.xpath('//*[@id="ebooks-img-canvas"]/img/@src')
            if _image:
                self.image = _image[0]
            else:
                self.image = json.loads(html.xpath('//*[@id="dp-container"]/script[2]/text()')[0]).get('landingImageUrl')
            self.description = ''.join(html.xpath('//div[@id="bookDescription_feature_div"]/div/div[1]/span/text()'))
        except:
            return None
        return self
    
    def get_google(self, gid = None, intitle = None, isbn = None):
        params = {"key": gbook_key}
        if gid is not None:
            url = f'https://www.googleapis.com/books/v1/volumes/{gid}'
            result = requests.get(url=url, timeout=10, params=params)
            if result.status_code != 200:
                return None
            data = result.json()['volumeInfo']
        else:
            isbn = isbn or self.isbn
            if isbn is not None:
                params["q"] = f"isbn:{isbn}"
            else:
                params["q"] = f"intitle:{intitle}"
            url = 'https://www.googleapis.com/books/v1/volumes'
            result = requests.get(url=url, timeout=10, params=params).json()
            if result['totalItems'] == 0:
                return None
            data = result['items'][0]['volumeInfo']
        self.name = data['title']
        self.authors = data['authors']
        self.image = data['imageLinks']['thumbnail']
        self.description = data['description']
        self.brand = data['publisher']
        self.publisher = data['publisher']
        return self