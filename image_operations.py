from os.path import exists, isdir, isfile
import struct
import os, time, math, random

class ImageOperator:
    def __init__(self, temp_file_name:str, cahce_folder:str="cache"):
        self.cache_folder = cahce_folder
        self.file_temp_location = cahce_folder + temp_file_name

    def set_source_image(self, file_path:str):
        self.source_image = file_path

    def find_SOS_segment(self) -> tuple[int, int, int] | None:
        if not self.source_image:
            raise ValueError("READ ERROR: Source image path has not been set")

        with open(self.source_image, "rb") as file:
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


    def scramble_image(self, 
                        parts_num:int, 
                        delay_s:int=0,
                        start_part_locked:bool=False, end_part_locked:bool=False,
                        start_byte_locked:bool=False, end_byte_locked:bool=False):

        if not self.source_image:
            raise ValueError("READ ERROR: Source image path has not been set")
        
        # Find the start of the SOS data
        data = self.find_SOS_segment()

        if not data:
            raise ValueError("No SOS data found in JPEG")

        # The silly parse
        start_byte_locked = int(start_byte_locked)
        end_byte_locked = int(end_byte_locked )

        # Calculate image data values
        offset_sos, size_sos_marker, offset_eoi = data
        offset_sos += start_byte_locked
        offset_sos_true = offset_sos + size_sos_marker + 2 #2 for the marker size
        size_sos = offset_eoi - offset_sos_true - end_byte_locked

        print(f"READ: Found sos marker at {hex(offset_sos)} with size {size_sos_marker}")
        print(f"READ: eoi marker found at {hex(offset_eoi)} making the total sos section the size of {size_sos} bytes")
        print(f"READ: non sos data starts at offset {hex(offset_sos_true)} and has the size of {size_sos} bytes")

        print(f"READ: Left offset override: +{start_byte_locked}, Right offset override: -{end_byte_locked}")

        # Calculate the number and order of the file parts
        part_size = math.ceil(size_sos / parts_num)

        # Generate list of parts and positions
        parts = list(range(0, parts_num))
        positions = list(range(0, parts_num))
        random.shuffle(positions)

        # Lock the position of the first or last slice to their actual spot by swapping the index of their randomized value with their proper one
        # This guarantees the entire image renders correctly, unless the start and end offsets are used
        if(start_part_locked):
            index_first_part = positions.index(0) # 0 is the value i'm looking for, not the index (thats what im trying to find)
            positions[index_first_part] = positions[0]
            positions[0] = 0

        if(end_part_locked):
            index_first_part = positions.index(len(positions) - 1)
            positions[index_first_part] = positions[-1]
            positions[-1] = len(positions) - 1
        
        # Create the image cache folder if it doesn't exist
        if not os.path.isdir(self.cache_folder):
            os.mkdir(self.cache_folder)

        # Write chunks
        with open(self.source_image, "rb") as source, open(self.file_temp_location, 'wb') as dest:
            # Write everything before the sensor data
            dest.write(source.read(offset_sos_true - 1)) # -1 because it is before the SOS data address

            # Write the End Of Image section
            source.seek(offset_eoi - end_byte_locked)
            dest.seek(source.tell())
            dest.write(source.read(2 + end_byte_locked)) # EOI is 2 bytes, override is added


            # Write in between, randomly
            for part in parts:
                position = positions[part]
                offset_old = (part_size * part) + offset_sos_true
                offset_new = (part_size * position) + offset_sos_true
                source.seek(offset_old)
                dest.seek(offset_new)

                dest.write(source.read(part_size))
                print(f"WRITE: Writing part {part}({hex(offset_old)}) to position {position}({hex(offset_new)})")
                time.sleep(delay_s)
            
            print("WRITE: Finished writing all parts")