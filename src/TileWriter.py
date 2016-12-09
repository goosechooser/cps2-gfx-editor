from struct import unpack, iter_unpack
from PIL import Image
import numpy as np
from Tile import Tile, pack_data

#TileWriter is currently responsible for:
#read from bmp -> split to array(s) -> pack new data to tile(s)
#Should it also handle writing to files??

#wip
def image_to_tiles(image, addresses):
    image_array = _read_image(image)
    tiles_array = _split_array(image_array)

    subtile_groups = [_deinterleave_tile_array(tile_array) for tile_array in tiles_array]
    addr = flatten_list(addresses)

    tiles = []
    filtered = [zipped for zipped in zip(addr, subtile_groups) if zipped[0] != 'blank']

    for tile in filtered:
        data = []
        data = _array_group_to_tile(tile[1])
        packed = pack_data(bytes(data))
        tiles.append(Tile(tile[0], packed, 16))

    #print(len(tiles))
    return tiles

def _read_image(image):
    """Opens .bmp image.

    Returns an array.
    """
    img = Image.open(image)
    return np.asarray(img, dtype='>H')

#Splits image into 16x16 tiles
def _split_array(image):
    """Splits an image into 16x16 sized tiles.

    Returns a list of arrays.
    """
    tiles = []
    dims = image.shape
    split_image = np.vsplit(image, int(dims[0]/16))
    for tile in split_image:
        tiles.extend(np.hsplit(tile, int(dims[1]/16)))
    return tiles

def _deinterleave_tile_array(tile_array):
    """Deinterleaves the array representing a 16x16 tile.

    Returns a list of arrays.
    """
    temp_tiles = []
    split_tiles = np.vsplit(tile_array, 2)

    for half in split_tiles:
        temp_tiles.extend(np.hsplit(half, 2))

    return [temp_tiles[0], temp_tiles[2], temp_tiles[1], temp_tiles[3]]

#Currently for 16x16 tiles only
def _array_group_to_tile(subtiles):
    rows = []
    for sub in subtiles:
        for row in sub.tolist():
            rows.extend(row)
    return rows

#converts the addresses mame displays when you press 'F4' to something else
def convert_mame_addr(mame_addr, tile_size):
    tile_bytes = 0
    addr = int(mame_addr, 16)
    if tile_size is '8':
        tile_bytes = 32
    if tile_size is '16':
        tile_bytes = 128

    converted_addr = addr * tile_bytes
    memory_bank_size = int('0x1000000', 16)

    #currently the 8 eproms are split into 2 banks
    #wouldnt need this if you combined the 2 bank files into 1 file
    if converted_addr > memory_bank_size:
        converted_addr -= memory_bank_size

    return converted_addr

def flatten_list(rolled_list):
    flat = [x for sublist in rolled_list for x in sublist]
    return flat

#write image to graphics file
#wasn't writing the data from the gfx_file that comes after the tile data to the file
def write_tiles_to_gfx(tiles, gfx_file):
    #should read file and store results in a buffer with first 'with open'
    #then write pre-edit, edit, and post-edit data with a 2nd 'with open'
    #look into struct, could pack 16x16 tiles as a struct
    with open(gfx_file, 'wb+') as f:
        end = f.read()
        f.write(end)
        for tile in tiles:
            converted_addr = convert_mame_addr(tile.address, tile.dimensions)
            f.seek(converted_addr)
            f.write(tile.data)
