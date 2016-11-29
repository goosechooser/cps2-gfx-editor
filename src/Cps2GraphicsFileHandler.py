import os
from os.path import isfile, join

class Cps2GraphicsFileHandler:
    def _get_file_handles(self, folder):
        files = [f for f in os.listdir(folder) if isfile(join(folder, f))]
        file_handles = []
        for f in files:
            file_handles.append(open(folder + "/"+ f, 'rb'))

        return file_handles

    def _clean_up_file_handles(self, handles):
        [f.close() for f in handles]

    def deinterleave(self, handle, num_bytes):
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
    def interleave(self, file1, file2, num_bytes):
        to_write = bytearray()
        temp = file1.read(num_bytes)

        while True:
            if not temp:
                break
            to_write += temp
            to_write += file2.read(num_bytes)
            temp = file1.read(num_bytes)

        return to_write

    def first_interleave(self, input_files, output_files):
        if not os.path.exists(output_files):
            os.makedirs(output_files)

        handles = self._get_file_handles(input_files)
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

        self._clean_up_file_handles(handles)

    def second_interleave(self, input_files, output_files):
        if not os.path.exists(output_files):
            os.makedirs(output_files)

        handles = self._get_file_handles(input_files)
        for i, handle in enumerate(handles):
            file_name = handle.name.split("/")[-1]
            split_name = file_name.split("_")
            if split_name[1] in ["13", "14"]:
                interleaved = self.interleave(handles[i], handles[i+4], 64)
                temp = handles[i+4].name.split("/")[-1]
                temp = temp.split("_")
                split_name.insert(-1, temp[1])
                split_name.insert(-1, temp[2])
                write_out_name = "_".join(split_name)

                with open(output_files + write_out_name, 'wb') as f:
                    f.write(interleaved)

        self._clean_up_file_handles(handles)

    def final_interleave(self, input_files, output_files):
        if not os.path.exists(output_files):
            os.makedirs(output_files)

        handles = self._get_file_handles(input_files)
        for i, handle in enumerate(handles):
            split_name = handle.name.split("/")[-1]
            if split_name.split("_")[-1] == "evens":
                interleaved = self.interleave(handle, handles[i+1], 1048576)

                interleave_name = split_name.split("_")[:-1]
                interleave_name.append("final")
                interleave_name = "_".join(interleave_name)

                with open(output_files + interleave_name, 'wb') as f:
                    f.write(interleaved)

        self._clean_up_file_handles(handles)

    def first_deinterleave(self, input_files, output_files):
        if not os.path.exists(output_files):
            os.makedirs(output_files)

        handles = self._get_file_handles(input_files)
        for handle in handles:
            file_name = handle.name.split("/")[-1]
            file_name = "_".join(file_name.split("_")[:-1])

            [first_half, second_half] = self.deinterleave(handle, 1048576)
            with open(output_files + file_name + '_evens', 'wb') as f:
                f.write(first_half)

            with open(output_files + file_name + '_odds', 'wb') as f:
                f.write(second_half)

        self._clean_up_file_handles(handles)

    def second_deinterleave(self, input_files, output_files):
        if not os.path.exists(output_files):
            os.makedirs(output_files)

        handles = self._get_file_handles(input_files)
        for handle in handles:
            old_file_name = handle.name.split("/")[-1]
            [first_half, second_half] = self.deinterleave(handle, 64)

            file_name = old_file_name.split("_")
            prefix = file_name[0] + "_"

            even_name = prefix + "_".join(file_name[1:3]) + "_" + file_name[-1]
            with open(output_files + even_name, 'wb') as f:
                f.write(first_half)

            odd_name = prefix + "_".join(file_name[3:5]) + "_" + file_name[-1]
            with open(output_files + odd_name, 'wb') as f:
                f.write(second_half)

        self._clean_up_file_handles(handles)

    def final_deinterleave(self, input_files, output_files):
        if not os.path.exists(output_files):
            os.makedirs(output_files)

        handles = self._get_file_handles(input_files)
        for handle in handles:
            old_file_name = handle.name.split("/")[-1]
            [first_half, second_half] = self.deinterleave(handle, 2)

            file_name = old_file_name.split("_")
            prefix = file_name[0] + "_"

            even_name = prefix + file_name[1] + "_" + file_name[-1]
            with open(output_files + even_name, 'wb') as f:
                f.write(first_half)

            odd_name = prefix + file_name[2] + "_" + file_name[-1]
            with open(output_files + odd_name, 'wb') as f:
                f.write(second_half)

        self._clean_up_file_handles(handles)

    def interleave_to_gfx(self, input_files, output_files):
        if not os.path.exists(output_files):
            os.makedirs(output_files)

        handles = self._get_file_handles(input_files)
        for i, handle in enumerate(handles):
            split_name = handle.name.split("_")[-1]
            if split_name == "evens":
                interleaved = self.interleave(handles[i], handles[i+1], 2)
                file_name = "vm3." + handle.name.split("_")[-2]

                with open(output_files + file_name + "m", 'wb') as f:
                    f.write(interleaved)

        self._clean_up_file_handles(handles)

    #turn 4 interleaved roms back into their respective roms
    def binary_to_gfx(self, input_file, output_files):
        self.first_deinterleave(input_file, input_file + "first_split/")
        self.second_deinterleave(input_file + "/first_split/", input_file + "/second_split/")
        self.final_deinterleave(input_file + "/second_split", input_file + "/final_split/")
        self.interleave_to_gfx(input_file + "/final_split/", output_files)

    #splits a single gfx rom into its even and odd words, prep work ig
    def split_gfx_files(self, input_files, output_files):
        if not os.path.exists(output_files):
            os.makedirs(output_files)

        handles = self._get_file_handles(input_files)
        for handle in handles:
            [file1, file2] = self.deinterleave(handle, 2)
            file_name = handle.name.split("/")[-1].split(".")
            file_name = "_".join(file_name)

            with open(output_files + file_name + "_evens", 'wb') as f:
                f.write(file1)

            with open(output_files + file_name + "_odds", 'wb') as f:
                f.write(file2)

        self._clean_up_file_handles(handles)

    #turns gfx roms to a file viewable in a tile shitter
    def gfx_to_binary(self, input_files, output_file):
        self.split_gfx_files(input_files, output_file + "prep/")
        self.first_interleave(output_file + "prep/",
                              output_file + "first_interleave/")
        self.second_interleave(output_file + "first_interleave/",
                               output_file + "second_interleave/")
        self.final_interleave(output_file + "second_interleave/",
                              output_file + "final_interleave/")
