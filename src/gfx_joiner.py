import os
from os.path import isfile, join
import subprocess

def get_file_handles(folder):
    files = [f for f in os.listdir(folder) if isfile(join(folder, f))]
    file_handles = []
    for f in files:
        file_handles.append(open(folder + "/"+ f, 'rb'))
    return file_handles

def clean_up_file_handles(handles):
    for f in handles:
        f.close()

def deinterleave(handle, num_bytes):
    evens = bytearray()
    odds = bytearray()

    temp = handle.read(num_bytes)
    while True:
        if not temp:
            break
        evens += temp
        odds += handle.read(num_bytes)
        temp = handle.read(num_bytes)

    return [evens, odds]

#interleave //TWO// files, offset is number of words (in decimal)
def interleave(file1, file2, num_bytes):
    to_write = bytearray()
    temp = file1.read(num_bytes)

    while True:
        if not temp:
            break
        to_write += temp
        to_write += file2.read(num_bytes)
        temp = file1.read(num_bytes)

    return to_write

def run_diff(file1, file2, save_diff_path):
    with open("diff", 'ab') as f:
        subprocess.run(["radiff2", file1, file2], stdout=f)
        if not os.stat(save_diff_path).st_size:
            print(file2 + " - no diff")
        else:
            print(file2 + " - see diff file")

def first_interleave(input_files, output_files):
    if not os.path.exists(output_files):
        os.makedirs(output_files)

    handles = get_file_handles(input_files)
    for i, handle in enumerate(handles):
        file_name = handle.name.split("/")[-1]
        split_name = file_name.split("_")
        if split_name[1] in ["13", "14", "17", "18"]:
            interleaved = interleave(handles[i], handles[i+4], 2)
            temp = handles[i+4].name.split("/")[-1]
            temp = temp.split("_")[1]
            split_name.insert(-1, temp)
            write_out_name = "_".join(split_name)
            with open(output_files + write_out_name, 'wb') as f:
                f.write(interleaved)

    clean_up_file_handles(handles)

def second_interleave(input_files, output_files):
    if not os.path.exists(output_files):
        os.makedirs(output_files)

    handles = get_file_handles(input_files)
    for i, handle in enumerate(handles):
        file_name = handle.name.split("/")[-1]
        split_name = file_name.split("_")
        if split_name[1] in ["13", "14"]:
            interleaved = interleave(handles[i], handles[i+4], 64)
            temp = handles[i+4].name.split("/")[-1]
            temp = temp.split("_")
            split_name.insert(-1, temp[1])
            split_name.insert(-1, temp[2])
            write_out_name = "_".join(split_name)

            with open(output_files + write_out_name, 'wb') as f:
                f.write(interleaved)

    clean_up_file_handles(handles)

def final_interleave(input_files, output_files):
    if not os.path.exists(output_files):
        os.makedirs(output_files)

    handles = get_file_handles(input_files)
    for i, handle in enumerate(handles):
        split_name = handle.name.split("/")[-1]
        if split_name.split("_")[-1] == "evens":
            interleaved = interleave(handle, handles[i+1], 1048576)

            interleave_name = split_name.split("_")[:-1]
            interleave_name.append("final")
            interleave_name = "_".join(interleave_name)

            with open(output_files + interleave_name, 'wb') as f:
                f.write(interleaved)

    clean_up_file_handles(handles)

def first_deinterleave(input_files, output_files):
    if not os.path.exists(output_files):
        os.makedirs(output_files)

    handles = get_file_handles(input_files)
    for handle in handles:
        file_name = handle.name.split("/")[-1]
        file_name = "_".join(file_name.split("_")[:-1])

        [first_half, second_half] = deinterleave(handle, 1048576)
        with open(output_files + file_name + '_evens', 'wb') as f:
            f.write(first_half)

        with open(output_files + file_name + '_odds', 'wb') as f:
            f.write(second_half)

        #run_diff(path_to_new_splits + file_name + "_evens",
        #         path_to_old_splits + file_name + "_evens", "diff")

        #run_diff(path_to_new_splits + file_name + "_odds",
        #         path_to_old_splits + file_name +"_odds", "diff")

    clean_up_file_handles(handles)

def second_deinterleave(input_files, output_files):
    if not os.path.exists(output_files):
        os.makedirs(output_files)

    handles = get_file_handles(input_files)
    for handle in handles:
        old_file_name = handle.name.split("/")[-1]
        [first_half, second_half] = deinterleave(handle, 64)

        file_name = old_file_name.split("_")
        prefix = file_name[0] + "_"

        even_name = prefix + "_".join(file_name[1:3]) + "_" + file_name[-1]
        with open(output_files + even_name, 'wb') as f:
            f.write(first_half)

        odd_name = prefix + "_".join(file_name[3:5]) + "_" + file_name[-1]
        with open(output_files + odd_name, 'wb') as f:
            f.write(second_half)

    clean_up_file_handles(handles)

def final_deinterleave(input_files, output_files):
    if not os.path.exists(output_files):
        os.makedirs(output_files)

    handles = get_file_handles(input_files)
    for handle in handles:
        old_file_name = handle.name.split("/")[-1]
        [first_half, second_half] = deinterleave(handle, 2)

        file_name = old_file_name.split("_")
        prefix = file_name[0] + "_"

        even_name = prefix + file_name[1] + "_" + file_name[-1]
        with open(output_files + even_name, 'wb') as f:
            f.write(first_half)

        odd_name = prefix + file_name[2] + "_" + file_name[-1]
        with open(output_files + odd_name, 'wb') as f:
            f.write(second_half)

        #even_diff_name = even_name.split("_")
        #even_diff_name = even_diff_name[1] + "_" + even_diff_name[0] + "_" + even_diff_name[2]
        #run_diff(path_to_new_splits + even_name,
        #         path_to_compare_splits + even_diff_name, "diff")
        
        #odd_diff_name = odd_name.split("_")
        #odd_diff_name = odd_diff_name[1] + "_" + odd_diff_name[0] + "_" + odd_diff_name[2]
        #run_diff(path_to_new_splits + odd_name,
        #         path_to_compare_splits + odd_diff_name, "diff")

    clean_up_file_handles(handles)

def interleave_to_gfx(input_files, output_files):
    if not os.path.exists(output_files):
        os.makedirs(output_files)

    handles = get_file_handles(input_files)
    for i, handle in enumerate(handles):
        split_name = handle.name.split("_")[-1]
        if split_name == "evens":
            interleaved = interleave(handles[i], handles[i+1], 2)
            file_name = "vm3." + handle.name.split("_")[-2]

            with open(output_files + file_name, 'wb') as f:
                f.write(interleaved)

    clean_up_file_handles(handles)

#turn 4 interleaved roms back into their respective roms
def binary_to_gfx(input_file, output_files):
    first_deinterleave(input_file, input_file + "first_split/")
    second_deinterleave(input_file + "/first_split/", input_file + "/second_split/")
    final_deinterleave(input_file + "/second_split", input_file + "/final_split/")
    interleave_to_gfx(input_file + "/final_split/", output_files)

#splits a single gfx rom into its even and odd words, prep work ig
def split_gfx_files(input_files, output_files):
    if not os.path.exists(output_files):
        os.makedirs(output_files)

    handles = get_file_handles(input_files)
    for handle in handles:
        [file1, file2] = deinterleave(handle, 2)
        file_name = handle.name.split("/")[-1].split(".")
        file_name = "_".join(file_name)

        with open(output_files + file_name + "_evens", 'wb') as f:
            f.write(file1)

        with open(output_files + file_name + "_odds", 'wb') as f:
            f.write(file2)

    clean_up_file_handles(handles)
    return "hi"

#turns gfx roms to a file viewable in a tile shitter
def gfx_to_binary(input_files, output_file):
    print("starting")
    split_gfx_files(input_files, output_file + "prep/")
    first_interleave(output_file + "prep/", output_file + "first_interleave/")
    second_interleave(output_file + "first_interleave/", output_file + "second_interleave/")
    final_interleave(output_file + "second_interleave/", output_file + "final_interleave/")
    print("done")
if __name__ == "__main__":
    gfx_to_binary("gfx_original", "gfx_test/")
    #binary_to_gfx("gfx_test/", "gfx_test/roms/")
