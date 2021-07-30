#!/usr/bin/python3
#Folio generator
#Co(d|mb)ded by Prof. Dr. Dr. Daniel Devatman Hromada as a first visual content generator of the digital Primer (fibel.digital) project
#Commercial use without explicit consent of the author prohibited
#Where appropriate, CC BY-NC-SA applies, in all other cases mrGPL
#UdK / ECDF / wizzion.com AE5001, January 2020
#Berlin, Deutschland, EU


from PIL import Image, ImageDraw
from Fibel.image_utils import ImageText
#import Fibel.drivers.drivers_base as drivers_base
#import Fibel.drivers.it8951 as driver_it8951
import os,time,sys

#concating the slash as anticipation of future command-line laziness, not sure if it could not potentially cause some ITsec issues in future ?
topic=sys.argv[1]+'/'
author=sys.argv[2]
font=sys.argv[3]

#driver=driver_it8951.IT8951()
#driver.init(partial=True)

#white_image = Image.new("1", (600,800), color='#FFFFFF')
#driver.load_image(0,0,white_image,img_addr=driver.img_addr)
#driver.display_buffer_area(0,0,800,600,2,driver.img_addr)

for label_full in os.listdir(topic+'/Units/'):
    print(label_full)
    label=os.path.splitext(label_full)[0]
    folio = ImageText((600,800), background=(255,255,255))
    folio_up = ImageText((600,100), background=(255,255,255))
    folio_up.write_text('center','center',label, font_filename='Fonts/'+font+'.otf',font_size='fill', max_height=100, max_width=560,color=(0,0,0))
    folio.image.paste(folio_up.image,(0,0))

    folio_down = ImageText((600,100), background=(255,255,255))
    folio_down.write_text('center','center',label.upper(), font_filename='Fonts/'+font+'.otf',font_size='fill', max_height=100, max_width=560,color=(0,0,0))
    folio.image.paste(folio_down.image,(0,680))

    cue_image=Image.open('Lexikon/BMP/'+label_full+'/'+author)
    folio.image.paste(cue_image,(int((600-cue_image.width)/2),150))
    out=folio.image.convert(mode='P',colors=16)

    #driver.load_image(0,0,out,img_addr=driver.img_addr)
    #driver.display_buffer_area(0,0,400,600,1,driver.img_addr)
    #driver.display_buffer_area(0,0,800,600,2,driver.img_addr)
    if not os.path.exists(topic+'Foliae/'+label_full):
            os.makedirs(topic+'Foliae/'+label_full)
    filename=topic+'Foliae/'+label_full+'/'+author+'#'+font+'.bmp'
    out.save(filename)
    os.system('convert "'+filename+'" +dither -colors 16 -type palette BMP3:"'+filename+'"')
