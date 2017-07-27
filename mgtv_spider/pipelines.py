# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.conf import settings

COL_DRAMA = "dramas"
COL_COMMENT = "comments"

class MgtvSpiderPipeline(object):

  def __init__(self, uri, port, dbname):
    self.mongo_uri = uri
    self.mongo_port = port
    self.db_name = dbname

  @classmethod
  def from_crawler(cls, crawler):
    uri = settings.get("MONGO_URI")
    print("connecting to mongodb: {}".format(uri))
    return cls(
      uri.get("MONGO_HOST"),
      uri.get("MONGO_PORT"),
      crawler.settings.get("MONGO_DATABASE").get("DB_NAME"))

  def open_spider(self, spider):
    self.client = pymongo.MongoClient(self.mongo_uri, self.mongo_port)
    print(">>>> conect to db : {}:{}/{}".format(
      self.mongo_uri, self.mongo_port, self.db_name))
    self.db = self.client[self.db_name]

  def saveDrama(self, item):
    self.db[COL_DRAMA].update(
      { "id": item["id"] },
      { "$set": dict(item) }, True)

  def appendEpisodes(self, item):
    eps = item["episodes"]
    self.db[COL_DRAMA].update(
      { "id": item["drama"] },
      { "$push": {
        "episodes": { "$each": eps }
      } })

  def saveStars(self, item):
    dramaId = item["drama"]
    stars = item["stars"]
    self.db[COL_DRAMA].update(
      { "id": dramaId },
      { "$push": {
        "stars": { "$each": stars }
      } })

  def saveComments(self, item):
    dramaId = item["drama"]
    videoId = item["videoId"]
    for comment in item["comments"]:
      comment["dramaId"] = dramaId
      # comment["videoId"] = videoId
      self.db[COL_COMMENT].insert(comment)


  def process_item(self, item, spider):
    # this is a drama
    if item.get("title") and item.get("total"):
      print(" --------- this is drama")
      self.saveDrama(item)
    elif item.get("drama") and item.get("episodes"): # ep list
      print(" --------- ep list")
      self.appendEpisodes(item)
    elif item.get("drama") and item.get("stars"): # star list
      print(" --------- stars list")
      self.saveStars(item)
    elif item.get("drama") and item.get("comments"): # comments list
      print(" --------- comments list")
      self.saveComments(item)

    return item
