from mcatools.region import Region


def test_filename_for_block_coords():
    assert Region.filename_for_block_coords(0, 0) == "r.0.0.mca"
    assert Region.filename_for_block_coords(-1, 0) == "r.-1.0.mca"
    assert Region.filename_for_block_coords(511, 511) == "r.0.0.mca"
    assert Region.filename_for_block_coords(512, 0) == "r.1.0.mca"
    assert Region.filename_for_block_coords(512, 512) == "r.1.1.mca"


def test_coordinate_bounds_for_region_coords():
    assert Region.coordinate_bounds_for_region_coords(0, 0) == (0, 0, 511, 511)
    assert Region.coordinate_bounds_for_region_coords(-1, -1) == (-512, -512, -1, -1)
    assert Region.coordinate_bounds_for_region_coords(1, 0) == (512, 0, 1023, 511)
    assert Region.coordinate_bounds_for_region_coords(0, 1) == (0, 512, 511, 1023)
    assert Region.coordinate_bounds_for_region_coords(1, 1) == (512, 512, 1023, 1023)
