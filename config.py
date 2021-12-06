from xdg import xdg_config_home, xdg_cache_home
from datetime import datetime
from video import Video
import json


CONFIG_PATH = xdg_config_home() / "tyts"
CONFIG_FILE = CONFIG_PATH / "tyts.json"
CACHE_PATH = xdg_cache_home() / "tyts"
CACHE_FILE = CACHE_PATH / "videos.json"
THUMB_FILE = CACHE_PATH / "hqdefault.jpg"

DEFAULT_CONFIG = {
    "channels": []
}


def createConfig():
    CONFIG_PATH.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open(mode="w") as f:
        json.dump(DEFAULT_CONFIG, f)

def loadConfig():
    c = json.loads(CONFIG_FILE.read_text())
    return c


def createCache():
    CACHE_PATH.mkdir(parents=True, exist_ok=True)
    with CACHE_FILE.open(mode="w") as f:
        json.dump([], f)

def loadCache():
    if not CACHE_FILE.exists():
        createCache()
    try:
        c = json.loads(CACHE_FILE.read_text())
        c = [Video(*x[:-1], datetime.fromtimestamp(x[-1])) for x in c]
    except ValueError:
        c = []
    return c

def writeCache(c):
    with CACHE_FILE.open(mode="w") as f:
        json.dump(c, f, default=lambda x: x.toJSON())
