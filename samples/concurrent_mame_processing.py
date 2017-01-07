import subprocess
import os
import sys
import asyncio
from threading import Thread
from multiprocessing import Pool, Queue
from queue import Empty
import logging
import json
import jsonpickle
from src import Sprite
from src import helper

GFX_FILE = "inputs/refactor/vm3.13.15.17.19.final"
TILE_FILE = "inputs/op_info_json.txt"

BASE_PATH = os.getcwd()
MAME_PATH = "D:\\Desktop\\mame174\\"

logging.basicConfig(
    level=logging.INFO,
    format='PID %(process)s %(name)8s: %(message)s',
    stream=sys.stderr,
)

def enqueue_output(out, q):
    log = logging.getLogger('enqueue_output')
    log.info('thread spawned')

    for line in iter(out.readline, ''):
        q.put(line)

    out.close()

async def decode_json(q):
    log = logging.getLogger('decode_json')

    try:
        line = q.get_nowait()
    except Empty:
        log.error("queue empty")
    else:
        try:
            result = jsonpickle.decode(line)
        except json.JSONDecodeError:
            log.error("not json: " + line)
        else:
            return result

async def process_frame(q):
    frame = await decode_json(q)
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

async def get_frames(p, q, folder, id):
    log = logging.getLogger('save')

    while p.poll() is None:
        result = await process_frame(q)
        if result:
            file_name = 'frame_' + str(result[0]) + '_' + str(id) + '.txt'
            with open(folder + file_name, 'w') as f:
                for res in result[1]:
                    f.write(jsonpickle.encode(res) + "\n")

    log.info("mame process closed")

    remaining = q.qsize()
    log.info("%s frames left in queue", remaining)

    for i in range(remaining):
        result = await process_frame(q)
        if result:
            log.info("%s frames left in queue", q.qsize())
            file_name = 'frame_' + str(result[0]) + '_' + str(id) + '.txt'
            with open(folder + file_name, 'w') as f:
                for res in result[1]:
                    f.write(jsonpickle.encode(res) + "\n")

    log.info("queue emptied")

def main_concurrent(output_folder, id):
    log = logging.getLogger('main_concurrent')
    os.chdir(MAME_PATH)
    script = "lua_scripts\\scrape_data_concurrent_" + str(id) + ".lua"
    cmd = ["mame64", "vsav", "-autoboot_script", script, "-nomax"]

    q = Queue()
    p = subprocess.Popen(cmd, bufsize=1, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    t = Thread(target=enqueue_output, args=(p.stdout, q), daemon=True)
    t.start()

    save_ = BASE_PATH + output_folder

    log.info("loop started")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_frames(p, q, save_, id))
    loop.close()

    log.info("loop closed")

def main(output, num_workers=1):
    log = logging.getLogger('main')
    log.info('starting')

    pool = Pool(processes=num_workers)
    results = [pool.apply_async(main_concurrent, (output, i)) for i in range(num_workers)]
    log.info('results %s', [res.get() for res in results])
    log.info('closing')

#Instead of just writing out a bunch of scripts
#I would prefer to just pass arguements to the lua script
#Haven't seen any confirmation that MAME allows this
def setup():
    template = MAME_PATH + "lua_scripts\\scrape_data_concurrent_template.lua"
    #start = 0x700000
    start = 0x708000
    offset = 1024
    config = helper.create_config(start, offset, 4)
    helper.write_lua_scripts(template, config)

if __name__ == "__main__":
    #setup()
    output_folder = "\\outputs\\pool_json\\"
    main(output_folder, 4)

