from Cps2GraphicsFileHandler import Cps2GraphicsFileHandler
import subprocess
import os

def run_diff(file1, file2, save_diff_path):
    with open("diff", 'ab') as f:
        subprocess.run(["radiff2", file1, file2], stdout=f)
        if not os.stat(save_diff_path).st_size:
            print(file2 + " - no diff")
        else:
            print(file2 + " - see diff file")

if __name__ == "__main__":
    handler = Cps2GraphicsFileHandler()
    handler.gfx_to_binary("inputs/gfx_original", "outputs/gfx_test/")
    #handler.binary_to_gfx("inputs/tiles_to_write/", "outputs/gfx_test/roms/")
    