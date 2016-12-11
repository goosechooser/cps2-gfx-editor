from random import shuffle
from Tile import Tile
from tile_printer import process_tile_order, tile_to_bmp, make_tiles
from tile_writer import image_to_tiles, flatten_list, write_tiles_to_gfx

def print_single_tile(path, addr):
    read_data = 0
    with open(path, 'rb') as f:
        f.seek(int(addr, 16))
        read_data = f.read(128)
    tile = Tile(addr, read_data, 16)
    tile_to_bmp(tile, "outputs/bin_to_bmp/struct_test")

def print_dirty_beret_logo():
    addrs = [['blank', '2F810', '2F811', '2F812', '2F813', '2F814'],
             ['blank', '2F820', '2F821', '2F822', '2F823', '2F824'],
             ['2F7FF', '2F830', '2F831', '2F832', '2F833', '2F834'],
             ['2F80F', '2F840', '2F841', '2F842', '2F843', '2F844'],
             ['2F815', '2F816', '2F817', '2F818', '2F819', 'blank']]
    #print(sorted(flatten_list(addrs)))

    tiles = image_to_tiles("inputs/tiles_to_write/temp_ass_edit.bmp", addrs)
    write_tiles_to_gfx(tiles, "inputs/refactor/vm3.14.16.18.20.final")

def shuffle_dirty_beret_logo():
    addrs = [hex(int(addr/128)) for addr in range(24903808, 24933504, 128)]
    tiles = make_tiles('inputs/tiles_to_write/vm3_14_16_18_20_final', addrs)
    shuffle(addrs)

    for pair in zip(tiles, addrs):
        #print('tile addr: ' + pair[0].address + ' shuffled addr ' + pair[1])
        pair[0].address = pair[1]
        #print('tile addr: ' + pair[0].address + ' shuffled addr ' + pair[1])

    write_tiles_to_gfx(tiles, "inputs/refactor/vm3.14.16.18.20.final")

def shuffle_entire_gfx_file(gfx_file):
    addrs = [hex(int(addr/128)) for addr in range(0, 16694016, 128)]
    tiles = make_tiles(gfx_file, addrs)
    shuffle(addrs)

    for pair in zip(tiles, addrs):
        #print('tile addr: ' + pair[0].address + ' shuffled addr ' + pair[1])
        pair[0].address = pair[1]
        #print('tile addr: ' + pair[0].address + ' shuffled addr ' + pair[1])

    write_tiles_to_gfx(tiles, gfx_file, "inputs/roms/vm3.13.15.17.19.final")

def main():
    #shuffle_dirty_beret_logo()
    shuffle_entire_gfx_file("inputs/refactor/vm3.13.15.17.19.final")
    #print_single_tile("inputs/tiles_to_write/vm3_14_16_18_20_final_edited_test", "0000200")
    #print_dirty_beret_logo("inputs/tiles_to_write/vm3_14_16_18_20_final", addrs, 16)

if __name__ == "__main__":
    main()
