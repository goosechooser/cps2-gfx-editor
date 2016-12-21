#from struct import iter_unpack
from PIL import Image
from src import tile_printer, Sprite, Tile

def list_to_2D_list(list_1d, row_length):
    list_2d = []
    for i in range(row_length):
        offset = row_length * i
        list_2d.append(list_1d[offset:offset + row_length])

    return list_2d

def print_color_picture(tiles, picture_name):
    color_array = tile_printer.process_tile_order(tiles)
    concat_array = tile_printer.concat_arrays(color_array)

    image = Image.fromarray(concat_array, 'RGB')
    image.save(picture_name + ".png")

def do_it():
    gfx_file = "inputs/refactor/vm3.13.15.17.19.final"
    tile_file = "inputs/tile_info.txt"

    sprites = []
    tile_factory = Tile.Factory(gfx_file)
    tile_factory.open()

    sprite_factory = Sprite.Factory(tile_file, tile_factory)
    sprite_factory.open()

    sprite = sprite_factory.new()
    while sprite is not 'EOF':
        sprites.append(sprite)
        sprite = sprite_factory.new()

    for sprite in sprites:
        print(sprite)

    print(len(sprites))
    #print(sprite.to2dlist())
    sprite_factory.close()
    tile_factory.close()
    #sprite_factory = Sprite.Factory(tile_file, Tile.Factory(gfx_file))

    #make_tile_group(gfx_file, tile_file)
    #color_tiles = make_color_tiles(gfx_file, tile_file)

    #sorted_tiles = sorted(color_tiles,
    #                      key=lambda tile: (tile.location[0], tile.location[1]))

    #print(len(sorted_tiles))
    #sorted_2d = list_to_2D_list(sorted_tiles[:70], 7)
    #print_color_picture(sorted_2d, "bless")

def put_benwa_into_video_game(benwa_path, gfx_file):
    benwaddrs = [['1B4E0', '1B4E1', '1B4E2'],
                 ['1B4F0', '1B4F1', '1B4F2']]

    #benwa_tiles = tile_printer.image_to_tiles(benwa_path, benwaddrs)
    #benwa_tiles = [[benwa_tiles[0], benwa_tiles[1], benwa_tiles[2]],
    #               [benwa_tiles[3], benwa_tiles[4], benwa_tiles[5]]]

    #benwa_tiles = process_tile_order(benwa_tiles)


    #benwa_tiles = concat_arrays(benwa_tiles)

    #for x in np.nditer(benwa_tiles, op_flags=['readwrite']):
    #    val = int.from_bytes(np.asscalar(x[...]), byteorder='big')
    #    if val == 1:
    #        x[...] = abs(val - 16).to_bytes(1, byteorder='big')

    #image = Image.fromarray(benwa_tiles, 'P')
    #image.save('help.bmp')

if __name__ == "__main__":
    do_it()

    #gfx_to_bmp(gfx_file, benwaddrs, "dmitri_face.bmp")

    #put_benwa_into_video_game("inputs/testwa.bmp", gfx_file)
    #tiles = image_to_tiles('help.bmp', benwaddrs)
    #write_tiles_to_gfx(tiles, gfx_file, "inputs/roms/vm3.13.15.17.19.final")
