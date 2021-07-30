import json
import logging
import glob
import queue
import threading
import os
import sys
import time
import subprocess
import re
import Fibel.drivers.it8951 as driver_it8951
from Fibel.FolioText import FolioText
from random import randrange
from PIL.ImageOps import invert
from PIL import Image
import mutagen
import simpleaudio as sa
from typing import List, Dict
from Fibel.input.gesture_driver_narrator import gesture_driver


#while implementing i realized the communication between these need to be bidirectional - so the coordinator needs to know when audiofolio is finsihed loading the individual parts - this relate

def sort_human(l):
    convert = lambda text: float(text) if text.isdigit() else text
    alphanum = lambda key: [convert(c) for c in re.split('([-+]?[0-9]*\.?[0-9]*)', key)]
    l.sort(key=alphanum)
    return l

class Oggparser:

    def __init__(self, audio):
        self.time_stamps = []
        self.parsed = {}
        self.cwd = os.getcwd()
        self.audio = audio
        self.text = ""

    def parse_json(self):
        b = mutagen.File(self.audio)
        try:
            toparse = b["text"]
            new_parse = "[" + toparse[0].replace("\t", "") + "]"
            new_parse = new_parse.replace(',]', ']')
            self.parsed = json.loads(new_parse)
        except:
            print(b)
            print("ERROR ENCODING")


    def get_text(self):
        for i in self.parsed:
            self.text = self.text + i["w"] + "§"
        print(self.text)
        return self.text

    def get_timestamps(self):
        for i in self.parsed:
            self.time_stamps.append({"start" : int(i["start"]), "end": int(i["stop"])})
        return self.time_stamps


class Timer(threading.Thread):

    def __init__(self, triggers, q_audiofolio_output, q_timer_input):
        #this needs an implemented input querry to stop :(
        super(Timer, self).__init__()
        self.triggers = triggers[1:]
        self.q_audiofolio = q_audiofolio_output
        self.start_time = 0
        self.end_time = 0
        self.elapsed_time = 0
        self.timestamp_counter = 0
        self.alive = True
        self.q_timer_input = q_timer_input

    def start_timer(self):
        self.start_time = time.time()

    def stop_timer(self):
        return self.get_Elapsed_Time()

    def reset(self):
        self.start_time = 0
        self.elapsed_time = 0

    def get_Elapsed_Time(self):
        elapsed_time = self.elapsed_time
        elapsed_time += ((time.time() - self.start_time) * 1000)
        return int(elapsed_time)

    def check_current_timestamp(self, current_elapsed_time):
        if current_elapsed_time > self.triggers[self.timestamp_counter]["start"]:
            self.send_event_next()
            self.timestamp_counter += 1

    def check_event_timer(self, item):
        return bool(item["timer"][0]["state"] == "exit")

    def send_event_next(self):
        self.q_audiofolio.put({"timer":[{"state":"next"}]})

    def send_event_end(self):
        self.q_audiofolio.put({"timer":[{"state":"end"}]})

    def run(self):
        self.start_timer()
        current_elapsed_time = 0
        while current_elapsed_time < self.triggers[len(self.triggers)-1]["end"] and self.timestamp_counter < len(self.triggers) and self.alive:
            if not self.q_timer_input.empty():
                item = self.q_timer_input.get(block=True, timeout=None)
                if self.check_event_timer(item):
                    self.alive = False
                    print("THREAD KILLED YEAY")
            current_elapsed_time = self.get_Elapsed_Time()
            self.check_current_timestamp(current_elapsed_time)
            time.sleep(0.001)
        self.send_event_end()

class Audioplayer(threading.Thread):

    def __init__(self, eventqueue, audio_path=""):
        #this needs an implemented input querry to stop :(
        super(Audioplayer, self).__init__()
        self.path = audio_path
        self.q_event = eventqueue
        self.alive = True
        self.current_file_playing = 0

    def check_event(self, item: dict):
        if item["player"][0]["state"] == "play":
            self.path = item["player"][1]["path"]
            self.play_audiofile()
        elif item["player"][0]["state"] == "exit":
            self.alive = False
        elif item["player"][0]["state"] == "stop":
            self.current_file_playing.stop()

    def play_audiofile(self):
        file_to_play = sa.WaveObject.from_wave_file(self.path)
        self.current_file_playing = file_to_play.play()

    def run(self):
        while self.alive:
            try:
                item = self.q_event.get(block=True, timeout=None)
                self.check_event(item)
                self.q_event.task_done()
            except:
                print("something got seriously wrong")

class Navigator(threading.Thread):

    def __init__(self, folioqueue_input, folioqueue_output, drivers, text, timestamps, font=os.path.join(os.path.dirname(__file__), 'Fonts/schola.otf')):
        super(Navigator, self).__init__()
        self.q_folio_input = folioqueue_input
        self.q_folio_output = folioqueue_output
        self.screendriver = drivers
        self.foliopointers = []
        self.text = text
        self.timestamps = timestamps
        self.font = font
        self.current_folio = 0
        self.current_word = 0
        self.current_page = 0
        self.buffer_slots = dict()
        self.direction_forward = True
        self.alive = True
        self.buffercounter = 1
        self.ringbuffercounter = 0

    def calc_bufferaddress_wh(self, _id, height, width):
        return (self.screendriver.img_addr + 480000 + _id * (1 * height * width))


    def check_event(self, item: dict):
        if item["folio"][0]["state"] == "init":
            self.text = item["folio"][1]["data"]
            self.generate_first()
        elif item["folio"][0]["state"] == "nextpage":
            self.next_page()
        elif item["folio"][0]["state"] == "previouspage":
            self.previous_page()
        elif item["folio"][0]["state"] == "nextword":
            self.display_next_buffer_area()
        elif item["folio"][0]["state"] == "resetword":
            self.resetset_current_word()
        elif item["folio"][0]["state"] == "exit":
            self.alive = False
            print("Get here goodby")
            self.put_events_in_output_q({"folio" : [{"state":"finishedtask"}, {"task":"Goodby"}]})

    def textsize_regulation(self, textarray: List[str]) -> int:
        testlenght = len(textarray)
        if testlenght in range(0, 150):
            return 55
        elif testlenght in range(150, 180):
            return 53
        elif testlenght in range(180, 210):
            return 50
        elif testlenght in range(210, 220):
            return 45
        elif testlenght in range(210, 250):
            return 42
        else:
            return 40


    def generate_next(self):
        for i in range(0,4):
            word_pointers = []
            slot = self.current_page + i
            text_image = FolioText((600, 800), pointers=word_pointers, background=255, mode='1')
            self.textsize_regulation(self.text[slot])
            new_font_size = self.textsize_regulation(self.text[slot])
            assert isinstance(new_font_size, int)
            text_image.write_text_box(20, 0, self.text[slot], 560, self.font, font_size=new_font_size, justify_last_line=True)
            buffer_address_positiv = self.calc_bufferaddress_wh((slot % 8) + self.buffercounter , 800, 600)
            content_image = text_image.image
            print("loaded image to: "+ str(buffer_address_positiv))
            self.screendriver.load_image(0, 0, content_image, img_addr=buffer_address_positiv)
            self.buffer_slots[slot % 8] = { "page_number" : self.current_page + i , "buffer_address": buffer_address_positiv, "word_pointers":text_image.pointers }


    def generate_previous(self):
        for i in range(0,4):
            word_pointers = []
            slot = self.current_page - i
            text_image = FolioText((600, 800), pointers=word_pointers, background=255, mode='1')
            print(self.text[slot])
            text_image.write_text_box(20, 0, self.text[slot], 560, self.font, font_size=48, justify_last_line=True)
            buffer_address_positiv = self.calc_bufferaddress_wh((slot % 8) + self.buffercounter , 800, 600)
            content_image = text_image.image
            print("loaded image to: "+ str(buffer_address_positiv))
            self.screendriver.load_image(0, 0, content_image, img_addr=buffer_address_positiv)
            self.buffer_slots[slot % 8] = {"page_number" : self.current_page - i ,"buffer_address": buffer_address_positiv, "word_pointers":text_image.pointers }

    def generate_first(self):
        black_image = Image.new("1", (600, 800), color='#000000')
        self.screendriver.load_image(0, 0, black_image, img_addr=self.screendriver.img_addr)
        self.generate_next()
        self.display()
        self.put_events_in_output_q({"folio" : [{"state":"finishedtask"}, {"task":"loadinital"}]})

    def next_page(self):
        self.current_page = self.current_page + 1
        self.direction_forward = True
        self.test_for_next_load()
        self.display()
        self.put_events_in_output_q({"folio" : [{"state":"finishedtask"}, {"task":"nextpage"}]})

    def previous_page(self):
        self.current_page = self.current_page - 1
        self.direction_forward = False
        self.test_for_next_load()
        self.display()
        self.put_events_in_output_q({"folio" : [{"state":"finishedtask"}, {"task":"previouspage"}]})

    def display(self):
        self.screendriver.display_buffer_area(0, 0, 800, 600, 2, self.buffer_slots[self.current_page % 8]['buffer_address'])
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Page Number" + str(self.current_page))
        print("show bufferslot " + str(self.current_page % 8) + ": " + str(self.buffer_slots[self.current_page % 8]['buffer_address']))
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")

    def test_for_next_load(self):
        if self.current_page % 4 == 0:
            if self.direction_forward:
                print("_______________________________")
                print("direction_forward")
                self.generate_next()
                # print(a.buffer_slots)
            elif not self.direction_forward:
                print("direction_backward")
                self.generate_previous()
                # print(a.buffer_slots)


    def display_next_buffer_area(self):
        try:
            pointer = self.buffer_slots[self.current_page % 8]['word_pointers'][self.current_word]
            self.screendriver.display_buffer_area(pointer[1]+pointer[3], (-1)*pointer[0]+600-pointer[2], 5, pointer[2], 2, self.screendriver.img_addr)
            if self.current_word > 0:
                previous_pointer = self.buffer_slots[self.current_page % 8]['word_pointers'][self.current_word - 1]
                self.screendriver.display_buffer_area(previous_pointer[1]+previous_pointer[3], (-1)*previous_pointer[0]+600-previous_pointer[2] ,5 , previous_pointer[2], 2, self.buffer_slots[self.current_page % 8]['buffer_address'])
            self.current_word = self.current_word + 1
        except:
            print("this should not called after iteration is finished") #Fixme

    def resetset_current_word(self):
        self.current_word = 0

    def put_events_in_output_q(self, event_dict):
        self.q_folio_output.put(event_dict)


    def run(self):
        while self.alive:
            item = self.q_folio_input.get(block=True, timeout=None)
            self.check_event(item)
            self.q_folio_input.task_done()


class Coordinator():

    def __init__(self, audioplay_queue, folio_in, folio_output, timestamps, waves, q_gesture_input, q_gesture_output, texts):
        self.q_audio_input = audioplay_queue
        self.timer_queue_back = queue.Queue()
        self.q_folio_input = folio_in
        self.all_time_stamps = timestamps
        self.waves = waves
        self.page = 0
        self.texts = texts
        self.q_folio_output = folio_output
        self.q_gesture_input = q_gesture_input
        self.q_gesture_output = q_gesture_output
        self.q_timer_input = queue.Queue()


    def run_all(self):
        show_foliae = {"folio":[{"state":"nextpage"}]}
        show_next_word = {"folio":[{"state":"nextword"}]}
        reset_word = {"folio":[{"state":"resetword"}]}
        set_folia = {"folio":[{"state":"setfolio"}]}

        #prepare
        self.sendinit()
        item = self.q_folio_output.get(block=True, timeout=None)
        print(item)

        #run for each folio
        while self.page < 24:
            #initalise reading for individual
            new_timer = Timer(self.all_time_stamps[self.page], self.timer_queue_back, self.q_timer_input)
            new_timer.start()
            play = {"player":[{"state":"play"}, {"path": self.waves[self.page]}]}
            self.q_audio_input.put(play)
            end_signal = True
            direction = True   # true = forward / false backward
            while end_signal:
                if not self.q_gesture_output.empty():
                    gesture_input = self.q_gesture_output.get(block=False, timeout=None)
                    print(gesture_input)
                    if self.check_event_gesture(gesture_input) == "forward":
                        self.q_audio_input.put({"player":[{"state":"stop"}]})
                        self.q_timer_input.put({"timer":[{"state":"exit"}]})
                        end_signal = False
                    elif self.check_event_gesture(gesture_input) == "backwards":
                        self.q_audio_input.put({"player":[{"state":"stop"}]})
                        self.q_timer_input.put({"timer":[{"state":"exit"}]})
                        end_signal = False
                        direction = False
                        ## audio signal needs to end and also timer needs to be reseted
                item = self.timer_queue_back.get(block=True, timeout=None)
                if item["timer"][0]["state"] == "next":
                    self.q_folio_input.put(show_next_word)
                elif item["timer"][0]["state"] == "end":
                    end_signal = False
                    print("END Folio")
            if direction:
                self.sendresetword()
                self.sendnextpage()
                self.page = self.page + 1
            else:
                self.sendresetword()
                self.sendpreviospage()
                self.page = self.page - 1
            item = self.q_folio_output.get(block=True, timeout=None)   #this makes sure we wait for the foliotext
            print(item)


        self.sendexit()
        item = self.q_folio_output.get(block=True, timeout=None)   #this makes sure we wait for the foliotext
        print(item)
        #for timestamps in self.all_time_stamps:

    # def check_event_gesture(self, item):
    #     return bool(item["gesture"][1]["mov"] == "U")

    def check_event_gesture(self, item):
        returnback = ""
        if (item["gesture"][1]["mov"] == "U"):
            returnback = "forward"
        elif (item["gesture"][1]["mov"] == "D"):
            returnback = "backwards"
        print(returnback)
        return returnback


    #this needs all possible signals
    def sendresetword(self):
        self.q_folio_input.put({"folio":[{"state":"resetword"}]})

    def sendexit(self):
        self.q_folio_input.put({"folio" : [{"state":"exit"}]})
        self.q_audio_input.put({"player":[{"state":"exit"}]})
        print("send exit")
        #here all other queues need to get messages to

    def sendinit(self):
        self.q_folio_input.put({"folio":[{"state":"init"}, {"data":self.texts}]})
        print("send init")
        #here all other queues need to get messages to

    def sendnextpage(self):
        self.q_folio_input.put({"folio":[{"state":"nextpage"}]})

    def sendpreviospage(self):
        print("send backwards")
        self.q_folio_input.put({"folio":[{"state":"previouspage"}]})



def start_all():
    screendriver = driver_it8951.IT8951()
    screendriver.init(rotate=1, screen="front")

    q_audioplay_input = queue.Queue()
    q_folio_input = queue.Queue()
    q_folio_output = queue.Queue()
# audioplayer = Audioplayer(q_audioplay)
# audioplayer.start()

    waves = []
    texts = []
    stamps = []


    audiotext = 'Aschenputtel/Dorothea'

    for oggfile in sort_human(glob.glob("/home/fibel/data/audiotext/Märchen/"+audiotext+"/*.ogg")):
        wavfile = oggfile +".wav"
        print(wavfile)

        if not os.path.isfile(wavfile):
            subprocess.run(["opusdec", "--force-wav", oggfile, wavfile])

        a = Oggparser(oggfile)
        a.parse_json()
        stamps.append(a.get_timestamps())
        texts.append(a.get_text())
        waves.append(wavfile)

    logger = logging.getLogger('simple_example')

    audioplayer = Audioplayer(q_audioplay_input)
    audioplayer.start()

    folio_instance = Navigator(q_folio_input, q_folio_output, screendriver, texts, stamps)
    folio_instance.start()

    q_gesture_input = queue.Queue()
    q_gesture_output = queue.Queue()
    q_folio = queue.Queue()
    thread_gesture = gesture_driver(1, q_gesture_input, q_gesture_output, logger)
    thread_gesture.start()
    newCoordinator = Coordinator(q_audioplay_input, q_folio_input, q_folio_output, stamps, waves, q_gesture_input, q_gesture_output, texts )
    newCoordinator.run_all()

# q_folio_input.put(generate_foliae,block=True, timeout=5)
# item = q_folio_output.get(block=True, timeout=15)
# print(item)

####this will become the coordinator
#general message format


# while endsignal:
#     #nextprocess = True
#     nexttask = tasklist.get(block=True, timeout=4)
#     print(endsignal)
#     assigning_task(nexttask)
#     item = q_folio_output.get(block=True, timeout=None)   #this makes sure we wait for the foliotext
    # print(item)
    # q_folio_output.task_done()


if __name__ == '__main__':
    start_all()



print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")

#
# for i in range(0,14):
#     a.previous_page()
#     time.sleep(1)
