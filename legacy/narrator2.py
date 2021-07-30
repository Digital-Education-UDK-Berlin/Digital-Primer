import json
import glob
import time, queue, threading
import subprocess
import Fibel.drivers.it8951 as driver_it8951
import os, time
from Fibel.FolioText import FolioText
from random import randrange
from PIL.ImageOps import invert
import mutagen
import pyaudio
import simpleaudio as sa

#from Fibel.input.minrecorder import recorder

import re
def sort_human(l):
    convert = lambda text: float(text) if text.isdigit() else text
    alphanum = lambda key: [convert(c) for c in re.split('([-+]?[0-9]*\.?[0-9]*)', key)]
    l.sort(key=alphanum)
    return l


class oggparser:

    def __init__(self,audio):
        self.timestamps = []
        self.parsed = {}
        self.cwd = os.getcwd()
        self.audio = audio
        self.text = ""

    def parse_json(self):
        b = mutagen.File(self.audio)
        try:
            toparse = b["text"]
            new_parse = "[" + toparse[0].replace("\t","") + "]"
            new_parse=new_parse.replace(',]',']')
            self.parsed = json.loads(new_parse)
        except:
            #print(b)
            print("ERROR ENCODING")


    def get_text(self):
        for i in self.parsed:
            self.text = self.text + i["w"] + "§"
        return self.text

    def get_timestamps(self):
        start = 0
        for i in self.parsed:
            self.timestamps.append({"start" : int(start),"end": int(i["stop"])})
            start = i["stop"]
        return self.timestamps

class audioplayer(threading.Thread):

    def __init__(self,eventqueue,audio_path=""):
        super(audioplayer, self).__init__()
        self.p = pyaudio.PyAudio()
        self.path = audio_path
        self.eventqueue = eventqueue

    def check_event(self, item: dict):
        if item["player"][0]["state"] == "play":
            self.path = item["player"][1]["path"]
            self.play_audiofile()

    def play_audiofile(self):
        file_to_play = sa.WaveObject.from_wave_file(self.path)
        file_to_play.play()

    def run(self):
        while True:
            try:
            #if 1:
                item = self.eventqueue.get(block=True, timeout=None)
                self.check_event(item)
                self.eventqueue.task_done()
            except:
                print("something got seriously wrong")


class audiofolio(threading.Thread):

    def __init__(self, folioqueue, drivers, text, timestamps,waves,audioplay_queue,font=os.path.join(os.path.dirname(__file__), 'Fonts/schola.otf')):
            super(audiofolio, self).__init__()
            self.folioqueue = folioqueue
            self.screendriver = drivers
            self.foliopointers = []
            self.text = text
            self.timestamps = timestamps
            self.waves=waves
            self.audioplay_queue=audioplay_queue
            self.font=font

    def check_event(self, item: dict):
        if item["folio"][0]["state"] == "generate":
            self.text = item["folio"][1]["text"]
            self.generate_folio()
        elif item["folio"][0]["state"] == "show":
            self.show()
        elif item["folio"][0]["state"] == "jump":
            pass

    def calc_bufferaddress_wh(self, _id, height, width,screendriver):
            return (self.screendriver.img_addr + 480000 + _id * ( 1 * height * width))

    def generate_folio(self):
        temp_height = 200
        big_height = 800
        word_counter = 0
        buffercounter = 1
        for text in self.text:
            word_pointers = []
            if buffercounter>10:
                break
            text_image = FolioText((600,  big_height), pointers = word_pointers, background=255, mode='L')
            text_image.write_text_box(20,0,text,560,self.font,font_size=48,justify_last_line=True)
            buffer_address_positiv = self.calc_bufferaddress_wh(buffercounter, big_height, 600,screendriver)
            buffer_address_negativ = self.calc_bufferaddress_wh(buffercounter+1, big_height, 600,screendriver)
            content_image = text_image.image
            invert_image = invert(content_image.convert('L'))
            self.screendriver.load_image(0,0,content_image, img_addr=buffer_address_positiv)
            self.screendriver.load_image(0,0,invert_image, img_addr=buffer_address_negativ)
            self.foliopointers.append({"buffer_address_positiv":buffer_address_positiv,"buffer_address_negativ":buffer_address_negativ,"word_pointers":text_image.pointers})
            buffercounter = buffercounter+2
            text_image.pointers = []

    def show(self):
        for foliopointer in self.foliopointers:
            self.screendriver.display_buffer_area(0,0,800,600,2,foliopointer['buffer_address_positiv'])
            wordp = foliopointer['word_pointers']
            folio_timestamps = self.timestamps.pop(0)
            token_counter = 0
            before_end = 0

            play = {"player":[{"state":"play"}, {"path": self.waves.pop(0)}]}
            self.audioplay_queue.put(play)

            for pointer in wordp:
                screendriver.display_buffer_area(pointer[1],(-1)*pointer[0]+600-pointer[2],pointer[3],pointer[2],2,foliopointer['buffer_address_negativ'])
                if token_counter>0:
                    screendriver.display_buffer_area(previous_pointer[1],(-1)*previous_pointer[0]+600-previous_pointer[2],previous_pointer[3],previous_pointer[2],2,foliopointer['buffer_address_positiv'])
                current_end = folio_timestamps[token_counter]['end']
                difference = current_end - before_end
                time.sleep(difference*0.0001)
                token_counter = token_counter + 1
                before_end = current_end
                previous_pointer=pointer

    def run(self):
        while True:
            item = self.folioqueue.get(block=True, timeout=None)
            self.check_event(item)
            self.folioqueue.task_done()

screendriver = driver_it8951.IT8951()
screendriver.init(rotate=1, screen="front")

audioplay_queue = queue.Queue()
folio_queue = queue.Queue()
audioplayer= audioplayer(audioplay_queue)
audioplayer.start()

waves=[]
texts=[]
stamps=[]

audiotext='Hans im Glück/Dorothea'

for oggfile in sort_human(glob.glob("/home/fibel/data/audiotext/Märchen/"+audiotext+"/*.ogg")):
    wavfile = oggfile +".wav"

    if not os.path.isfile(wavfile):
        subprocess.run(["opusdec", "--force-wav", oggfile , wavfile])

    a = oggparser(oggfile)
    a.parse_json()
    stamps.append(a.get_timestamps())
    texts.append(a.get_text())
    waves.append(wavfile)


generate_foliae = {"folio":[{"state":"generate"}, {"text":texts}]}

folio_queue.put(generate_foliae)
folio_instance = audiofolio(folio_queue, screendriver, texts, stamps, waves, audioplay_queue)
folio_instance.start()

show_foliae = {"folio":[{"state":"show"}]}
folio_queue.put(show_foliae)

