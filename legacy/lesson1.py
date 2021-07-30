#!/usr/bin/python3 -u
#Digital Primer Lesson 0
#1st exercise: SPRECHEN : Read & record words
#2nd exercise: ZUORDNEN : Associate words to images
#3rd exercise: ERKENNEN : Distinguish between words and non-words

from PIL import Image, ImageDraw
from Fibel.image_utils import ImageText
import Fibel.drivers.drivers_base as drivers_base
import Fibel.drivers.it8951 as driver_it8951
from random import sample,choice,randint,getrandbits
from Fibel.input.gesture import *
from Fibel.input.fibelaudio import *
from Fibel.globals import *
import os,time,sys,string
import wave
import simpleaudio as sa
import threading

if len(sys.argv)>1:
    lesson=sys.argv[2]
    max_labels=int(sys.argv[1])
else:
    lesson=1
    max_labels=10

#voice="ask"
#font="schola"
#img_author="lux"
#root_dir='/home/fibel/Primer_v1/'
#topic_dir=root_dir+'Lesen/Tiere/'
lesson_dir=topic_dir+'Lectiones/1/'
folio_dir=lesson_dir+'Foliae/'

#start
driver=driver_it8951.IT8951()
driver.init(partial=True)
black=driver.black
white=driver.white

pointers=dict()
old_pointer=0
start_load=time.time()
loaded_foliae=0
lock = threading.Condition()
#labels = sample(os.listdir(folio_dir), max_labels)
labels = sorted(sample(os.listdir(folio_dir),max_labels))
active_label=""

pointer=driver.img_addr

def say(msg):
    print(msg)

#COVER
def cover():
    content_image=Image.open(lesson_dir+'cover.bmp')
    driver.load_image(0,0,content_image,img_addr=pointer)
    driver.display_buffer_area(0,0,800,600,2,pointer)

    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Titles/Epoche_1-ddh', 'rb')).play()
    time.sleep(2.35)
    driver.display_buffer_area(0,0,70,600,2,pointer)

    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Words/lesen/-ddh', 'rb')).play()
    time.sleep(1.84)
    driver.display_buffer_area(60,0,140,600,2,pointer)

    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Titles/Thema_1-ddh', 'rb')).play()
    time.sleep(2.6)
    driver.display_buffer_area(200,0,80,600,2,pointer)

    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Words/Tiere/-ddh', 'rb')).play()
    time.sleep(1.83)
    driver.display_buffer_area(270,0,140,600,2,pointer)

    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Titles/Lektion_1-ddh', 'rb')).play()
    time.sleep(2.6)
    driver.display_buffer_area(600,0,200,600,2,pointer)

cover()

pointer=driver.img_addr+(2*driver.width*driver.height+1)

def load_foliae():
    global pointer,loaded_foliae,active_label
    for label in labels:
        print(label)
        pointers[label]=dict()
        pointers[label]["audio"]=sa.WaveObject.from_wave_read(wave.open(topic_dir+"Indizien/WAV/"+label+"/"+voice+".wav"))
        pointers[label]['folio']=pointer
        folio_image=Image.open(folio_dir+label)
        lock.acquire()
        driver.load_image(0,0,folio_image,img_addr=pointer)
        driver.display_buffer_area(0,0,800,600,2,pointer)
        pointers[label]["audio"].play()
        fa.active_label=label
        lock.release()
        pointers[label]["image"]=pointer
        pointer+=(driver.width*driver.height+1)
        loaded_foliae+=1
    print ("Images loaded in "+str(start_load-time.time()))

#START LOADING FOLIOS FOR EXERCICE 1 AND 2
#x = threading.Thread(target=load_foliae, args=(max_labels,))
#x.start()

fa=fibelaudio()
fa.run()

g=gesture()
try:
    g.init()
except:
    g.init()

#load folios on a controller
load_foliae()

say("Bitte wiederhole die Woerter die Du hoeren wirst. Wenn Du bereits fuer die Aufnahme bist dann drücke den Aufnahmeknopf, halte ihn gedrückt bis das Wort ganz gesprochen wird. Danach lass den Knopf frei.")


#SPRECHEN
def imitate():
    #displaying first folio
    cursor=0
    fa.active_label=labels[cursor]
    driver.display_buffer_area(0,0,200,600,1,pointers[labels[cursor]]["folio"])
    driver.display_buffer_area(600,0,200,600,1,pointers[labels[cursor]]["folio"]+1600)
     
    #if cursor>0:
    #    pointers[labels[cursor-1]]["audio"].wait_done()
    #pointers[labels[cursor]]["audio"].play().wait_done()
    driver.display_buffer_area(200,0,400,600,2,pointers[labels[cursor]]["folio"]+800)
    pointers[labels[cursor]]["audio"].play().wait_done()
    old_audiofile=""

    while(True):
        #when recording was successful show new folio
        if fa.last_audiofile and fa.last_audiofile!=old_audiofile:
            cursor+=1
            if cursor<len(labels):
                driver.display_buffer_area(0,0,200,600,1,pointers[labels[cursor]]["folio"])
                driver.display_buffer_area(600,0,200,600,1,pointers[labels[cursor]]["folio"]+1600)
                pointers[labels[cursor]]["audio"].play().wait_done()
                driver.display_buffer_area(200,0,400,600,2,pointers[labels[cursor]]["folio"]+800)
                fa.active_label=labels[cursor]
                fa.last_audiofile=""
                time.sleep(0.2)
            else:
                break


print("BEGIN Aufgabe 1 :: SPRECHEN")
try:
    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Titles/Aufgabe1-Sprechen-ddh', 'rb')).play().wait_done()
except:
    err="Could not play file"

imitate()
print("END Aufgabe 1 :: SPRECHEN")


#EXERCISE 2 :: ZUORDNEN

def feedback_negative():
    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Feedback/Neg/qwack-tm.wav', 'rb')).play()

def feedback_positive():
    #sa.WaveObject.from_wave_read(wave.open('Audio/Feedback/Pos/juhuu-tm.wav', 'rb')).play()
    l=1

def zuordnen1():
    for true_cursor in range(0,len(labels)):
        task_start=time.time()
        driver.display_buffer_area(200,0,600,600,2,pointers[labels[true_cursor]]["folio"])
        pointers[labels[true_cursor]]["audio"].play()
        false_cursor=randint(0,max_labels-1)
        false_cursor_start=false_cursor
        trajectory=''
        driver.display_buffer_area(0,0,200,600,1,pointers[labels[false_cursor]]["folio"])
        while(True):
            cmd=g.get_gesture()
            if cmd=='C' or cmd=='A':
                pointers[labels[true_cursor]]["audio"].play()
            if cmd=='R' or cmd=='L':
                trajectory+=cmd
                if cmd=='R':
                    false_cursor+=1
                    false_cursor%=max_labels
                if cmd=='L':
                    false_cursor-=1
                    false_cursor%=max_labels
                driver.display_buffer_area(0,0,200,600,1,pointers[labels[false_cursor]]["folio"])
            elif cmd=='F':
                if true_cursor==false_cursor:
                    status='T'
                    feedback_positive()
                else:
                    status='F'
                    feedback_negative()
                print(status+';'+labels[true_cursor]+';'+labels[false_cursor]+';'+str(round(time.time()-task_start,2))+';'+labels[false_cursor_start]+';'+trajectory)
                break
            time.sleep(0.01)

say("Bitte zuordne das Wort in grossen Buchstaben mit dem entsprechenden Wort in kleinen Buchstaben. Moegliche Zeichen die Du meinem Sensor waehrend dieser Aufgabe geben kannst sind: Bewegung nach rechts zeigt das naechstes Wort, Bewegung nach links zeigt das vergangenes Wort, Bewegung zu Sensor bedeutet Bestatigung und Kreis-bewegung bedeutet Aussage wiederholen.")

print("BEGIN Aufgabe 2 :: ZUORDNEN")
sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Titles/Aufgabe2-Zuordnen-ddh', 'rb')).play().wait_done()
zuordnen1()
print("END Aufgabe 1 :: ZUORDNEN")

def randomString(stringLength):
    letters = string.ascii_letters
    return ''.join(choice(letters) for i in range(stringLength))

from Fibel.BDLP import *


white_image = Image.new("1", (600,800), color='#FFFFFF')
driver.load_image(0,0,white_image,img_addr=driver.img_addr)
driver.load_image(0,0,white_image,img_addr=driver.img_addr+(2*driver.width*driver.height+1))

say("BEGIN Aufgabe 3 :: Berliner digitale Leseprobe")
bdlp_image = ImageText((600,200), background=(255,255,255))
bdlp_image.write_text(20,0,"Berliner digitale Leseprobe", font_size='fill', max_height=200, max_width=560,color=(0,0,0))
driver.load_image(0,100,bdlp_image.image,img_addr=driver.img_addr)
driver.display_buffer_area(0,0,800,600,2,driver.img_addr+(2*driver.width*driver.height+1))
driver.display_buffer_area(0,0,400,600,1,driver.img_addr)
sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Titles/Aufgabe3-BDLP-ddh', 'rb')).play().wait_done()

say("Bitte bewege dein Hand in Richtung des gesprochenes Wortes - entweder von dir / nach oben oder zu dir / nach unten.")
labels = sample(os.listdir(root_dir+'Audio/WLLPR/WAV'), 50)
for label_full in labels:
    true_label=os.path.splitext(label_full)[0]
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
    else:
        false_label=BDLP_nn_dict[true_label]
        false_label_image=Image.open(root_dir+'titles_bg255/'+false_label+'.bmp')
        if proba<30:
            false_label_image=false_label_image.transpose(Image.FLIP_LEFT_RIGHT)
            operator_flag="true_verticalflip"
        elif proba<40:
            false_label_image=false_label_image.transpose(Image.FLIP_TOP_BOTTOM)
            operator_flag="true_horizontalflip"
    true_label_image=Image.open(root_dir+'titles_bg255/'+true_label+'.bmp')
    true_up=bool(getrandbits(1))
    if true_up:
        pointer_true=driver.img_addr
        pointer_false=driver.img_addr+(2*driver.width*driver.height+1)
    else:
        pointer_true=driver.img_addr+(2*driver.width*driver.height+1)
        pointer_false=driver.img_addr
    driver.load_image(0,100,true_label_image,img_addr=pointer_true)
    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/WLLPR/WAV/'+true_label+'.wav', 'rb')).play()
    driver.load_image(0,100,false_label_image,img_addr=pointer_false)
    if true_up:
        driver.display_buffer_area(0,0,400,600,1,pointer_true)
        driver.display_buffer_area(400,0,400,600,1,pointer_false+1200)
    else:
        driver.display_buffer_area(0,0,400,600,1,pointer_false)
        driver.display_buffer_area(400,0,400,600,1,pointer_true+1200)
    task_start=time.time()
    while True:
        cmd=g.get_gesture()
        if cmd=='C' or cmd=='A':
            sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/WLLPR/WAV/'+true_label+'.wav', 'rb')).play()
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



say("END Aufgabe 3 :: Berliner digitale Leseprobe")
