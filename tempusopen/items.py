# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Swimmer(scrapy.Item):
    name = scrapy.Field()
    id = scrapy.Field()
    born = scrapy.Field()
    team = scrapy.Field()
    status = scrapy.Field()
    license = scrapy.Field()
    styles = scrapy.Field()
    gender = scrapy.Field()

class Style(scrapy.Item):
    name = scrapy.Field()
    #length = scrapy.Field()
    times = scrapy.Field()
    #swimmer = scrapy.Field()

class Time(scrapy.Item):
    date = scrapy.Field()
    time = scrapy.Field()
    competition = scrapy.Field()
    #style = scrapy.Field()
    #swimmer = scrapy.Field()
