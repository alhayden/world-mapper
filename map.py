#!/usr/bin/env python3
import argparse
import chunks
import math
import sys
import os
import imager
from PIL import Image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("min_x", type=int, help="The X coordinate of the bottom left of the map.")
    parser.add_argument("min_z", type=int, help="The Z coordinate of the bottom left of the map.")
    parser.add_argument("max_x", type=int, help="The width of the map (along X)")
    parser.add_argument("max_z", type=int, help="The height of the map (along Z)")
    parser.add_argument("output_file", help="The .ppm file to output the image to")
    parser.add_argument("data_directory", help="The directory where region files are stored")
    parser.add_argument("map_type", default='minecraft', help='The type of map to generate')#, choices=['heightmap', 'minecraft'])
    args = parser.parse_args()
    x_start = math.floor(args.min_x / 16 / 32)
    z_start = math.floor(args.min_z / 16 / 32)
    x_end = math.floor(args.max_x / 16 / 32)
    z_end = math.floor(args.max_z / 16 / 32)
    if args.map_type not in ['minecraft', 'heightmap'] and args.map_type[:2] != 'y=':
        args.map_type = 'minecraft';
    
    progress = 0
    image = Image.new('RGB', (args.max_x - args.min_x, args.max_z - args.min_z))
#    image = [[None for z in range(args.max_x - args.min_x)] for x in range(args.max_z - args.min_z)]
    for x in range(x_start, x_end+1):
        r_x = x * 512

        for z in range(z_start, z_end+1):
            progress += 1
            status = f", region {progress} of {(x_end - x_start + 1) * (z_end - z_start + 1)}     "
            r_z = z * 512
            loaded_chunks = {}
            try:
                loaded_chunks.update(chunks.read_mca(os.path.join(args.data_directory, f"r.{x}.{z-1}.mca")))
            except FileNotFoundError:
                pass
            try:
                loaded_chunks.update(chunks.read_mca(os.path.join(args.data_directory, f"r.{x}.{z}.mca")))
            except FileNotFoundError:
                continue
            length = 512

            if args.min_z > r_z:
                length -= (args.min_z - r_z)
            if args.max_z < r_z + 512:
                length -= (r_z + 512 - args.max_z)

            width = 512
            if args.min_x > r_x:
                width -= (args.min_x - r_x)
            if args.max_x < r_x + 512:
                width -= (r_x + 512 - args.max_x)
            image_chunk = imager.make_image(loaded_chunks, (width, length), (max(args.min_x, r_x), max(args.min_z, r_z)), mode=args.map_type, status=status)

            orig_x = max(args.min_x, r_x)
            orig_z = max(args.min_z, r_z)
            for a in range(len(image_chunk[0])):
                for b in range(len(image_chunk)):
                    # image[orig_z + b - args.min_z][orig_x + a - args.min_x] = image_chunk[b][a];
                    image.putpixel((orig_x + a - args.min_x, orig_z + b - args.min_z), image_chunk[b][a])
#    print(image)
    image.save(args.output_file)
    # with open(args.output_file, "w") as f:
    #     f.write("P3\n")
    #     f.write(f"{len(image[0])} {len(image)}\n")
    #     f.write("255\n")
    #     for row in image:
    #         for PicEl in row:
    #             for color in PicEl:
    #                 f.write(f"{color} ")

if __name__ == '__main__':
    main()
