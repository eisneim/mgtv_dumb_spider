import scrapy
from scrapy import Field


class DramaItem(scrapy.Item):
  title = Field()
  id = Field()
  isvip = Field()
  type = Field()
  desc = Field()
  total = Field()
  count = Field()
  # lead actor and actress
  stars = Field()
  episodes = Field()

