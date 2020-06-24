import chunks
import decoder
import json
import NBTparser

json_dump = {}

chunk_array = chunks.read_mca('./region/r.0.0.mca').values()

blocks = [[None for z in range(512)] for x in range(512)]
Y_VAL = 70

for chunk in chunk_array:
    c_x = chunk['Level']['xPos'] * 16
    c_z = chunk['Level']['zPos'] * 16
    for section in chunk['Level']['Sections']:
        if section['Y'] != 4:
            continue
        if 'Palette' not in section:
            continue
        palette = section['Palette']
        block_states = decoder.longs_to_int(section['BlockStates'])
        delta = max(4, (len(palette) - 1).bit_length())
        for i in range(4096):

            if i // 256 == 6:
                blocks[c_x + i % 16][c_z + ((i // 16) % 16)] = palette[(block_states >> (i * delta)) & ((1 << delta) - 1)]

for i in range(9):
    map_nbt = NBTparser.read_nbt(f"./data/map_{i}.dat")['data']
    z_c = map_nbt['zCenter']
    x_c = map_nbt['xCenter']
    z = z_c - 64
    x = x_c - 64
    for v in range(16384):
        colorID = map_nbt['colors'][v] // 4
        matching_block = blocks[x + (v % 128)][z + (v // 128)]
        json_dump[str(matching_block)] = colorID

print(blocks[1][3])

with open("palette.json", "w") as f:
    f.write(json.dumps(json_dump))


