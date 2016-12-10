from gfx_file_handler import interleave_files, deinterleave_files

if __name__ == "__main__":
    #GFX_DATA = interleave_files("inputs/gfx_original")
    #for k, v in GFX_DATA.items():
    #    with open('outputs/refactor/roms/' + k, 'wb') as f:
    #        f.write(v)

    GFX_DATA = deinterleave_files("inputs/refactor")
    for k, v in GFX_DATA.items():
        with open('outputs/refactor/roms/' + k + 'm', 'wb') as f:
            f.write(v)
    