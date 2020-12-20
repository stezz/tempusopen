import scrapy
from tempusopen.settings import swimmers
from tempusopen.items import Swimmer, Time, Style
from scrapy.loader import ItemLoader


class BaseUrl(scrapy.Item):
    url = scrapy.Field()


class RecordsSpider(scrapy.Spider):
    name = 'records_spider'
    allowed_domains = ['www.tempusopen.fi']

    def start_requests(self):
        base_url = ('https://www.tempusopen.fi/index.php?r=swimmer/index&Swimmer[first_name]={firstname}&'
                    'Swimmer[last_name]={lastname}&Swimmer[searchChoice]=1&Swimmer[swimmer_club]={team}&'
                    'Swimmer[class]=1&Swimmer[is_active]=1')
        urls = [base_url.format_map(x) for x in swimmers]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        swimmer_url = response.xpath('//table//tbody/tr/td/a[@class="view"]/@href').get()
        swimmer = Swimmer()
        yield response.follow(swimmer_url, callback=self.parse_records, meta={'swimmer': swimmer})

    def parse_records(self, response):
        distances = response.xpath('//table//tbody/tr/td/a[@class="view"]/@href').extract()
        swimmer_data = response.xpath("//div[@class='container main']//"
                                      "div[@class='sixteen columns']//text()").extract()
        swimmer = response.meta['swimmer']
        swimmer['id'] = response.url.split('=')[-1]
        swimmer['name'] = swimmer_data[1]
        swimmer['team'] = swimmer_data[5].strip('\n').split(',')[0].split(':')[1].strip()
        swimmer['status'] = swimmer_data[5].split(',')[1:]
        swimmer_data = response.xpath("//div[@class='container main']//"
                                      "div[@class='clearfix']//div[@class='six columns']"
                                      "//text()").extract()
        swimmer['born'] = swimmer_data[2].strip('\n')
        swimmer['license'] = swimmer_data[4].strip('\n')
        for url in distances:
            yield response.follow(url, callback=self.parse_distances, meta={'swimmer': swimmer})

    def parse_distances(self, response):
        swimmer = response.meta['swimmer']
        style = Style()
        try:
            swimmer['styles']
        except:
            swimmer['styles'] = []
        distance = response.xpath('//div[@class="container main"]//p/text()').extract_first()
        distance = distance.strip().split('\n')[1]
        style['name'] = distance
        try:
            style['times']
        except:
            style['times'] = []
        swimmer['styles'].append(style)
        table_rows = response.xpath("//table//tbody/tr")
        for tr in table_rows:
            t = Time()
            t['time'] = tr.xpath("./td[1]/text()").extract_first().strip("\n\xa0")
            t['date'] = tr.xpath("./td[4]/text()").extract_first()
            t['competition'] = tr.xpath("./td[5]/text()").extract_first()
            style['times'].append(t)
        return swimmer
