from you_get.common import any_download
from mgtv_spider.settings import VIDEO_SAVE_FOLDER, MONGO_DATABASE, MONGO_URI
import pymongo
import os
import sys
import traceback
from os.path import exists


# thos videos are not downloadable for some reason
# have to escape them manually
corruptedVideos = ["417897", "417899", "417902", "417903", "417905", "417906", "417920", "417916", "417912", "417910", "417921",
  # 放弃我抓紧我 - 8
  "3740132", "3741915", "3752656",
  "1874358", "1869189", "1873084", "1874359",
  "1864733"]


def downloadMgtvVideo(url, outputDir, streamId="ld"):
  args = {
    'stream_id': streamId,
    'output_dir': outputDir,
    'merge': True,
    'info_only': False,
    'json_output': False,
    'caption': True
  }
  any_download(url, **args)


db = None
COL_DRAMA = "dramas"
COL_COMMENT = "comments"


def downloadOneVideo(drama, ep):
  epNumber = ep["t1"]
  folder = VIDEO_SAVE_FOLDER + "/" + drama["title"] + "/" + epNumber
  if not exists(folder):
    os.makedirs(folder)
  # took a lot time
  url = "http://www.mgtv.com" + ep["url"]
  tryCount = 0
  isCanceld = False
  while True:
    try:
      downloadMgtvVideo(url, folder)
      break
    except Exception as e:
      # print("Unexpected error:", sys.exc_info()[0])
      print("[Error]", traceback.format_exc())

      tryCount += 1
      if tryCount >= 2:
        print(" >>>> [Error] Maxium download try reached, exit now")
        isCanceld = True
        break
      print("[Warning] download: {} failed, retry".format(url))

  if isCanceld:
    return
  # onece it's done, update this record
  ep["videofile"] = folder
  return db[COL_DRAMA].update_one({"_id": drama["_id"]}, {
      "$set": { "episodes": drama["episodes"] }
    })


def downloadForOneDrama(drama):
  dramaname = drama["title"]
  print(" >>>> donwload episodes for drama: {}".format(dramaname))
  if drama["isvip"] != "0":
    print(" >>> {} is vip only, skiping".format(dramaname))
    return

  for ep in drama.get("episodes"):
    epNumber = ep["t1"]
    if str(ep["video_id"]) in corruptedVideos:
      print(" >>> force to escape {} - {}".format(dramaname, epNumber))
      continue

    if "videofile" in ep:
      # this file has already downloaded.
      print("{}-ep.{} has already downloaded.".format(dramaname, epNumber))
      continue
    result = downloadOneVideo(drama, ep)
    # print("update result>>", result.matched_count)


def main():
  global db
  # conect to mongodb
  uri = MONGO_URI
  print("connecting to mongodb: {}".format(uri))
  client = pymongo.MongoClient(uri.get("MONGO_HOST"), uri.get("MONGO_PORT"))
  db = client[MONGO_DATABASE["DB_NAME"]]

  for drama in db[COL_DRAMA].find():
    downloadForOneDrama(drama)


if __name__ == "__main__":
  main()
# url = "http://www.mgtv.com/b/314239/3892612.html"
# outputDir = "/Users/eisneim/www/pyProject/mgtv_spider"
# downloadMgtvVideo(url, outputDir)