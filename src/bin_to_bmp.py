from PIL import Image
from cps2TileBuilder import cps2TileBuilder

#need some kind of reader? something to handle data input
#need something to build a single 8x8 and 16x16 tile
#need something to assemble 16x16 tiles into a larger thing
#need to print out tiles

def test_make_tile8(chunk, number):
    tile_builder = cps2TileBuilder()
    with open(chunk, 'rb') as f:
        f.seek(224)
        for i in range(0, number):
            print("tile " + str(i) + " at " + str(f.tell()))
            plane = tile_builder.make_tile8(f.read(32))
            image = Image.fromarray(plane, 'P')
            image.save("bin_to_bmp/tile_test/tile_" + str(i) + ".bmp")

def test_make_tile16(gfx_file, mem_addresses):
    tile_builder = cps2TileBuilder()
    with open(gfx_file, 'rb') as f:
        for mame_addr in mem_addresses:
            addr = int(mame_addr, 16)
            f.seek(addr)
            before_addr = f.tell()
            chunks = [f.read(32), f.read(32), f.read(32), f.read(32)]
            file_name = "tile_" + hex(int(before_addr))
            plane = tile_builder.make_tile16(chunks)
            image = Image.fromarray(plane, 'P')
            image.save("bin_to_bmp/tiles/" + file_name + ".bmp")

def main():
    test_make_tile16("bin_to_bmp/vm3_14_16_18_20_final", ['007C2000'])

if __name__ == "__main__":
    main()
