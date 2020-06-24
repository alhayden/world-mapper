import os
import io
import zlib
import time
import struct
import NBTparser

def get_locations(region_file):
    chunks = []
    for i in range(1024):
        loc = struct.unpack('>i', b'\0' + region_file.read(3))[0]
        sector_count = struct.unpack('b', region_file.read(1))[0]
        # print(f"Sector count = {sector_count}")
        if loc != 0:
            chunks.append(loc * 4096)
    return chunks

def read_mca(fname):
    chunks = {}
    with open(fname, 'rb') as f:
        chunk_locations = get_locations(f)
        # print([round(c / 1_000_000) for c in chunk_locations])
        for loc in chunk_locations:
            # print(f"\nChunk begins at {loc}")
            f.seek(loc)
            # print(f"bad {f.read(4)}")
            f.seek(loc)
            length = struct.unpack('>i', f.read(4))[0]
            # print(f"Chunk length is {length}")
            compression_type = struct.unpack('B', f.read(1))[0]
            # print(f"Compression type is {compression_type}")
            compressed_data = f.read(length - 1)
            # print(f"Compressed data has length {len(compressed_data)}")
            raw_nbt = zlib.decompress(compressed_data)
            nbt_view = io.BytesIO(raw_nbt)
            chunk = {}
            NBTparser.decode_nbt(nbt_view, NBTparser.get_type(nbt_view), chunk)
            if '' in chunk:
                chunk = chunk['']
            chunks[chunk['Level']['xPos'], chunk['Level']['zPos']] = chunk
            if chunk['Level']['xPos'] == 0 and chunk['Level']['zPos'] == 2:
                with open("c.0.2.nbt", 'wb') as tmp_f:
                    tmp_f.write(raw_nbt)
    return chunks

def main():
    print("start")
    start = time.time()
    chunks = read_mca("r.0.0.mca")
    d = time.time() - start
    print(chunks[(0,0)])
    print(f"finished in {d} seconds, {d*1429 / 60 / 60} hours for all")
    # print(chunks)

if __name__ == '__main__':
    main()
