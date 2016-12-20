from struct import iter_unpack, unpack
from PIL import Image
import numpy as np
from src import Tile, helper

#TilePrinter is currently responsible for:
#read combined eprom file(s) -> create tile(s) -> convert to array(s) -> create bmp(s)

#Eventually should be responsible for:
#pass in tiles [created elsewhere] -> convert to array(s) -> create bmp(s)

#Changing to arrays allows for more flexible processing of 16x16 tiles
#without mucking around at a lower level
#Ideas for glitchy tileset -> just rearrage all the tiles and write back like regular

#the way a group of 16x16 tiles is given, is how the final picture is assembled
#example of how addresses are formatted
#addrs = [['blank', '2F810',],
#         ['blank', '2F820',]]

def make_tiles(gfx_file, addresses, tile_dim=16):
    """Given a list of addresses and tile dimensions (8 or 16),
    reads from the provided graphics file and creates Tile object(s).abs

    Returns either a list of Tiles or a list of lists of Tiles.
    """
    tiles = []
    with open(gfx_file, 'rb') as f:
        if any(isinstance(el, list) for el in addresses):
            for row_of_addresses in addresses:
                row = []
                for tile_addr in row_of_addresses:
                    if tile_addr.upper() != 'BLANK':
                        f.seek(helper.convert_mame_addr(tile_addr, tile_dim))
                        if tile_dim == 8:
                            read_data = f.read(32)
                        if tile_dim == 16:
                            read_data = f.read(128)
                        row.append(Tile.Tile(tile_addr, read_data, tile_dim))
                    else:
                        row.append(Tile.EmptyTile(16))
                tiles.append(row)
        else:
            for tile_addr in addresses:
                if tile_addr.upper() != 'BLANK':
                    f.seek(helper.convert_mame_addr(tile_addr, tile_dim))
                    if tile_dim == 8:
                        read_data = f.read(32)
                    if tile_dim == 16:
                        read_data = f.read(128)
                    tiles.append(Tile.Tile(tile_addr, read_data, tile_dim))
                else:
                    tiles.append(Tile.EmptyTile(16))

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
            row.append(tile.toarray())

        pic_array.append(row)

    return pic_array

def concat_arrays(arrays):
    """Concatenates a 2D list of arrays into one array.

    Returns an array.
    """
    array_rows = []
    for row in arrays:
        array_rows.append(np.concatenate(row, axis=1))
    assembled = np.concatenate(array_rows, axis=0)

    return assembled

def gfx_to_bmp(gfx_file, addresses, output_image, tile_dim=16):
    """Encapsulates all the seperate steps.
    Produces a BMP file.
    """
    tiles = make_tiles(gfx_file, addresses, tile_dim)
    pic_array = process_tile_order(tiles)
    assembled = concat_arrays(pic_array)

    image = Image.fromarray(assembled, 'P')

    image.save(output_image)
