import scrapy
from tempusopen.settings import swimmers


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
        yield response.follow(swimmer_url, callback=self.parse_records)

    def parse_records(self, response):
        distances = response.xpath('//table//tbody/tr/td/a[@class="view"]/@href').extract()
        for url in distances:
            yield response.follow(url, callback=self.parse_distances)

    def parse_distances(self, response):
        name = response.xpath('//div[@class="container main"]//h2/text()').extract_first()
        distance = response.xpath('//div[@class="container main"]//p/text()').extract_first()
        distance = distance.strip().split('\n')[1]
        print(name, distance)
        table_rows = response.xpath("//table//tbody/tr")
        for tr in table_rows:
            time = tr.xpath("./td[1]/text()").extract_first().strip("\n\xa0")
            date = tr.xpath("./td[4]/text()").extract_first()
            competition = tr.xpath("./td[5]/text()").extract_first()
            print(time, date, competition)
