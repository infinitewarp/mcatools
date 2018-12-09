import numpy as np
import tqdm
from PIL import Image

from mcatools.biome import colors_rgb, colors_hex_reverse


def save_biome_image_rgb(biome_data: np.ndarray, filename: str):
    color_data = np.zeros((biome_data.size, 3), dtype=np.uint8)
    for index, biome_id in tqdm.tqdm(
        enumerate(biome_data.flatten()), desc="coloring biome", total=biome_data.size
    ):
        color_data[index] = colors_rgb[biome_id]
    colors = color_data.reshape(biome_data.shape[0], biome_data.shape[1], 3)

    im = Image.fromarray(colors, "RGB")
    im.save(filename)


def load_biome_image_rgb(filename: str):
    image = Image.open(filename)
    pixels = image.load()
    biome_data = np.zeros((image.width, image.height), dtype=np.uint8)
    for z in range(image.height):
        for x in range(image.width):
            hex_color = "%02x%02x%02x" % pixels[(x, z)]
            try:
                biome_id = colors_hex_reverse[hex_color]
            except KeyError:
                biome_id = 0
            # Yes, "flipping" the x/z axes is correct here.
            biome_data[z][x] = biome_id
    return biome_data


def save_biome_image_mono(biome_data: np.ndarray, filename: str):
    brighter = biome_data / biome_data.max() * 256
    im = Image.fromarray(np.uint8(brighter))
    im.save(filename)
