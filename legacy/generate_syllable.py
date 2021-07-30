#!/usr/bin/python3
#Folio generator
#Co(d|mb)ded by Prof. Dr. Dr. Daniel Devatman Hromada as a first visual content generator of the digital Primer (fibel.digital) project
#Commercial use without explicit consent of the author prohibited
#Where appropriate, CC BY-NC-SA applies, in all other cases mrGPL
#UdK / ECDF / wizzion.com AE5001, January 2020
#Berlin, Deutschland, EU


from PIL import Image, ImageDraw
from Fibel.image_utils import ImageText
import Fibel.drivers.drivers_base as drivers_base
import Fibel.drivers.it8951 as driver_it8951
import os,time,sys

#concating the slash as anticipation of future command-line laziness, not sure if it could not potentially cause some ITsec issues in future ?
topic=sys.argv[1]+'/'
font='schola'

#driver=driver_it8951.IT8951()
#driver.init(partial=True)

#white_image = Image.new("1", (600,800), color='#FFFFFF')
#driver.load_image(0,0,white_image,img_addr=driver.img_addr)
#driver.display_buffer_area(0,0,800,600,2,driver.img_addr)
#for label in os.listdir(topic+'BMP/'):

for label_full in os.listdir(topic+'/Labels/'):
    print(label_full)
    folio = ImageText((600,800), background=(255,255,255))
    label=os.path.splitext(label_full)[0]
    folio.write_text('center',0,label.upper(), font_filename='Fonts/'+font+'.otf',font_size='fill', max_height=200, max_width=560,color=(0,0,0))
    folio.write_text('center','center',label.lower(), font_filename='Fonts/'+font+'.otf',font_size='fill', max_height=200, max_width=560,color=(0,0,0))
    folio.write_text('center',600,label, font_filename='Fonts/'+font+'.otf',font_size='fill', max_height=200, max_width=560,color=(0,0,0))
    out=folio.image.convert(mode='1')

    folio_bw = ImageText((600,800), background=(0,0,0))
    label=os.path.splitext(label_full)[0]
    folio_bw.write_text('center',0,label.upper(), font_filename='Fonts/'+font+'.otf',font_size='fill', max_height=200, max_width=560,color=(255,255,255))
    folio_bw.write_text('center','center',label.lower(), font_filename='Fonts/'+font+'.otf',font_size='fill', max_height=200, max_width=560,color=(255,255,255))
    folio_bw.write_text('center',600,label, font_filename='Fonts/'+font+'.otf',font_size='fill', max_height=200, max_width=560,color=(255,255,255))
    out_bw=folio_bw.image.convert(mode='1')


    #driver.load_image(0,0,out,img_addr=driver.img_addr)
    #driver.display_buffer_area(0,0,800,600,2,driver.img_addr)
    if not os.path.exists(topic+'Foliae/'+label_full):
            os.makedirs(topic+'Foliae/'+label_full)
    filename=topic+'Foliae/'+label_full+'/wb#'+font+'.bmp'
    out.save(filename)
    filename_bw=topic+'Foliae/'+label_full+'/bw#'+font+'.bmp'
    out_bw.save(filename_bw)
    #os.system('convert "'+filename+'" +dither -colors 16 -type palette BMP3:"'+filename+'"')
