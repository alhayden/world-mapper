from chunkreader import decode_h_map, get_blockstate_at
import math
import json

BG_COLOR = (0xD6, 0xBE, 0x96)

color_list = json.loads(open('color_palette.json','r').read())['colors']
color_map = json.loads(open('palette.json', 'r').read())


def make_image(chunks, size, origin, mode='minecraft', status='     '):
    image = [[BG_COLOR for i in range(size[0])] for z in range(size[1])]
    progress = 0
    if mode[:2] == 'y=':
        y = int(mode[2:])

    for chunkX in range(origin[0] // 16, math.ceil((size[0] + origin[0])/ 16)):
        prev_heights = None
        for chunkZ in range(origin[1] // 16 - 1, math.ceil((size[1] + origin[1])/ 16)):
            if (chunkX, chunkZ) not in chunks:
                prev_heights = None
                continue
            progress += 1
            print(f" Working on chunk {progress} of ~{(size[0] // 16 + 2) * (size[1] // 16 + 2)}{status}", end='\r')
            chunk = chunks[chunkX, chunkZ]['Level']
            chunk['DataVersion'] = chunks[chunkX, chunkZ]['DataVersion']
            base_x = chunk['xPos'] * 16
            base_z = chunk['zPos'] * 16

            if base_x < origin[0] - 16 or base_z < origin[1] - 16:
                continue
            if base_x > origin[0] + size[0] or base_z > origin[1] + size[1]:
                continue
            if 'Heightmaps' not in chunk or 'WORLD_SURFACE' not in chunk['Heightmaps'] or 'Sections' not in chunk:
                continue
            if mode[:2] == 'y=':
                heights = [[y for z in range(16)] for x in range(16)]
                ocean_heights = [[y for z in range(16)] for x in range(16)]
            else:
                heights = decode_h_map({'Level': chunk, 'DataVersion':chunk['DataVersion']}, 'WORLD_SURFACE')
                ocean_heights = decode_h_map({'Level': chunk, 'DataVersion':chunk['DataVersion']}, 'OCEAN_FLOOR')
            if mode == 'minecraft' or mode[:2] == 'y=':
                #blocks = make_block_map(chunk)
                pass
            for i in range(256):
                x = i % 16
                z = i // 16
                y = heights[x][z]
                if mode == 'minecraft' or mode[:2] == 'y=':
                    color = get_color_from_block(chunk, heights, prev_heights, ocean_heights, x, y, z)

                if base_x + x < origin[0] or base_z + z < origin[1]:
                    continue
                if base_x + x >= origin[0] + size[0] or base_z + z >= origin[1] + size[1]:
                    continue;
                if mode == 'heightmap':
                    image[base_z + z - origin[1]][base_x + x - origin[0]] = (y, y, y)
                if mode == 'minecraft' or mode[:2] == 'y=':
                    image[base_z + z - origin[1]][base_x + x - origin[0]] = color#get_color_from_block(blocks, heights, prev_heights, ocean_heights, x, y, z)
            prev_heights = heights
    return image

def make_block_map(chunk):
    block_map = [[[{'Name':'minecraft:air'} for z in range(16)] for y in range(256)] for x in range(16)] # default block is air
    for sub_chunk in chunk['Sections']:
        base_y = 16 * sub_chunk['Y']
        if 'Palette' not in sub_chunk:
            continue
        palette = sub_chunk['Palette']

        blocks = decoder.longs_to_int(sub_chunk['BlockStates'])
        delta = max(4, (len(palette) - 1).bit_length())
        for i in range(4096):
            block_map[i % 16][i // 256 + base_y][(i // 16) % 16] = palette[(blocks >> ((i) * delta)) & ((1 << (delta)) - 1)]
    return block_map


def get_color_from_block(chunk, heights, northern_heights, ocean_heights, x, y, z):
    mapped_color = color_map.setdefault(str(get_blockstate_at({'Level': chunk, 'DataVersion':chunk['DataVersion']}, x, y, z)), 0)

    while mapped_color == 0 and y >= 0: # scan down through transparent blocks
        y -= 1
        mapped_color = color_map.setdefault(str(get_blockstate_at({'Level': chunk, 'DataVersion':chunk['DataVersion']}, x, y, z)), 0)
        heights[x][z] = y

    if y <= 0:
        mapped_color = 11

    if mapped_color == 0: # invalid color detected!
        return BG_COLOR

    if mapped_color == 12:
        return get_water_color(chunk, heights, ocean_heights, x, y, z)

    c = tuple(color_list[mapped_color][0:3])

    if z != 0:
        if heights[x][z] < heights[x][z-1]:
            c = c[0] * 180 // 255, c[1] * 180 // 255, c[2] * 180 // 255
        elif heights[x][z] == heights[x][z-1]:
            c = c[0] * 220 // 255, c[1] * 220 // 255, c[2] * 220 // 255
    elif northern_heights is not None:
        if heights[x][z] < northern_heights[x][15]:
            c = c[0] * 180 // 255, c[1] * 180 // 255, c[2] * 180 // 255
        if heights[x][z] == northern_heights[x][15]:
            c = c[0] * 220 // 255, c[1] * 220 // 255, c[2] * 220 // 255

    return c


def get_water_color(chunk, heights, ocean_heights, x, y, z):
    depth = y - ocean_heights[x][z]
    if y != heights[x][z]:
        surface_y = y
        while color_map.setdefault(str(get_blockstate_at({'Level': chunk, 'DataVersion':chunk['DataVersion']}, x, y, z)), 0) in (1, 12):
            y -= 1
        depth = surface_y - y
    c = tuple(color_list[12][0:3])
    c_med = c[0] * 220 // 255, c[1] * 220 // 255, c[2] * 220 // 255
    c_dark = c[0] * 180 // 255, c[1] * 180 // 255, c[2] * 180 // 255

    if depth == 0 or depth == 1:
        return c
    elif depth == 2 or depth == 3:
        if (x + z) % 2 == 0:
            return c
        else:
            return c_med
    elif depth == 4 or depth == 5:
        return c_med
    elif depth >= 6 and depth <= 8:
        if (x + z) % 2 == 0:
            return c_med
        else:
            return c_dark
    elif depth > 8:
        return c_dark
    else:
        # print(depth)
        return c_dark
