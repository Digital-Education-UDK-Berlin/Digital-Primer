from PIL import Image, ImageDraw
from Fibel.image_utils import ImageText
import Fibel.drivers.drivers_base as drivers_base
import Fibel.drivers.it8951 as driver_it8951
from random import sample,choice,randint,getrandbits
from Fibel.input.gesture import *
from Fibel.input.fibelaudio import *
#from Fibel.globals import *
#from Fibel.core import *
import os,time,sys,string,re
import wave
import simpleaudio as sa
import threading

#global g,default_voice,font,img_author,lexikon_dir,root_dir,topic_dir,lesson_dir,deck_dir,max_labels,driver,pointers,pointer,lock,loaded_foliae,folio_links,active_label,start_load,fa,labels,default_voice,title_height

def init(voice='ddh',script='schola',illustrator='',root='/home/fibel/data/teacher/',lexikon='/home/fibel/data/teacher/Lexikon/',curriculum='Lesen',thema='Tiere',lesson='1',folio_amount=10,label_height=100,screen="front",gesture_active=True):
    #have to do this horrible assigments because of the bloody-blood 'name "whatever" is parameter and global' error
    global gesture,default_voice,font,img_author,lexikon_dir,root_dir,topic_dir,lesson_dir,deck_dir,max_labels,driver,pointers,pointer,lock,loaded_foliae,folio_links,active_label,start_load,fa,labels,default_voice,title_height,session_id
    default_voice=voice
    font=script
    img_author=illustrator
    root_dir=root
    lexikon_dir=lexikon
    topic_dir=root_dir+'/'+curriculum+'/'+thema
    lesson_dir=topic_dir+'/Lectiones/'+lesson+'/'
    deck_dir=lesson_dir+'Deck/'
    #print(deck_dir)
    max_labels=folio_amount
    title_height=label_height
    #ACTIVATE AUDIO
    #fa=fibelaudio()
    #fa.run()

    #if len(sys.argv)>3:
    #    max_labels=int(sys.argv[3])
    #else:
    #    max_labels=10

    driver=driver_it8951.IT8951()
    #driver.init(partial=True)
    driver.init(screen=screen)

    pointers=dict()
    old_pointer=0
    start_load=time.time()
    loaded_foliae=0
    lock = threading.Condition()
    folio_links = sorted(sample(os.listdir(deck_dir),max_labels))
    labels=[re.sub("^\d+[\-.]","", folio_link) for folio_link in folio_links]
    active_label=""
    pointer=driver.img_addr

    #ACTIVATE AUDIO
    #fa=fibelaudio()
    #fa.run()
    #print(screen)
    if not gesture_active:
        print('no gest')
        return
    if screen=='back':
        busno=1
    else:
        busno=1
    try:
        gesture=gesture(busno=busno,caseflag=1)
    except:
        sys.stderr.write("NO SENSOR at "+str(busno))
