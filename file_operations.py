import os, time, math, random

def transfer_file(source_path:str, dest_path:str, parts_num:int, delay_s:int=0):

    # Calculate the number and order of the file parts
    file_size = os.path.getsize(source_path)
    part_size = math.ceil(file_size / parts_num)

    # Generate list of parts and positions
    # end is exclusive, but the last part is written separately
    parts = list(range(2, parts_num))
    positions = list(range(2, parts_num))
    random.shuffle(positions)

    # Transfer chunks
    with open(source_path, "rb") as source, open(dest_path, 'wb') as dest:
        # Write first chunk
        dest.write(source.read(part_size))
        print(part_size)

        # Write last chunk
        source.seek(file_size - part_size)
        print(file_size - part_size)
        dest.seek(file_size - part_size)
        dest.write(source.read(part_size))


        # Write in between, randomly
        for part in parts:
            position = positions[part - 2] #preventing reading out of bounds
            source.seek(part_size * part)
            dest.seek(part_size * position)

            dest.write(source.read(part_size))
            print(f"Writing part {part} to position {position} at byte {part_size * position}")
            time.sleep(delay_s)
        
        print("Finished writing all parts")