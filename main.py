import tkinter
from tkinter import *
from PIL import ImageTk, Image, ImageDraw, ImageFont
from urllib.request import urlopen
from urllib.error import HTTPError
import tkinter.messagebox as msgbox
from tkinter.filedialog import asksaveasfilename, askopenfilename
from os import mkdir, path

#TODO: Add location for watermark, anchor NW, NE, CENTER, SW, SE, using radiobuttons
#TODO: Option to change colour/opacity for watermark

RAW_IMAGE: Image = None
WATERMARKED_IMAGE: Image = None
LOGO: Image = None
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
        global RAW_IMAGE
        RAW_IMAGE = Image.open(image_loc).convert("RGBA")
        scale_image(RAW_IMAGE)
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


def add_text():
    watermark_label.config(state=NORMAL)
    watermark_label.delete(0, END)
    watermark_label.insert(END, "Insert Watermark text here")
    watermark_import_logo.config(state=DISABLED)
    add_watermark_button.config(command=add_watermark_text)


def add_logo():
    watermark_label.delete(0, END)
    watermark_label.insert(END, "Import from files")
    watermark_label.config(state=DISABLED)
    watermark_import_logo.config(state=NORMAL)
    add_watermark_button.config(command=add_watermark_logo)

def import_logo():
    logo = askopenfilename()
    global LOGO
    LOGO = Image.open(logo).convert("RGBA")


def add_watermark_text():

    # TODO: Create a decorator to remove duplicated code for text/logo
    try:
        width, height = RAW_IMAGE.size
    except AttributeError:
        watermark_label.delete(0, END)
        watermark_label.insert(END, "No image to watermark")
    else:
        text = watermark_label.get()
        text_image = Image.new("RGBA", RAW_IMAGE.size, (255, 255, 255, 0))

        if width < 250:
            anchor_w = width - 5
            anchor_h = height - 5
            font_size = 15
        else:
            anchor_w = width - 25
            anchor_h = height - 25
            font_size = int(width / 15)
        # print(f"{width} {font_size}")
        d = ImageDraw.Draw(text_image)
        font = ImageFont.truetype("arial.ttf", font_size)
        d.text((anchor_w, anchor_h), text, font=font, fill=(0, 0, 0, 128), anchor="rs")
        global WATERMARKED_IMAGE
        WATERMARKED_IMAGE = Image.alpha_composite(RAW_IMAGE, text_image)
        # output_image.show()
        # WATERMARKED_IMAGE.save
        scale_image(WATERMARKED_IMAGE)
        save_img_txt.delete(0, END)
        save_img_txt.focus()


def add_watermark_logo():
    # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.paste
    # or https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.alpha_composite
    try:
        base_width, base_height = RAW_IMAGE.size
        logo_width, logo_height = LOGO.size
    except AttributeError:
        watermark_label.delete(0, END)
        watermark_label.insert(END, "No image/Logo to watermark")
    else:
        # text = watermark_label.get()

        if base_width < 250:
            anchor_w = base_width - 5
            anchor_h = base_height - 5
        else:
            anchor_w = base_width - 25
            anchor_h = base_height - 25

        coords = (anchor_w - logo_width, anchor_h - logo_height, anchor_w, anchor_h)

        global WATERMARKED_IMAGE
        RAW_IMAGE.paste(LOGO, coords)
        WATERMARKED_IMAGE = RAW_IMAGE
        scale_image(WATERMARKED_IMAGE)


def save_image():
    filename = save_img_txt.get()
    file_path = f"watermarked/{filename}.png"

    if path.isfile(file_path):
        confirmation = msgbox.askokcancel("Warning!", "Filename already exists in folder, overwrite file?")
    else:
        confirmation = msgbox.askyesno(f"{filename}",
                                       f"Would you like to save image as {filename}?")
    if confirmation:
        try:
            rgb_im = WATERMARKED_IMAGE.convert("RGB")
            rgb_im.save(file_path)
        except AttributeError:
            pass
        except FileNotFoundError:
            mkdir("watermarked")
            rgb_im.save(file_path)
        else:
            msgbox.showinfo("Get in", "Image saved")


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
watermark_variable = tkinter.StringVar()
# Text
watermark_text = Radiobutton(window, text=" Text ", bg=FG, indicatoron=False, value="text", variable=watermark_variable,
                             command=add_text)
watermark_text.grid(row=6, column=2)
watermark_label = Entry(width=32, state=DISABLED)
watermark_label.grid(row=7, column=2, columnspan=2)

# Logo
watermark_logo = Radiobutton(window, text=" Logo ", bg=FG, indicatoron=False, value="logo", variable=watermark_variable,
                             command=add_logo)
watermark_logo.grid(row=6, column=3, padx=(0, 30))
watermark_import_logo = Button(text="Choose Logo", command=import_logo, state=DISABLED)
watermark_import_logo.grid(row=8, column=2)

add_watermark_button = Button(text="Add")
add_watermark_button.grid(row=8, column=3, columnspan=2)

save_title = Label(text="Save as PNG", fg=FG, bg=BG, font=HEADERS)
save_title.grid(row=9, column=2, columnspan=2, pady=Y_PAD)
save_img_txt = Entry(width=20)
save_img_txt.grid(row=10, column=2)
save_button = Button(text="Save", command=save_image)
save_button.grid(row=10, column=3,)

original_size = Label(text="Original Size:", bg=BG, fg=FG)
original_size.grid(row=12, column=2)
original_size_text = Label(text="", bg=BG, fg=FG)
original_size_text.grid(row=12, column=3)
rescaled_size = Label(text="Rescaled Size:", bg=BG, fg=FG)
rescaled_size.grid(row=13, column=2)
rescaled_size_text = Label(text="", bg=BG, fg=FG)
rescaled_size_text.grid(row=13, column=3)
window.mainloop()

