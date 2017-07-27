import scrapy
from scrapy import Request
from scrapy.conf import settings
import json
from urllib.parse import urlsplit, parse_qs
import math

from mgtv_spider.models.comment import CommentItem
from mgtv_spider.models.drama import DramaItem
from mgtv_spider.models.episode import EpisodeItem
from mgtv_spider.models.star import StarItem

# those pramameter should not be changed, the api is fixed to those number
# strange isn't it?
VIDEO_PER_PAGE = 40
# COMMENTS_PER_PAGE = 15


class MgtvSpider(scrapy.Spider):
  name = "mgtv"

  startPage = "http://www.mgtv.com/b/293193/3960734.html"
  startVidId = settings.get("START_VID_ID") or "3960734"
  URL_VID = "http://pcweb.api.mgtv.com/episode/list?video_id={videoId}&page={page}&size={size}"
  URL_COMMENT = "http://comment.mgtv.com/video_comment/list/?drama_id={dramaId}&subject_id={videoId}&page={page}&type=hunantv2014"
  URL_STAR = "http://pcweb.api.mgtv.com/star/list?video_id={videoId}&drama={dramaId}"
  # 电视剧热播榜
  URL_RANK = "http://rc.mgtv.com/pc/ranklist?rt=c&c=2&guid=890357281248776192&limit=200"
  # similar tv show
  URL_LIKE = "http://rc.mgtv.com/pc/like?vid={videoId}"

  def start_requests(self):
    yield Request(self.URL_VID.format(videoId=self.startVidId,
      page=1, size=VIDEO_PER_PAGE), self.parseVideoList)
    # get popular dramas
    yield Request(self.URL_RANK, self.parseRanks)


  def parseVideoList(self, response):
    result = json.loads(response.text)["data"]
    currentPage = result["current_page"]
    totalPage = result["total_page"]

    theDrama = DramaItem()
    # extract drama id from episoid url
    firstEpUrl = result["list"][0]["url"]
    theDrama["id"] = firstEpUrl.split("/")[2]

    infoFields = ["desc", "isvip", "title", "type"]
    for field in infoFields:
      if field in result["info"].keys():
        theDrama[field] = result["info"].get(field)
    theDrama["total"] = result["total"]
    theDrama["count"] = result["count"]
    theDrama["stars"] = []
    theDrama["episodes"] = result["list"]

    firstVideoId = theDrama["episodes"][0]["video_id"]

    for idx in range(totalPage - currentPage):
      pangeNum = currentPage + idx + 1
      yield Request(self.URL_VID.format(videoId=firstVideoId,
        page=pangeNum, size=VIDEO_PER_PAGE), self.parseVideoListOnePage)

    yield theDrama


    # get related series
    yield Request(self.URL_LIKE.format(videoId=firstVideoId), self.parseSimilarDrama)
    # get actor and actress info
    yield Request(self.URL_STAR.format(videoId=firstVideoId, dramaId=theDrama["id"]),
      self.parseStars)
    # get comments for each video
    for vid in theDrama["episodes"]:
      yield self.parseCommentsForOneVideo(theDrama["id"], vid["video_id"])

  # only parse rest of the video pages
  # @TODO: parseVideoListOnePage is ugly, should refactor
  def parseVideoListOnePage(self, response):
    result = json.loads(response.text)["data"]
    eps = result["list"]
    dramaId = eps[0]["url"].split("/")[2]
    episodes = {
      "drama": dramaId,
      "episodes": eps
    }
    yield episodes
    # get comments for each video
    for vid in eps:
      yield self.parseCommentsForOneVideo(dramaId, vid["video_id"])

  def parseCommentsForOneVideo(self, dramaId, videoId):
    return Request(self.URL_COMMENT.format(
      dramaId=dramaId, videoId=videoId, page=1), self.parseCommentsFirstPage)

  def parseCommentsFirstPage(self, response):
    result = json.loads(response.text)
    comments = result["comments"]
    perpage = result["perpage"]
    count = result["total_number"]
    urlobj = parse_qs(urlsplit(response.url).query)
    dramaId = urlobj["drama_id"][0]
    videoId = urlobj["subject_id"][0]
    print(">>>>> comments for drama:{} and video: {}".format(dramaId, videoId))
    yield {
      "drama": dramaId,
      "videoId": videoId,
      "comments": comments
    }

    totalPages = math.ceil(count / perpage)
    for p in range(totalPages):
      pageNum = p + 1
      if pageNum == 1:
        continue
      yield Request(self.URL_COMMENT.format(
        dramaId=dramaId, videoId=videoId, page=pageNum), self.parseComments)

  def parseComments(self, response):
    comments = json.loads(response.text)["comments"]
    urlobj = parse_qs(urlsplit(response.url).query)
    # it returnes a list!!!!
    dramaId = urlobj["drama_id"][0]
    videoId = urlobj["subject_id"][0]
    yield {
      "drama": dramaId,
      "videoId": videoId,
      "comments": comments
    }

  def parseSimilarDrama(self, response):
    dramas = json.loads(response.text)["data"]
    for drama in dramas:
      yield Request(self.URL_VID.format(videoId=drama["videoId"],
      page=1, size=VIDEO_PER_PAGE), self.parseVideoList)

  def parseStars(self, response):
    stars = json.loads(response.text)["data"]
    dramaId = response.url.split("?")[1].split("=")[2]
    if type(stars) is list and len(stars) > 0:
      yield {
        "drama": dramaId,
        "stars": stars
      }

  def parseRanks(self, response):
    dramas = json.loads(response.text)["data"]
    for drama in dramas:
      yield Request(self.URL_VID.format(videoId=drama["videoId"],
      page=1, size=VIDEO_PER_PAGE), self.parseVideoList)

