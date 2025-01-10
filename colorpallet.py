# get_dominant_colors by https://stackoverflow.com/a/61730849

from PIL import Image, ImageEnhance
import requests


def _get_dominant_colors(pil_img, palette_size=16, num_colors=10):
    # Resize image to speed up processing
    img = pil_img.copy()
    img.thumbnail((100, 100))

    # Reduce colors (uses k-means internally)
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=palette_size)

    # Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)

    dominant_colors = []
    for i in range(num_colors):
      palette_index = color_counts[i][1]
      dominant_colors.append(palette[palette_index*3:palette_index*3+3])

    return dominant_colors


def compute_pallet(img_url, num_colors=6):
    res = requests.get(img_url ,stream=True).raw
    im = Image.open(res)

    # consider reducing pallet with .quantize
    # but explicitly set a pallet that looks
    # good on the LEDs
    boost_saturation = ImageEnhance.Color(im)

    img = boost_saturation.enhance(1.6)
    return _get_dominant_colors(img, num_colors=num_colors)


#print(compute_pallet(
#    "https://lastfm.freetls.fastly.net/i/u/770x0/903616162a8a4f1ca1ac63497e551c07.jpg#903616162a8a4f1ca1ac63497e551c07"
#    , 1))
#print(compute_pallet(
#    "https://lastfm.freetls.fastly.net/i/u/770x0/903616162a8a4f1ca1ac63497e551c07.jpg#903616162a8a4f1ca1ac63497e551c07"
#    , 10))
