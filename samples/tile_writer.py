from PIL import Image
import numpy as np
from src import Tile, helper

#TileWriter is currently responsible for:
#read from bmp -> split to array(s) -> pack new data to tile(s)
#write image to graphics file
def write_tiles_to_gfx(tiles, gfx_file, output_file=None):
    """Writes tile data to a given file."""
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
