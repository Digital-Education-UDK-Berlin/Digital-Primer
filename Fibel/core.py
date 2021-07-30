from PIL import Image, ImageDraw
from Fibel.init import *

def say(msg):
    print(msg)

def cover():
    content_image=Image.open(lesson_dir+'cover.bmp')
    driver.load_image(0,0,content_image,img_addr=pointer)
    driver.display_buffer_area(0,0,800,600,2,pointer)
    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Titles/Epoche_1-ddh', 'rb')).play()
    time.sleep(2.35)
    driver.display_buffer_area(730,0,70,600,2,pointer)
    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Words/lesen/-ddh', 'rb')).play()
    time.sleep(1.84)
    driver.display_buffer_area(600,0,140,600,2,pointer)
    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Titles/Thema_1-ddh', 'rb')).play()
    time.sleep(2.6)
    driver.display_buffer_area(520,0,80,600,2,pointer)
    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Words/Tiere/-ddh', 'rb')).play()
    time.sleep(1.83)
    driver.display_buffer_area(390,0,140,600,2,pointer)
    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Titles/Lektion_1-ddh', 'rb')).play()
    time.sleep(2.6)
    driver.display_buffer_area(0,0,200,600,2,pointer)

def load_foliae(voice='ddh'):
    global pointer,loaded_foliae,active_label
    pointer=driver.img_addr+(2*driver.width*driver.height+1)
    for folio_link in folio_links:
        label=re.sub("^\d+\. ?","", folio_link)
        pointers[label]=dict()
        pointers[label]["audio"]=dict()
        try:
            pointers[label]["audio"][voice]=sa.WaveObject.from_wave_read(wave.open(lexikon_dir+"WAV/"+label+"/"+voice+".wav"))
        except:
            try:
                pointers[label]["audio"][default_voice]=sa.WaveObject.from_wave_read(wave.open(lexikon_dir+"WAV/"+label+"/"+default_voice+".wav"))
            except:
                1
        pointers[label]['folio']=pointer
        folio_image=Image.open(deck_dir+folio_link)
        lock.acquire()
        driver.load_image(0,0,folio_image,img_addr=pointer)
        driver.display_buffer_area(0,0,800,600,2,pointer)
        #pointers[label]["audio"].play().wait_done()
        try:
            pointers[label]["audio"][voice].play()
        except:
            try:
                pointers[label]["audio"][default_voice].play()
            except:
                sys.stderr.write("no audio for "+label)
        #fa.active_label=label
        lock.release()
        pointers[label]["image"]=pointer
        pointer+=(driver.width*driver.height+1)
        loaded_foliae+=1
    #print ("Images loaded in "+str(start_load-time.time()))

def fallback_play(cursor,voice):
    label=labels[cursor]
    #global pointers,labels
    try:
        pointers[labels[cursor]]["audio"][voice].play().wait_done()
    except:
        try:
            pointers[label]["audio"][voice]=sa.WaveObject.from_wave_read(wave.open(lexikon_dir+"WAV/"+label+"/"+voice+".wav"))
            pointers[labels[cursor]]["audio"][voice].play().wait_done()
        except:
            try:
                pointers[labels[cursor]]["audio"][default_voice].play().wait_done()
            except:
                sys.stderr.write("could not play "+labels[cursor])

def lesen(name,labels):
    global fa
    if 'fa' not in globals():
      fa=fibelaudio()
      fa.run()
    #displaying first folio
    cursor=0
    fa.active_label=name+'-'+name
    text_image = ImageText((600,200), background=(255,255,255))
    text_image.write_text(20,0,name, font_size='fill', max_height=200, max_width=560,color=(0,0,0))

    driver.load_image(0,100,text_image.image,img_addr=driver.img_addr)
    driver.display_buffer_area(0,0,800,600,2,driver.img_addr)

    #fallback_play(cursor,voice)

    old_audiofile=""
    session_start=time.time()
    fa.label_displayed=session_start
    print('#SESSION#'+name+'#'+str(session_start))

    while(True):
        #when recording was successful show new folio
        if fa.last_audiofile and fa.last_audiofile!=old_audiofile:
            print(cursor)
            if cursor<len(labels):
                print(labels[cursor])
                text_image = ImageText((600,200), background=(255,255,255))
                text_image.write_text(20,0,labels[cursor], font_size='fill', max_height=200, max_width=560,color=(0,0,0))
                driver.load_image(0,100,text_image.image,img_addr=driver.img_addr)
                driver.display_buffer_area(0,0,800,600,1,driver.img_addr)
                #fallback_play(cursor,voice)
                fa.label_displayed=time.time()
                fa.active_label=labels[cursor]+'-'+name.upper()
                fa.last_audiofile=""
                time.sleep(0.2)
                cursor+=1
            else:
                fa.last_audiofile=''
                print('#ENDSESSION#'+str(session_start)+'#'+name+'#'+str(time.time()-session_start))
                break


def imitate(voice='ddh'):
    global fa
    fa=fibelaudio()
    fa.run()
    #displaying first folio
    cursor=0
    fa.active_label=labels[cursor]
    #driver.display_buffer_area(0,0,100,600,1,pointers[labels[cursor]]["folio"])
    #driver.display_buffer_area(700,0,100,600,1,pointers[labels[cursor]]["folio"]+1600)
    #if cursor>0:
    #    pointers[labels[cursor-1]]["audio"].wait_done()
    #pointers[labels[cursor]]["audio"].play().wait_done()
    #driver.display_buffer_area(100,0,600,600,2,pointers[labels[cursor]]["folio"]+800)
    driver.display_buffer_area(0,0,800,600,2,pointers[labels[cursor]]["folio"])
    fallback_play(cursor,voice)
    old_audiofile=""

    while(True):
        #when recording was successful show new folio
        #print(fa.last_audiofile+"LAL"+old_audiofile)
        if fa.last_audiofile and fa.last_audiofile!=old_audiofile:
            print(fa.last_audiofile+"BAB"+old_audiofile)
            cursor+=1
            if cursor<len(labels):
                driver.display_buffer_area(0,0,800,600,2,pointers[labels[cursor]]["folio"])
                #driver.display_buffer_area(700,0,100,600,1,pointers[labels[cursor]]["folio"]+1600)
                #driver.display_buffer_area(100,0,600,600,2,pointers[labels[cursor]]["folio"]+800)
                #pointers[labels[cursor]]["audio"].play().wait_done()
                fallback_play(cursor,voice)
                fa.active_label=labels[cursor]
                fa.last_audiofile=""
                time.sleep(0.2)
            else:
                break

def feedback_negative():
    sa.WaveObject.from_wave_read(wave.open(root_dir+'Audio/Feedback/Neg/qwack-tm.wav', 'rb')).play()

def feedback_positive():
    sa.WaveObject.from_wave_read(wave.open('dankelia.wav', 'rb')).play()
    #sa.WaveObject.from_wave_read(wave.open('Audio/Feedback/Pos/juhuu-tm.wav', 'rb')).play()
    l=1

def zuordnen1(voice='ddh',title_height=100,variable='up',screen='front'):
    global active_screen,gesture
    for true_cursor in range(0,len(labels)):
        task_start=time.time()
        driver.display_buffer_area(title_height,0,800-title_height,600,2,pointers[labels[true_cursor]]["folio"])
        #pointers[labels[true_cursor]]["audio"].play()
        fallback_play(true_cursor,voice)
        false_cursor=randint(0,max_labels-1)
        false_cursor_start=false_cursor
        trajectory=''
        if variable=='down':
            if screen=='front':
                driver.display_buffer_area(0,0,title_height,600,1,pointers[labels[false_cursor]]["folio"])
            else:
                driver.display_buffer_area(800-title_height,0,title_height,600,1,pointers[labels[false_cursor]]["folio"])
        else:
            if screen=='front':
                driver.display_buffer_area(800-title_height,0,title_height,600,1,pointers[labels[false_cursor]]["folio"])
            else:
                driver.display_buffer_area(0,0,title_height,600,1,pointers[labels[false_cursor]]["folio"])
        while(True):
            cmd=gesture.get_gesture()
            #print(cmd)
            #print(g.busnum)
            if cmd=='C' or cmd=='A':
                #pointers[labels[true_cursor]]["audio"].play()
                fallback_play(true_cursor,voice)
            if cmd=='R' or cmd=='L' or cmd=='U' or cmd=='D':
                trajectory+=cmd
                if cmd=='R' or cmd=='L':
                    false_cursor+=1
                    false_cursor%=max_labels
                if cmd=='U' or cmd=='D':
                    false_cursor-=1
                    false_cursor%=max_labels
                if variable=='down':
                    if screen=='front':
                        driver.display_buffer_area(0,0,title_height,600,1,pointers[labels[false_cursor]]["folio"])
                    else:
                        driver.display_buffer_area(800-title_height,0,title_height,600,1,pointers[labels[false_cursor]]["folio"])
                else:
                    if screen=='front':
                        driver.display_buffer_area(800-title_height,0,title_height,600,1,pointers[labels[false_cursor]]["folio"])
                    else:
                        driver.display_buffer_area(0,0,title_height,600,1,pointers[labels[false_cursor]]["folio"])
            elif cmd=='F' or cmd=='B':
                if true_cursor==false_cursor:
                    status='T'
                    feedback_positive()
                else:
                    status='F'
                    feedback_negative()
                print(status+';'+labels[true_cursor]+';'+labels[false_cursor]+';'+str(round(time.time()-task_start,2))+';'+labels[false_cursor_start]+';'+trajectory)
                break
            time.sleep(0.1)


def randomString(stringLength):
    letters = string.ascii_letters
    return ''.join(choice(letters) for i in range(stringLength))
