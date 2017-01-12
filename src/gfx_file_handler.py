from struct import Struct

#GFX files (for cps2) seem to always be in batches of 4
#workflow along the lines of 
#point at first file (in batch of 4)
#grap the four files
#interleave the 4 in one go

def deinterleave(data, num_bytes):
    """Deinterleaves a bytearray.

    Returns two bytearrays.
    """
    evens = []
    odds = []
    deinterleave_s = Struct('c' * num_bytes)
    deinterleave_iter = deinterleave_s.iter_unpack(data)

    for i in deinterleave_iter:
        evens.extend([*i])
        odds.extend([*next(deinterleave_iter)])

    return b''.join(evens), b''.join(odds)

def interleave(file1, file2, num_bytes):
    """Interleaves two bytearray buffers together.

    Returns a bytearray.
    """
    interleaved = []
    interleave_s = Struct('c' * num_bytes)
    file1_iter = interleave_s.iter_unpack(file1)
    file2_iter = interleave_s.iter_unpack(file2)

    for i in file1_iter:
        file2_next = next(file2_iter)
        interleave_temp = [*i, *file2_next]
        interleaved.extend(interleave_temp)

    return  b''.join(interleaved)

def _get_handles(filepath):
    splitpath = filepath.split("/")
    fsplit = splitpath[-1].split('.')

    fname = fsplit[0]
    fnum = int(fsplit[1][:-1])

    fnums = [''.join([str(fnum + (i * 2)), 'm']) for i in range(4)]
    fnames = ['.'.join([fname, num]) for num in fnums]
    joinedpath = '/'.join(splitpath[:-1]) + '/'

    return [open(joinedpath  + name, 'rb') for name in fnames]

def _close_handles(handles):
    for f in handles:
        f.close()

def _combine_file_names(fnames):
    fsplit = [name.split("/")[-1] for name in fnames]
    base = fsplit[0].split(".")[0]
    fnums = [name.split(".")[-1] for name in fsplit]

    return '.'.join([base, *fnums, 'combined'])

def interleave_cps2(fname):
    """Interleaves a set of 4 cps2 graphics files."""
    handles = _get_handles(fname)
    names = [handle.name for handle in handles]
    to_split = [bytearray(handle.read()) for handle in handles]
    _close_handles(handles)

    split_data = [(deinterleave(data, 2)) for data in to_split]
    interleaved = []
    data_iter = iter(split_data)

    for sdata in data_iter:
        next_data = next(data_iter)
        even = interleave(sdata[0], next_data[0], 2)
        odd = interleave(sdata[1], next_data[1], 2)
        interleaved.append((even, odd))

    inter_iter = iter(interleaved)

    second_interleave = []
    for i in inter_iter:
        next_data = next(inter_iter)
        second_interleave.append(interleave(i[0], next_data[0], 64))
        second_interleave.append(interleave(i[1], next_data[1], 64))

    final = interleave(second_interleave[0], second_interleave[1], 1048576)

    basepath = fname.split('/')[:-1]
    comb_fname = _combine_file_names(names)

    with open('/'.join([*basepath, comb_fname]), 'wb') as f:
        f.write(final)

def _first_deinterleave(to_deinterleave):
    keys = []
    values = []

    for k, v in to_deinterleave.items():
        name = k.split('.')[:-1]
        new_keys = ['.'.join([*name, 'even']), '.'.join([*name, 'odd'])]
        keys.extend(new_keys)
        values.extend(deinterleave(v, 1048576))

    return dict(zip(keys, values))

def _second_deinterleave(to_deinterleave):
    keys = []
    values = []

    for k, v in to_deinterleave.items():
        name = k.split('.')
        new_keys = ['.'.join([*name[:3], name[-1]]),
                    '.'.join([name[0], *name[3:]])]
        keys.extend(new_keys)
        values.extend(deinterleave(v, 64))

    return dict(zip(keys, values))

def _final_deinterleave(to_deinterleave):
    keys = []
    values = []

    for k, v in to_deinterleave.items():
        name = k.split('.')
        new_keys = ['.'.join([*name[:2], name[-1]]),
                    '.'.join([name[0], *name[2:]])]
        keys.extend(new_keys)
        values.extend(deinterleave(v, 2))

    interleaving = dict(zip(keys, values))

    #Need to interleave all the odd/even files back together
    keys = []
    values = []
    rom_prefix = next(iter(to_deinterleave.keys())).split('.')[0]

    for num in range(13, 21):
        name = [rom_prefix, str(num)]
        joined = '.'.join(name)
        keys.append(joined)

        even = '.'.join([joined, 'even'])
        odd = '.'.join([joined, 'odd'])

        values.append(interleave(interleaving[even], interleaving[odd], 2))

    return dict(zip(keys, values))

def deinterleave_files(folder_path):
    graphics_data = _prep_files(folder_path)
    graphics_data = _first_deinterleave(graphics_data)
    graphics_data = _second_deinterleave(graphics_data)
    graphics_data = _final_deinterleave(graphics_data)

    return graphics_data
    #for k, v in graphics_data.items():
    #    with open('outputs/refactor/roms/' + k, 'wb') as f:
    #        f.write(v)

# class Cps2Handler(object):
#     def __init__(self)