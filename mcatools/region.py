import datetime
import functools
import io
import itertools
import logging
import math
import zlib

import nbtlib
import numpy as np
import tqdm

from mcatools.definitions import (
    CHUNK_WIDTH_BLOCKS,
    REGION_WIDTH_CHUNKS,
    REGION_TOTAL_CHUNKS,
    REGION_WIDTH_BLOCKS_BITS,
    REGION_TOTAL_BLOCKS,
    REGION_WIDTH_BLOCKS,
)


int_from_bytes = functools.partial(int.from_bytes, byteorder="big")
int_to_bytes = functools.partial(int.to_bytes, byteorder="big")


def calculate_chunk_bounds(index):
    """
    Calculate a chunk's location bounds in the flattened blocks.
    :param index:
    :return:
    """
    # Remember: z increments and wraps around before x increments!
    z_start = (index % REGION_WIDTH_CHUNKS) * CHUNK_WIDTH_BLOCKS
    z_end = z_start + CHUNK_WIDTH_BLOCKS
    x_start = math.floor(index / REGION_WIDTH_CHUNKS) * CHUNK_WIDTH_BLOCKS
    x_end = x_start + CHUNK_WIDTH_BLOCKS
    return z_start, z_end, x_start, x_end


def extract_nbt_data(chunk_data: bytes) -> nbtlib.tag.Compound:
    """
    Extract, decompress, and parse NBT data from raw chunk data.

    :param chunk_data: the full raw bytes from disk for one whole chunk
    :return: nbtlib.tag.Compound: the NBT data's root node
    """
    length = int_from_bytes(chunk_data[0:4])
    compression_type = int_from_bytes(chunk_data[4:5])
    if compression_type != 2:
        logging.info(
            f"Unsupported compression type {compression_type}; expect the unexpected"
        )
    data_start = 5
    data_end = data_start + length
    compressed_data = chunk_data[data_start:data_end]
    raw_nbt_data = zlib.decompress(compressed_data)
    bytes_io = io.BytesIO(raw_nbt_data)
    bytes_io.name = None  # because nbtlib expects a name
    nbt_data = nbtlib.File.from_buffer(bytes_io)
    return nbt_data


def extract_chunk_data(data: bytes) -> list:
    """
    Extract chunks from a raw `mca` Anvil region binary file data.

    :param data: the complete Anvil region file in bytes
    :return: list of populated Chunk objects
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
    return chunks


def build_anvil_data(chunks: list) -> bytes:
    if len(chunks) != REGION_TOTAL_CHUNKS:
        raise RuntimeError(
            f"anvil requires {REGION_TOTAL_CHUNKS} chunks, not {len(chunks)} "
        )

    locations = bytes()
    timestamps = bytes()
    chunk_data = bytes()

    compression_type = int_to_bytes(2, 1)  # "2" means we always use zlib
    empty_location = int_to_bytes(0, 4)
    empty_timestamp = int_to_bytes(0, 4)

    current_offset = 2  # first chunk starts after the 2-sector file header
    for z, x in tqdm.tqdm(
        itertools.product(range(REGION_WIDTH_CHUNKS), range(REGION_WIDTH_CHUNKS)),
        desc="saving region data",
        total=REGION_TOTAL_CHUNKS,
    ):
        chunk_index = x * REGION_WIDTH_CHUNKS + z
        chunk = chunks[chunk_index]
        assert chunk.x == x and chunk.z == z
        if not chunk.empty:
            #########################
            # Zip the NBT data so we can get its size.
            nbt_bytes_io = io.BytesIO()  # because chunk.write needs a file-like object
            chunk.nbt_data.write(nbt_bytes_io, byteorder="big")
            nbt_bytes_io.seek(0)
            nbt_bytes = nbt_bytes_io.read()
            zipped_nbt_bytes = zlib.compress(nbt_bytes, 9)
            zipped_nbt_bytes_length = len(zipped_nbt_bytes)

            #########################
            # Do some math for the location and chunk header.
            # Add 5 to include the length of the chunk header.
            unpadded_chunk_length = zipped_nbt_bytes_length + 5
            chunk_pad_count = (
                math.ceil(unpadded_chunk_length / 4096) * 4096 - unpadded_chunk_length
            )
            sector_count = math.ceil(
                (zipped_nbt_bytes_length + 5 + chunk_pad_count) / 4096
            )

            #########################
            # Write the location.
            offset_bytes = int_to_bytes(current_offset, 3)
            locations += offset_bytes

            sector_count_byte = int_to_bytes(sector_count, 1)
            locations += sector_count_byte

            #########################
            # Write the timestamp.
            timestamp_bytes = int_to_bytes(chunk.timestamp, 4)
            timestamps += timestamp_bytes

            #########################
            # Write the chunk data.
            chunk_data += int_to_bytes(zipped_nbt_bytes_length, 4)
            chunk_data += compression_type
            chunk_data += zipped_nbt_bytes
            chunk_data += bytes(chunk_pad_count)

            current_offset += sector_count
        else:
            locations += empty_location
            timestamps += empty_timestamp

    return locations + timestamps + chunk_data


class Region(object):
    """Collection of 1024 Chunk objects."""

    def __init__(self, chunks: list):
        if len(chunks) != REGION_TOTAL_CHUNKS:
            raise Exception(
                f"Region needs { REGION_TOTAL_CHUNKS } chunks, not {len(chunks)}."
            )
        self.chunks = chunks
        self._biomes = None

    @classmethod
    def load(cls, filename):
        with open(filename, "rb") as f:
            data = f.read()
        chunks = extract_chunk_data(data)
        return cls(chunks)

    def save(self, filename):
        data = build_anvil_data(self.chunks)
        with open(filename, "wb") as f:
            f.write(data)

    def get_biomes(self, force_reread: bool = False) -> np.ndarray:
        """
        Extract the full region's biome ids into a region-shaped numpy array.

        :return: np.ndarray: region-shaped numpy array of biome ids
        """
        if self._biomes and not force_reread:
            return self._biomes

        region_biomes = np.zeros(REGION_TOTAL_BLOCKS, dtype=np.uint8).reshape(
            REGION_WIDTH_BLOCKS, REGION_WIDTH_BLOCKS
        )

        for index, chunk in enumerate(self.chunks):
            z_start, z_end, x_start, x_end = calculate_chunk_bounds(index)

            if chunk.empty:
                continue

            chunk_biome = chunk.nbt_data.root["Level"]["Biomes"].reshape(
                CHUNK_WIDTH_BLOCKS, CHUNK_WIDTH_BLOCKS
            )
            region_biomes[z_start:z_end, x_start:x_end] = chunk_biome

        self._biomes = region_biomes
        return self._biomes

    def set_biomes(self, new_biomes):
        """
        Overwrite the region's chunk's current data with the given biomes.

        :param new_biomes: region-shaped numpy array of biome ids
        :type new_biomes: np.ndarray
        """
        self._biomes = new_biomes

        for index, chunk in enumerate(self.chunks):
            z_start, z_end, x_start, x_end = calculate_chunk_bounds(index)

            if chunk.empty:
                continue

            chunk.nbt_data.root["Level"]["Biomes"] = nbtlib.IntArray(
                new_biomes[z_start:z_end, x_start:x_end].flatten()
            )

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
