from struct import iter_unpack
from PIL import Image
import numpy as np
from Tile import Tile, unpack_tile, interleave_subtiles

#Responsible for (already created) tile(s) -> array(s) -> bmp(s)
def tile_to_array(tile):
    """Uses 8x8 or 16x16 Tile data to create an array of the tile's data.

    Returns an array.
    """
    unpacked_tile = unpack_tile(tile)

    if tile.dimensions == 16:
        interleaved_tiles = interleave_subtiles(unpacked_tile)
    else:
        interleaved_tiles = unpacked_tile

    tile_fmt = tile.dimensions * 'c'
    tile_iter = iter_unpack(tile_fmt, interleaved_tiles)
    tiles = [subtile for subtile in tile_iter]

    return np.array(tiles)

def tile_to_bmp(tile, path_to_save):
    """Creates a .bmp image from a single 8x8 or 16x16 tile."""
    tile_array = tile_to_array(tile)
    image = Image.fromarray(tile_array, 'P')
    image.save(path_to_save + "1.bmp")

    unpacked = unpack_tile(tile)
    data = interleave_subtiles(unpacked)
    image = Image.frombytes('P', (tile.dimensions, tile.dimensions), data)
    image.save(path_to_save + "2.bmp")

def test(path, addr):
    read_data = 0
    with open(path, 'rb') as f:
        f.seek(int(addr, 16))
        read_data = f.read(128)
    tile = Tile(addr, read_data, 16)
    tile_to_bmp(tile, "outputs/bin_to_bmp/struct_test")

def _interleave_arrays(subtiles):
    """Interleaves 4 8x8 tile arrays.

    Returns an array representing a 16x16 tile."""
    tile_halfs = []
    tile_halfs.append(np.concatenate([subtiles[0], subtiles[2]], axis=1))
    tile_halfs.append(np.concatenate([subtiles[1], subtiles[3]], axis=1))
    return np.concatenate(tile_halfs, axis=0)

#This could probably be done as make data for Tile and whambam
def _make_blank_tile8():
    zero = int('0x10', 16)
    zero = zero.to_bytes(1, byteorder='big')
    row = row = [zero] * 8
    tile = [row] * 8

    return np.array(tile)

def _make_blank_tile16():
    subtiles = [_make_blank_tile8()] * 4
    return _interleave_arrays(subtiles)

#the way a group of 16x16 tiles is given, is how the final picture is assembled
#example of how addresses are formatted
#addrs = [['blank', '2F810',],
#         ['blank', '2F820',]]
#Should make this so it only needs a list of tiles and a path to save the image
def process_tile_order(gfx_file, addresses, tile_dim):
    tiles = []
    with open(gfx_file, 'rb') as f:
        for row_of_addresses in addresses:
            row = []
            for tile_addr in row_of_addresses:
                if tile_addr != 'blank':
                    f.seek(convert_mame_addr(tile_addr, tile_dim))
                    if tile_dim == 8:
                        read_data = f.read(32)
                    if tile_dim == 16:
                        read_data = f.read(128)
                    row.append(tile_to_array(Tile(tile_addr, read_data, tile_dim)))
                else:
                    row.append(_make_blank_tile16())
            tiles.append(row)

    array_rows = []
    for row in tiles:
        array_rows.append(np.concatenate(row, axis=1))
    assembled = np.concatenate(array_rows, axis=0)

    image = Image.fromarray(assembled, 'P')
    file_name = "temp_ass"
    image.save("outputs/bin_to_bmp/tiles/" + file_name + ".bmp")

    #converts the addresses mame displays when you press 'F4' to something else,,
def convert_mame_addr(mame_addr, tile_size):
    tile_bytes = 0
    addr = int(mame_addr, 16)
    if tile_size == 8:
        tile_bytes = 32
    if tile_size == 16:
        tile_bytes = 128

    converted_addr = addr * tile_bytes
    memory_bank_size = int('0x1000000', 16)

    #currently the 8 eproms are split into 2 banks
    if converted_addr > memory_bank_size:
        converted_addr -= memory_bank_size

    return converted_addr
