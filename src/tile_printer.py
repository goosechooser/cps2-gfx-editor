from struct import iter_unpack
from PIL import Image
import numpy as np
from Tile import Tile, unpack_tile, interleave_subtiles

#TilePrinter is currently responsible for:
#read combined eprom file(s) -> create tile(s) -> convert to array(s) -> create bmp(s)

#Eventually should be responsible for:
#pass in tiles [created elsewhere] -> convert to array(s) -> create bmp(s)

#Changing to arrays allows for more flexible processing of 16x16 tiles
#without mucking around at a lower level
#Ideas for glitchy tileset -> just rearrage all the tiles and write back like regular

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
    image.save(path_to_save + ".bmp")

#This could probably be done as make data for Tile and whambam
def _make_blank_tile(size):
    zero = int('0x20', 16).to_bytes(1, byteorder='big')
    row = [zero] * size
    tile = [row] * size

    return np.array(tile)

#the way a group of 16x16 tiles is given, is how the final picture is assembled
#example of how addresses are formatted
#addrs = [['blank', '2F810',],
#         ['blank', '2F820',]]

def make_tiles(gfx_file, addresses, tile_dim):
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
                    row.append(Tile(tile_addr, read_data, tile_dim))
                else:
                    row.append(Tile('blank', 0, 16))
            tiles.append(row)

    return tiles

#Should make this so it only needs a list of tiles and a path to save the image
def process_tile_order(tiles):
    """Stitches multiple Tiles together into one array suitable for producing an image file.

    Returns an np.array.
    """
    pic_array = []
    for row_of_tiles in tiles:
        row = []
        for tile in row_of_tiles:
            if tile.address != 'blank':
                row.append(tile_to_array(tile))
            else:
                row.append(_make_blank_tile(16))
        pic_array.append(row)

    return pic_array
    #array_rows = []
    #for row in tiles:
    #    array_rows.append(np.concatenate(row, axis=1))
    #assembled = np.concatenate(array_rows, axis=0)

    #image = Image.fromarray(assembled, 'P')
    #file_name = "temp_ass"
    #image.save("outputs/bin_to_bmp/tiles/" + file_name + ".bmp")

def concat_tiles(tiles):
    array_rows = []
    for row in tiles:
        array_rows.append(np.concatenate(row, axis=1))
    assembled = np.concatenate(array_rows, axis=0)

    return assembled

def gfx_to_bmp(gfx_file, addresses, tile_dim, file_path):
    tiles = make_tiles(gfx_file, addresses, tile_dim)
    pic_array = process_tile_order(tiles)
    assembled = concat_tiles(pic_array)

    image = Image.fromarray(assembled, 'P')

    image.save(file_path)

    #converts the addresses mame displays when you press 'F4' to something else
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
