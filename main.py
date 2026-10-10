import image_operations
import tkinter as tk
from PIL import ImageTk, Image, ImageOps
import crossfiledialog

import image_operations

# Init window
window = tk.Tk()
window.attributes("-type", "utility")

# Init file operator
imageOp = image_operations.ImageOperator("temp_img.jpg")

# Init variables
lock_first_part = tk.IntVar()
lock_last_part = tk.IntVar()
lock_first_byte = tk.IntVar()
lock_last_byte = tk.IntVar()

# Init image label
img_label = tk.Label()

# Set functions
def load_file():
    imageOp.source_image = crossfiledialog.open_file(filter=["*.jpg", "*.JPG"])
    update_image_data()

def update_image_data(event=None):
    print("-------------------------")
    imageOp.scramble_image(
                    int(parts_slider.get()), 
                    delay_s=0, 
                    start_part_locked=bool(lock_first_part.get()), end_part_locked=bool(lock_last_part.get()),
                    start_byte_locked=bool(lock_first_byte.get()), end_byte_locked=bool(lock_last_byte.get()))
    update_image_element()


def update_image_element():
    img = Image.open(imageOp.target_image_temp_location)
    try:
        img = ImageOps.exif_transpose(img)
    except:
        print("DISPLAY ERROR: Failed to interact with EXIF data")
    img = img.resize((300, 400))

    imgTK = ImageTk.PhotoImage(img)
    img_label.configure(image=imgTK)
    img_label.image = imgTK


# Set geometry
width = 500
height = 500
posx = int((window.winfo_screenwidth() / 2) - width / 2)
posy = int((window.winfo_screenheight() / 2) - height / 2)

window.geometry(f"{width}x{height}+{posx}+{posy}")

# Open Image and Re-Scramble image buttons
img_btn = tk.Button(window, text="Load image", command=load_file)
reload_button = tk.Button(window, text="Re-Scramble image", command=update_image_data)

# Parts Slider
parts_slider = tk.Scale(window, from_=1,to=16, orient="horizontal", command=update_image_data)

# ock first and last byte checkboxes
lock_first_byte_checkbox = tk.Checkbutton(window, text="Lock first byte", variable=lock_first_byte, command=update_image_data)
lock_last_byte_checkbox = tk.Checkbutton(window, text="Lock last byte", variable=lock_last_byte, command=update_image_data)

# Lock first and last part checkboxes
lock_first_part_checkbox = tk.Checkbutton(window, text="Lock first segment", variable=lock_first_part, command=update_image_data)
lock_last_part_checkbox = tk.Checkbutton(window, text="Lock last segment", variable=lock_last_part, command=update_image_data)

# Position elements
img_btn.pack()
reload_button.pack()
img_label.pack()
parts_slider.pack()
lock_first_part_checkbox.pack()
lock_first_byte_checkbox.pack()
lock_last_part_checkbox.pack()
lock_last_byte_checkbox.pack()

# Start main event loop
window.mainloop()