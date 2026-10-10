import image_operations
import tkinter as tk
from PIL import ImageFile, ImageTk, Image, ImageOps
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
img = ImageFile.ImageFile

# Init image label and frames
frame_left = tk.Frame(window, bg="grey")
frame_right = tk.Frame(window, bg="dark grey")
img_label = tk.Label(frame_left)

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
    global img
    img = Image.open(imageOp.target_image_temp_location)
    try:
        img = ImageOps.exif_transpose(img)
    except:
        print("DISPLAY ERROR: Failed to interact with EXIF data")
    img = img.resize((img_label.winfo_width(), 400))

    imgTK = ImageTk.PhotoImage(img)
    img_label.configure(image=imgTK)
    img_label.image = imgTK

def on_resize(event):
    global img
    if event.widget == window:
        img = img.resize((img_label.winfo_width(), 400))
        imgTK = ImageTk.PhotoImage(img)
        img_label.configure(image=imgTK)
        img_label.image = imgTK


# Set geometry
width = 500
height = 500
posx = int((window.winfo_screenwidth() / 2) - width / 2)
posy = int((window.winfo_screenheight() / 2) - height / 2)

window.geometry(f"{width}x{height}+{posx}+{posy}")

# Frame elements
frame_locks = tk.Frame(frame_right)
frame_locks_left = tk.Frame(frame_locks)
frame_locks_right = tk.Frame(frame_locks)

# Open Image and Re-Scramble image buttons
img_btn = tk.Button(frame_right, text="Load image", command=load_file)
reload_button = tk.Button(frame_right, text="Re-Scramble image", command=update_image_data)

# Parts Slider
parts_slider = tk.Scale(frame_right, from_=1,to=16, orient="horizontal", command=update_image_data)

# ock first and last byte checkboxes
lock_first_byte_checkbox = tk.Checkbutton(
    frame_locks_left, 
    text="Lock first\nbyte", 
    variable=lock_first_byte, 
    command=update_image_data,
)

lock_last_byte_checkbox = tk.Checkbutton(
    frame_locks_right, 
    text="Lock last\nbyte", 
    variable=lock_last_byte, 
    command=update_image_data,
)

# Lock first and last part checkboxes
lock_first_part_checkbox = tk.Checkbutton(
    frame_locks_left, 
    text="Lock first\nsegment", 
    variable=lock_first_part, 
    command=update_image_data,
)

lock_last_part_checkbox = tk.Checkbutton(
    frame_locks_right, 
    text="Lock last\nsegment", 
    variable=lock_last_part, 
    command=update_image_data,
)

# UI positioning
frame_left.place(relwidth=0.6, relheight=1, relx=0, rely=0)
img_label.place(relwidth=1, relheight=1)


frame_right.place(relwidth=0.4, relheight=1, relx=0.6, rely=0)
img_btn.place(relwidth=1, relheight=0.1, rely=0)
parts_slider.place(relwidth=1, relheight=0.1, rely=0.1)
reload_button.place(relwidth=1, relheight=0.1, rely=0.2)


frame_locks.place(relwidth=1, relheight=0.25, rely=0.75)
frame_locks_left.place(relwidth=0.5, relheight=1)
lock_last_part_checkbox.place(relwidth=1, relheight=0.5)
lock_last_byte_checkbox.place(relwidth=1, relheight=0.5, rely=0.5)

frame_locks_right.place(relwidth=0.5, relheight=1, relx=0.5)
lock_first_part_checkbox.place(relwidth=1, relheight=0.5)
lock_first_byte_checkbox.place(relwidth=1, relheight=0.5, rely=0.5)

# Bindings
window.bind("<Configure>", on_resize)

# Start main event loop
window.mainloop()