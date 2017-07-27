import scrapy
from scrapy import Request
import json

VIDEO_PER_PAGE = 40



class MgtvSpider(scrapy.Spider):
  name = "mgtv"

  startPage = "http://www.mgtv.com/b/293193/3960734.html"
  startVidId = "3960734"
  URL_VID = "http://pcweb.api.mgtv.com/episode/list?video_id={videoId}&page={page}&size={size}"
  URL_COMMENT = "http://comment.mgtv.com/video_comment/list/?type=hunantv2014&subject_id={videoId}&page={}"
  URL_STAR = "http://pcweb.api.mgtv.com/star/list?video_id={videoId}"
  # 电视剧热播榜
  URL_RANK = "http://rc.mgtv.com/pc/ranklist?rt=c&c=2&guid=890357281248776192&limit=200"
  # similar tv show
  URL_LIKE = "http://rc.mgtv.com/pc/like?guid=890357281248776192&uid=1&vid={videoId}&c=2"

  def start_requests(self):
    yield Request(self.URL_VID.format(videoId=self.startVidId,
      page=1, size=VIDEO_PER_PAGE), self.parseVideoList)
    # get related series
    yield Request()

  def parseVideoList(self, response):
    result = json.load(response.text)["data"]

