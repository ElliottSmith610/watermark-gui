from tkinter import *
from PIL import ImageTk, Image, ImageDraw, ImageFont
from urllib.request import urlopen
from urllib.error import HTTPError
import tkinter.messagebox
from tkinter.filedialog import asksaveasfilename, askopenfilename
from os import mkdir

#TODO: Add location for watermark, anchor NW, NE, CENTER, SW, SE, using radiobuttons
#TODO: Option to change colour/opacity for watermark

RAW_IMAGE = None
WATERMARKED_IMAGE = None
BG = "black"
FG = "white"

HEADERS = ("Callibri", 16, "bold")
Y_PAD = (10, 0)

window = Tk()
window.title("Watermark Generator")
window.geometry("800x520")
window.config(bg=BG)  # padx=10, pady=10,
window.maxsize(width=740, height=520)
window.minsize(width=740, height=520)

canvas = Canvas(width=500, height=500, bg="grey", highlightthickness=0)
canvas.grid(row=0, column=0, rowspan=20, padx=(10, 10), pady=(10, 10))

title = Label(text="Watermark\nGenerator", bg=BG, fg=FG,
              font=("Callibri", 20, "bold"))
title.grid(row=0, column=2, columnspan=2, pady=(20, 10))


def import_file():
    try:
        image_loc = askopenfilename()
        image = Image.open(image_loc)
        global RAW_IMAGE
        RAW_IMAGE = image.convert("RGBA")
        scale_image(image)
        watermark_label.delete(0, END)
        watermark_label.focus()
    except AttributeError:
        pass


def import_url():
    try:
        image = Image.open(urlopen(entry_url.get()))
        global RAW_IMAGE
        RAW_IMAGE = image.convert("RGBA")
        scale_image(image)
        watermark_label.delete(0, END)
        watermark_label.focus()
    except ValueError:
        entry_url.delete(0, END)
        entry_url.insert(END, "Paste valid img url!")
    except HTTPError:
        entry_url.delete(0, END)
        entry_url.insert(END, "Forbidden from site, try downloading first")


def scale_image(image):

    width, height = image.size
    # print(f"Width: {width} - {width / 500}")
    # print(f"Height: {height} - {height / 500}")
    size_str = f"{width}x{height}"
    original_size_text.configure(text=size_str)
    # If Image is greater than the canvas, reduces image size to
    # maxwidth and a % of height, keeping aspect ratio
    if (width / 500) > 1 or (height / 500) > 1:
        width_percent = 500 / width
        hsize = int(height * width_percent)
        # print(f"% - {width_percent}")
        display_image = image.resize((500, hsize))

        pwidth, pheight = display_image.size  # using p prefix to differentiate from original width/height
        if (pheight / 500) > 1:
            height_percent = 500 / pheight
            wsize = int(pwidth * height_percent)
            display_image = display_image.resize((wsize, 500))
            pwidth, pheight = display_image.size
        rescaled_size_text.config(text=f"{pwidth}x{pheight}")
    else:
        rescaled_size_text.config(text=f" - - - ")
        display_image = image

    # raw_image = ImageTk.PhotoImage(image)  # ImageTk.PhotoImage(
    display_image = ImageTk.PhotoImage(display_image)
    canvas.image = display_image
    canvas.itemconfig(image_container, image=canvas.image)


def add_watermark_text():

    try:
        text_image = Image.new("RGBA", RAW_IMAGE.size, (255, 255, 255, 0))
    except AttributeError:
        watermark_label.delete(0, END)
        watermark_label.insert(END, "No image to watermark")
    else:
        text = watermark_label.get()
        width, height = RAW_IMAGE.size

        if width < 250:
            anchor_w = width - 5
            anchor_h = height - 5
            font_size = 15
        else:
            anchor_w = width - 25
            anchor_h = height - 25
            font_size = int(width / 15)
        print(f"{width} {font_size}")
        d = ImageDraw.Draw(text_image)
        font = ImageFont.truetype("arial.ttf", font_size)
        d.text((anchor_w, anchor_h), text, font=font, fill=(0, 0, 0, 128), anchor="rs")
        output_image = Image.alpha_composite(RAW_IMAGE, text_image)
        # output_image.show()
        global WATERMARKED_IMAGE
        WATERMARKED_IMAGE = output_image
        WATERMARKED_IMAGE.save
        scale_image(output_image)
        save_img_txt.delete(0, END)
        save_img_txt.focus()

def add_watermark_logo():
    # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.paste
    pass

def save_image():
    try:
        rgb_im = WATERMARKED_IMAGE.convert("RGB")
        mkdir("watermarked")
    except AttributeError:
        pass
    except FileExistsError:
        pass
    else:
        rgb_im.save(f"watermarked/{save_img_txt.get()}.png")


image_container = canvas.create_image(250, 250)

source_title = Label(text="Source IMG", bg=BG, fg=FG, font=HEADERS)
source_title.grid(row=1, column=2, columnspan=2, pady=Y_PAD)
open_file = Button(text="Choose Picture From File", command=import_file)
open_file.grid(row=2, column=2, columnspan=2)

entry_url = Entry(width=32)
entry_url.grid(row=3, column=2, pady=(20, 1), columnspan=2)
open_url = Button(text="Choose Picture From URL", command=import_url)
open_url.grid(row=4, column=2, columnspan=2)

watermark_title = Label(text="Watermark", bg=BG, fg=FG, font=HEADERS)
watermark_title.grid(row=5, column=2, columnspan=2, pady=Y_PAD)
watermark_label = Entry(width=32)
watermark_label.insert(END, "Insert Watermark text here")
watermark_label.grid(row=6, column=2, columnspan=2)
add_watermark_button = Button(text="Add Watermark", command=add_watermark_text)
add_watermark_button.grid(row=7, column=2, columnspan=2)

save_title = Label(text="Save as PNG", fg=FG, bg=BG, font=HEADERS)
save_title.grid(row=8, column=2, columnspan=2, pady=Y_PAD)
save_img_txt = Entry(width=20)
save_img_txt.grid(row=9, column=2)
save_button = Button(text="Save", command=save_image)
save_button.grid(row=9, column=3,)

original_size = Label(text="Original Size:", bg=BG, fg=FG)
original_size.grid(row=11, column=2)
original_size_text = Label(text="", bg=BG, fg=FG)
original_size_text.grid(row=11, column=3)
rescaled_size = Label(text="Rescaled Size:", bg=BG, fg=FG)
rescaled_size.grid(row=12, column=2)
rescaled_size_text = Label(text="", bg=BG, fg=FG)
rescaled_size_text.grid(row=12, column=3)
window.mainloop()

