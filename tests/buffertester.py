import Fibel.drivers.it8951 as driver_it8951
import os, time
from Fibel.FolioText import FolioText
from random import randrange


trees=['die Birke','die Buche','die Linde','die Eiche','die Tanne','der Apfelbaum','die Eiche','die Tanne','der Apfelbaum']
#trees=['die Birke','die Buche','die Linde','die Eiche']
dirname = os.path.dirname(__file__)
font = os.path.join(dirname, 'Fonts/schola.otf')


def calc_bufferaddress_wh(_id, height, width,screendriver):
        return (screendriver.img_addr + 480000 + _id * ( 1 * height * width))

#not used
def create_whitepage(setzkasten):
    text_image = FolioText((600,  800), pointers = [], background=255, mode='L')
    buffer_address = screendriver.img_addr
    screendriver.load_image(0, 0, text_image.image,img_addr=buffer_address)
    setzkasten["blankpage"] = {"address":buffer_address,"height":800,"width":600,"ypos":0}
    return setzkasten

def generate_setzkasten(wordz,driver):
    global font
    screendriver = driver
    setzkasten = {}
    word_pointers = []
    temp_height = 200
    big_height = 800
    id = 0
    word_counter = 0
    chunks = [wordz[x:x+4] for x in range(0, len(wordz), 4)]
    print(chunks)
    for b in chunks:
        text_image = FolioText((600,  big_height), pointers = word_pointers, background=255, mode='L')
        buffer_address = calc_bufferaddress_wh(id, big_height, 600,screendriver)
        for i in range(0,len(b)):
            ypos = i*(200)
            text_image.write_text(0,ypos,wordz[word_counter], font_size='fill', font_filename=font, max_height=temp_height, max_width=600,color=0)
            setzkasten[wordz[word_counter]] = {"address":buffer_address,"height":200,"width":600,"ypos":ypos}
            content_image = text_image.image
            word_counter = word_counter + 1
        id = id + 1
        screendriver.load_image(0, 0, content_image,img_addr=buffer_address)
        print("finished loading folia" + str(id))
    return setzkasten

def generate_setzkasten_text(wordz,driver):
    global font
    screendriver = driver
    setzkasten = {}
    word_pointers = []
    temp_height = 200
    big_height = 800
    id = 0
    word_counter = 0
    # for i in words:




# screendriver = driver_it8951.IT8951()
# screendriver.init(rotate=1, screen="front")
# setzkasten = generate_setzkasten(trees)
# print(setzkasten)
#blank = setzkasten["blankpage"]
#_word = setzkasten["die Tanne"]
#screendriver.display_buffer_area(0,0,_word["height"],_word["width"],2,_word["address"]+_word["ypos"])
def testrun_1():
    screendriver = driver_it8951.IT8951()
    screendriver.init(rotate=1, screen="front")
    setzkasten = generate_setzkasten(trees,screendriver)
    for i in trees:
        _word = setzkasten[i]
        time.sleep(1)
        screendriver.display_buffer_area(0,0,_word["height"],_word["width"],2,_word["address"]+_word["ypos"])
        print("display:" + str(i))

def testrun_3():
    screendriver = driver_it8951.IT8951()
    screendriver.init(rotate=3, screen="front")
    setzkasten = generate_setzkasten(trees,screendriver)
    # _word = setzkasten["die Eiche"]
    # screendriver.display_buffer_area(0,0,_word["height"],_word["width"],2,_word["address"] + _word["ypos"] + 200)
    # _word = setzkasten["die Birke"]
    # screendriver.display_buffer_area(600,0,_word["height"],_word["width"],2,_word["address"] + _word["ypos"] - 200)
    for i in trees:
        _word = setzkasten[i]
        time.sleep(1)
        screendriver.display_buffer_area(600,0,_word["height"],_word["width"],2,_word["address"]+_word["ypos"] + 200)
        print("display:" + str(i))

#testrun_1()
testrun_1()
