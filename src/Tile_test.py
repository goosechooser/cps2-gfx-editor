from struct import Struct
from Tile import Tile, unpack_tile, pack_data

TEST_ADDR = ''
TEST_DATA = 'F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4'
TEST_DATA16 = TEST_DATA * 4
ROW_FMT = Struct(8 * 'c')

def test_unpack_tile1():
    tile = Tile(TEST_ADDR, bytearray.fromhex(TEST_DATA), '8')

    for row in ROW_FMT.iter_unpack(unpack_tile(tile)):
        assert bytearray(b''.join(row)).hex() == '0f0f0f0f0001060a'

def test_unpack_tile2():
    tile = Tile(TEST_ADDR, bytearray.fromhex(TEST_DATA16), '16')

    for row in ROW_FMT.iter_unpack(unpack_tile(tile)):
        assert bytearray(b''.join(row)).hex() == '0f0f0f0f0001060a'

def test_pack_data1():
    tile = Tile(TEST_ADDR, bytearray.fromhex(TEST_DATA), '8')
    unpacked = unpack_tile(tile)

    for row in ROW_FMT.iter_unpack(pack_data(unpacked)):
        assert bytearray(b''.join(row)).hex() == 'f1f2f3f4f1f2f3f4'

def test_pack_data2():
    tile = Tile(TEST_ADDR, bytearray.fromhex(TEST_DATA16), '16')
    unpacked = unpack_tile(tile)

    for row in ROW_FMT.iter_unpack(pack_data(unpacked)):
        assert bytearray(b''.join(row)).hex() == 'f1f2f3f4f1f2f3f4'

if __name__ == "__main__":
    #test_unpack_tile1()
    #test_unpack_tile2()
    test_pack_data1()
    test_pack_data2()

