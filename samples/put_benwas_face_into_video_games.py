#from struct import iter_unpack
import os
import sys
import mmap
from PIL import Image
from src import tile_printer, Sprite, Tile, image_handler, helper

#Change as necessary
GFX_FILE = "inputs/refactor/vm3_combined"
GFX_F = open(GFX_FILE, 'r+b')
GFX_MM = mmap.mmap(GFX_F.fileno(), 0)
FRAMES_FOLDER = "inputs/smol_json/"
OUTPUT_FOLDER = "outputs/cosprites3/"

def do_it(gfx_file, tile_file):
    dicts = helper.fromlua(tile_file)
    sprites = [Sprite.fromdict(dict_) for dict_ in dicts]

    with open(gfx_file, 'r') as f:
        for i, sprite in enumerate(sprites):
            tiles2d = tile_printer.make_tiles(gfx_file, sprite.addrs2d())
            sprites[i].tiles = helper.flatten_list(tiles2d)

    sorted_sprites = sorted(sprites,
                            key=lambda sprite: (sprite.location[1], sprite.location[0]))

    return sorted_sprites

def frames_to_png(gfx_file, frames_folder, output_folder):
    for filename in os.listdir(frames_folder):

        sprites = helper.fromlua(frames_folder + filename)

        for i, sprite in enumerate(sprites):
            tiles2d = tile_printer.make_tiles_mmap(GFX_MM, sprite.addrs2d())
            sprites[i].tiles = helper.flatten_list(tiles2d)

        put_sprites(sprites, output_folder + filename[:-4])

def print_sprites(sprites, path):
    """Turns individual sprites into .png files"""
    for i, v in enumerate(sprites):
        v.topng(path + v.tiles[0].address)

def write_sprites(sprite, image):
    tiles = image_handler.to_tiles(image, sprite.addrs2d(), sprite.palette)
    sprite.tiles = tiles
    sprite.topng("outputs/sprites/0x1abaa_test")

def stitch_sprites(sprites, output):
    tiles = []
    for sprite in sprites:
        tiles.append([sprite.toarray()])

    concat = tile_printer.concat_arrays(tiles)
    image = Image.fromarray(concat, 'RGB')
    image.save(output + ".png")

def put_sprites(sprites, output):
    """Takes a list of sprites and creates a .png image.
    Sprites are placed in the image at the x,y location they would occupy on the cps2.
    """
    canvas = Image.new('RGB', (400, 400))
    for sprite in sprites:
        im = Image.fromarray(sprite.toarray(), 'RGB')
        canvas.paste(im, sprite.location)
    canvas.save(output + ".png")

if __name__ == "__main__":
    frames_to_png(GFX_FILE, FRAMES_FOLDER, OUTPUT_FOLDER)
    #stitch_sprites(sprites, "outputs/temp")
    #print_sprites(sprites, "outputs/sprites/")
    #put_sprites(sprites,"outputs/put_test")
    #write_sprites(sprites[10], "outputs/sprites/0x1abaa.png")


