import numpy as np
from PIL import Image

class Cps2TileWriter:

    def read_image(self, image):
        img = Image.open(image)
        return np.asarray(img, dtype='>H')

    #Splits image into 16x16 tiles
    def _split_to_tile16(self, image):
        tiles = []
        split_image = np.vsplit(image, 5)
        for tile in split_image:
            tiles.append(np.hsplit(tile, 6))
        return tiles

    def  _convert_row_of_pixels_to_4bpp(self, row_of_pixels):
        pixels = row_of_pixels.tolist()[0]
        bitplanes = [int(b'00000000')] * 4
        mask = int(b'00000001')

        for pixel in pixels:
            for i, plane in enumerate(bitplanes):
                bitplanes[i] = (plane << 1) | (pixel & mask)
                pixel = pixel >> 1
        #print(bitplanes)
        return bitplanes

    #for each row of pixels: convert each pixel into its bitplane equivalent
    #producing 4 bitplanes of length 8
    def _tile_to_bitplanes(self, tile):
        rows = np.vsplit(tile, 8)
        bitplanes = []
        for row in rows:
            bitplanes.extend(self._convert_row_of_pixels_to_4bpp(row))

        return bitplanes

    def write_tile8(self, tile):
        bitplane_values = []
        #need to flip array
        flipped_tile = np.fliplr(tile)
        bitplane_values = self._tile_to_bitplanes(flipped_tile)

        #need to flip bits
        reversed_bits = [int('{:08b}'.format(n)[::-1], 2) for n in bitplane_values]
        bitplane_bytes = [value.to_bytes(1, byteorder='big') for value in reversed_bits]

        poppin = []
        
        for i in range(8):
            offset = 4 * i
            temp = bitplane_bytes[offset:offset+4]
            temp.reverse()
            poppin.extend(temp)
        
        #push it all back on in correct order ie push plane3, plane2, plane1 etc
        #write tile to given address
        return poppin

     #Turn 1 16x16 tile into 4 8x8 tiles (and also row interleave them ig)
    #should reconsider this function name
    def _deinterleave_tile(self, tile):
        temp_tiles = []
        split_tiles = np.vsplit(tile, 2)

        for half in split_tiles:
            temp_tiles.extend(np.hsplit(half, 2))

        return [temp_tiles[0], temp_tiles[2], temp_tiles[1], temp_tiles[3]]

    def write_tile16(self, tile):
        deinterleaved = self._deinterleave_tile(tile)
        tile_bytes = []
        for tile8 in deinterleaved:
            tile_bytes.extend(self.write_tile8(tile8))
        return tile_bytes

    def write_tile(self, tile, dim):
        if dim == '8':
            return self.write_tile8(tile)
        if dim == '16':
            return self.write_tile16(tile)

    #converts the addresses mame displays when you press 'F4' to something else
    def convert_mame_addr(self, mame_addr, tile_size):
        tile_bytes = 0
        addr = int(mame_addr, 16)
        if tile_size is '8':
            tile_bytes = 32
        if tile_size is '16':
            tile_bytes = 128

        converted_addr = addr * tile_bytes
        memory_bank_size = int('0x1000000', 16)

        #currently the 8 eproms are split into 2 banks
        if converted_addr > memory_bank_size:
            converted_addr -= memory_bank_size

        return converted_addr
    
    def unroll_addresses(self, addresses):
        unroll = []
        [unroll.extend(row) for row in addresses]
        return unroll

    #write image to graphics file
    def write_to_gfx(self, image, gfx_file, addresses, tile_dim):
        tiles = self.unroll_addresses(self._split_to_tile16(image))
        addrs = self.unroll_addresses(addresses)
        to_write = [[]]
        for i, addr in enumerate(addrs):
                if addr != 'blank':
                    tile_bytes = self.write_tile(tiles[i], tile_dim)
                    converted_addr = self.convert_mame_addr(addrs[i], tile_dim)
        with open(gfx_file, 'wb+') as f:
            end = f.read()
            f.write(end)
            for i, addr in enumerate(addrs):
                if addr != 'blank':
                    tile_bytes = self.write_tile(tiles[i], tile_dim)
                    converted_addr = self.convert_mame_addr(addrs[i], tile_dim)
                    f.seek(converted_addr)
                    for tile_byte in tile_bytes:
                        f.write(tile_byte)
            


