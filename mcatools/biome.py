import numpy as np

from mcatools.region import calculate_chunk_bounds, Region
from mcatools.definitions import (
    CHUNK_WIDTH_BLOCKS,
    REGION_WIDTH_BLOCKS,
    REGION_TOTAL_BLOCKS,
)


def biome_id_to_rgb(biome_id):
    # TODO build a static color map with meaningful values.
    color_int = int(biome_id / 180 * 16777215)  # FIXME magic numbers
    color_bytes = color_int.to_bytes(3, byteorder="big")
    return np.array([color_bytes[0], color_bytes[1], color_bytes[2]], dtype=np.uint8)


def extract_region_biomes(region: Region) -> np.ndarray:
    """
    Extract the full region's biome definition into a region-shaped array.

    :return: np.ndarray: the biome ids
    """
    region_biomes = np.zeros(REGION_TOTAL_BLOCKS, dtype=np.uint8).reshape(
        REGION_WIDTH_BLOCKS, REGION_WIDTH_BLOCKS
    )

    for index, chunk in enumerate(region.chunks):
        # Remember: z increments and wraps around before x increments!
        z_start, z_end, x_start, x_end = calculate_chunk_bounds(index)

        if chunk.empty:
            continue

        chunk_biome = chunk.nbt_data["Level"]["Biomes"].reshape(
            CHUNK_WIDTH_BLOCKS, CHUNK_WIDTH_BLOCKS
        )
        region_biomes[z_start:z_end, x_start:x_end] = chunk_biome

    return region_biomes
