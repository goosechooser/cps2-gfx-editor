from src import gfx_file_handler

if __name__ == "__main__":
    #GFX_DATA = gfx_file_handler.interleave_files("inputs/gfx_original")
    #for k, v in GFX_DATA.items():
    #    with open('outputs/refactor/roms/' + k, 'wb') as f:
    #        f.write(v)

    GFX_DATA = gfx_file_handler.deinterleave_files("inputs/roms")
    for k, v in GFX_DATA.items():
        with open('outputs/roms/' + k + 'm', 'wb') as f:
            f.write(v)
    