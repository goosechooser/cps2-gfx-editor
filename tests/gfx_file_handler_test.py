from src import gfx_file_handler
#from gfx_file_handler import deinterleave, interleave

#note to self: should add test_deinterleave_files() and test_interleave_files()
#would help demonstrate correctness without needing external .bat scripts
def test_deinterleave():
    test_data = bytearray.fromhex('F1 FF 00 00 00 01 FF FF')
    #handler = Cps2GraphicsFileHandler()

    deinterleaved = gfx_file_handler.deinterleave(test_data, 2, 2)
    assert bytearray(deinterleaved[0]).hex() == 'f1ff0001'
    assert bytearray(deinterleaved[1]).hex() == '0000ffff'

    deinterleaved = gfx_file_handler.deinterleave(test_data, 4, 2)
    assert bytearray(deinterleaved[0]).hex() == 'f1ff0000'
    assert bytearray(deinterleaved[1]).hex() == '0001ffff'

def test_interleave():
    test_data = [bytearray.fromhex('F1FF0001'),
                 bytearray.fromhex('0000FFFF')]
    interleaved = gfx_file_handler.interleave([test_data[0], test_data[1]], 2)
    assert bytearray(interleaved).hex() == 'f1ff00000001ffff'

    interleaved = gfx_file_handler.interleave([test_data[0], test_data[1]], 4)
    assert bytearray(interleaved).hex() == 'f1ff00010000ffff'

if __name__ == "__main__":
    test_deinterleave()
    