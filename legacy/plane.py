#import Fibel.drivers.drivers_base as drivers_base
import time, os, random, queue, threading
import Fibel.drivers.it8951 as driver_it8951
import fibel_logger
from Fibel.input.gesture_driver import gesture_driver
from Fibel.input.minrecorder import recorder
from Fibel.input.minbutton import fib_button
from Fibel.FolioText import FolioText
from Fibel.witty_interface.witty_logger import thread_logger as tl
from Fibel.witty_interface.witty_interface import wpi_interface as wi
#testing
from random import randrange
import random


def get_random_string(length):
    # put your letters in the following string
    sample_letters = 'abcdefghi'
    result_str = ''.join((random.choice(sample_letters) for i in range(length)))
    return result_str



# a minimal class initalising all drivers with parameters and providing a continuous interface
# at one point this might need to become a factory class  -> https://en.wikipedia.org/wiki/Factory_method_pattern

#for ref about color modes: https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes

#for ref rotate values
# ROTATE_0   = 0
# ROTATE_90  = 1
# ROTATE_180 = 2
# ROTATE_270 = 3

# wpi = wi()
# functions_to_log = [wpi.read_v_in, wpi.read_v_out, wpi.read_cur_out]
# variables_to_log = ["v_in","v_out","cur_out"]
# timeintervall = 3
# path = 'testwrite.csv'
#
# a = tl(path, timeintervall, functions_to_log, variables_to_log)
wordz = []
logger_name = 'plane'
trees=['die Birke','die Buche','die Linde','die Eiche','die Tanne']
#trees=['die Birke','die Buche','die Linde','die Eiche','die Tanne','die Fichte','der Apfelbaum','die Pappel','die Haselnuss','der Holunder','der Ahorn']

def testing():
    for i in range(0,2):
        randstr = get_random_string(12)
        wordz.append(randstr)


class new_screen(threading.Thread):

    def __init__(self, alignment, rotation, screen_queue, logger):
        super(new_screen, self).__init__()
        self.dirname = os.path.dirname(__file__)
        self.font = os.path.join(self.dirname, 'Fonts/schola.otf')
        self.alignment = alignment
        self.rotation = rotation
        self.screendriver = driver_it8951.IT8951()
        self.vertical = False
        self.buffer_sizes = []
        self.screen_queue = screen_queue
        self.logger = logger
        self.setzkasten = {}
        if self.rotation == 0 or self.rotation == 2:
            self.height = 600
            self.width = 800
            self.vertical = True
        elif self.rotation == 1 or self.rotation == 3:
            self.height = 800
            self.width = 600
        else:
            quit()


    def inital_screen(self):
        self.screendriver.init(rotate=self.rotation, screen=self.alignment)

    def calc_bufferaddress_wh(self, _id, height, width):
        #return (self.screendriver.img_addr + _id * (2 * width * height +1 ))
        if self.vertical:
            return (self.screendriver.img_addr + 960000 + _id * (1 * height * width +1 ))
        else:
            #_id+=1
            return (self.screendriver.img_addr + 960000 + _id * ( 4 * height * width +1 ))

    def write_white_screen(self):
        id = 0
        text_image = FolioText((self.width, self.height), pointers = [], background=255, mode='L')
        content_image = text_image.image
        pointer = self.screendriver.img_addr
        self.screendriver.load_image(0,0,content_image,img_addr=pointer)
        self.screendriver.display_buffer_area(0,0,self.height ,self.width,2,pointer)
        print("white screen")

    def generate_setzkasten(self, wordz, factor):
        word_pointers = []
        temp_height = 200
        temp_height0 = 200
        id = 0
        i=0
        #text_image = FolioText((self.width,  self.height), pointers = word_pointers, background=255, mode='L')
        for i in wordz:
            if self.rotation == 0:
               text_image = FolioText((self.width,  temp_height0), pointers = word_pointers, background=255, mode='L')
               text_image.write_text(0,0,str(i), font_size='fill', font_filename=self.font, max_height=temp_height0, max_width=self.width,color=0)
            elif self.rotation == 1:
               text_image = FolioText((self.width, temp_height), pointers = word_pointers, background=255, mode='L')
               text_image.write_text(0,0,str(i), font_size='fill', font_filename=self.font, max_height=temp_height, max_width=self.width,color=0)
            elif self.rotation == 2:
               text_image = FolioText((self.width,  temp_height0), pointers = word_pointers, background=255, mode='L')
               text_image.write_text(0,0,str(i), font_size='fill', font_filename=self.font, max_height=temp_height0, max_width=self.width,color=0)
            elif self.rotation == 3:
               text_image = FolioText((self.width,  temp_height), pointers = word_pointers, background=255, mode='L')
               text_image.write_text(0,0,str(i), font_size='fill', font_filename=self.font, max_height=temp_height0, max_width=self.width,color=0)
            else:
               text_image = FolioText((self.width, temp_height), pointers = word_pointers, background=randrange(255), mode='L')
               print("here i should not get")
            # text_image.write_text(0,i*temp_height,str(word), font_size='fill', font_filename=self.font, max_height=temp_height0, max_width=self.width,color=0)
            buffer_address = self.calc_bufferaddress_wh(id ,temp_height, self.width)
            content_image = text_image.image
            self.setzkasten[i] = {"address":buffer_address,"height":content_image.height,"width":content_image.width}
            print(self.setzkasten[i])
            id = id + 1
            self.screendriver.load_image(0,0,content_image,img_addr=buffer_address)



    def display_img_word(self,word):
        _word = self.setzkasten[word]
        #print(_word)
        print("----------------------------")
        if self.rotation == 0:
            self.screendriver.display_buffer_area(0,0,_word["width"],_word["height"],2,_word["address"])
        elif self.rotation == 1:
            #self.screendriver.display_buffer_area(0,0,_word["height"],_word["width"],2,_word["address"])
            self.screendriver.display_buffer_area(0,0,_word["height"],_word["width"],2,_word["address"])
        elif self.rotation == 2:
            self.screendriver.display_buffer_area(0,self.height-_word["height"],_word["width"],_word["height"],2,_word["address"])   #450
        elif self.rotation == 3:
            self.screendriver.display_buffer_area(self.width,0,_word["height"],_word["width"],2,_word["address"])   #450

    #### legacy functions - dont use

    def generate_and_load_buffer(self, text, factor, buffer_position):
        word_pointers = []
        #self.buffer_sizes.append()
                #print(int(self.height/factor))
        if self.vertical:
            text_image = FolioText((self.width, int(self.height/(factor/2))), pointers = word_pointers, background=255, mode='L')
            text_image.write_text(0,0,str(text), font_size='fill', font_filename=self.font, max_height=self.width, max_width=self.width,color=0)
        else:
            text_image = FolioText((self.width, int(self.height/factor)), pointers = word_pointers, background=255, mode='L')
            text_image.write_text(0,0,str(text), font_size='fill', font_filename=self.font, max_height=self.height/factor, max_width=self.width,color=0)
        content_image = text_image.image
        self.screendriver.load_image(0,0,content_image,img_addr=buffer_position)
        return True


    def generate_and_load(self,text,factor):
        word_pointers = []
        print(int(self.height/factor))
        if self.vertical:
            text_image = FolioText((self.width, int(self.height/(factor/2))), pointers = word_pointers, background=255, mode='L')
            text_image.write_text(0,0,str(text), font_size='fill', font_filename=self.font, max_height=self.width, max_width=self.width,color=0)
        else:
            text_image = FolioText((self.width, int(self.height/factor)), pointers = word_pointers, background=255, mode='L')
            text_image.write_text(0,0,str(text), font_size='fill', font_filename=self.font, max_height=self.height/factor, max_width=self.width,color=0)
        content_image = text_image.image
        pointer = self.screendriver.img_addr
        self.screendriver.load_image(0,0,content_image,img_addr=pointer)
        return pointer


    def write_texttest(self,text):
        word_pointers = []
        text_image = FolioText((self.width, self.height), pointers = word_pointers, background=int(random.random()*255), mode='L')
        text_image.write_text(0,0,str(text), font_size='fill', font_filename=self.font, max_height=self.height, max_width=self.width,color=0)
        content_image = text_image.image
        pointer = self.screendriver.img_addr
        self.screendriver.load_image(0,0,content_image,img_addr=pointer)
        if self.vertical:
            self.screendriver.display_buffer_area(0,0,self.width,self.height,2,pointer)
        else:
            self.screendriver.display_buffer_area(0,0,self.height ,self.width,2,pointer)


    def write_textbox(self,text):
        word_pointers = []
        text_image = FolioText((self.width, self.height), pointers = word_pointers, background=255, mode='L')
        text_image.write_text_box(0,0,str(text),self.width-50,font_size=50, font_filename=self.font,color=0)
        content_image = text_image.image
        pointer = self.screendriver.img_addr
        self.screendriver.load_image(0,0,content_image,img_addr=pointer)
        if self.vertical:
            self.screendriver.display_buffer_area(0,0,self.width,self.height,2,pointer)
        else:
            self.screendriver.display_buffer_area(0,0,self.height ,self.width,2,pointer)


    def check_event(self, item: dict):
        if item["screen"][0]["state"] == "generate_and_load":
            new_word = item["screen"][1]["word"]
            factor = item["screen"][2]["factor"]
            pointer = self.generate_and_load(new_word,factor)
            self.display_img_from_buffer(pointer)
        elif item["screen"][0]["state"] == "write_textbox":
            new_text = item["screen"][1]["text"]
            self.write_textbox(new_text)
        elif item["screen"][0]["state"] == "display_img":
            word = item["screen"][1]["word"]
            #factor = item["screen"][2]["factor"]
            self.display_img_word(word)

    def run(self):
        timeout=0
        self.logger.info('start screen')
        while timeout < 3:
            try:
                item = self.screen_queue.get(timeout = 2)
                self.check_event(item)
                self.screen_queue.task_done()
            except:
                self.logger.debug('empty screen')
                timeout = timeout + 1
        self.logger.error('timeout screen')


class plane:

    def __init__(self, busno_gesture, alligment, rotation, event_queue, sensor_queue, screen_queue, audio_dir, logger):
         self.busno_gesture = busno_gesture
         self.audiodriver = None
         self.screen = new_screen(alligment, rotation, screen_queue, logger)
         self.gesturedriver = None
         self.witty = None
         self.witty_logger = None
         self.audio_dir = audio_dir
         self.sensor_queue = sensor_queue
         self.event_queue = event_queue
         self.screen_queue = screen_queue
         self.buttondriver = None
         self.logger = logger
         self.setztkasten = {}

    def init_witty(self):
        self.witty = wi()
        self.logger.debug('initalize Witty')

    def init_witty_logger(self,logtime,path):
        if self.witty:
            functions_to_log = [self.witty.read_v_in, self.witty.read_v_out, self.witty.read_cur_out]
            variables_to_log = ["v_in","v_out","cur_out"]
            timeintervall = logtime
            #path = 'testwrite.csv'
            self.witty_logger = tl(path, timeintervall, functions_to_log, variables_to_log)

    def init_screen(self):
        self.screen.inital_screen()
        self.logger.info('initalize screen')

    def init_audio(self):
        self.audiodriver = recorder(self.event_queue, self.audio_dir, self.logger)

    def init_gesture(self):
        self.gesturedriver = gesture_driver(self.busno_gesture, self.sensor_queue, self.logger)

    def init_button(self):
        self.buttondriver = fib_button(self.sensor_queue, self.logger)

    ##helperfunctions to return the class methods of the specifc drivers, these could be usefull for prototyping

    def return_methods_audio(self):
        print(dir(self.audiodriver))

    def return_methods_screen(self):
        print(dir(self.screen))

    def return_methods_gesture(self):
        print(dir(self.gesturedriver))

def helpergesture(g):
    while True:
        print("_______")
        print(g.gesturedriver.get_gesture())
        print("_______")

if __name__ == "__main__":
    new_logger = fibel_logger.initalize_logger(logger_name)
    sensor_queue = queue.Queue()
    event_queue = queue.Queue()
    screen_queue = queue.Queue()

    example_path = "/home/fibel/finalprimer/fibel/testrecordings/"
    #screen_queue.put({"screen":[{"state":"generate_and_load"},{"word":"Test Screen"},{"factor": 3}]})

    # a = plane(1, "front", 1, event_queue, sensor_queue, screen_queue, example_path, new_logger)   #1 works
    # a.init_screen()
    # a.screen.write_white_screen()



    # a = plane(1, "front", 3, event_queue, sensor_queue, screen_queue, example_path, new_logger)   #1 works
    # a.init_screen()
    # a.screen.generate_setzkasten(wordz,2)
    # a.screen.display_img_word(wordz[0])
    #testing()
    a = [0,1]
    for i in a:
        print("initalize with: " + str(i))
        a = plane(1, "front", i, event_queue, sensor_queue, screen_queue, example_path, new_logger)   #1 works
        time.sleep(1)
        a.init_screen()
        a.screen.generate_setzkasten(trees,2)
        print(a.screen.setzkasten)
        for b in range(0,3):
            a.screen.display_img_word(trees[b])
            time.sleep(1)



    #a.init_witty()
    #a.init_witty_logger(0.1,'testwrite_battery.csv')
    #a.witty_logger.start()
    #a.screen.display_img_from_buffer(a.screen.setzkasten["die Birke"]["address"],factor=1)
    # pointer = a.screen.generate_and_load("der TEST",1)
    # a.screen.display_img_from_buffer(pointer, 1)    #2 works

    #a.witty_logger.stop()
    # a.initaudio()
    # a.returnmethods_audio()
    # a.audiodriver.run()
