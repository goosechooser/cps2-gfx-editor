from struct import unpack, iter_unpack
from PIL import Image
import numpy as np
from Tile import Tile, pack_data

# bmp -> array -> tile ig
def image_to_tiles(image):
    image_array = _read_image(image)
    tiles = _split_array(image_array)
    tiles = [_deinterleave_tile(tile) for row in tiles for tile in row]
    [print(tile.shape) for tile in tiles]

def _read_image(image):
    """Opens .bmp image. 

    Returns an array.
    """
    img = Image.open(image)
    return np.asarray(img, dtype='>H')

#Splits image into 16x16 tiles
def _split_array(image):
    tiles = []
    dims = image.shape

    split_image = np.vsplit(image, int(dims[1]/16))
    for tile in split_image:
        tiles.append(np.hsplit(tile, int(dims[0]/16)))
    return tiles

def _deinterleave_tile(tile):
    temp_tiles = []
    split_tiles = np.vsplit(tile, 2)

    for half in split_tiles:
        temp_tiles.extend(np.hsplit(half, 2))

    return [temp_tiles[0], temp_tiles[2], temp_tiles[1], temp_tiles[3]]

#def  _convert_row_of_pixels_to_4bpp(row_of_pixels):
#    pixels = row_of_pixels.tolist()[0]
#    bitplanes = [int(b'00000000')] * 4
#    mask = int(b'00000001')

#    for pixel in pixels:
#        for i, plane in enumerate(bitplanes):
#            bitplanes[i] = (plane << 1) | (pixel & mask)
#            pixel = pixel >> 1
    #print(bitplanes)
#    return bitplanes

#for each row of pixels: convert each pixel into its bitplane equivalent
#producing 4 bitplanes of length 8
#def _tile_to_bitplanes(tile):
#    rows = np.vsplit(tile, 8)
#    bitplanes = []
#    for row in rows:
#        bitplanes.extend(_convert_row_of_pixels_to_4bpp(row))

#    return bitplanes

#def write_tile8(tile):
#    bitplane_values = []
#    #need to flip array
#    flipped_tile = np.fliplr(tile)
#    bitplane_values = _tile_to_bitplanes(flipped_tile)

    #need to flip bits
#    reversed_bits = [int('{:08b}'.format(n)[::-1], 2) for n in bitplane_values]
#    bitplane_bytes = [value.to_bytes(1, byteorder='big') for value in reversed_bits]

#    poppin = []

    #this part would be _pack_bitplanes()
#    for i in range(8):
#        offset = 4 * i
#        temp = bitplane_bytes[offset:offset+4]
#        temp.reverse()
#        poppin.extend(temp)

    #push it all back on in correct order ie push plane3, plane2, plane1 etc
    #write tile to given address
 #   return poppin

#Turn 1 16x16 tile into 4 8x8 tiles (and also row interleave them ig)
#should reconsider this function name


def write_tile16(tile):
    deinterleaved = _deinterleave_tile(tile)
    tile_bytes = []
    for tile8 in deinterleaved:
        tile_bytes.extend(write_tile8(tile8))
    return tile_bytes

def write_tile(tile, dim):
    if dim == '8':
        return write_tile8(tile)
    if dim == '16':
        return write_tile16(tile)

#converts the addresses mame displays when you press 'F4' to something else
def convert_mame_addr(mame_addr, tile_size):
    tile_bytes = 0
    addr = int(mame_addr, 16)
    if tile_size is '8':
        tile_bytes = 32
    if tile_size is '16':
        tile_bytes = 128

    converted_addr = addr * tile_bytes
    memory_bank_size = int('0x1000000', 16)

    #currently the 8 eproms are split into 2 banks
    #wouldnt need this if you combined the 2 bank files into 1 file
    if converted_addr > memory_bank_size:
        converted_addr -= memory_bank_size

    return converted_addr

def unroll_addresses(addresses):
    unroll = []
    return [unroll.extend(row) for row in addresses]

#write image to graphics file
def write_to_gfx(image, gfx_file, addresses, tile_dim):
    tiles = unroll_addresses(_split_to_tile16(image))
    addrs = unroll_addresses(addresses)

    for i, addr in enumerate(addrs):
        if addr != 'blank':
            tile_bytes = write_tile(tiles[i], tile_dim)
            converted_addr = convert_mame_addr(addrs[i], tile_dim)

    #should read file and store results in a buffer with first 'with open'
    #then write pre-edit, edit, and post-edit data with a 2nd 'with open'
    #look into struct, could pack 16x16 tiles as a struct
    with open(gfx_file, 'wb+') as f:
        end = f.read()
        f.write(end)
        for i, addr in enumerate(addrs):
            if addr != 'blank':
                tile_bytes = write_tile(tiles[i], tile_dim)
                converted_addr = convert_mame_addr(addrs[i], tile_dim)
                f.seek(converted_addr)
                for tile_byte in tile_bytes:
                    f.write(tile_byte)
