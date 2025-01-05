import json

import colorpallet
import lastfm

with open("test.json", mode="r", encoding="utf-8") as read_file:
    urls = lastfm.extract_img_urls(json.load(read_file))
    print(urls)
    for url in urls:
        print(colorpallet.compute_pallet(url))
        print("\n")
