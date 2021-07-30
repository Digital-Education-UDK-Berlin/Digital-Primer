#!/usr/bin/python3
#Cover generator
#Co(d|mb)ded by Prof. Dr. Dr. Daniel Devatman Hromada as a second visual content generator of the digital Primer (fibel.digital) project
#Commercial use without explicit consent of the author prohibited
#Where appropriate, CC BY-NC-SA applies, in all other cases mrGPL
#UdK / ECDF / wizzion.com AE5001, January 2020
#Berlin, Deutschland, EU, Gaia

from Fibel.image_utils import ImageText
import glob,os,sys
from PIL import Image
import Fibel.drivers.drivers_base as drivers_base
import Fibel.drivers.it8951 as driver_it8951

epoch_id=sys.argv[1]
epoch=sys.argv[2]
thema_id=sys.argv[3]
thema=sys.argv[4]
lesson_id=sys.argv[5]
thema_dir='Lesen/'+thema+'/'
lesson_dir=thema_dir+'Lectiones/'+lesson_id+'/'
folio_dir=lesson_dir+'Foliae/'

color = (0,0,0)
font = 'schola.otf'
disp_width=600
disp_height=800
img_out = ImageText((disp_width,disp_height), background=(255,255,255))
img_out.write_text(20,0,   "EPOCHE "+epoch_id, font_size='fill', max_height=100, max_width=300,color=color)
img_out.write_text(20,60,   epoch.upper(), font_size='fill', max_height=100, max_width=300,color=color)
img_out.write_text(20,200,   "THEMA "+thema_id, font_size='fill', max_height=100, max_width=300,color=color)
img_out.write_text(20,270,   thema.upper(), font_size='fill', max_height=100, max_width=300,color=color)
img_out.write_text(100,620, "LEKTION "+lesson_id, font_size='fill', max_height=160, max_width=400,color=color)
#img_out.write_text(20,400, "SPRECHEN", font_size='fill', max_height=100, max_width=560,color=color)
#img_out.write_text(20,500, "ZUORDNEN", font_size='fill', max_height=100, max_width=560,color=color)
#img_out.write_text(20,600, "ERKENNEN", font_size='fill', max_height=100, max_width=560,color=color)
cover=img_out.image.convert("1")
cover.save(lesson_dir+'cover.bmp')

driver=driver_it8951.IT8951()
driver.init(partial=True)
pointer=driver.img_addr
driver.load_image(0,0,cover,img_addr=pointer)
driver.display_buffer_area(0,0,800,600,2,pointer)
 
