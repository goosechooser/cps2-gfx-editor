from __future__ import generators
from struct import Struct

class Tile():

    def __init__(self, addr, data, dimensions):
        self.tile_addr = addr
        self.tile_data = data
        self.tile_dimensions = dimensions

    @property
    def address(self):
        """Get the address in memory where the tile is located."""
        return self.tile_addr

    @property
    def data(self):
        """Get the bitplane packed data."""
        return self.tile_data

    @property
    def dimensions(self):
        """Get the pixel value data."""
        return self.tile_dimensions

#class Tile16(Tile8):
#   tile16 = Struct(32 * 'c')

#    def __init__(self, addr, data):
#        Tile8.__init__(self, addr, data)
#        self.tile_addr = addr
#        self.tile_data = data
#        self.tile_unpacked = self._unpack_data()
#        self.tile_interleaved = self._interleave_tiles()

#    def _unpack_data(self):
#        """This returns the data for 4 8x8 tiles deinterleaved."""
#        Tile8._unpack_data(self)
#        tiles = []
#        for tile8 in self.tile16.iter_unpack(self.tile_data):
#            result = self._bitplanes_to_tile(b''.join(tile8))
#            tiles.append(result)

#        return b''.join(tiles)

#Functions to manipulate tile objects below ig
def unpack_tile(tile):
    """Unpacks a 4bpp planar tile and returns a byte() of pixel values.
    Doesn't check if a tile is 8x8 or 16x16, should it?
    Should this return raw data or should it return a Tile obj?
    """
    tile_fmt = Struct(32 * 'c')
    tile_iter = tile_fmt.iter_unpack(tile.data)

    tiles = [_bitplanes_to_tile(b''.join(tile)) for tile in tile_iter]
    return b''.join(tiles)

def _bitplanes_to_tile(data):
    bitplanes = _unpack_bitplanes(data)

    pixels = []
    for i in range(0, 8):
        temp_val = [bitplanes[0][i], bitplanes[1][i],
                    bitplanes[2][i], bitplanes[3][i]]
        row = _make_row_of_pixels(temp_val)

        pixels.append(row)

    return b''.join(pixels)

def _unpack_bitplanes(data):
    planes = [[], [], [], []]
    data_iter = Struct('c').iter_unpack(data)

    for bp in data_iter:
        planes[0].extend(*bp)
        planes[1].extend(*next(data_iter))
        planes[2].extend(*next(data_iter))
        planes[3].extend(*next(data_iter))

    return planes

def _make_row_of_pixels(bitplane_rows):
    mask = int(b'00000001')
    bitplane_values = bitplane_rows
    row_of_pixels = []
    for loc in range(0, 8):
        masked = [value & mask for value in bitplane_values]
        bitplane_values = [value >> 1 for value in bitplane_values]
        bit_plane_val = masked[0] << 3 | masked[1] << 2 | masked[2] << 1 | masked[3]
        row_of_pixels.append(bit_plane_val.to_bytes(1, byteorder='big'))

    row_of_pixels.reverse()

    return b''.join(row_of_pixels)

def pack_data(data):
    """Converts pixel values into 4bpp and packs it for Tile use.
    Returns bytes()
    """

    tile_fmt = Struct(32 * 'c')
    tile_iter = tile_fmt.iter_unpack(data)

    bitplane_values = [_tile_to_bitplanes(b''.join(tile)) for tile in tile_iter]
    return b''.join(bitplane_values)

def _tile_to_bitplanes(data):
    bitplanes = []
    row_fmt = Struct(8 * 'c')
    row_iter = row_fmt.iter_unpack(data)

    bitplanes = [_pixel_row_to_4bpp(row) for row in row_iter]

    return b''.join(bitplanes)

def _pixel_row_to_4bpp(row):
    bitplanes = [0, 0, 0, 0]
    mask = int(b'00000001')
    row = [int.from_bytes(val, byteorder='big') for val in row]

    for pixel in row:
        for i, plane in enumerate(bitplanes):
            bitplanes[i] = (plane << 1) | (pixel & mask)
            pixel = pixel >> 1

    bitplanes.reverse()
    return bytearray(bitplanes)
