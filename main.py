import json
import os
from dotenv import load_dotenv

import colorpallet
import lastfm

load_dotenv()
endpoint_url = lastfm.make_url_params("scringly", os.getenv('LASTFM_API_KEY'))

#with open("test.json", mode="r", encoding="utf-8") as read_file:
#    data = json.load(read_file)

def top_colors():
    data = lastfm.get_top_albums("7day", 3, endpoint_url)[0]
    urls = lastfm.extract_img_urls(data)
    print(urls)
    for url in urls:
        print(colorpallet.compute_pallet(url))
        print("\n")

def week_colors():
    data = lastfm.get_weekly_chart(endpoint_url)[0]
    urls = lastfm.get_weekly_imgs(data, endpoint_url)
    print(urls)
