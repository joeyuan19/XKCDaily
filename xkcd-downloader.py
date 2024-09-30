from __future__ import print_function, division
from bs4 import BeautifulSoup as bs
from urllib2 import urlopen
from PIL import Image, ImageFont, ImageDraw
import os
import ctypes
import datetime

# To Do
#   [ ] Add alt-text
#   [ ] Multiplatformness

DEFAULT_BORDER_COLOR = (50, 80, 255, 255)
DEFAULT_BORDER_X = 5
DEFAULT_BORDER_Y = 5
DEFAULT_ALT_TEXT_COLOR = (255, 255, 255, 255)
DEFAULT_ALT_TEXT_SIZE = 14
DEFAULT_ALT_TEXT_FILL = (0, 0, 0, 255)
DEFAULT_ALT_TEXT_FONT = 'C:\Windows\Fonts\CascadiaMono.ttf'
DEFAULT_ALT_TEXT_LEFT_MARGIN = 2
DEFAULT_ALT_TEXT_RIGHT_MARGIN = 2
DEFAULT_ALT_TEXT_TOP_MARGIN = 2
DEFAULT_ALT_TEXT_BOTTOM_MARGIN = 5

def create_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def time_now():
    return datetime.datetime.today().strftime("%m/%d/%Y %H:%M:%S")

def write_log(*args):
    s = ""
    for arg in args:
        s += str(arg) + " "
    with open("err.log","a") as f:
        f.write(str(time_now() + ": " + str(s) + "\n"))

# image processing

def add_text_space(img, height, fill=DEFAULT_ALT_TEXT_FILL):
    data = img_to_2D_data(img)
    data = _add_text_space(data, height, fill)
    w, h = img.size
    img = img.resize((w, h + height))
    img.putdata(data_2D_to_img(data))
    return img

def _add_text_space(xy_data, height, fill):
    w = len(xy_data[0])
    new_data = xy_data + [[fill]*w for i in range(height)]
    return new_data

def put_border(img,border_x=DEFAULT_BORDER_X,border_y=DEFAULT_BORDER_Y,
        border_color=DEFAULT_BORDER_COLOR):
    data = img_to_2D_data(img)
    data = _put_border(data, border_x, border_y, border_color)
    w,h = img.size
    img = img.resize((w+2*border_x,h+2*border_y))
    img.putdata(data_2D_to_img(data))
    return img

def _put_border(xy_data, border_x, border_y, border_color):
    w = len(xy_data[0])
    new_data = [[border_color]*w for i in range(border_y)] + xy_data + [
        [border_color]*w for i in range(border_y)]
    for i in range(len(new_data)):
        new_data[i] = ([border_color]*border_x + new_data[i] + 
            [border_color]*border_x)
    return new_data

def img_to_2D_data(img):
    w,h = img.size
    data = list(img.getdata())
    xy_data = []
    for y in range(h):
        temp = []
        for x in range(w):
            temp.append(data[y*w + x])
        xy_data.append(temp)
    return xy_data

def data_2D_to_img(xy_data):
    data = []
    for line in xy_data:
        data += line
    return data

def put_caption(img, caption,
        font_path=DEFAULT_ALT_TEXT_FONT,
        font_size=DEFAULT_ALT_TEXT_SIZE,
        left_margin=DEFAULT_ALT_TEXT_LEFT_MARGIN,
        right_margin=DEFAULT_ALT_TEXT_RIGHT_MARGIN,
        bottom_margin=DEFAULT_ALT_TEXT_BOTTOM_MARGIN,
        top_margin=DEFAULT_ALT_TEXT_TOP_MARGIN,
        color=DEFAULT_ALT_TEXT_COLOR):
    font = ImageFont.truetype(font_path, font_size)
    text_x = left_margin
    text_y = img.height + top_margin

    img_draw = ImageDraw.Draw(img)
    text_w, text_h = img_draw.textsize(caption, font=font)

    text_box_width = img.width - left_margin - right_margin

    pixel_per_char = text_w/len(caption)
    chars_per_line = int(text_box_width/pixel_per_char)
    words = caption.split()
    caption = ""
    line_count = 0
    for word in words:
        line_count += len(word)
        if line_count >= chars_per_line:
            line_count = len(word) + 1
            caption += "\n" + word + " "
        else:
            line_count += 1
            caption += word + " "
    text_w, text_h = img_draw.textsize(caption, font=font)
    text_box_height = top_margin + bottom_margin + text_h
    img = add_text_space(img, text_box_height, fill=DEFAULT_ALT_TEXT_FILL)

    img_draw = ImageDraw.Draw(img)
    img_draw.text((text_x, text_y), caption, font=font, fill=color)
    return img

def process_image(local_image_path, caption, desktop_bg_path):
    img = Image.open(local_image_path).convert('RGBA')
    img = put_caption(img, caption)
    img = put_border(img)
    img.save(desktop_bg_path)

# set desktop
def set_desktop_wallpaper(path_to_image):
    from sys import platform
    if platform in ["linux", "linux2"]:
        raise NotImplementedError("Linux not implemented")
    elif platform == "darwin":
        raise NotImplementedError("OSX not implemented")
    elif platform in ["win32", "cygwin"]:
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoA(
            SPI_SETDESKWALLPAPER, 0, path_to_image, 0)
    else:
        raise NotImplementedError("Not implemented for <{}>".format(platform))

# Web calls

def save_image(storage_directory, save_unique_copy=False):
    base_url = "http://www.xkcd.com/"
    soup = bs(urlopen(base_url), features="html.parser")
    soup = soup.find("div",{"id":"comic"})
    src = soup.find("img")["src"]
    caption = soup.find("img")["title"]
    img_name = src[src.rfind("/")+1:]
    if not save_unique_copy:
        img_type = img_name[img_name.rfind('.'):]
        img_name = 'temp' + img_type
    image_path = os.path.join(storage_directory, img_name)
    
    res = urlopen("https:"+src)
    with open(image_path, 'wb') as f:
        f.write(''.join(i for i in res))
    return image_path, caption


pwd = os.path.dirname(os.path.realpath(__file__)) 
storage_directory = os.path.join(pwd, "pics")
desktop_image_name = "desktop.bmp"
path_to_background = os.path.join(storage_directory, desktop_image_name)

# Check if the dump directory exists
create_directory(storage_directory)

# try:
print("Pulling image...", end='')
image_path, caption = save_image(storage_directory)
print("done")

# convert image to bmp
print("Processing image...", end='')
process_image(image_path, caption, path_to_background)
print("done")

# Windows - set to BG
print("Setting desktop...")
set_desktop_wallpaper(path_to_background)
print("done")
# except Exception as e:
#     raise e
#     write_log(e)


