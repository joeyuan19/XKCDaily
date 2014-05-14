from BeautifulSoup import BeautifulSoup as bs
from urllib2 import urlopen
from urllib import urlretrieve
import os
import sys
import ctypes

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

URL = "http://www.xkcd.com/"
DIR = "pics"
RENAME = "current.bmp"
PWD = os.path.dirname(os.path.realpath(__file__)) 

try:
	soup = bs(urlopen(URL))
	soup = bs(str(soup.find("div",{"id":"comic"})))
	src = soup.find("img")["src"]
	img_name = src[src.rfind("/")+1:]
	img_loc = join(PWD,DIR,img_name)
	urlretrieve(src,img_loc)

	from PIL import Image
	img = Image.open(img_loc)
	img.save(join(PWD,DIR,RENAME))

	ctypes.windll.user32.SystemParametersInfoA(20, 0, r"C:\Users\Joe\Desktop\Projects\xkcd-auto-download\pics\current.bmp", 0)	
except Exception as e:
	write_log(e)

