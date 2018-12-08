from mcatools.region import Region


def test_filename_for_block_coords():
    assert Region.filename_for_block_coords(0, 0) == "r.0.0.mca"
    assert Region.filename_for_block_coords(-1, 0) == "r.-1.0.mca"
    assert Region.filename_for_block_coords(511, 511) == "r.0.0.mca"
    assert Region.filename_for_block_coords(512, 0) == "r.1.0.mca"
    assert Region.filename_for_block_coords(512, 512) == "r.1.1.mca"
