import struct
from PIL import Image
import numpy as np
from src import Tile, helper

#Responsible for handling images.

def to_tiles(image, addresses, palette=None):
    """Converts an image into a list of tiles.

    Returns a list.
    """
    image_array = _read_img(image, palette)
    tiles_array = _split_array(image_array)

    addr = helper.flatten_list(addresses)

    filtered = [zipped for zipped in zip(addr, tiles_array) if zipped[0] != 'BLANK']

    tiles = []
    for tile in filtered:
        data = []
        data = _to_tile(tile[1])
        tile_ = Tile.Tile(tile[0], bytes(data), 16, packed=False)
        tiles.append(tile_.deinterleave_subtiles())

    return tiles

def _read_img(img, palette=None):
    im = Image.open(img)
    if palette:
        pd = _pal_to_dict(palette)
        cond = [_strip_palette(pix, pd) for pix in _condense(im)]

        cond2d = []
        for i in range(im.height):
            offset = im.width * i
            cond2d.append(cond[offset:offset + im.width])

        return np.asarray(cond2d, dtype='>H')

    return np.asarray(im, dtype='>H')

def _condense(img):
    """PNG image is returned as 3 bands representing RGB on each plane.
    Flattens into 1 plane array with each (R,G,B) value represented as RGB.

    """
    im = [band.tobytes() for band in img.split()]
    band_fmt = 'c'
    band_iter = [struct.iter_unpack(band_fmt, split_im) for split_im in im]
    comb = []

    for val in band_iter[0]:
        val_2 = next(band_iter[1])
        val_3 = next(band_iter[2])
        comb.append(b''.join([*val, *val_2, *val_3]))

    return comb

def _strip_palette(pixel, pal_dict):
    return pal_dict[pixel]

def _pal_to_dict(palette):
    pd = {}
    for i, v in enumerate(palette):
        pd[v] = i
    return pd

#Splits image into 16x16 tiles
def _split_array(image):
    """Splits an image into 16x16 sized tiles.

    Returns a list of arrays.
    """

    tiles = []
    dims = image.shape
    split_image = np.vsplit(image, int(dims[0]/16))
    for tile in split_image:
        tiles.extend(np.hsplit(tile, int(dims[1]/16)))
    return tiles

#Currently for 16x16 tiles only
def _to_tile(array_):
    rows = []
    for row in array_.tolist():
        rows.extend(row)
    return rows

