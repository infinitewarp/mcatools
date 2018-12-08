import datetime
import math

import nbtlib

from mcatools.definitions import (
    CHUNK_WIDTH_BLOCKS,
    REGION_WIDTH_CHUNKS,
    REGION_TOTAL_CHUNKS,
    REGION_WIDTH_BLOCKS_BITS,
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

    @staticmethod
    def filename_for_block_coords(block_x, block_z):
        """
        Get the filename for the region containing the (x,z) coordinate block.

        :param block_x: x coordinate of a block
        :type block_x: int
        :param block_z: z coordinate of a block
        :type block_z: int
        :return: string filename for the region
        """
        region_x = block_x >> REGION_WIDTH_BLOCKS_BITS
        region_z = block_z >> REGION_WIDTH_BLOCKS_BITS
        return f"r.{region_x}.{region_z}.mca"

    @staticmethod
    def coordinate_bounds_for_region_coords(region_x, region_z):
        """
        Get the min and max block coordinate bounded by the given region coordinate.

        :param region_x: x coordinate of a region ("x" part of the filename)
        :type region_x: int
        :param region_z: z coordinate of a region ("z" part of the filename)
        :type region_x: int
        :return: tuple (min_x, min_z, max_x, max_z) for the bounded blocks
        """
        min_block_x = region_x << REGION_WIDTH_BLOCKS_BITS
        min_block_z = region_z << REGION_WIDTH_BLOCKS_BITS
        max_block_x = ((region_x + 1) << REGION_WIDTH_BLOCKS_BITS) - 1
        max_block_z = ((region_z + 1) << REGION_WIDTH_BLOCKS_BITS) - 1
        return min_block_x, min_block_z, max_block_x, max_block_z


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
