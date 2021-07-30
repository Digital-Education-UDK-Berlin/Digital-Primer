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
from random import randrange
from typing import List, Dict

import inspect
import importlib.util
from pathlib import Path

full_path = os.path.dirname(os.path.abspath(__file__))
rootpath = (str(Path(full_path).parents[1]))
spec_gesture = importlib.util.spec_from_file_location("gesture_driver", rootpath + str("/Fibel/input/gesture_driver_narrator.py"))
spec_screendriver = importlib.util.spec_from_file_location("it8951", rootpath + str("/Fibel/drivers/it8951.py"))
spec_oggparser = importlib.util.spec_from_file_location("Oggparser", full_path + str("/oggparser.py"))
spec_audioplayer = importlib.util.spec_from_file_location("Audioplayer", full_path + str("/audioplayer.py"))
spec_navigator = importlib.util.spec_from_file_location("Navigator", full_path + str("/navigator.py"))

gesture_driver_module = importlib.util.module_from_spec(spec_gesture)
driver_it8951 = importlib.util.module_from_spec(spec_screendriver)
oggparser_module = importlib.util.module_from_spec(spec_oggparser)
audioplayer_module = importlib.util.module_from_spec(spec_audioplayer)
navigator_module = importlib.util.module_from_spec(spec_navigator)

spec_gesture.loader.exec_module(gesture_driver_module)
spec_screendriver.loader.exec_module(driver_it8951)
spec_oggparser.loader.exec_module(oggparser_module)
spec_audioplayer.loader.exec_module(audioplayer_module)
spec_navigator.loader.exec_module(navigator_module)


# def sort_human(l):
#     convert = lambda text: float(text) if text.isdigit() else text
#     alphanum = lambda key: [convert(c) for c in re.split('([-+]?[0-9]*\.?[0-9]*)', key)]
#     l.sort(key=alphanum)

def sort_human(l):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    l.sort(key=alphanum_key)
    return l


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


# def getstringkey(namestring):
#     position = 0
#     counter = 0
#     for i in namestring:
#         print(i)
#         counter = counter +1
#         if i.isdigit():
#             position = counter
#     print(position)
#     return namestring[:position]
#


# def sortfunctiontemp(_list):
#     convert = lambda text: int(text) if text.isdigit() else text
#     alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]

def start_all(name):
    screendriver = driver_it8951.IT8951()
    screendriver.init(rotate=1, screen="front")

    q_audioplay_input = queue.Queue()
    q_folio_input = queue.Queue()
    q_folio_output = queue.Queue()

    waves = []
    texts = []
    stamps = []


    #audiotext = 'Aschenputtel/Dorothea'

    #fixme path need to be argument of function
    # [{content:}]

    buildpath = rootpath + "/data/audiotext/Märchen/"+name+"/ogg/"+"/*.ogg"
    # print(buildpath)
    #
    #
    #
    #
    # print(sorted(glob.glob(buildpath),key=alphanum_key))
    # print("_______")
    print(sort_human(glob.glob(buildpath)))
    for oggfile in sort_human(glob.glob(buildpath)):
        wavfile = oggfile +".wav"
        print(wavfile)

        if not os.path.isfile(wavfile):
            subprocess.run(["opusdec", "--force-wav", oggfile, wavfile])

        a = oggparser_module.Oggparser(oggfile)
        a.parse_json()
        stamps.append(a.get_timestamps())
        texts.append(a.get_text())
        waves.append(wavfile)

    logger = logging.getLogger('simple_example')

    audioplayer = audioplayer_module.Audioplayer(q_audioplay_input)
    audioplayer.start()
    # demotextes = [{"format": text, "content": string / pathto tmp},{"format": text, "content": string / pathto tmp}]
    folio_instance = navigator_module.Navigator(q_folio_input, q_folio_output, screendriver, texts, stamps)
    folio_instance.start()

    q_gesture_input = queue.Queue()
    q_gesture_output = queue.Queue()
    q_folio = queue.Queue()
    thread_gesture = gesture_driver_module.gesture_driver(1, q_gesture_input, q_gesture_output, logger)
    thread_gesture.start()
    newCoordinator = Coordinator(q_audioplay_input, q_folio_input, q_folio_output, stamps, waves, q_gesture_input, q_gesture_output, texts )
    newCoordinator.run_all()


if __name__ == '__main__':
    start_all("Kleines Sylabisches Lexikon")
