import struct

def longs_to_int(data):
    # pad = '0' * datumLength
    # return bin(int(''.join([(pad + bin(d)[2:])[-datumLength:] for d in data]), 2))
    num = 0
    for i in range(len(data)):
        num = num << 64 | data[len(data) - 1 - i]
    return num
