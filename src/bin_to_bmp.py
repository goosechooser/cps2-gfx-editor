from random import shuffle
from Tile import Tile
from tile_printer import process_tile_order, tile_to_bmp, make_tiles
from tile_writer import image_to_tiles, flatten_list, write_tiles_to_gfx
#need some kind of reader? something to handle data input - FileHandler
#need something to build a single 8x8 and 16x16 tile - Tile
#need something to assemble 16x16 tiles into a larger thing -
#need to print out tiles
def test(path, addr):
    read_data = 0
    with open(path, 'rb') as f:
        f.seek(int(addr, 16))
        read_data = f.read(128)
    tile = Tile(addr, read_data, 16)
    tile_to_bmp(tile, "outputs/bin_to_bmp/struct_test")

def test_writing():
    addrs = [['blank', '2F810', '2F811', '2F812', '2F813', '2F814'],
             ['blank', '2F820', '2F821', '2F822', '2F823', '2F824'],
             ['2F7FF', '2F830', '2F831', '2F832', '2F833', '2F834'],
             ['2F80F', '2F840', '2F841', '2F842', '2F843', '2F844'],
             ['2F815', '2F816', '2F817', '2F818', '2F819', 'blank']]
    #print(sorted(flatten_list(addrs)))

    tiles = image_to_tiles("inputs/tiles_to_write/temp_ass_edit.bmp", addrs)
    write_tiles_to_gfx(tiles, "inputs/refactor/vm3.14.16.18.20.final")

def generate_addresses():
    addrs = [hex(int(addr/128)) for addr in range(24903808, 24933504, 128)]
    tiles = make_tiles('inputs/tiles_to_write/vm3_14_16_18_20_final', addrs, 16)
    shuffle(addrs)

    for pair in zip(tiles, addrs):
        print('tile addr: ' + pair[0].address + ' shuffled addr ' + pair[1])
        pair[0].address = pair[1]
        print('tile addr: ' + pair[0].address + ' shuffled addr ' + pair[1])

    write_tiles_to_gfx(tiles, "inputs/refactor/vm3.14.16.18.20.final")

def main():
    generate_addresses()
    #test_writing()
    #test("inputs/tiles_to_write/vm3_14_16_18_20_final_edited_test", "0000200")
    #process_tile_order("inputs/tiles_to_write/vm3_14_16_18_20_final", addrs, 16)
    #image_to_tiles("inputs/tiles_to_write/temp_ass_edit.bmp", addrs)
    #writer = Cps2TileWriter()
    #img = writer.read_image("inputs/tiles_to_write/temp_ass_edit.bmp")
    #writer.write_to_gfx(img, "inputs/tiles_to_write/vm3_14_16_18_20_final", addrs, '16')

if __name__ == "__main__":
    main()
