import os, time

source_path = "./image.jpg"
dest_path = "./new_image.jpg"
chunk = 500

size = os.path.getsize(source_path)
with open(source_path, "rb") as source, open(dest_path, 'wb') as dest:
    # Write first chunk
    dest.write(source.read(chunk))

    # Write last chunk
    dest.seek(size - chunk)
    dest.seek(size - chunk)
    dest.write(source.read())

    # Write the middle
    source.seek(chunk)
    dest.seek(chunk)
    while True:
        part = source.read(chunk)
        if not part:
            break
        dest.write(part)
        time.sleep(1)