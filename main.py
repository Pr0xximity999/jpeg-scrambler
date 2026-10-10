from file_operations import scramble_image, find_SOS_segment
import tkinter as tk
from PIL import ImageTk, Image, ImageOps
import crossfiledialog

# Init window
window = tk.Tk()
window.attributes("-type", "utility")

# Init variables
source_path= ""
dest_path = "new_image.jpg"
lock_first_part = tk.IntVar()
lock_last_part = tk.IntVar()
lock_first_byte = tk.IntVar()
lock_last_byte = tk.IntVar()

# Init image label
img_label = tk.Label()
    

# Set functions
def load_file():
    global source_path
    source_path = crossfiledialog.open_file(filter=["*.jpg", "*.JPG"])
    update_image_data()
    


def update_image_data(event=None):
    print("-------------------------")
    global source_path, dest_path, parts
    scramble_image(source_path, dest_path, 
                    int(parts_slider.get()), 
                    delay_s=0, 
                    start_part_locked=bool(lock_first_part.get()), end_part_locked=bool(lock_last_part.get()),
                    start_byte_locked=bool(lock_first_byte.get()), end_byte_locked=bool(lock_last_byte.get()))
    update_image_element()


def update_image_element():
    global dest_path
    img = Image.open(dest_path)
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