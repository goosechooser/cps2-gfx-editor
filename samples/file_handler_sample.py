from src import gfx_file_handler

if __name__ == "__main__":
    input_file = 'YOUR FILE HERE'
    gfx_file_handler.interleave_cps2(input_file)

    # This is being changed
    # GFX_DATA = gfx_file_handler.deinterleave_files("inputs/roms")
    # for k, v in GFX_DATA.items():
    #     with open('outputs/roms/' + k + 'm', 'wb') as f:
    #         f.write(v)
    