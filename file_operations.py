import struct
import os, time, math, random

# WIP: Try and find the start of scan (SOS) segment for better image splicing
def find_SOS_segment(file_path):
    with open(file_path, "rb") as file:
        offset_sos = 0
        size_sos_marker = 0
        offset_eoi = 0
        # Verify if the file is an actual JPEG
        if file.read(2) != b"\xff\xd8":
            raise ValueError("Supplied file not a JPEG")

        while True:

            # Grab next Byte
            b = file.read(1)
            if not b:
                return None

            # Search until the first marker
            if b != b"\xFF":
                continue

            # Grab the marker descriptor
            marker = file.read(1)
            while marker == b"\xFF":
                marker = file.read(1)
            
            if not marker:
                return None

            mark = marker[0]

            # Found SOS
            if mark == 0xDA:
                offset_sos = file.tell() - 2
                size_sos_marker = struct.unpack(">H", file.read(2))[0] # Reads the first 2 bytes, big endian (>) uint16 (H)

            # Found other segment
            if mark == 0x01 or 0xD0 <= mark <= 0xD8 or mark == 0x00:
                continue # markers with no length field
            if mark == 0xD9: # EOI was found before SOS
                offset_eoi = file.tell() - 2
                break

            # If the segment has a length field, use it to skip the entire segment
            seg_len = struct.unpack(">H", file.read(2))[0]
            file.seek(seg_len - 2, 1) # skip segment payload

        return offset_sos, size_sos_marker, offset_eoi


def scramble_image(source_path:str, dest_path:str, parts_num:int, delay_s:int=0, end_locked:bool=False):
    # Find the start of the SOS data
    data = find_SOS_segment(source_path)

    if not data:
        raise ValueError("No SOS data found in JPEG")

    # Calculate image data values
    offset_sos, size_sos_marker, offset_eoi = data
    offset_sos_true = offset_sos + size_sos_marker + 2 #2 for the marker size
    size_sos = offset_eoi - offset_sos_true

    print(f"Found sos marker at {hex(offset_sos)} with size {size_sos_marker}")
    print(f"eoi marker found at {hex(offset_eoi)} making the total sos section the size of {size_sos} bytes")
    print(f"non sos data starts at offset {hex(offset_sos_true)} and has the size of {size_sos} bytes")

    # Calculate the number and order of the file parts
    part_size = math.ceil(size_sos / parts_num)

    # Generate list of parts and positions
    parts = list(range(0, parts_num))
    positions = list(range(0, parts_num))
    random.shuffle(positions)

    # Lock the position of the last slice to the first spot by swapping value 0 with whats on index 0
    # This guarantees the entire image renders correctly
    if(end_locked):
        index_first_part = positions.index(len(positions) - 1) # 0 is the value i'm looking for, not the index (thats what im trying to find)
        positions[index_first_part] = positions[-1]
        positions[-1] = len(positions) - 1

    # Write chunks
    with open(source_path, "rb") as source, open(dest_path, 'wb') as dest:
        # Write everything before the sensor data
        dest.write(source.read(offset_sos_true - 1 + 32 * 8)) # -1 because it is before the SOS data address

        # Write the End Of Image section
        source.seek(offset_eoi)
        dest.seek(source.tell())
        dest.write(source.read(2)) # EOI is 2 bytes


        # Write in between, randomly
        for part in parts:
            position = positions[part]
            offset_old = (part_size * part) + offset_sos_true
            offset_new = (part_size * position) + offset_sos_true
            source.seek(offset_old)
            dest.seek(offset_new)

            dest.write(source.read(part_size))
            print(f"Writing part {part}({hex(offset_old)}) to position {position}({hex(offset_new)})")
            time.sleep(delay_s)
        
        print("Finished writing all parts")