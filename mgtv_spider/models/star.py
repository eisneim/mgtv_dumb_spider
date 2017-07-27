import scrapy
from scrapy import Field


class StarItem(scrapy.Item):
  img = Field()
  name = Field()
  uid = Field()
  hot = Field()