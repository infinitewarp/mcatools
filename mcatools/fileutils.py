import functools
import io
import itertools
import logging
import zlib

import nbtlib
import numpy as np
import tqdm
from PIL import Image

from mcatools.definitions import REGION_WIDTH_CHUNKS, REGION_TOTAL_CHUNKS
from mcatools.biome import colors_rgb
from mcatools.region import Region, Chunk


def save_biome_image_rgb(biome_data: np.ndarray, filename: str):
    color_data = np.zeros((biome_data.size, 3), dtype=np.uint8)
    for index, block in tqdm.tqdm(
        enumerate(biome_data.flatten()), desc="coloring biome", total=biome_data.size
    ):
        try:
            color_data[index] = colors_rgb[block]
        except KeyError:
            logging.error(f"Unknown biome id {block}")
            color_data[index] = colors_rgb[999]  # magic value for unknown biomes
    colors = color_data.reshape(biome_data.shape[0], biome_data.shape[1], 3)

    im = Image.fromarray(colors, "RGB")
    im.save(filename)


def save_biome_image_mono(biome_data: np.ndarray, filename: str):
    brighter = biome_data / biome_data.max() * 256
    im = Image.fromarray(np.uint8(brighter))
    im.save(filename)


def readfile(filename):
    with open(filename, "rb") as f:
        data = f.read()
    return data


def extract_nbt_data(chunk_data: bytes) -> nbtlib.tag.Compound:
    """
    Extract, decompress, and parse NBT data from raw chunk data.

    :param chunk_data: the full raw bytes from disk for one whole chunk
    :return: nbtlib.tag.Compound: the NBT data's root node
    """
    length = int_from_bytes(chunk_data[0:4])
    compression_type = int_from_bytes(chunk_data[4:1])
    if compression_type != 2:
        logging.info(
            f"Unsupported compression type {compression_type}; expect the unexpected"
        )
    data_start = 5
    data_end = data_start + length - 1
    compressed_data = chunk_data[data_start:data_end]
    raw_nbt_data = zlib.decompress(compressed_data)
    bytes_io = io.BytesIO()
    bytes_io.write(raw_nbt_data)
    bytes_io.seek(0)
    nbt_data = nbtlib.File.parse(bytes_io).root
    return nbt_data


def extract_region(data: bytes) -> Region:
    """
    Extract chunks from a raw `mca` region file.

    :param data: bytes of the complete region file
    :return: Region with populated Chunk objects that represent the region file's data
    """
    chunks = []
    for x, z in tqdm.tqdm(
        itertools.product(range(REGION_WIDTH_CHUNKS), range(REGION_WIDTH_CHUNKS)),
        desc="extracting region data",
        total=REGION_TOTAL_CHUNKS,
    ):
        location_data_start = 4 * (
            (x % REGION_WIDTH_CHUNKS) + (z % REGION_WIDTH_CHUNKS) * REGION_WIDTH_CHUNKS
        )
        location_data_end = location_data_start + 4
        location_data = data[location_data_start:location_data_end]
        offset = int_from_bytes(location_data[0:3])
        sector_count = location_data[3]

        timestamp_data_start = location_data_start + 4096
        timestamp_data_end = timestamp_data_start + 4
        timestamp = int_from_bytes(data[timestamp_data_start:timestamp_data_end])

        chunk = Chunk(x, z, offset, sector_count, timestamp)
        if not chunk.empty:
            chunk_data_start = offset * 4096
            chunk_data_end = chunk_data_start + sector_count * 4096
            chunk_data = data[chunk_data_start:chunk_data_end]
            nbt_data = extract_nbt_data(chunk_data)
            chunk.nbt_data = nbt_data
        chunks.append(chunk)
    region = Region(chunks)
    return region


int_from_bytes = functools.partial(int.from_bytes, byteorder="big")
