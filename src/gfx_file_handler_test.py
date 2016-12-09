from gfx_file_handler import deinterleave, interleave

def test_deinterleave():
    test_data = bytearray.fromhex('F1 FF 00 00 00 01 FF FF')
    #handler = Cps2GraphicsFileHandler()

    deinterleaved = deinterleave(test_data, 2)
    assert bytearray(deinterleaved[0]).hex() == 'f1ff0001'
    assert bytearray(deinterleaved[1]).hex() == '0000ffff'

    deinterleaved = deinterleave(test_data, 4)
    assert bytearray(deinterleaved[0]).hex() == 'f1ff0000'
    assert bytearray(deinterleaved[1]).hex() == '0001ffff'

def test_interleave():
    test_data = [bytearray.fromhex('F1FF0001'),
                 bytearray.fromhex('0000FFFF')]
    interleaved = interleave(test_data[0], test_data[1], 2)
    assert bytearray(interleaved).hex() == 'f1ff00000001ffff'

    interleaved = interleave(test_data[0], test_data[1], 4)
    assert bytearray(interleaved).hex() == 'f1ff00010000ffff'

if __name__ == "__main__":
    test_deinterleave()
    