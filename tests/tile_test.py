from struct import Struct
from src import Tile

TEST_ADDR = ''
TEST_DATA = 'F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4'
TEST_DATA16 = TEST_DATA * 4
TEST_PALETTE_DATA = '100200300510620730840A60C80EA0FB3FD3FE4FF7FFA012FFFFFFFFFFFFFFFF'
ROW_FMT = Struct(8 * 'c')
TILE_FMT = Struct(64 * 'c')

def test_unpack_tile1():
    tile = Tile.Tile(TEST_ADDR, bytearray.fromhex(TEST_DATA), '8')

    for row in ROW_FMT.iter_unpack(tile.unpack()):
        assert bytearray(b''.join(row)).hex() == '0f0f0f0f00080605'

def test_unpack_tile2():
    tile = Tile.Tile(TEST_ADDR, bytearray.fromhex(TEST_DATA16), '16')

    for row in ROW_FMT.iter_unpack(tile.unpack()):
        assert bytearray(b''.join(row)).hex() == '0f0f0f0f00080605'

def test_pack_data1():
    tile = Tile.Tile(TEST_ADDR, bytearray.fromhex(TEST_DATA), '8')
    unpacked = tile.unpack()

    tile.pack(unpacked)
    for row in ROW_FMT.iter_unpack(tile.data):
        assert bytearray(b''.join(row)).hex() == 'f1f2f3f4f1f2f3f4'

def test_pack_data2():
    tile = Tile.Tile(TEST_ADDR, bytearray.fromhex(TEST_DATA16), '16')
    unpacked = tile.unpack()

    tile.pack(unpacked)
    for row in ROW_FMT.iter_unpack(tile.data):
        assert bytearray(b''.join(row)).hex() == 'f1f2f3f4f1f2f3f4'

def test_interleave_subtiles():
    test_data = 'F1' * 32 + 'F2' * 32 + 'F3' * 32 + 'F4' * 32
    tile = Tile.Tile(TEST_ADDR, bytearray.fromhex(test_data), '16')

    tile = tile.interleave_subtiles()
    interleaved = tile.unpack()

    tiles = [tile for tile in TILE_FMT.iter_unpack(interleaved)]
    assert bytearray(b''.join(tiles[0])).hex() == '0f0f0f0f0000000f0f0f0f0f00000f0f' * 4
    assert bytearray(b''.join(tiles[1])).hex() == '0f0f0f0f0000000f0f0f0f0f00000f0f' * 4
    assert bytearray(b''.join(tiles[2])).hex() == '0f0f0f0f00000f000f0f0f0f000f0000' * 4
    assert bytearray(b''.join(tiles[3])).hex() == '0f0f0f0f00000f000f0f0f0f000f0000' * 4

if __name__ == "__main__":
    print("sup")
    