from struct import Struct, iter_unpack
from PIL import Image
import numpy as np

class Tile(object):
    def __init__(self, addr, data, dimensions=16, packed=True):
        self._tile_addr = addr
        if packed:
            self._tile_data = data
        else:
            self._tile_data = self.pack(data)
        self._tile_dimensions = dimensions
        self._packed = packed

    def __repr__(self):
        return "Tile: " + str(self._tile_addr)

    @property
    def address(self):
        """Get the address in memory where the tile is located."""
        return self._tile_addr

    @address.setter
    def address(self, value):
        self._tile_addr = value

    @property
    def data(self):
        """Get the bitplane packed data."""
        return self._tile_data

    @property
    def dimensions(self):
        """Get the pixel value data."""
        return self._tile_dimensions

    @property
    def packed(self):
        """Get the pack state of the tile."""
        return self._packed

#Functions to manipulate tile objects below ig
#Doesn't check if a tile is 8x8 or 16x16, should it?
#Should this return raw data or should it return a Tile obj?
    def unpack(self):
        """Unpacks a 4bpp planar tile.

        Returns a byte() of pixel values.
        """
        tile_fmt = Struct(32 * 'c')
        tile_iter = tile_fmt.iter_unpack(self._tile_data)

        tiles = [self._bitplanes_to_tile(b''.join(tile)) for tile in tile_iter]
        return b''.join(tiles)

    def _bitplanes_to_tile(self, data):
        bitplanes = self._unpack_bitplanes(data)

        pixels = []
        for i in range(0, 8):
            temp_val = [bitplanes[0][i], bitplanes[1][i],
                        bitplanes[2][i], bitplanes[3][i]]
            row = self._make_row_of_pixels(temp_val)

            pixels.append(row)

        return b''.join(pixels)

    def _unpack_bitplanes(self, data):
        """The values that make up a row of pixels are organized like:
        [bp1-row1] [bp2-row1] [bp3-row1] [bp4-row1]...
        [bp1-row8] [bp2-row8] [bp3-row8] [bp4-row8]

        Returns a list of lists containing bitplane values (bytes).
        """
        planes = [[], [], [], []]
        data_iter = Struct('c').iter_unpack(data)

        for bp in data_iter:
            planes[0].extend(*bp)
            planes[1].extend(*next(data_iter))
            planes[2].extend(*next(data_iter))
            planes[3].extend(*next(data_iter))

        return planes

    def _make_row_of_pixels(self, bitplane_rows):
        """Converts the 4 bytes of bitplanes 1-4 for a given row into a row of pixel values

        Returns bytes()
        """
        mask = int(b'00000001')
        bitplane_values = bitplane_rows
        row_of_pixels = []
        for loc in range(0, 8):
            masked = [value & mask for value in bitplane_values]
            bitplane_values = [value >> 1 for value in bitplane_values]
            bit_plane_val = masked[3] << 3 | masked[2] << 2 | masked[1] << 1 | masked[0]
            row_of_pixels.append(bit_plane_val.to_bytes(1, byteorder='big'))

        row_of_pixels.reverse()

        return b''.join(row_of_pixels)

    def pack(self, data):
        """Converts pixel values into 4bpp and packs it for Tile use.
        Returns bytes()
        """

        tile_fmt = Struct(32 * 'c')
        tile_iter = tile_fmt.iter_unpack(data)

        bitplane_values = [self._tile_to_bitplanes(b''.join(tile)) for tile in tile_iter]
        return b''.join(bitplane_values)

    def _tile_to_bitplanes(self, data):
        bitplanes = []
        row_fmt = Struct(8 * 'c')
        row_iter = row_fmt.iter_unpack(data)

        bitplanes = [self._pixel_row_to_4bpp(row) for row in row_iter]

        return b''.join(bitplanes)

    def _pixel_row_to_4bpp(self, row):
        bitplanes = [0, 0, 0, 0]
        mask = int(b'00000001')
        row = [int.from_bytes(val, byteorder='big') for val in row]

        for pixel in row:
            for i, plane in enumerate(bitplanes):
                bitplanes[i] = (plane << 1) | (pixel & mask)
                pixel = pixel >> 1

        return bytearray(bitplanes)

    def toarray(self):
        """Uses 8x8 or 16x16 Tile data to create an array of the tile's data.

        Returns an array.
        """
        interleaved_tile = self.interleave_subtiles()

        tile_fmt = interleaved_tile.dimensions * 'c'
        tile_iter = iter_unpack(tile_fmt, interleaved_tile.unpack())
        tiles = [subtile for subtile in tile_iter]

        return np.array(tiles)

    def tobmp(self, path_to_save):
        """Creates a .bmp image from a single 8x8 or 16x16 tile."""
        image = Image.fromarray(self.toarray(), 'P')
        image.save(path_to_save + ".bmp")

#Would need to interleave like [subtile1-row1] [subtile3-row1]
#                          ... [subtile1-row16] [subtile3-row16]
#                              [subtile2-row1] [subtile4-row1]
#                          ... [subtile4-row16] [subtile4-row16]
    def interleave_subtiles(self):
        """Row interleaves the 4 8x8 subtiles in a 16x16 tile.

        Returns a new packed Tile.
        """
        tile_fmt = Struct(32 * 'c')
        tile_iter = tile_fmt.iter_unpack(self._tile_data)

        subtiles = [b''.join(subtile) for subtile in tile_iter]

        top = self._interleave(subtiles[0], subtiles[2])
        bottom = self._interleave(subtiles[1], subtiles[3])

        interleaved = [*top, *bottom]
        return Tile(self._tile_addr, b''.join(interleaved), self._tile_dimensions)

    def _interleave(self, subtile1, subtile2):
        """Interleaves two 8x8 tiles like
        [subtile1-row1] [subtile2-row1] ...
        [subtile1-row16] [subtile2-row16]

        Returns bytes()
        """
        interleaved = []
        interleave_fmt = Struct(4 * 'c')

        left_iter = interleave_fmt.iter_unpack(subtile1)
        right_iter = interleave_fmt.iter_unpack(subtile2)

        for i in left_iter:
            right_next = next(right_iter)
            interleaved.extend([*i, *right_next])

        return interleaved

    def deinterleave_subtiles(self):
        tile_fmt = Struct(64 * 'c')
        tile_iter = tile_fmt.iter_unpack(self._tile_data)

        subtiles = []
        for subtile in tile_iter:
            subtiles.extend(self._deinterleave(b''.join(subtile)))

        deinterleaved = [subtiles[0], subtiles[2], subtiles[1], subtiles[3]]
        return Tile(self._tile_addr, b''.join(deinterleaved), self._tile_dimensions)

    def _deinterleave(self, data):
        deinterleaved = [[], []]

        deinterleave_fmt = Struct(4 * 'c')
        deinterleave_iter = deinterleave_fmt.iter_unpack(data)

        for i in deinterleave_iter:
            deinterleaved[0].extend([*i])
            deinterleaved[1].extend([*next(deinterleave_iter)])

        return [b''.join(data) for data in deinterleaved]

class EmptyTile(Tile):

    def __init__(self, dimensions):
        super().__init__('BLANK', None, dimensions)

    def toarray(self):
        zero = int('0x20', 16).to_bytes(1, byteorder='big')
        row = [zero] * self._tile_dimensions
        tile = [row] * self._tile_dimensions

        return np.array(tile)
