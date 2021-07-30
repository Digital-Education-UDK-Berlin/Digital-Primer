from PIL import Image, ImageDraw
from image_utils import ImageText
import drivers.drivers_base as drivers_base
import drivers.it8951 as driver_it8951
import os,time,sys
from random import sample,getrandbits,choice
import simpleaudio as sa
import wave
import string

#topic=sys.argv[1]
max_labels=20
driver=driver_it8951.IT8951()
driver.init(partial=True)
black=driver.black
white=driver.white

white_image = Image.new("1", (600,800), color='#FFFFFF')
#white_image.save('titles_bg255/FFF.bmp')
driver.load_image(0,0,white_image,img_addr=driver.img_addr)
driver.load_image(0,0,white_image,img_addr=driver.img_addr+(2*driver.width*driver.height+1))
#driver.display_buffer_area(0,0,800,600,2,driver.img_addr)
def randomString(stringLength):
    letters = string.ascii_letters
    return ''.join(choice(letters) for i in range(stringLength))

#for label in os.listdir(topic+'BMP/'):
labels = sample(os.listdir('WLLPR/WAV'), max_labels)
for label_full in labels:
    label=os.path.splitext(label_full)[0]
    false_label=randomString(len(label))
    false_label_image = ImageText((600,200), background=(255,255,255))
    false_label_image.write_text(20,0,false_label, font_size='fill', max_height=200, max_width=560,color=(0,0,0))
    rotated_image=false_label_image.image.convert('1').rotate(180)
    #label_image.save('titles_bg255/'+label+'.bmp')
    label_image=Image.open('titles_bg255/'+label+'.bmp')
    #rotated_image=label_image.rotate(180) 
    true_up=bool(getrandbits(1))
    if true_up:
        pointer_true=driver.img_addr
        pointer_false=driver.img_addr+(2*driver.width*driver.height+1)
    else:
        pointer_true=driver.img_addr+(2*driver.width*driver.height+1)
        pointer_false=driver.img_addr
    driver.load_image(0,100,label_image,img_addr=pointer_true)
    sa.WaveObject.from_wave_read(wave.open('WLLPR/WAV/'+label+'.wav', 'rb')).play()
    driver.load_image(0,100,rotated_image,img_addr=pointer_false)
    if true_up:
        driver.display_buffer_area(0,0,400,600,1,pointer_true)
        driver.display_buffer_area(400,0,400,600,1,pointer_false+1200)
    else:
        driver.display_buffer_area(0,0,400,600,1,pointer_false)
        driver.display_buffer_area(400,0,400,600,1,pointer_true+1200)
  
