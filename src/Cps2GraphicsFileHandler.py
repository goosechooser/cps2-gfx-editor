from os.path import isfile, join, exists
from os import listdir
from struct import *
#temporary will remove eventually
import os

#class GraphicsData:
#    def __init__(self, name, data):
#        self.name = name
#        self.data = data

class Cps2GraphicsFileHandler:
    def _get_file_handles(self, folder):
        files = [f for f in listdir(folder) if isfile(join(folder, f))]
        file_handles = [open(folder + "/"+ f, 'rb') for f in files]

        return file_handles

    def _clean_up_file_handles(self, handles):
        [f.close() for f in handles]

    #deinterleaves a buffer based on the number of bytes
    def deinterleave(self, data, num_bytes):
        evens = []
        odds = []
        deinterleave_s = Struct('c' * num_bytes)
        deinterleave_iter = deinterleave_s.iter_unpack(data)

        for i in deinterleave_iter:
            evens.extend([*i])
            odds.extend([*next(deinterleave_iter)])

        evens = b''.join(evens)
        odds = b''.join(odds)

        return evens, odds

    #interleaves two buffers together, based on number of bytes
    def interleave(self, file1, file2, num_bytes):
        interleaved = []
        interleave_s = Struct('c' * num_bytes)
        file1_iter = interleave_s.iter_unpack(file1)
        file2_iter = interleave_s.iter_unpack(file2)

        for i in file1_iter:
            file2_next = next(file2_iter)
            interleave_temp = [*i, *file2_next]
            interleaved.extend(interleave_temp)
   
        interleaved = b''.join(interleaved)
        return interleaved

    def _prep_files_for_interleave(self, file_handles):
        keys = []
        values = []
        handles = self._get_file_handles(file_handles)

        for handle in handles:
            keys.append(handle.name.split("/")[-1])
            values.append(bytearray(handle.read()))

        self._clean_up_file_handles(handles)

        return dict(zip(keys, values))

    def _split_gfx_files(self, to_split):
        keys = []
        values = []
        #self.deinterleave(to_split['vm3_13'], 2)
        for k, v in to_split.items():
            new_keys = ['.'.join([k, 'even']), '.'.join([k, 'odd'])]
            keys.extend(new_keys)
            values.extend(self.deinterleave(v, 2))

        return dict(zip(keys, values))

    def _first_interleave(self, to_interleave):
        values = []
        keys = []
        file_numbers = [13, 14, 17, 18]

        key_view = next(iter(to_interleave.keys()))
        split_name = key_view.split('.')[0]

        data = self._split_gfx_files(to_interleave)

        for i in file_numbers:
            temp_keys = [[split_name, str(i), 'even'],
                         [split_name, str(i+2), 'even'],
                         [split_name, str(i), 'odd'],
                         [split_name, str(i+2), 'odd']]
            temp_keys = ['.'.join(key) for key in temp_keys]

            print('interleaving ' + temp_keys[0] + ' and ' + temp_keys[1])
            print('interleaving ' + temp_keys[2] + ' and ' + temp_keys[3])

            values.append(self.interleave(data[temp_keys[0]],
                                          data[temp_keys[1]], 2))
            values.append(self.interleave(data[temp_keys[2]],
                                          data[temp_keys[3]], 2))

            temp_keys = [[split_name, str(i), str(i+2), 'even'],
                         [split_name, str(i), str(i+2), 'odd']]
            keys.extend(['.'.join(key) for key in temp_keys])

        print(keys)
        return dict(zip(keys, values))

    def first_interleave(self, input_files, output_files):
        if not exists(output_files):
            os.makedirs(output_files)

        handles = self._get_file_handles(input_files)
        for i, handle in enumerate(handles):
            file_name = handle.name.split("/")[-1]
            split_name = file_name.split("_")
            if split_name[1] in ["13", "14", "17", "18"]:
                interleaved = self.interleave(handles[i].read(),
                                              handles[i+4].read(), 2)
                temp = handles[i+4].name.split("/")[-1]
                temp = temp.split("_")[1]
                split_name.insert(-1, temp)
                write_out_name = "_".join(split_name)
                with open(output_files + write_out_name, 'wb') as f:
                    f.write(interleaved)

        self._clean_up_file_handles(handles)

    def second_interleave(self, input_files, output_files):
        if not exists(output_files):
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

    #turns gfx roms to a file viewable in a tile shitter
    #def _gfx_to_binary(self, input_files, output_file):
        #self.split_gfx_files(input_files, output_file + "prep/")
        #self._first_interleave(output_file + "prep/",
        #                      output_file + "first_interleave/")
        #self.second_interleave(output_file + "first_interleave/",
        #                       output_file + "second_interleave/")
        #self.final_interleave(output_file + "second_interleave/",
        #                      output_file + "final_interleave/")
    def test_run(self):
        graphics_data = self._prep_files_for_interleave("inputs/gfx_original")
        #[print(key) for key in iter(graphics_data)]
        graphics_data = self._first_interleave(graphics_data)
        #[print(key) for key in iter(graphics_data)]

if __name__ == "__main__":
    #test = bytearray.fromhex('F1 FF 00 00 00 01 FF FF')
    handler = Cps2GraphicsFileHandler()
    handler.test_run()
    #handler._first_interleave(graphics_data)
    #deinterleaved = handler.deinterleave(test, 2)
    #handler.interleave(deinterleaved[0], deinterleaved[1], 2)



