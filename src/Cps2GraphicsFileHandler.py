from os.path import isfile, join
from os import listdir
from struct import Struct

class Cps2GraphicsFileHandler:

    #deinterleaves a buffer based on the number of bytes
    def deinterleave(self, data, num_bytes):
        """Deinterleaves a file and returns two lists."""
        evens = []
        odds = []
        deinterleave_s = Struct('c' * num_bytes)
        deinterleave_iter = deinterleave_s.iter_unpack(data)

        for i in deinterleave_iter:
            evens.extend([*i])
            odds.extend([*next(deinterleave_iter)])

        return b''.join(evens), b''.join(odds)

    def interleave(self, file1, file2, num_bytes):
        """Interleaves two buffers together and return a dict."""
        interleaved = []
        interleave_s = Struct('c' * num_bytes)
        file1_iter = interleave_s.iter_unpack(file1)
        file2_iter = interleave_s.iter_unpack(file2)

        for i in file1_iter:
            file2_next = next(file2_iter)
            interleave_temp = [*i, *file2_next]
            interleaved.extend(interleave_temp)

        return  b''.join(interleaved)

    def _get_file_handles(self, folder):
        """Takes a path to a folder. Returns a list of file handles"""
        files = [f for f in listdir(folder) if isfile(join(folder, f))]
        file_handles = [open(folder + "/"+ f, 'rb') for f in files]

        return file_handles

    def _close_handles(self, handles):
        for f in handles: f.close()

    def _prep_files(self, file_handles):
        """Reads the entirety of each file in a folder. Returns a dict."""
        keys = []
        values = []
        handles = self._get_file_handles(file_handles)

        for handle in handles:
            keys.append(handle.name.split("/")[-1])
            values.append(bytearray(handle.read()))

        self._close_handles(handles)

        return dict(zip(keys, values))

    def _split_gfx_files(self, to_split):
        """Splits files into even and odd words. Returns a dict."""
        keys = []
        values = []

        for k, v in to_split.items():
            new_keys = ['.'.join([k, 'even']), '.'.join([k, 'odd'])]
            keys.extend(new_keys)
            values.extend(self.deinterleave(v, 2))

        return dict(zip(keys, values))

    def _first_interleave(self, to_interleave):
        """Interleaves data on a 2 byte basis. Returns a dict"""
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

        return dict(zip(keys, values))

    def _second_interleave(self, to_interleave):
        """Interleaves data on a 64 byte basis. Returns a dict"""
        print("second interleave starts")
        values = []
        keys = []
        file_numbers = [13, 14]

        key_view = next(iter(to_interleave.keys()))
        split_name = key_view.split('.')[0]

        data = to_interleave

        for i in file_numbers:
            temp_keys = [
                [split_name, str(i), str(i+2), 'even'],
                [split_name, str(i+4), str(i+6), 'even'],
                [split_name, str(i), str(i+2), 'odd'],
                [split_name, str(i+4), str(i+6), 'odd']
                ]

            temp_keys = ['.'.join(key) for key in temp_keys]

            print('interleaving ' + temp_keys[0] + ' and ' + temp_keys[1])
            print('interleaving ' + temp_keys[2] + ' and ' + temp_keys[3])

            values.append(self.interleave(data[temp_keys[0]],
                                          data[temp_keys[1]], 64))
            values.append(self.interleave(data[temp_keys[2]],
                                          data[temp_keys[3]], 64))

            temp_keys = [
                [split_name, str(i), str(i+2), str(i+4), str(i+6), 'even'],
                [split_name, str(i), str(i+2), str(i+4), str(i+6), 'odd']
                ]
            keys.extend(['.'.join(key) for key in temp_keys])

        return dict(zip(keys, values))

    def _final_interleave(self, to_interleave):
        """Interleaves data on a 1048576 byte basis. Returns a dict"""
        print("final interleave starts")
        values = []
        keys = []
        file_numbers = [13, 14]

        key_view = next(iter(to_interleave.keys()))
        split_name = key_view.split('.')[0]

        data = to_interleave

        for i in file_numbers:
            temp_keys = [
                [split_name, str(i), str(i+2), str(i+4), str(i+6), 'even'],
                [split_name, str(i), str(i+2), str(i+4), str(i+6), 'odd']
                ]

            temp_keys = ['.'.join(key) for key in temp_keys]

            print('interleaving ' + temp_keys[0] + ' and ' + temp_keys[1])

            values.append(self.interleave(data[temp_keys[0]],
                                          data[temp_keys[1]], 1048576))

            temp_keys = [
                [split_name, str(i), str(i+2), str(i+4), str(i+6), 'final']
                ]
            keys.extend(['.'.join(key) for key in temp_keys])

        return dict(zip(keys, values))

    def _first_deinterleave(self, to_deinterleave):
        keys = []
        values = []

        for k, v in to_deinterleave.items():
            name = k.split('.')[:-1]
            new_keys = ['.'.join([*name, 'even']), '.'.join([*name, 'odd'])]
            keys.extend(new_keys)
            values.extend(self.deinterleave(v, 1048576))

        print(keys)
        return dict(zip(keys, values))

    def _second_deinterleave(self, to_deinterleave):
        keys = []
        values = []

        for k, v in to_deinterleave.items():
            name = k.split('.')
            new_keys = ['.'.join([*name[:3], name[-1]]),
                        '.'.join([name[0], *name[3:]])]
            keys.extend(new_keys)
            values.extend(self.deinterleave(v, 64))

        print(keys)
        return dict(zip(keys, values))

    def _final_deinterleave(self, to_deinterleave):
        keys = []
        values = []

        for k, v in to_deinterleave.items():
            name = k.split('.')
            new_keys = ['.'.join([*name[:2], name[-1]]),
                        '.'.join([name[0], *name[2:]])]
            keys.extend(new_keys)
            values.extend(self.deinterleave(v, 2))

        interleaving = dict(zip(keys, values))
        print(keys)

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

            values.append(self.interleave(interleaving[even],
                                          interleaving[odd], 2))

        print(keys)
        return dict(zip(keys, values))

    def test_interleave_process(self):
        graphics_data = self._prep_files("inputs/gfx_original")
        graphics_data = self._first_interleave(graphics_data)
        for k, v in graphics_data.items():
            with open('outputs/refactor/first_interleave/' + k, 'wb') as f:
                f.write(v)

        graphics_data = self._second_interleave(graphics_data)

        for k, v in graphics_data.items():
            with open('outputs/refactor/second_interleave/' + k, 'wb') as f:
                f.write(v)

        graphics_data = self._final_interleave(graphics_data)
        for k, v in graphics_data.items():
            with open('outputs/refactor/final_interleave/' + k, 'wb') as f:
                f.write(v)

    def test_deinterleave_process(self):
        graphics_data = self._prep_files("inputs/refactor")
        graphics_data = self._first_deinterleave(graphics_data)
        #for k, v in graphics_data.items():
        #    with open('outputs/refactor/first_deinterleave/' + k, 'wb') as f:
        #        f.write(v)
        graphics_data = self._second_deinterleave(graphics_data)
        graphics_data = self._final_deinterleave(graphics_data)
        for k, v in graphics_data.items():
            with open('outputs/refactor/roms/' + k, 'wb') as f:
                f.write(v)

if __name__ == "__main__":
    handler = Cps2GraphicsFileHandler()
    #handler.test_interleave_process()
    handler.test_deinterleave_process()

