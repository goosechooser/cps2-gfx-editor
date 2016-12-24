#from struct import iter_unpack
from PIL import Image
import jsonpickle
from src import tile_printer, Sprite, Tile, image_handler, helper

GFX_FILE = "inputs/refactor/vm3.13.15.17.19.final"
TILE_FILE = "inputs/tile_info_json.txt"

def do_it(gfx_file, tile_file):
    dicts = fromlua(tile_file)
    sprites = [Sprite.fromdict(dict_) for dict_ in dicts]

    with open(gfx_file, 'r') as f:
        for i, sprite in enumerate(sprites):
            tiles2d = tile_printer.make_tiles(gfx_file, sprite.addrs2d())
            sprites[i].tiles = helper.flatten_list(tiles2d)

    sorted_sprites = sorted(sprites,
                            key=lambda sprite: (sprite.location[1], sprite.location[0]))

    return sorted_sprites

def fromlua(lua):
    with open(lua, 'r') as f:
        return [jsonpickle.decode(line) for line in f]

def print_sprites(sprites, path):
    print("printing sprites")
    for i, v in enumerate(sprites):
        v.topng(path + v.tiles[0].address)

    print("done printing")

def write_sprites_test(sprite, image):
    print(image_handler.tobytes(image, sprite.palette))
    return


if __name__ == "__main__":
    sprites = do_it(GFX_FILE, TILE_FILE)
    print_sprites(sprites, "outputs/sprites/")
    write_sprites_test(sprites[10], "outputs/sprites/0x1abaa.png")
    

