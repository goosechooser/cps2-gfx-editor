#from struct import iter_unpack
import os
import sys
import mmap
import logging
import time
import asyncio
from concurrent.futures import ProcessPoolExecutor

from PIL import Image
from src import tile_printer, helper

GFX_FILE = "inputs/refactor/vm3_combined"
GFX_F = open(GFX_FILE, 'r+b')
GFX_MM = mmap.mmap(GFX_F.fileno(), 0)
FRAMES_FOLDER = "inputs/smol_json/"
OUTPUT_FOLDER = "outputs/cosprites3/"

logging.basicConfig(
    level=logging.INFO,
    format='PID %(process)s %(name)8s: %(message)s',
    stream=sys.stderr,
)

def pool_sprites(filepath):
    log = logging.getLogger('pool_sprites')
    #log.setLevel(logging.INFO)

    sprites = helper.fromlua(filepath)
    filename = filepath.split("/")[2]

    log.info("starting %s", filepath)
    time_point1 = time.process_time()

    for i, sprite in enumerate(sprites):
        tiles2d = tile_printer.make_tiles_mmap(GFX_MM, sprite.addrs2d())
        sprites[i].tiles = helper.flatten_list(tiles2d)

    time_point2 = time.process_time()
    delta_t = time_point2 - time_point1
    #log.info("making sprites took %s to complete", delta_t)

    time_point3 = time.process_time()
    put_sprites(sprites, OUTPUT_FOLDER + filename[:-4])
    time_point4 = time.process_time()

    delta_t2 = time_point4 - time_point3
    #log.info("putting sprites took %s to complete", delta_t2)
    log.info("ending %s", filepath)
    return delta_t, delta_t2

async def process_frames(executor, tile_folder):
    log = logging.getLogger('process_frames')
    log.info('starting')

    log.info('creating tasks')

    loop = asyncio.get_event_loop()
    filenames = [tile_folder + filename for filename in os.listdir(tile_folder)]
    tasks = [loop.run_in_executor(executor, pool_sprites, filename) for filename in filenames]

    log.info('awaiting results')
    completed, pending = await asyncio.wait(tasks)
    results = [t.result() for t in completed]

    make_sum = sum([res[0] for res in results])
    put_sum =  sum([res[1] for res in results])

    log.info('avg time to make sprites: %s', make_sum/len(results))
    log.info('avg time to put sprites: %s', put_sum/len(results))

    log.info('closing')
    GFX_MM.close()

def put_sprites(sprites, output):
    """Takes a list of sprites and creates a .png image.
    Sprites are placed in the image at the x,y location they would occupy on the cps2.
    """
    #log.setLevel(logging.INFO)
    #log.info('running')
    canvas = Image.new('RGB', (400, 400))
    for sprite in sprites:
        im = Image.fromarray(sprite.toarray(), 'RGB')
        canvas.paste(im, sprite.location)
    canvas.save(output + ".png")
    #log.info('done')
    return

if __name__ == "__main__":
    #pool_main(FRAMES_FOLDER)

    event_loop = asyncio.get_event_loop()
    executor = ProcessPoolExecutor(max_workers=4)

    try:
        event_loop.run_until_complete(process_frames(executor, FRAMES_FOLDER))
    finally:
        event_loop.close()
