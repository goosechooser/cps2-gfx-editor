from struct import iter_unpack
from PIL import Image
import numpy as np

#A sprite is a collection of tiles that use the same palette
class Sprite():
    def __init__(self, tiles, palette):
        self._tiles = [None]
        self._palette = None
        self._loc = (0, 0)
        self._size = (len(tiles), len(tiles[0]))

    #def __repr__(self):
    #    addrs = [tile for tile in self._tiles]
    #    return "Contains tiles: " + str(len(addrs)) + " Location: " + #(self._loc)

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
        #figure out way to fill in values for array and you can have
        #tile.toarray()
        #color(blahblahblah)
        pic_array = []
        for row in self._tiles:
            row = []
            for tile in row:
                interleaved_tile = tile.interleave_subtiles()
                tile_fmt = interleaved_tile.dimensions * 'c'
                tile_iter = iter_unpack(tile_fmt, interleaved_tile.unpack())
                tiles = [subtile for subtile in tile_iter]
                row.append(self._colortile(tiles))

            pic_array.append(row)

        return np.array(pic_array)

    def tobmp(self, path_to_save):
        """Returns a .bmp file"""
        image = Image.fromarray(self.toarray(), 'RGB')
        image.save(path_to_save + ".bmp")
