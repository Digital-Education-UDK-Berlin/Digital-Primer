from PIL import Image, ImageDraw
from Fibel.image_utils import ImageText
from random import sample,choice,randint,getrandbits

import os,time,sys,string,re
import simpleaudio as sa
import wave

from Fibel.Corpora.BDLP_nn import *
from Fibel.input.gesture import *
import Fibel.drivers.it8951 as driver_it8951

screen_id=sys.argv[1]

#content_image=Image.open('/home/fibel/Primer_v1/Lesen/Tiere/Lectiones/1/cover.bmp')
content_image=Image.open('/home/fibel/Primer_v1/Books/ABC_Buch/intro/bild2.bmp')
text_image = ImageText((600,800), background=(255,255,255))
text_image.write_text(20,0,"Das ABC Buch", font_size='fill', max_height=200, max_width=560,color=(0,0,0))
text_image.write_text(20,100,"von Karl Philipp Moritz", font_size='fill', max_height=100, max_width=560,color=(0,0,0))
text_image.image.paste(content_image.resize((396,300)),(102,210))
content_image=text_image.image

white_image = Image.new("1", (600,800), color='#FFFFFF')
black_image = Image.new("1", (600,800), color='#000000')

if screen_id != "back":
    print("front")
    driver_front=driver_it8951.IT8951()
    driver_front.init(rotate=1)
    pointer_front=driver_front.img_addr
    pointer_front2=driver_front.img_addr+(2*driver_front.width*driver_front.height+1)
    driver_front.load_image(0,0,content_image,img_addr=pointer_front2)
    #driver_front.load_image(400,0,text_image,img_addr=pointer_front2)
    #driver_front.display_buffer_area(400,0,500,600,2,pointer_front2)
    driver_front.display_buffer_area(0,0,800,600,2,pointer_front2)
if screen_id != "front":
    print("back")
    driver_back=driver_it8951.IT8951()
    driver_back.init(screen="back")
    pointer_back=driver_back.img_addr
    pointer_back2=driver_back.img_addr+(2*driver_back.width*driver_back.height+1)
    driver_back.load_image(0,0,content_image,img_addr=pointer_back2)
    #driver_back.load_image(400,0,text_image,img_addr=pointer_back2)
    #driver_back.display_buffer_area(0,0,500,600,2,pointer_back2)
    driver_back.display_buffer_area(0,0,800,600,2,pointer_back2)

