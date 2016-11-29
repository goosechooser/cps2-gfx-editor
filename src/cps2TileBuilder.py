import numpy as np

class Cps2TileBuilder:
    #put each bitplane in a seperate list
    def _deinterleave_bitplanes(self, chunk):
        planes = [[], [], [], []]
        for i in range(0, 8):
            planes[0].append(chunk.pop())
            planes[1].append(chunk.pop())
            planes[2].append(chunk.pop())
            planes[3].append(chunk.pop())
        return planes

    def _make_row_of_pixels(self, bitplane_rows):
        mask = int(b'00000001')
        bitplane_values = bitplane_rows
        row_of_pixels = []
        for loc in range(0, 8):
            masked = [value & mask for value in bitplane_values]
            bitplane_values = [value >> 1 for value in bitplane_values]
            bit_plane_val = masked[0] << 3 | masked[1] << 2 | masked[2] << 1 | masked[3]
            row_of_pixels.append(bit_plane_val.to_bytes(1, byteorder='big'))

        return row_of_pixels

    #slices off the LSB and arranges data as [BP1 BP2 BP3 BP4], lsr byte and repeat
    def _bitplanes_to_tile(self, planes):
        pixels = []
        for i in range(0, 8):
            temp_val = [planes[0][i], planes[1][i], planes[2][i], planes[3][i]]
            row = self._make_row_of_pixels(temp_val)
            pixels.append(row)

        return pixels
    def _interleave_tiles(self, subtiles):
        tile_halfs = []
        tile_halfs.append(np.concatenate([subtiles[0], subtiles[2]], axis=1))
        tile_halfs.append(np.concatenate([subtiles[1], subtiles[3]], axis=1))
        return np.concatenate(tile_halfs, axis=0)

    def make_blank_tile8(self):
        zero = int('0x10', 16)
        zero = zero.to_bytes(1, byteorder='big')
        row = row = [zero] * 8
        tile = [row] * 8

        return(np.array(tile))

    def make_tile8(self, chunk):
        mask = int('ff', 16)
        tile_chunk = chunk
        data = int.from_bytes(tile_chunk, byteorder='big')

        #split our 32 byte chunk into 1 byte pieces
        chunk_bytes = []
        for i in range(0, 32):
            chunk_bytes.append(data & mask)
            data = data >> 8

        planes = self._deinterleave_bitplanes(chunk_bytes)
        pixels = self._bitplanes_to_tile(planes)
        pixels = np.array(pixels)
        pixels = np.fliplr(pixels)

        return pixels

    def make_blank_tile16(self):
        subtiles = [self.make_blank_tile8()] * 4
        #subtiles.append(self.make_blank_tile8())
        #subtiles.append(self.make_blank_tile8())
        #subtiles.append(self.make_blank_tile8())
        #subtiles.append(self.make_blank_tile8())

        return self._interleave_tiles(subtiles)

    def make_tile16(self, chunks):
        subtiles = [self.make_tile8(chunk) for chunk in chunks]
        return self._interleave_tiles(subtiles)

    def make_tile(self, chunks, tile_dim):
        dim = tile_dim
        if dim == '8':
            return self.make_tile8(chunks)
        if dim == '16':
            return self.make_tile16(chunks)
