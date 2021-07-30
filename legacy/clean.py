from PIL import Image, ImageDraw
from Fibel.image_utils import ImageText
from random import sample,choice,randint,getrandbits

import os,time,sys,string,re
import simpleaudio as sa
import wave

from Fibel.Corpora.BDLP_nn import *
from Fibel.input.gesture import *
import Fibel.drivers.it8951 as driver_it8951

driver_front=driver_it8951.IT8951()
driver_back=driver_it8951.IT8951()
driver_front.init()
driver_back.init(screen="back")

white_image = Image.new("1", (600,800), color='#FFFFFF')
black_image = Image.new("1", (600,800), color='#000000')

pointer_front=driver_front.img_addr
driver_front.load_image(0,0,black_image,img_addr=pointer_front)

pointer_back=driver_back.img_addr
driver_back.load_image(0,0,black_image,img_addr=pointer_back)


pointer_front2=driver_front.img_addr+(2*driver_front.width*driver_front.height+1)
driver_front.load_image(0,0,white_image,img_addr=pointer_front2)

pointer_back2=driver_back.img_addr+(2*driver_back.width*driver_back.height+1)
driver_back.load_image(0,0,white_image,img_addr=pointer_back2)

for i in range(1,5):
    driver_front.display_buffer_area(0,0,800,600,2,pointer_front)
    driver_back.display_buffer_area(0,0,800,600,2,pointer_back)
    driver_front.display_buffer_area(0,0,800,600,2,pointer_front2)
    driver_back.display_buffer_area(0,0,800,600,2,pointer_back2)

