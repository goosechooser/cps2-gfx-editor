#from struct import iter_unpack
from PIL import Image
from src import ColorTile, tile_printer

def argb_to_rgb(color):
    return bytes.fromhex(color[1] * 2 + color[2] * 2 + color[3] * 2)
    #return color[1] * 2 + color[2] * 2 + color[3] * 2

def format_line_read(line):
    strip_line = line.lstrip('{')
    strip_line = strip_line.rstrip(' }\n')
    properties = strip_line.split(", ")
    line_properties = dict()
    for prop in properties:
        stripped = prop.split(" = ")
        line_properties[stripped[0].lstrip(' ')] = stripped[1]

    del line_properties['pal_number']
    return line_properties

def read_tile_file(file_name):
    tile_dicts = []

    with open(file_name, 'r') as f:
        for line in f:
            formatted = format_line_read(line)
            tile_dicts.append(formatted)

    for td in tile_dicts:
        tile_colors = []
        for color in td['palette'].split(" "):
            tile_colors.append(argb_to_rgb(color))
        td['palette'] = tile_colors

    return tile_dicts

def list_to_2D_list(list_1d, row_length):
    list_2d = []
    for i in range(row_length):
        offset = row_length * i
        list_2d.append(list_1d[offset:offset + row_length])

    return list_2d

def make_color_tiles(gfx_file, tile_numbers):
    dmitri_tiles = tile_printer.make_tiles(gfx_file, tile_numbers)
    dmitri_array = tile_printer.process_tile_order(dmitri_tiles)
    dmitri_array = tile_printer.concat_arrays(dmitri_array)

    image = Image.fromarray(dmitri_array, 'RGB')
    image.save("bless.bmp")

def invert_value(value):
    return bytes(abs(value - 16))

def do_it():
    gfx_file = "inputs/refactor/vm3.13.15.17.19.final"
    tile_dicts = read_tile_file("inputs/tile_info_new.txt")
    tile_numbers = [td['tile_number'] for td in tile_dicts]


    tiles = tile_printer.make_tiles(gfx_file, tile_numbers)

    #is this the new make_color_tiles()?
    color_tiles = []
    for i, tile in enumerate(tiles):
        t_d = tile_dicts[i]
        palette = t_d['palette']
        location = (int(t_d['x']), int(t_d['y']))
        size = (int(t_d['width']), int(t_d['height']))
        color_tile = ColorTile.ColorTile(tile.address, tile.data, palette, location, size)
        color_tiles.append(color_tile)

    sorted_tiles = sorted(color_tiles,
                          key=lambda tile: (tile.location[0], tile.location[1]))

    sorted_tiles[0].tobmp("help")
    sorted_tiles = list_to_2D_list(sorted_tiles[:25], 5)

    
    dmitri_array = tile_printer.process_tile_order(sorted_tiles)
    dmitri_array = tile_printer.concat_arrays(dmitri_array)

    image = Image.fromarray(dmitri_array, 'RGB')
    image.save("bless.bmp")

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
