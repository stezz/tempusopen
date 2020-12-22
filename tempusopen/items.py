# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, TakeFirst

clean_text = Compose(str.strip('\n'))
team_text = Compose(lambda s: s.strip('\n'), lambda s: s.split(',')[0], lambda s: s.split(':')[1], str.strip)
status = Compose(lambda s: s.split(',')[1:])
first = Compose(TakeFirst)
clean_time = Compose(TakeFirst, lambda s: s.strip("\n\xa0"))
clean_distance = Compose(lambda s: s.strip(), lambda s: s.split('\n')[1])


class Swimmer(Item):
    name = Field()
    id = Field()
    born = Field()
    team = Field()
    status = Field()
    license = Field()
    styles = Field()


class Style(Item):
    name = Field()
    # length = Field()
    times = Field()
    # swimmer = Field()


class Time(Item):
    date = Field()
    time = Field()
    competition = Field()
    # style = Field()
    # swimmer = Field()


class SwimmerLoader(ItemLoader):
    default_item_class = Swimmer
    team_out = team_text
    status_out = status
    born_out = clean_text
    license_out = clean_text


class TimeLoader(ItemLoader):
    default_item_class = Time
    time_out = clean_time
    date_out = first
    competition_out = first


class StyleLoader(ItemLoader):
    default_item_class = Style
    name_out = clean_distance
