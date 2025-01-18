"""
lastfm API handling
"""
import requests
from requests.adapters import HTTPAdapter, Retry
import json

_endpoint = "https://ws.audioscrobbler.com/2.0/?"

def make_url_params(user, key):
    def aux(params):
        return f"{params}&user={user}&api_key={key}&format=json"
    return aux

def create_api_session():
    """
    returns a requests session so that we get
    retries and such
    """
    sesh = requests.Session()
    retries = Retry(total=5, backoff_factor=1
                    , status_forcelist=[104,500,502,503,504])
    sesh.mount("https://", HTTPAdapter(max_retries=retries))
    return sesh



def get_top_albums(period, limit, url, sesh):
    params = url(f"method=user.gettopalbums&period={period}&limit={limit}")
    res = sesh.get(_endpoint+params)
    data = None

    if (res.status_code == 200):
        data = json.loads(res.text)
    
    return (data, res.status_code)


# doesnt have img urls have to use https://www.last.fm/api/show/album.getInfo
# to get the images one by one
def get_weekly_chart(url, sesh):
    params = url(f"method=user.getweeklyalbumchart")
    res = sesh.get(_endpoint+params)
    data = None

    if (res.status_code == 200):
        data = json.loads(res.text)
    
    return (data, res.status_code)

def get_weekly_imgs(chart, url, sesh):
    """
    Fetches the image url for each album in the weekly
    chart
    """
    urls = []
    for album in chart["weeklyalbumchart"]["album"]:
        params = url(f'method=album.getinfo&mbid={album["mbid"]}')
        res = sesh.get(_endpoint+params)
        # ignoring failed reqs
        if (res.status_code == 200):
            data = json.loads(res.text)
            urls.append(data["album"]["image"][0]["#text"])

    return urls

def extract_img_urls(data, size=0):
    """
    extracts the image urls from data returned from get_top_albums
    size: select the target image size to extract
        0: small, 1: medium
    """
    urls = []
    for album in data["topalbums"]["album"]:
        if album["image"][size]["#text"]:
            urls.append(album["image"][size]["#text"])

    return urls



#print(get_top_albums("7day",3,url))
#print(get_weekly_chart(url))
