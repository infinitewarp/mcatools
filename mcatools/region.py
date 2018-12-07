import datetime
import math

import nbtlib

from mcatools.definitions import (
    CHUNK_WIDTH_BLOCKS,
    REGION_WIDTH_CHUNKS,
    REGION_TOTAL_CHUNKS,
)


def calculate_chunk_bounds(index):
    """
    Calculate a chunk's location bounds in the flattened blocks.
    :param index:
    :return:
    """
    z_start = (index % REGION_WIDTH_CHUNKS) * CHUNK_WIDTH_BLOCKS
    z_end = z_start + CHUNK_WIDTH_BLOCKS
    x_start = math.floor(index / REGION_WIDTH_CHUNKS) * CHUNK_WIDTH_BLOCKS
    x_end = x_start + CHUNK_WIDTH_BLOCKS
    return z_start, z_end, x_start, x_end


class Region(object):
    """Collection of 1024 Chunk objects."""

    def __init__(self, chunks: list):
        if len(chunks) != REGION_TOTAL_CHUNKS:
            raise Exception(
                f"Region needs { REGION_TOTAL_CHUNKS } chunks, not {len(chunks)}."
            )
        self.chunks = chunks


class Chunk(object):
    """Everything you need to know about a 16x256x16 chunk."""

    def __init__(
        self,
        x: int,
        z: int,
        offset: int,
        sector_count: int,
        timestamp: int,
        nbt_data: nbtlib.tag.Compound = None,
    ):
        self.x = x
        self.z = z
        self.offset = offset
        self.sector_count = sector_count
        self.timestamp = timestamp
        self.nbt_data = nbt_data

    @property
    def empty(self) -> bool:
        return 0 == self.offset == self.sector_count

    @property
    def datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.timestamp)

    def __repr__(self):
        repr_data = {
            "x": self.x,
            "z": self.z,
            "empty": self.empty,
            "datetime": str(self.datetime),
        }
        return f"<{self.__class__.__name__} {repr_data}>"
