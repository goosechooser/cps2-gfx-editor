from src import tile_writer, tile_printer
from PIL import Image

ADDRS = [['blank', '2F810', '2F811', '2F812', '2F813', '2F814'],
         ['blank', '2F820', '2F821', '2F822', '2F823', '2F824'],
         ['2F7FF', '2F830', '2F831', '2F832', '2F833', '2F834'],
         ['2F80F', '2F840', '2F841', '2F842', '2F843', '2F844'],
         ['2F815', '2F816', '2F817', '2F818', '2F819', 'blank']]
GFX = "inputs/tiles_to_write/vm3_14_16_18_20_final"
TILES = tile_printer.make_tiles(GFX, ADDRS, 16)

def test_image_to_tiles(tmpdir):
    pic_tiles = tile_printer.process_tile_order(TILES)
    pic_array = tile_printer.concat_arrays(pic_tiles)
    image = Image.fromarray(pic_array, 'P')
    fn = tmpdir.mkdir('data').join('temp.bmp')
    image.save(str(fn))

    test_tiles = tile_writer.image_to_tiles(str(fn), ADDRS)
    original_tiles = tile_writer.flatten_list(TILES)
    filtered_original = [tile for tile in original_tiles if tile.address != 'blank']

    for tile_pair in zip(filtered_original, test_tiles):
        assert tile_pair[0].data == tile_pair[1].data



