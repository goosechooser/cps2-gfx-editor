from struct import iter_unpack
from PIL import Image
import numpy as np

#A sprite is a collection of tiles that use the same palette
class Sprite():
    def __init__(self, tiles, palette, loc, size):
        self._tiles = tiles
        self._palette = palette
        self._loc = loc
        self._size = size

    def __repr__(self):
        addrs = [tile._tile_addr for tile in self._tiles]
        loc = " Location: (" + str(self._loc[0]) + ", " + str(self._loc[1])
        size = " Size: (" + str(self._size[0]) + ", " + str(self._size[1])
        return "Sprite contains tiles: " + str(addrs) + loc + ")" + size + ")"

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

    def to2dlist(self):
        list_2d = []
        for i in range(self._size[1]):
            offset = self._size[0] * i
            list_2d.append(self._tiles[offset:offset + self._size[0]])

        return list_2d

class Factory:
    def __init__(self, sprite_file, tile_factory):
        self._sprite_file = sprite_file
        self._factory = tile_factory
        self._fp = None

    def open(self):
        self._fp = open(self._sprite_file, 'r')

    def close(self):
        self._fp.close()

    def new(self):
        formatted = self._format_line()
        if formatted is 'EOF':
            return 'EOF'

        spd = self._read_file(formatted)
        tiles = []

        for i in range(spd['height']):
            for j in range(spd['width']):
                offset = i * 0x10 + j * 0x1
                tiles.append(self._factory.new(hex(spd['tile_number'] + offset), 16))

        loc = (spd['x'], spd['y'])
        size = (spd['width'], spd['height'])
        return Sprite(tiles, spd['palette'], loc, size)

    def _read_file(self, formatted):
        tile_colors = []
        for color in formatted['palette'].split(" "):
            tile_colors.append(self._argb_to_rgb(color))
        formatted['palette'] = tile_colors

        return formatted

    def _format_line(self):
        line = self._fp.readline()
        if not line:
            return "EOF"
        strip_line = line.lstrip('{')
        strip_line = strip_line.rstrip(' }\n')
        properties = strip_line.split(", ")
        line_properties = dict()
        for prop in properties:
            stripped = prop.split(" = ")
            key = stripped[0].lstrip(' ')
            value = stripped[1]

            if key == 'tile_number':
                line_properties[key] = int(value, 16)

            elif key != 'palette':
                line_properties[key] = int(value)
            else:
                line_properties[key] = value

        del line_properties['pal_number']
        return line_properties

    def _argb_to_rgb(self, color):
        return bytes.fromhex(color[1] * 2 + color[2] * 2 + color[3] * 2)


