import scrapy
from scrapy import Field


class CommentItem(scrapy.Item):
  comment_id = Field()
  videoId = Field()
  up_num = Field()
  user = Field()
  device = Field()
  content = Field()
