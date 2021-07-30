#from Fibel.init import *
#from Fibel.core import *
from PIL import Image, ImageDraw
from Fibel.image_utils import ImageText
from Fibel.utils import randomString
from random import sample,choice,randint,getrandbits

import os,time,sys,string,re
import simpleaudio as sa
import wave

from Fibel.Corpora.BDLP_nn import *
from Fibel.input.gesture import *
import Fibel.drivers.it8951 as driver_it8951

def say(msg):
    print(msg)

def feedback_negative():
    global score
    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Feedback/Neg/qwack-tm.wav', 'rb')).play()
    score-=1

def feedback_positive():
    global score
    #sa.WaveObject.from_wave_read(wave.open('Audio/Feedback/Pos/juhuu-tm.wav', 'rb')).play()
    l=1
    score+=1

def init_BDLP(root='/home/fibel/Primer_v1/',busno=1,screen='front'):
    global gesture_sensor,driver,root_dir
    root_dir=root
    driver=driver_it8951.IT8951()
    driver.init(screen=screen)
    try:
        if gesture_sensor.active:
           gesture_sensor=gesture(busno=busno,caseflag=1)
           #print(gesture_sensor.get_gesture()+"INIT")
           #gesture=gesture()
    except:
           gesture_sensor=gesture(busno=busno,caseflag=1)
           print(gesture_sensor.get_gesture()+"OK")
        #gesture="NO SENSOR"

def BDLP():
    global gesture_sensor,score
    score=0
   # say("BEGIN Aufgabe 3 :: Berliner digitale Leseprobe")
    white_image = Image.new("1", (600,800), color='#FFFFFF')
    driver.load_image(0,0,white_image,img_addr=driver.img_addr)
    driver.load_image(0,0,white_image,img_addr=driver.img_addr+(2*driver.width*driver.height+1))
    bdlp_image = ImageText((600,200), background=(255,255,255))
    bdlp_image.write_text(20,0,"Berliner digitale Leseprobe", font_size='fill', max_height=200, max_width=560,color=(0,0,0))
    driver.load_image(0,200,bdlp_image.image,img_addr=driver.img_addr)
    driver.display_buffer_area(0,0,800,600,2,driver.img_addr+(2*driver.width*driver.height+1))
    driver.display_buffer_area(0,0,800,600,1,driver.img_addr)
    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Titles/Aufgabe3-BDLP-ddh', 'rb')).play().wait_done()

    say("Bitte bewege dein Hand in Richtung des gesprochenes Wortes - entweder von dir / nach oben oder zu dir / nach unten.")
    labels = sample(os.listdir(root_dir+'Audio/WLLPR/WAV'), 50)
    for label_full in labels:
        true_label=os.path.splitext(label_full)[0]
        true_label_image=Image.open(root_dir+'titles_bg255/'+true_label+'.bmp')
        proba=randint(1,100)
        operator_flag=""
        if proba<20:
            false_label=randomString(len(true_label))
            false_image = ImageText((600,200), background=(255,255,255))
            false_image.write_text(20,0,false_label, font_size='fill', max_height=200, max_width=560,color=(0,0,0))
            false_label_image=false_image.image
            operator_flag="random"
            if proba<10:
                false_label_image=false_label_image.convert('1').rotate(180)
                operator_flag="random_rotate180"
        elif proba<60:
                false_label=''
                false_label_image=true_label_image.transpose(Image.FLIP_LEFT_RIGHT)
                operator_flag="true_verticalflip"
        elif proba<100:
                false_label=''
                false_label_image=true_label_image.transpose(Image.FLIP_LEFT_RIGHT)
                operator_flag="true_verticalflip"
        else:
            #nearest neighbor case
            false_label=BDLP_nn_dict[true_label]
            try:
                false_label_image=Image.open(root_dir+'titles_bg255/'+false_label+'.bmp')
            #if nn does not exist then just do a vertical flip (better would be to generate the new bmp and cache it)
            except:
                false_label_image=false_label_image.transpose(Image.FLIP_LEFT_RIGHT)
                operator_flag="true_verticalflip"
            if proba<30:
                false_label_image=false_label_image.transpose(Image.FLIP_LEFT_RIGHT)
                operator_flag="true_verticalflip"
            elif proba<40:
                false_label_image=false_label_image.transpose(Image.FLIP_TOP_BOTTOM)
                operator_flag="true_horizontalflip"
        true_up=bool(getrandbits(1))
        if true_up:
            pointer_true=driver.img_addr
            pointer_false=driver.img_addr+(2*driver.width*driver.height+1)
        else:
            pointer_true=driver.img_addr+(2*driver.width*driver.height+1)
            pointer_false=driver.img_addr
        #score_image = ImageText((600,50), background=(255,255,255))
        #score_image.write_text(20,0,str(score), font_size='fill', max_height=50, max_width=560,color=(0,0,0))
        #driver.load_image(0,100,score_image.image,img_addr=driver.img_addr)
        #driver.display_buffer_area(200,0,200,600,1,driver.img_addr)
        driver.load_image(0,600,true_label_image,img_addr=pointer_true)
        sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/WLLPR/WAV/'+true_label+'.wav', 'rb')).play()
        driver.load_image(0,600,false_label_image,img_addr=pointer_false)
        if true_up:
            driver.display_buffer_area(0,0,400,600,1,pointer_true)
            driver.display_buffer_area(400,0,400,600,1,pointer_false+1200)
        else:
            driver.display_buffer_area(0,0,400,600,1,pointer_false)
            driver.display_buffer_area(400,0,400,600,1,pointer_true+1200)
        task_start=time.time()
        while True:
            cmd=gesture_sensor.get_gesture()
            #if cmd:
            #    print(cmd)
            if cmd=='C' or cmd=='A':
                sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/WLLPR/WAV/'+true_label+'.wav', 'rb')).play()
            #rotate results in case of rotated screen, most probably should be put into gesture.py itself
            if driver.ROTATE==driver.ROTATE_270:
                if cmd=='U':
                   cmd='D'
                elif cmd=='D':
                   cmd='U'
                if cmd=='R':
                   cmd='L'
                if cmd=='L':
                   cmd='R'
            if cmd=='U' or cmd=='D':
                if cmd=='U':
                    if true_up:
                        feedback_positive()
                        status='T'
                    else:
                        feedback_negative()
                        status='F'
                if cmd=='D':
                    if not true_up:
                        feedback_positive()
                        status='T'
                    else:
                        feedback_negative()
                        status='F'
                print(status+';'+true_label+';'+false_label+';'+str(round(time.time()-task_start,2))+';'+operator_flag)
                break
            time.sleep(0.01)


