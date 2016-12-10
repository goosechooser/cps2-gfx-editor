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
    @address.setter
    def address(self, value):
        self.tile_addr = value

    @property
    def data(self):
        """Get the bitplane packed data."""
        return self.tile_data

    @property
    def dimensions(self):
        """Get the pixel value data."""
        return self.tile_dimensions

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

#Would need to interleave like [subtile1-row1] [subtile3-row1]
#                          ... [subtile1-row16] [subtile3-row16]
#                              [subtile2-row1] [subtile4-row1]
#                          ... [subtile4-row16] [subtile4-row16]
def interleave_subtiles(unpacked_tile_data):
    """Row interleaves the 4 8x8 subtiles in a 16x16 tile.

    Returns bytes().
    """
    tile_fmt = Struct(64 * 'c')
    tile_iter = tile_fmt.iter_unpack(unpacked_tile_data)

    subtiles = [b''.join(subtile) for subtile in tile_iter]

    top = _interleave(subtiles[0], subtiles[2])
    bottom = _interleave(subtiles[1], subtiles[3])

    interleaved = [*top, *bottom]
    return b''.join(interleaved)

def _interleave(subtile1, subtile2):
    """Interleaves two 8x8 tiles like
    [subtile1-row1] [subtile2-row1] ...
    [subtile1-row16] [subtile2-row16]

    Returns bytes()
    """
    interleaved = []
    interleave_fmt = Struct(8 * 'c')

    left_iter = interleave_fmt.iter_unpack(subtile1)
    right_iter = interleave_fmt.iter_unpack(subtile2)

    for i in left_iter:
        right_next = next(right_iter)
        interleaved.extend([*i, *right_next])

    return interleaved

