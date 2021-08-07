import scrapy
from tempusopen.settings import swimmers
from tempusopen.items import Swimmer, Time, Style


class BaseUrl(scrapy.Item):
    url = scrapy.Field()


class RecordsSpider(scrapy.Spider):
    name = 'records_spider'
    allowed_domains = ['www.tempusopen.fi']

    def start_requests(self):
        base_url = ('https://www.tempusopen.fi/index.php?r=swimmer/index&Swimmer[first_name]={firstname}&'
                    'Swimmer[last_name]={lastname}&Swimmer[searchChoice]=1&Swimmer[swimmer_club]={team}&'
                    'Swimmer[class]=99&Swimmer[is_active]=1')
        # swimmers is a dictionary that contains the {'name', 'surname', 'team'}
        # of the swimmers we want to crawl.
        # At the moment we need to give exact names since we search for the swimmer among
        # all the swimmers of the site and if we have multiple results
        # we only .get() the first one
        urls = [base_url.format_map(x) for x in swimmers]

        if urls:
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # For each swimmer we find in the search results we get his/her URL and...
        swimmer_url = response.xpath('//table//tbody/tr/td/a[@class="view"]/@href').get()
        swimmer_gender = response.xpath('//table//tbody/tr/td[6]/text()').get()
        swimmer = Swimmer()
        swimmer['gender'] = swimmer_gender
        if swimmer_url:
        # ... we fire a request to parse the records
            yield response.follow(swimmer_url, callback=self.parse_records, meta={'swimmer': swimmer})

    def parse_records(self, response):
        # now we are on a page that has the swimmer data, as you can see below
        # id, name, team, year of birth, status and license number.
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
        # This page also has all the different styles that the swimmer has ever swam
        # but it only has the personal best time of the swimmer and we really would
        # like to gather all the times for the different style
        # so we grab all the URLs of the various styles which will lead us to a page
        # that has all the times for that style
        distances = response.xpath('//table//tbody/tr/td/a[@class="view"]/@href').extract()
        # BUT because of the way how scrapy works rather than using a normal 'for' loop we need
        # to go through each URL one by one and exhaust the urls in distances before
        # returning a swimmer item back (if we don't do that we will return the same swimmer item
        # multiple times rather than once per swimmer).
        #
        # This is achieved by popping the first url and passing the distances_urls through
        # the next level and checking that we are really done with this swimmer before
        # firing a 'return' (in the next level of parsing)
        url = distances.pop()
        yield response.follow(url, callback=self.parse_distances, meta={'swimmer': swimmer,
                                                                        'distances': distances})

    def parse_distances(self, response):
        # Finally we have gotten to the page that has all the time for the given distance
        swimmer = response.meta['swimmer']
        # We create the Style item that will collect all the times...
        style = Style()
        try:
            swimmer['styles']
        except KeyError:
            swimmer['styles'] = []
        distance = response.xpath('//div[@class="container main"]//p/text()').extract_first()
        distance = distance.strip().split('\n')[1]
        style['name'] = distance
        try:
            style['times']
        except KeyError:
            style['times'] = []
        # ... and append it to the styles that the swimmer has swam
        swimmer['styles'].append(style)
        # Then we go to the table that has all the times for this style and
        # collect time, date and competition
        table_rows = response.xpath("//table//tbody/tr")
        for tr in table_rows:
            t = Time()
            t['time'] = tr.xpath("./td[1]/text()").extract_first().strip("\n\xa0")
            t['date'] = tr.xpath("./td[4]/text()").extract_first()
            t['competition'] = tr.xpath("./td[5]/text()").extract_first()
            t['FINA'] = tr.xpath("./td[2]/text()").extract_first()
            # and append this time to the list of times for the style
            style['times'].append(t)
            try:
                style['best']
            except KeyError:
                style['best'] = t
            # TODO
            #  save the best time of all in style['best']
            #  Hint: the best time is the first in the list of times
            #  if no style['best'] then style['best'] = first time you find
        distances = response.meta['distances']
        # This is where the magic happens...
        if distances:
            # we go to the next style by popping the url out of the distances_url list...
            url = distances.pop()
            # ... and recursively calling this parse_distances method until we exhaust
            # the distances urls list (yeah we are calling ourselves :/ )
            yield response.follow(url, callback=self.parse_distances, meta={'swimmer': swimmer,
                                                                            'distances': distances})
        else:
            # and finally if we really are done with the styles for this swimmer
            # we return a swimmer item. Exactly once per every swimmer.
            yield swimmer
