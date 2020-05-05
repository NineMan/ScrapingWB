import scrapy
from datetime import datetime


class WildSpider(scrapy.Spider):
    name = 'wild'

    start_urls = ['https://www.wildberries.ru']
    start_url_page = 'https://www.wildberries.ru/catalog/obuv/zhenskaya/dutiki-i-snoubutsy/snoubutsy'

    # to test. 9-10 goods
    # start_url_page = 'https://www.wildberries.ru/catalog/obuv/zhenskaya/baletki-i-cheshki/polupaltsy'

    # to test video and 360
    # start_url_page = 'https://www.wildberries.ru/catalog/obuv/zhenskaya/botforty'

    # URL to POST geo (Moscow)
    url_geo = 'https://www.wildberries.ru/geo/saveprefereduserlocation/77'      # Moscow
    # url_geo = 'https://www.wildberries.ru/geo/saveprefereduserlocation/34'      # Volgograd

    def parse(self, response):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'}
        yield scrapy.Request(url=self.url_geo,
                             callback=self.parse_geo,
                             method='POST',
                             headers=headers,)

    def parse_geo(self, response):
        yield scrapy.Request(url=self.start_url_page,
                             callback=self.parse_page)

    def parse_page(self, response):

        goods = response.css('div.j-card-item')
        for good in goods:

            good_url = good.css('a::attr(href)').get().split('?')[0]
            yield response.follow(url=good_url,
                                  callback=self.parse_good,
                                  cb_kwargs=dict(url=good_url))

        for a in response.css('a.next'):
            yield response.follow(a, callback=self.parse_page)

    def parse_good(self, response, url):

        item = dict()

        # Timestamp for machine or manual handling
        timestamp = datetime.today().timestamp()
        now = datetime.fromtimestamp(timestamp)
        # item['timestamp'] = [timestamp, now]
        item['timestamp'] = now

        # RPC and url
        item['RPC'] = response.css('span.j-article::text').get()
        item['url'] = url

        # Title
        brand = response.css('span.brand::text').get()
        name = response.css('span.name::text').get()
        color = response.css('span.color::text').get()
        title = brand + '/' + name + ', ' + color
        item['title'] = title

        # Marketing_tags
        # I didn't understand what was meant for this site
        item['marketing_tags'] = []

        # Brand
        item['brand'] = brand

        # Section
        item['section'] = response.css('a.breadcrumbs_url::attr(href)').getall()[1:]

        # Price_data
        price_data = dict()
        current = response.css('span.final-cost::text').get()
        current = float(current.strip().strip(' ₽').replace(' ', ''))
        price_data['current'] = current
        original = response.css('del.c-text-base::text').get()
        if original:
            original = float(original.strip().strip(' ₽').replace(' ', ''))
        else:
            original = current
        price_data['original'] = original
        sale_tag = 'Скидка {} %'.format(int((current / original) * 100))
        price_data['sale_tag'] = sale_tag
        item['price_data'] = price_data

        # Stock
        stock = dict()
        stock['in_stock'] = True    # always True if parse in page
        stock['count'] = 0          # no way to get info
        item['stock'] = stock

        # Assets
        assets = dict()
        assets['main_image'] = response.css('a.j-photo-link::attr(href)').get()
        assets['set_images'] = response.css('a.j-carousel-image::attr(href)').getall()
        assets['view360'] = response.css('j-3d-container::attr(data-path)').getall()
        assets['video'] = response.xpath("//meta[@property='og:video']/@content").getall()
        item['assets'] = assets

        # Metadata
        metadata = dict()
        a = response.xpath("//div[@class='pp']")
        for i in a:
            metadata[i.css('b::text').get()] = i.css('span::text').get()
        item['metadata'] = metadata

        # Variants
        item['variants'] = 1
        variants = len(response.css('li.j-color').getall())
        if variants:
            item['variants'] = variants

        yield item
