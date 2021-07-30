#!/usr/bin/python3 -u
#Digital Primer Reading & Recording App

#LESSON INITIALIZE
from Fibel.init import *
from random import shuffle
init()
from Fibel.core import *
import time

from io import BytesIO
#import simpleaudio as sa
#import wave

#NEUTRAL,NOISE,SLOW,FAST,NOISE,WHISPER,SING
mode='NEUTRAL'

wordz=['der Welpe','das Kätzchen','das Entchen','das Fohlen','das Zicklein','die Kuh','der Esel','das Huhn','das Schaf','das Schwein','der Löwe','der Elefant','der Affe','die Schlange','/']
        wordz=['der Affe','der Bär', 'der Esel','der Elefant','der Fisch','der Fuchs','der Hahn','der Hund','der Löwe','die Ente','die Gans','die Giraffe','die Henne','die Katze','die Kuh','die Ziege','das Huhn','das Kamel','das Kaninchen','das Pferd','das Reh','das Schaf','das Schwein']


from picamera import PiCamera
from PIL import Image

camera = PiCamera()
camera.color_effects = (128,128)
camera.resolution = (600, 800)
camera.rotation=90
camera.hflip=True

while True:
    shuffle(wordz)
    import os,glob
    last_session=os.path.basename(max(glob.glob(os.path.join('/home/fibel/data/pupils/sessions/*')), key=os.path.getmtime))
    session_id=str(int(last_session)+1)
    os.mkdir('/home/fibel/data/pupils/sessions/'+session_id+'/')
    lesen(session_id,wordz+['Danke!'])

    time.sleep(2)
    sa.WaveObject.from_wave_read(wave.open(lexikon_dir+'WAV/fünf/pic.wav', 'rb')).play()
    time.sleep(2)
    sa.WaveObject.from_wave_read(wave.open(lexikon_dir+'WAV/vier/pic.wav', 'rb')).play()
    time.sleep(2)
    sa.WaveObject.from_wave_read(wave.open(lexikon_dir+'WAV/drei/pic.wav', 'rb')).play()
    time.sleep(2)
    sa.WaveObject.from_wave_read(wave.open(lexikon_dir+'WAV/zwei/pic.wav', 'rb')).play()
    time.sleep(2)
    sa.WaveObject.from_wave_read(wave.open(lexikon_dir+'WAV/eins/pic.wav', 'rb')).play()
    time.sleep(2)
    sa.WaveObject.from_wave_read(wave.open(lexikon_dir+'WAV/Käsekuchen/pic.wav', 'rb')).play()

    visualstream = BytesIO()
    camera.capture(visualstream, format='bmp')
    visualstream.seek(0)
    camera.start_preview()
    photo = Image.open(visualstream)
    pointer_front2=driver.img_addr+(2*driver.width*driver.height+1)
    driver.load_image(0,0,photo,img_addr=pointer_front2)
    driver.display_buffer_area(0,0,800,600,2,pointer_front2)
    photo.save('/home/fibel/data/sessions/'+session_id,'/photo_final.png')
    time.sleep(10)

