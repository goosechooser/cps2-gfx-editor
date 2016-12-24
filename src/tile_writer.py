from PIL import Image
import numpy as np
from src import Tile, helper

#TileWriter is currently responsible for:
#read from bmp -> split to array(s) -> pack new data to tile(s)

def image_to_tiles(image, addresses):
    image_array = _read_image(image)
    tiles_array = _split_array(image_array)

    addr = flatten_list(addresses)

    filtered = [zipped for zipped in zip(addr, tiles_array) if zipped[0] != 'BLANK']

    tiles = []
    for tile in filtered:
        data = []
        data = _to_tile(tile[1])
        tile_ = Tile.Tile(tile[0], bytes(data), 16, packed=False)
        tiles.append(tile_.deinterleave_subtiles())

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

#Currently for 16x16 tiles only
def _to_tile(array_):
    rows = []

    for row in array_.tolist():
        rows.extend(row)
    return rows

def flatten_list(rolled_list):
    flat = [x for sublist in rolled_list for x in sublist]
    return flat

#write image to graphics file
#wasn't writing the data from the gfx_file that comes after the tile data to the file
def write_tiles_to_gfx(tiles, gfx_file, output_file=None):
    if output_file is None:
        output_file = gfx_file + '_edit'

    gfx_reader = open(gfx_file, 'rb')
    sorted_tiles = sorted(tiles, key=lambda tile: int(tile.address, 16))

    with open(output_file, 'wb') as f:
        for tile in sorted_tiles:
            converted_addr = helper.convert_mame_addr(tile.address, tile.dimensions)
            read_length = converted_addr - gfx_reader.tell()
            print("tile address: " + str(tile.address))
            #print("converted addr: " + str(converted_addr))
            #print("gfx reader tell before: " + str(gfx_reader.tell()))
            #print("read_length: " + str(read_length))
            if read_length == 128:
                gfx_reader.seek(read_length, 1)
                f.write(tile.data)
            else:
                unchanged_gfx = gfx_reader.read(read_length)
                f.write(unchanged_gfx)
                gfx_reader.seek(128, 1)
                f.write(tile.data)

        final_read = gfx_reader.read()
        #print(len(final_read))
        f.write(final_read)

    gfx_reader.close()
