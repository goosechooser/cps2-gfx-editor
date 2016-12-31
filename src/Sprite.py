import struct
from PIL import Image
import numpy as np
np.set_printoptions(threshold=np.inf)

from src import Tile

#A sprite is a collection of tiles that use the same palette
class Sprite(object):
    def __init__(self, base_tile, tiles, palette, loc, size):
        self._base_tile = base_tile
        self._tiles = tiles
        self._palette = palette
        self._loc = loc
        self._size = size

    def __repr__(self):
        addrs = [tile.address for tile in self._tiles if tile]
        loc = " Location: (" + str(self._loc[0]) + ", " + str(self._loc[1])
        size = " Size: (" + str(self._size[0]) + ", " + str(self._size[1])
        return "Sprite contains tiles: " + str(addrs) + loc + ")" + size + ")"

    @property
    def base_tile(self):
        return self._base_tile

    @base_tile.setter
    def base_tile(self, value):
        self._base_tile = value

    @property
    def tiles(self):
        return self._tiles

    @tiles.setter
    def tiles(self, value):
        self._tiles = value

    @property
    def palette(self):
        return self._palette

    @palette.setter
    def palette(self, value):
        self._palette = value

    @property
    def location(self):
        return self._loc

    @location.setter
    def location(self, value):
        self._loc = value

    @property
    def size(self):
        return self._size

    def height(self):
        return self._size[1]

    def width(self):
        return self._size[0]

    def _colortile(self, subtiles):
        color_tile = []
        for row in subtiles:
            color_row = []
            for val in row:
                index = int.from_bytes(val, byteorder='big')
                color_row.append(self._palette[index])

            color_tile.append(color_row)
        return color_tile

    def toarray(self):
        """Unpacks the tiles and fills in pixel color.

        Returns an array.
        """
        pic_array = []

        tiles = self.tiles2d()
        for tile_row in tiles:
            row = []
            for tile in tile_row:
                interleaved_tile = tile.interleave_subtiles()
                tile_fmt = interleaved_tile.dimensions * 'c'
                tile_iter = struct.iter_unpack(tile_fmt, interleaved_tile.unpack())
                subtiles = [subtile for subtile in tile_iter]

                row.append(self._colortile(subtiles))

            pic_array.append(row)

        array_rows = []
        for row in np.array(pic_array):
            array_rows.append(np.concatenate(row, axis=1))
        assembled = np.concatenate(array_rows, axis=0)

        return assembled

    def tobmp(self, path_to_save):
        """Returns a .bmp file"""
        concat = self.toarray()
        image = Image.fromarray(concat, 'RGB')
        image.save(path_to_save + ".bmp")

    def topng(self, path_to_save):
        """Returns a .png file"""
        concat = self.toarray()
        image = Image.fromarray(concat, 'RGB')
        image.save(path_to_save + ".png")

    def tiles2d(self):
        """Returns a list of lists containing the Sprite's tiles."""
        list_2d = []
        for i in range(self._size[1]):
            offset = self._size[0] * i
            list_2d.append(self._tiles[offset:offset + self._size[0]])

        return list_2d

    def addrs2d(self):
        """Returns a list of lists containing the tiles' addresses."""
        list_2d = []
        for i in range(self._size[1]):
            offset = self._size[0] * i
            list_2d.append([tile.address for tile in self._tiles[offset:offset + self._size[0]]])

        return list_2d

# Factories
def fromdict(dict_):
    """Returns a Sprite object with empty tiles property."""
    palette = [_argb_to_rgb(color[2:]) for color in dict_['palette']]

    tile_number = int(dict_['tile_number'], 16)
    size = (int(dict_['width']), int(dict_['height']))
    loc = (int(dict_['x']), int(dict_['y']))

    tiles = []
    for i in range(size[1]):
        for j in range(size[0]):
            offset = i * 0x10 + j * 0x1
            addr = str(hex(tile_number + offset))
            tiles.append(Tile.Tile(addr, None))

    return Sprite(hex(tile_number), tiles, palette, loc, size)

def _argb_to_rgb(color):
    """Converts the 2 byte ARGB format the cps2 uses.
    
    Returns a bytes() of 3 byte RGB.
    """
    if len(color) < 4:
        color = (4 - len(color)) * '0' + color
    return bytes.fromhex(color[1] * 2 + color[2] * 2 + color[3] * 2)
