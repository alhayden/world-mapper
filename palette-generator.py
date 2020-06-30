#! /bin/python3
import chunks
import chunkreader
import json
import NBTparser
import argparse
from os import listdir

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('world', help='the path to the world file')
    args = parser.parse_args()
    world_dir = args.world
    json_dump = {}

    chunk_dict = chunks.read_mca(f'{world_dir}/region/r.0.0.mca')

    Y_VAL = 70

    for path in listdir(f'{world_dir}/data/'):
        if not path.split('/')[-1].startswith('map_'):
            continue
        print(f'working on {path}...')
        map_nbt = NBTparser.read_nbt(f'{world_dir}/data/{path}')['data']
        z_c = map_nbt['zCenter']
        x_c = map_nbt['xCenter']
        z = z_c - 64
        x = x_c - 64
        for v in range(16384):
            v_x = x + (v % 128)
            v_z = z + (v // 128)
            colorID = map_nbt['colors'][v] // 4
            if (v_x // 16, v_z // 16) not in chunk_dict:
                chunk_dict.update(chunks.read_mca(f'{world_dir}/region/r.{v_x // 512}.{v_z // 512}.mca'))
                print(f'loaded region {v_x//512}.{v_z//512}...')
            matching_block = chunkreader.get_blockstate_at(chunk_dict[v_x // 16, v_z // 16], v_x % 16, Y_VAL, v_z % 16)

            json_dump[str(matching_block)] = colorID

    with open(f"palettes/palette.json", "w") as f:
        f.write(json.dumps(json_dump))

if __name__ == '__main__':
    main()
