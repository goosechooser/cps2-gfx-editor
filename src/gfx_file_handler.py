import os
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

def deinterleave_cps2(fname):
    """Deinterleaves a interleaved cps2 graphics file."""
    head, tail = os.path.split(fname)
    split_tail = tail.split('.')
    fnames = ['.'.join([split_tail[0], name]) for name in split_tail[1:-1]]

    data = 0
    with open(fname, 'rb') as f:
        data = bytearray(f.read())

    first = deinterleave(data, 1048576)

    second = []
    for half in first:
        second.extend(deinterleave(half, 64))

    final = []
    for quarter in second:
        final.extend(deinterleave(quarter, 2))

    deinterleaved = [interleave(final[i], final[i+4], 2) for i in range(4)]

    for i, fname in enumerate(fnames):
        with open(os.path.join(head, fname), 'wb') as f:
            f.write(deinterleaved[i])

if __name__ == "__main__":
    deinterleave_cps2("outputs/sfxgfx/")
