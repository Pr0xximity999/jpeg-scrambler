from file_operations import transfer_file
import tkinter as tk
from PIL import ImageTk, Image, ImageOps
from tkinter import Button, Label
import crossfiledialog

# Init variables
source_path= ""
dest_path = "new_image.jpg"
parts = 8

# Init window
window = tk.Tk()
window.attributes("-type", "utility")

# Init image label
img_label = Label()


# Set functions
def load_file():
    global source_path
    source_path = crossfiledialog.open_file(filter=["*.jpg", "*.JPG"])
    transform_file()
    
def transform_file():
    global source_path, dest_path, parts
    transfer_file(source_path, dest_path, parts, 0)

    # load image
    img = Image.open(dest_path)
    try:
        img = ImageOps.exif_transpose(img)
    except:
        print("ERROR: Failed to interact with EXIF data")
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

# Load buttons
img_btn = Button(window, text="Load image", command=load_file)
reload_button = Button(window, text="Re-Scramble image", command=transform_file)

# Position elements
img_btn.pack()
reload_button.pack()
img_label.pack()

# Start main event loop
window.mainloop()