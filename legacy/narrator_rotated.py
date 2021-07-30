#!/usr/bin/python3
#Dynamic text with audio synchronisation
#Coded by Daniel Devatman Hromada as part of the Digital Primer project
#Conditions of morally restricted variant of the GPL 2.0 Licence apply
#for related audio (voices by Daniel Hromada and Astrid Kraniger) conditions of CC BY-NC-SA license apply

from math import sqrt
import time,os,sys,json,wave
import simpleaudio as sa
from PIL import Image, ImageDraw
from PIL.ImageOps import invert,flip
import Fibel.drivers.drivers_base as drivers_base
import Fibel.drivers.it8951 as display_it8951
from Fibel.FolioText import FolioText
from Fibel.image_utils import ImageText
os.system('/usr/sbin/alsactl restore -f /home/fibel/Primer_v1/alsa.config')

sentences=[]
page_dir=sys.argv[1]

jsons=[]
wavs=[]
texts=[]

#utility function to have multiple poin
def pntr(id):
    global display 	
    return display.img_addr+id*(2*display.width*display.height+1)


#load the JSON file which describes Your text
lines=open(page_dir+'/content','r').readlines()
for line in lines:
    row=line.split(";")
    #print(row)
    texts.append(row[0])
    #print(row[1])
    jsons.append(json.loads('['+(row[1].rstrip())+']'))
    #transform WAV files into objects which are ready to be played
    try:
        wavs.append(sa.WaveObject.from_wave_read(wave.open(page_dir+'/'+row[0]+'.wav', 'rb')))
    except:
        wavs.append("")

#start
display=display_it8951.IT8951()
display.init(screen='back',rotate=1)
img_addr=display.img_addr

#image_blank = Image.new("1", (display.width, display.height), 0x255)
#display.load_image(0,0,image_blank,img_addr=img_addr)
#display.display_buffer_area(0,0,600,800,2,img_addr)
picture=Image.open('/home/fibel/Primer_v1/Books/ABC_Buch/intro/bild2.bmp')
text_image = ImageText((600,800), background=(255,255,255))
text_image.write_text(20,0,"Das ABC Buch", font_size='fill', max_height=200, max_width=560,color=(0,0,0))
#text_image.write_text(20,100,"von Karl Philipp Moritz", font_size='fill', max_height=100, max_width=560,color=(0,0,0))
text_image.write_text(20,100,"mit Stimme von Astrid Kraniger", font_size='fill', max_height=100, max_width=560,color=(0,0,0))
text_image.image.paste(picture.resize((396,300)),(102,210))
#content_image=text_image.image
text_image.image.save("tafel2.bmp")

font = 'Fonts/schola.otf'
margin_width = 20
color = 0
pntr_id=0

from Fibel.input.gesture import *
g=gesture()
refresh=0
while(True):
    #basic gesture sensing interface
    cmd=g.get_gesture()
    if cmd is 'L':
        pntr_id-=1
    elif cmd is 'R':
        pntr_id+=1
        if pntr_id==1:
            #content_image=Image.open('/home/fibel/Primer_v1/Books/ABC_Buch/intro/bild1.bmp')
            display.load_image(0,0,Image.open('tafel1.bmp'),img_addr=pntr(0))
            display.display_buffer_area(0,0,600,600,2,pntr(0))
        if pntr_id==3:
            #content_image=Image.open('/home/fibel/Primer_v1/Books/ABC_Buch/intro/bild2.bmp')
            display.load_image(0,0,Image.open('tafel2.bmp'),img_addr=pntr(0))
            display.display_buffer_area(0,0,600,600,2,pntr(0))
    elif cmd is 'C' or cmd is 'A':
        refresh=1
    else:
        time.sleep(0.1)
        continue
    text=texts[pntr_id]
 
    #generate next sentence BMP, 
    if not refresh:
        word_pointers = []
        folio = FolioText((int(display.height),int(display.width/2)), word_pointers)
        font_size=int(sqrt((140000/(len(text)+5))))
        folio.write_text_box(margin_width, 0, text, box_width=560, font_filename=font, font_size=font_size, color=color, place='justify')
        sys.stderr.write("loading folio "+str(pntr_id))
        display.load_image(0,500,folio.image,img_addr=pntr(1))
        display.load_image(0,500,invert(folio.image.convert('L')),img_addr=pntr(2))
        display.display_buffer_area(500,0,300,600,2,buff_addr=pntr(1))

    sentence=jsons[pntr_id]
    word_id=0
    last_onset=0
    #displaying blank page
    #display.display_buffer_area(0,0,600,400,2,buff_addr=pntr(2*page))
    try:
        wavs[pntr_id].play()
    except:
        ""
    old_y=offset_x=0
    for pointer in word_pointers:
        word=sentence[word_id]
        #standard mode
        #display.display_buffer_area(pointer[0],pointer[1],pointer[2],pointer[3],1,buff_addr=pageList(img_addr,page))
        #rot 90 mode
        #horizontal stripes
        #display.display_buffer_area(800-pointer[1]-97,0,97,600,2,buff_addr=pageList(img_addr,page+1))
        if pointer[1] is not old_y:
            offset_x=0
        else:
            offset_x=+pointer[2]
        display.display_buffer_area(500+pointer[1],600-pointer[2]-pointer[0],pointer[3],pointer[2],1,buff_addr=pntr(2))
        word_offset=int(word['stop'])
        word_length=word_offset-last_onset
        time.sleep(word_length/1500)
        display.display_buffer_area(500+pointer[1],600-pointer[2]-pointer[0],pointer[3],pointer[2],1,buff_addr=pntr(1))
        old_y=pointer[1]
        word_offset=int(word['stop'])
        last_onset=word_offset
        #print(word['w']+str(last_onset))
        word_id=word_id+1
    refresh=0

