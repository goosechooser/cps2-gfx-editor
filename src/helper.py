import jsonpickle
#helper functions

#MAME address values are based on the size of the tiles you are viewing.
#ie [ADDR] when viewing 8x8 and 16x16 tiles don't point to the same location.
#This is because MAME uses the address value as a sort of index
#to where the tile data starts.

def convert_mame_addr(mame_addr, tile_size, split=True):
    """Converts the address value MAME displays when you press 'F4'.

    Returns an int.
    """
    tile_bytes = 0
    addr = int(mame_addr, 16)
    if tile_size == 8:
        tile_bytes = 32
    if tile_size == 16:
        tile_bytes = 128

    converted_addr = addr * tile_bytes
    
    if not split:
        return converted_addr
    memory_bank_size = int('0x1000000', 16)

    #currently the 8 eproms are split into 2 banks
    if converted_addr > memory_bank_size:
        converted_addr -= memory_bank_size

    return converted_addr

def flatten_list(rolled_list):
    """Turns a list of lists into just a list.
    
    Returns list.
    """
    flat = [x for sublist in rolled_list for x in sublist]
    return flat

def fromlua(lua):
    with open(lua, 'r') as f:
        return [jsonpickle.decode(line) for line in f]

def mask_sprite_data(sprite_data):
    """Splits up the 4 bytes containing all the relevant sprite info.
    
    Returns a dict
    """
    byte_data = [int(data, 16) for data in sprite_data if data]

    dict_ = {}
    dict_['priority'] = (byte_data[0] & 0xC000) >> 14
    dict_['x'] = byte_data[0] & 0x03FF
    dict_['y'] = byte_data[1] & 0x03FF
    dict_['eol'] = (byte_data[1] & 0x8000) >> 15
    dict_['height'] = ((byte_data[3] & 0xF000) >> 12) + 1
    dict_['width'] = ((byte_data[3] & 0x0F00) >> 8) + 1
    #(0= Offset by X:-64,Y:-16, 1= No offset)
    dict_['offset'] = (byte_data[3] & 0x0080) >> 7
    #hex: {0:x};  oct: {0:o};  bin: {0:b}".format(42)
    top_half = "{0:#x}".format((byte_data[1] & 0x6000) >> 13)
    bottom_half = "{0:x}".format(byte_data[2])
    dict_['tile_number'] = top_half + bottom_half
    #Y flip, X flip (1= enable, 0= disable)
    dict_['yflip'] = (byte_data[3] & 0x0040) >> 6
    dict_['xflip'] = (byte_data[3] & 0x0020) >> 5
    dict_['pal_number'] = "{0:x}".format(byte_data[3] & 0x001F)

    return dict_

def create_config(start_addr, offset, length):
    """Creates the config dict to pass with a lua template.

    Returns a dict
    """
    return [
        {'start_addr' : start_addr + offset * i * 8, 'offset' : offset} for i in range(length)
    ]

def write_lua_scripts(template, config):
    """Takes a template file and prints out new scripts with values changed."""
    lines = []
    split_path = template.split('\\')
    base_folder = '\\'.join(split_path[:-1])
    base_name = split_path[-1]

    with open(template, 'r') as f:
        lines = list(f)

    #words = [w.replace('[br]', '<br />') for w in words]
    for i, c in enumerate(config):
        start = 'SPRITE_START_ADDR = {}\n'.format(hex(c['start_addr']))
        offset = 'RUN_LENGTH = {}\n'.format(c['offset'])

        c_file = [w.replace('SPRITE_START_ADDR = 0x0\n', start) for w in lines]
        c_file = [w.replace('RUN_LENGTH = 0x0\n', offset) for w in c_file]
        file_name = '\\' + base_name.split('.')[0]
        file_name = '_'.join(file_name.split('_')[:-1]) + '_' + str(i) + '.lua'

        with open(base_folder + file_name, 'w') as f:
            f.write(''.join(c_file))
