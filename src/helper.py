#helper functions

#MAME address values are based on the size of the tiles you are viewing.
#ie [ADDR] when viewing 8x8 and 16x16 tiles don't point to the same location.
#This is because MAME uses the address value as a sort of index
#to where the tile data starts.

def convert_mame_addr(mame_addr, tile_size):
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