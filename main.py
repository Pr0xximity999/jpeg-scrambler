import os, time

source_path = "./image.jpg"

size = os.path.getsize(source_path)
with open("./image.jpg", "rb") as source, open("./new_img.jpg", 'wb') as dest:
    while True:
        chunk = source.read(50000)
        if not chunk:
            break
        dest.write(chunk)
        time.sleep(1)