import numpy as np

from mcatools.definitions import (
    CHUNK_WIDTH_BLOCKS,
    REGION_WIDTH_BLOCKS,
    REGION_TOTAL_BLOCKS,
    MAX_BLOCK_ID,
)
from mcatools.region import calculate_chunk_bounds, Region


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


colors_hex = {
    0: "000070",
    1: "8db360",
    2: "fa9418",
    3: "606060",
    4: "056621",
    5: "0b6659",
    6: "07f9b2",
    7: "0000ff",
    8: "ff0000",
    9: "8080ff",
    10: "9090a0",
    11: "a0a0ff",
    12: "ffffff",
    13: "a0a0a0",
    14: "ff00ff",
    15: "a000ff",
    16: "fade55",
    17: "d25f12",
    18: "22551c",
    19: "163933",
    20: "72789a",
    21: "537b09",
    22: "2c4205",
    23: "628b17",
    24: "000030",
    25: "a2a284",
    26: "faf0c0",
    27: "307444",
    28: "1f5f32",
    29: "40511a",
    30: "31554a",
    31: "243f36",
    32: "596651",
    33: "454f3e",
    34: "507050",
    35: "bdb25f",
    36: "a79d64",
    37: "d94515",
    38: "b09765",
    39: "ca8c65",
    40: "8080ff",
    41: "8080ff",
    42: "8080ff",
    43: "8080ff",
    44: "0000ac",
    45: "000090",
    46: "202070",
    47: "000050",
    48: "000040",
    49: "202038",
    50: "404090",
    127: "282898",
    129: "b5db88",
    130: "ffbc40",
    131: "888888",
    132: "2d8e49",
    133: "338e81",
    134: "2fffda",
    140: "b4dcdc",
    149: "7ba331",
    151: "8ab33f",
    155: "589c6c",
    156: "47875a",
    157: "687942",
    158: "597d72",
    160: "818e79",
    161: "6d7766",
    162: "789878",
    163: "e5da87",
    164: "cfc58c",
    165: "ff6d3d",
    166: "d8bf8d",
    167: "f2b48d",
}


colors_rgb = np.full((MAX_BLOCK_ID, 3), fill_value=255, dtype=np.uint8)
for biome_id, hexstring in colors_hex.items():
    color_bytes = bytes.fromhex(hexstring)
    colors_rgb[biome_id] = color_bytes[0], color_bytes[1], color_bytes[2]
