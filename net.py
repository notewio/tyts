import ueberzug.lib.v0 as ueberzug
from bs4 import BeautifulSoup
from datetime import datetime
from video import Video
import requests
import shutil
import config
import util


def getVideos(channel_id):
    """ Retrieves RSS feed for channel_id. """
    url = "https://www.youtube.com/feeds/videos.xml?channel_id=" + channel_id
    xml = requests.get(url).text
    soup = BeautifulSoup(xml, "lxml")

    author = soup.find("author").find("name").text

    videos = []
    entries = soup.find_all("entry")
    for entry in entries:

        title = entry.find("title").text
        desc = entry.find("media:description").text

        id = entry.find("link")["href"]
        id = id.split('=')[-1]

        date = entry.find("published").text
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S+00:00")

        videos.append(Video(id, channel_id, author, title, desc, date))

    return author, videos


@util.debounce(wait_time=0.2)
def getThumbnail(id, thumb):
    """ Downloads thumbnail for video id and displays it with ueberzug. """
    url = "https://i1.ytimg.com/vi/{}/hqdefault.jpg".format(id)
    response = requests.get(url, stream=True)
    with config.THUMB_FILE.open(mode="wb") as f:
        shutil.copyfileobj(response.raw, f)
    thumb.path = str(config.THUMB_FILE)
    thumb.visibility = ueberzug.Visibility.VISIBLE
    del response
