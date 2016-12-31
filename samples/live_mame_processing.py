import subprocess
import os
import asyncio
from queue import Queue, Empty
from threading import Thread
import json
import jsonpickle
from src import Sprite

#This launches MAME in a subprocess and pipes back the raw data for processing
#Lets MAME run at like 96% speed instead of 10% or w/e it was doing before

#Look into setting up logger u shit!!
GFX_FILE = "inputs/refactor/vm3.13.15.17.19.final"
TILE_FILE = "inputs/op_info_json.txt"

jsonpickle.set_encoder_options('simplejson', ident=4)
BASE_PATH = os.getcwd()
Q = Queue()

def enqueue_output(out):
    print("thread spawned")
    for line in iter(out.readline, ''):
        Q.put(line)

    out.close()

def mask_sprite_data(sprite_data):
    byte_data = [int(data, 16) for data in sprite_data]

    dict_ = {}
    dict_['x'] = byte_data[0] & 0x03FF
    dict_['y'] = byte_data[1] & 0x03FF
    dict_['height'] = ((byte_data[3] & 0xF000) >> 12) + 1
    dict_['width'] = ((byte_data[3] & 0x0F00) >> 8) + 1
    #hex: {0:x};  oct: {0:o};  bin: {0:b}".format(42)
    top_half = "{0:#x}".format((byte_data[1] & 0x6000) >> 13)
    bottom_half = "{0:x}".format(byte_data[2])
    dict_['tile_number'] = top_half + bottom_half
    dict_['pal_number'] = "{0:x}".format(byte_data[3] & 0x001F)

    return dict_

async def consumer():
    try:
        line = Q.get_nowait()
    except Empty:
        stri = 'no output yet'
    else:
        return line

async def decode_json():
    result = await consumer()
    if result:
        try:
            line = jsonpickle.decode(result)
        except json.JSONDecodeError:
            #stri = "not json"
            print("not json: " + result)
        else:
            #do processing here?
            return line

async def process_frame():
    frame = await decode_json()
    if frame:
        sprites = [sprite for sprite in frame['sprites'].values()]
        palettes = frame['palette']
        masked = [mask_sprite_data(sprite) for sprite in sprites]

        for i, v in enumerate(masked):
            pal = v['pal_number']
            masked[i]['palette'] = palettes[pal]
            del masked[i]['pal_number']
        sprites = [Sprite.fromdict(dict_) for dict_ in masked]
        return (frame['frame_number'], sprites)

async def main(p, folder):
    save_ = BASE_PATH + folder
    while p.poll() is None:
        result = await process_frame()
        if result:
            file_name = 'frame_' + str(result[0]) + ".txt"
            with open(save_ + file_name, 'w') as f:
                f.write(jsonpickle.encode(result[1]))

def coroutine_temp(output_folder):
    os.chdir("D:\\Desktop\\mame2\\")
    cmd = ["mame", "vsav", "-autoboot_script", "scrape_sprite_pal_data.lua", "-window"]

    p = subprocess.Popen(cmd, bufsize=1, universal_newlines=True, stdout=subprocess.PIPE)

    t = Thread(target=enqueue_output, args=(p.stdout,), daemon=True)
    t.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(p, output_folder))
    loop.close()

if __name__ == "__main__":
    output_folder = "\\outputs\\processed_vsav_json_files\\"
    #pp_folder = "\\outputs\\pretty_vsav_json_files\\"
    coroutine_temp(output_folder)