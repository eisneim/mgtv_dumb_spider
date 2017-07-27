import scrapy
from scrapy import Field


class EpisodeItem(scrapy.Item):
  img = Field()
  next_id = Field()
  t1 = Field() # episode number
  t2 = Field() # episode title
  ts = Field() # release date?
  video_id = Field()
  url = Field()


