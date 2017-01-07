import subprocess
import os
import asyncio
from queue import Queue, Empty
from threading import Thread
import json
import jsonpickle
from src import Sprite
from src import helper

#Sequential (read: original) version of 'concurrent_mame_processing' 
#This launches MAME in a subprocess and pipes back the raw data for processing
#Lets MAME run at like 96% speed instead of 10% or w/e it was doing before

#Change these as needed
GFX_FILE = "inputs/refactor/vm3.13.15.17.19.final"
TILE_FILE = "inputs/op_info_json.txt"
MAME_PATH = "D:\\Desktop\\mame174\\"
LUA_SCRIPT = "lua_scripts\\scrape_data_concurrent.lua"
SPRITE_OUTPUT_FOLDER = "\\inputs\\sample_json\\"

jsonpickle.set_encoder_options('simplejson', ident=4)
BASE_PATH = os.getcwd()
Q = Queue()

def enqueue_output(out):
    print("thread spawned")
    for line in iter(out.readline, ''):
        Q.put(line)

    out.close()

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
            print("not json: " + result)
        else:
            return line

async def process_frame():
    frame = await decode_json()
    if frame:
        sprites = [sprite for sprite in frame['sprites'].values()]
        palettes = frame['palette']
        masked = [helper.mask_sprite_data(sprite) for sprite in sprites]

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
            file_name = 'frame_' + str(result[0]) + '.txt'
            with open(save_ + file_name, 'w') as f:
                for res in result[1]:
                    f.write(jsonpickle.encode(res) + "\n")

    remaining = Q.qsize()
    print(str(remaining) + " frames left")

    for i in range(remaining):
        result = await process_frame()
        if result:
            print(str(Q.qsize()) + " left in the queue")
            file_name = 'frame_' + str(result[0]) + '.txt'
            with open(save_ + file_name, 'w') as f:
                for res in result[1]:
                    f.write(jsonpickle.encode(res) + "\n")

if __name__ == "__main__":
    coroutine_temp()
    os.chdir(MAME_PATH)
    cmd = ["mame64", "vsav", "-autoboot_script", LUA_SCRIPT, "-window", "-nomax"]

    p = subprocess.Popen(cmd, bufsize=1, universal_newlines=True, stdout=subprocess.PIPE)

    t = Thread(target=enqueue_output, args=(p.stdout,), daemon=True)
    t.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(p, SPRITE_OUTPUT_FOLDER))
    loop.close()
    