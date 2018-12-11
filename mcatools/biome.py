import numpy as np

from mcatools.definitions import MAX_BLOCK_ID

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

colors_hex_reverse = {value: key for key, value in colors_hex.items()}


def match_color(input):
    """
    Get the closest known matching hex color.

    :param input: hex color string
    :return: tuple(hex color string, bool True if exact match)
    """
    if input in colors_hex.values():
        return input, True
    input_rgb = bytes.fromhex(input)
    known_rbgs = [bytes.fromhex(hexstring) for hexstring in colors_hex.values()]
    sorted_rgbs = sorted(
        known_rbgs,
        key=lambda x: (x[0] - input_rgb[0]) ** 2
        + (x[1] - input_rgb[1]) ** 2
        + (x[2] - input_rgb[2]) ** 2,
    )
    closest = sorted_rgbs[0]
    return "%02x%02x%02x" % (closest[0], closest[1], closest[2]), False


colors_rgb = np.full((MAX_BLOCK_ID, 3), fill_value=255, dtype=np.uint8)
for biome_id, hexstring in colors_hex.items():
    color_bytes = bytes.fromhex(hexstring)
    colors_rgb[biome_id] = color_bytes[0], color_bytes[1], color_bytes[2]
