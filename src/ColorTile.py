from struct import iter_unpack
from src import Tile
from PIL import Image
import numpy as np

class ColorTile(Tile.Tile):
    def __init__(self, addr, data, palette, location, size):
        super().__init__(addr, data)
        self._palette = palette
        self._loc = location
        self._size = size

    def __repr__(self):
        return "Address: " + str(self._tile_addr) + "\nDimension: " + str(self._tile_dimensions) + "\nData: " + str(self._tile_data) + ")\nPalette: " + str(self._palette) + "\nLocation: " + str(self._loc) + "\nSize: " + str(self._size)

    @property
    def palette(self):
        return self._palette

    @palette.setter
    def palette(self, value):
        self._palette = value

    @property
    def location(self):
        return self._loc

    @property
    def size(self):
        return self._size

    def toarray(self):
        """Unpacks the tile and fills in pixel color.

        Returns an array.
        """
        interleaved_tile = self.interleave_subtiles()
        tile_fmt = interleaved_tile.dimensions * 'c'
        tile_iter = iter_unpack(tile_fmt, interleaved_tile.unpack())
        tiles = [subtile for subtile in tile_iter]

        color_tile = []
        for row in tiles:
            color_row = []
            for val in row:
                index = int.from_bytes(val, byteorder='big')
                color_row.append(self._palette[index])

            color_tile.append(color_row)

        return np.array(color_tile)

    def tobmp(self, path_to_save):
        """Creates a .bmp image from a single 8x8 or 16x16 tile."""
        image = Image.fromarray(self.toarray(), 'RGB')
        image.save(path_to_save + ".bmp")
