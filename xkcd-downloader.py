from BeautifulSoup import BeautifulSoup as bs
from urllib2 import urlopen
from urllib import urlretrieve
from PIL import Image
import os
import sys
import ctypes


# To Do
#   [ ] Add alt-text
#   [ ] Multiplatformness


def time_now():
    import datetime
    return datetime.datetime.today().strftime("%m/%d/%Y %H:%M:%S")

def write_log(*args):
    s = ""
    for arg in args:
        s += str(arg) + " "
    with open("err.log","a") as f:
        f.write(str(time_now() + ": " + str(s) + "\n"))

def join(*paths):
    total_path = ""
    for path in paths:
        total_path = os.path.join(total_path,path)
    return total_path

def put_border(img,border_x=10,border_y=10,border_color=(255,255,255,255)):
    data = img_to_2D_data(img)
    data = _put_border(data,border_x,border_y,border_color)
    w,h = img.size
    img = img.resize((w+2*border_x,h+2*border_y))
    img.putdata(data_2D_to_img(data))
    return img

def _put_border(xy_data,border_x=10,border_y=10,border_color=(255,255,255,255)):
    w = len(xy_data[0])
    new_data = [[border_color]*w for i in range(border_y)] + xy_data + [[border_color]*w for i in range(border_y)]
    for i in xrange(len(new_data)):
        new_data[i] = [border_color]*border_x + new_data[i] + [border_color]*border_x
    return new_data

def img_to_2D_data(img):
    w,h = img.size
    data = list(img.getdata())
    xy_data = []
    for y in xrange(h):
        temp = []
        for x in xrange(w):
            temp.append(data[y*w + x])
        xy_data.append(temp)
    return xy_data

def data_2D_to_img(xy_data):
    data = []
    for line in xy_data:
        data += line
    return data

def put_caption(img):
    pass

URL = "http://www.xkcd.com/"
DIR = "pics"
RENAME = "current.bmp"
PWD = os.path.dirname(os.path.realpath(__file__)) 

try:
    # Check if the dump directory exists
    if not os.path.exists(join(PWD,DIR)):
        os.makedirs(join(PWD,DIR))
    
    # Pull img
    soup = bs(urlopen(URL))
    soup = bs(str(soup.find("div",{"id":"comic"})))
    src = soup.find("img")["src"]
    img_name = src[src.rfind("/")+1:]
    img_loc = join(PWD,DIR,img_name)
    urlretrieve(src,img_loc)

    # convert image to bmp
    img = Image.open(img_loc)
    img = put_border(img,border_color=255)
    img.save(join(PWD,DIR,RENAME))
    
    # Windows - set to BG
    ctypes.windll.user32.SystemParametersInfoA(20, 0, join(PWD,DIR,RENAME), 0)
except Exception as e:
    write_log(e)


