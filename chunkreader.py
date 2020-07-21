import struct
from functools import lru_cache

@lru_cache
def longs_to_int(data):
    # pad = '0' * datumLength
    # return bin(int(''.join([(pad + bin(d)[2:])[-datumLength:] for d in data]), 2))
    num = 0
    for i in range(len(data)):
        num = num << 64 | data[len(data) - 1 - i]
    return num



def get_blockstate_at(chunk, x, y, z):
    x %= 16
    z %= 16
    if 1451 <= chunk['DataVersion'] < 2529: # the flattening - right before they changed the format again
        return get_blockstate_at_115(chunk['Level'], x, y, z)
    elif 2529 <= chunk['DataVersion']: # new new new
        return get_blockstate_at_116(chunk['Level'], x, y, z)
    else:
        return get_blockstate_at_112(chunk['Level'], x, y, z)

def get_blockstate_at_112(chunk, x, y, z):
    for sub_chunk in chunk['Sections']:
        if sub_chunk['Y'] * 16 <= y < (sub_chunk['Y'] + 1) * 16 and 'Blocks' in sub_chunk:
            break
    else:
        return {'ID': 0, "Data": 0}
    i = x + z *16 + (y % 16) * 256
    blockID = sub_chunk['Blocks'][i]
    data = sub_chunk['Data'][i // 2]
    if i % 2 == 1:
        data = data >> 4
    else:
        data = data & 0xF
    return {'ID': blockID, 'Data': data}

def get_blockstate_at_115(chunk, x, y, z):
    # Find correct subchunk
    for sub_chunk in chunk['Sections']:
        if sub_chunk['Y'] * 16 <= y < (sub_chunk['Y'] + 1) * 16 and 'Palette' in sub_chunk:
            break
    else:
        return {'Name': 'minecraft:air'}
        #print("AAAAA")
        #raise RuntimeError("AAAAAAAAAAAAAAAAAAAAAAAAA")
    blocks = longs_to_int(sub_chunk['BlockStates'])
    delta = max(4, (len(sub_chunk['Palette']) - 1).bit_length())
    i = x + z * 16 + (y % 16) * 256
    return sub_chunk['Palette'][(blocks >> (i * delta)) & ((1 << delta) - 1)]


def get_blockstate_at_116(chunk, x, y, z):
    # Find correct subchunk
    for sub_chunk in chunk['Sections']:
        if sub_chunk['Y'] * 16 <= y < (sub_chunk['Y'] + 1) * 16 and 'Palette' in sub_chunk:
            break
    else:
        return {'Name': 'minecraft:air'}
    delta = max(4, (len(sub_chunk['Palette']) - 1).bit_length())
    i = x + z * 16 + (y % 16) * 256
    things_per_long = 64 // delta
    which_long_number = i // things_per_long
    the_bits_we_want = sub_chunk['BlockStates'][which_long_number] >> ((i % things_per_long) * delta) # haha you thought we would be readable
    only_the_bits_we_want = the_bits_we_want & ((1<<delta)-1)
    the_block_state_dictionary = sub_chunk['Palette'][only_the_bits_we_want]
    return the_block_state_dictionary



def decode_h_map(chunk, map_name):
    if 1451 <= chunk['DataVersion'] < 2529: # the flattening - right before they changed the format again
        return decode_h_map_115(chunk['Level'], map_name)
    elif 2529 <= chunk['DataVersion']: # new new new
        return decode_h_map_116(chunk['Level'], map_name)
    else:
        return [[255 for z in range(16)] for x in range(16)]

def decode_h_map_115(chunk, map_name):
    heights = [[255 for z in range(16)] for x in range(16)]
    raw_map = longs_to_int(chunk['Heightmaps'][map_name])
    for i in range(256):
        heights[i % 16][i // 16] = min((raw_map >> (i) * 9) & 0x1FF, 255)
    return heights

def decode_h_map_116(chunk, map_name):
    heights = [[255 for z in range(16)] for x in range(16)]

    delta = 9;
    things_per_long = 64 // delta
    raw_map = chunk['Heightmaps'][map_name]
    for i in range(256):
        which_long = i // things_per_long
        heights[i % 16][i // 16] = min((raw_map[which_long] >> ((i % things_per_long) * delta)) & 0x1FF, 255)
    return heights

