import json
import glob
import queue
import threading
import os
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

#from Fibel.input.minrecorder import recorder

#pseudocode for implementing "ringbuffer"
# all_pages = [0,1,2...]
# current_page = 0
# max_buffer_page = 5
# buffercontent = {1:{"bufferaddress":bufferaddressvalue,"page_number":pagenumbervalue}}
# boolen_load_to_front = false
#
#
# generate_next(numberofpages):
#
# for i in range:


def sort_human(l):
    convert = lambda text: float(text) if text.isdigit() else text
    alphanum = lambda key: [convert(c) for c in re.split('([-+]?[0-9]*\.?[0-9]*)', key)]
    l.sort(key=alphanum)
    return l


class Timer(threading.Thread):

    def __init__(self, triggers, q_audiofolio):
        super(Timer, self).__init__()
        self.triggers = triggers[1:]
        self.q_audiofolio = q_audiofolio
        self.start_time = 0
        self.end_time = 0
        self.elapsed_time = 0
        self.timestamp_counter = 0

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

    def send_event_next(self):
        self.q_audiofolio.put({"timer":[{"state":"next"}]})

    def send_event_end(self):
        self.q_audiofolio.put({"timer":[{"state":"end"}]})

    def run(self):
        self.start_timer()
        current_elapsed_time = 0
        while current_elapsed_time < self.triggers[len(self.triggers)-1]["end"] and self.timestamp_counter < len(self.triggers):
            current_elapsed_time = self.get_Elapsed_Time()
            self.check_current_timestamp(current_elapsed_time)
            time.sleep(0.001)
        self.send_event_end()


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

class Audioplayer(threading.Thread):

    def __init__(self, eventqueue, audio_path=""):
        super(Audioplayer, self).__init__()
        self.path = audio_path
        self.q_event = eventqueue

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
                item = self.q_event.get(block=True, timeout=None)
                self.check_event(item)
                self.q_event.task_done()
            except:
                print("something got seriously wrong")


class Audiofolio(threading.Thread):

    def __init__(self, folioqueue, drivers, text, timestamps, waves, q_audio, font=os.path.join(os.path.dirname(__file__), 'Fonts/schola.otf')):
        super(Audiofolio, self).__init__()
        self.q_folio = folioqueue
        self.screendriver = drivers
        self.foliopointers = []
        self.text = text
        self.timestamps = timestamps
        self.waves = waves
        self.q_audio = q_audio
        self.font = font
        self.current_folio = 0
        self.current_word = 0
        self.current_page = 0

    def check_event(self, item: dict):
        if item["folio"][0]["state"] == "generate":
            self.text = item["folio"][1]["text"]
            self.generate_folio()
        elif item["folio"][0]["state"] == "show":
            self.show()
        elif item["folio"][0]["state"] == "nextpage":
            self.display_next_page()
        elif item["folio"][0]["state"] == "nextword":
            self.display_next_buffer_area()
        elif item["folio"][0]["state"] == "resetword":
            self.resetset_current_word()
        elif item["folio"][0]["state"] == "setfolio":
            self.next_page()
            self.testcounter = 0

    def calc_bufferaddress_wh(self, _id, height, width):
        return (self.screendriver.img_addr + 480000 + _id * (1 * height * width))

    def generate_folio(self):
        big_height = 800
        buffercounter = 1
        black_image = Image.new("1", (600, 800), color='#000000')
        self.screendriver.load_image(0, 0, black_image, img_addr=self.screendriver.img_addr)
        for text in self.text:
            word_pointers = []
            if buffercounter > 7:
                break
            text_image = FolioText((600, big_height), pointers=word_pointers, background=255, mode='1')
            text_image.write_text_box(20, 0, text, 560, self.font, font_size=48, justify_last_line=True)
            buffer_address_positiv = self.calc_bufferaddress_wh(buffercounter, big_height, 600)
            #buffer_address_negativ = self.calc_bufferaddress_wh(buffercounter+1, big_height, 600,screendriver)
            content_image = text_image.image
            #invert_image = invert(content_image.convert('L'))
            self.screendriver.load_image(0, 0, content_image, img_addr=buffer_address_positiv)
            self.foliopointers.append({"buffer_address_positiv":buffer_address_positiv, "word_pointers":text_image.pointers})
            buffercounter = buffercounter + 1
            text_image.pointers = []

    def display_next_page(self):
        self.screendriver.display_buffer_area(0, 0, 800, 600, 2, self.foliopointers[self.current_folio]['buffer_address_positiv'])

    def next_page(self):
        self.current_folio = self.current_folio + 1

    def resetset_current_word(self):
        self.current_word = 0

    def display_next_buffer_area(self):
        try:
            pointer = self.foliopointers[self.current_folio]['word_pointers'][self.current_word]
            self.screendriver.display_buffer_area(pointer[1]+pointer[3], (-1)*pointer[0]+600-pointer[2], 5, pointer[2], 2, self.screendriver.img_addr)
            if self.current_word > 0:
                previous_pointer = self.foliopointers[self.current_folio]['word_pointers'][self.current_word - 1]
                self.screendriver.display_buffer_area(previous_pointer[1]+previous_pointer[3], (-1)*previous_pointer[0]+600-previous_pointer[2] ,5 ,previous_pointer[2], 2, self.foliopointers[self.current_folio]['buffer_address_positiv'])
            self.current_word = self.current_word + 1
        except:
            print("this should not called after iteration is finished")

    def show(self):
        #legacy function
        self.display_next_page()
        time.sleep(1)
        self.display_next_buffer_area()
        time.sleep(1)
        self.display_next_buffer_area()
        time.sleep(1)
        self.display_next_buffer_area()


    def run(self):
        while True:
            item = self.q_folio.get(block=True, timeout=None)
            self.check_event(item)
            self.q_folio.task_done()



class Coordinator():

    def __init__(self, audioplay_queue, folio_queue, timestamps, waves):
        self.audioplayer_queue = audioplay_queue
        self.timer_queue_back = queue.Queue()
        self.folio_queue = folio_queue
        self.all_time_stamps = timestamps
        self.waves = waves


    def run_all(self):
        show_foliae = {"folio":[{"state":"nextpage"}]}
        show_next_word = {"folio":[{"state":"nextword"}]}
        reset_word = {"folio":[{"state":"resetword"}]}
        set_folia = {"folio":[{"state":"setfolio"}]}
        counter = 0
        for timestamps in self.all_time_stamps:
            if counter < 8:
                counter = counter + 1
                self.folio_queue.put(show_foliae)
                time.sleep(1)
                new_timer = Timer(timestamps, self.timer_queue_back)
                new_timer.start()
                end_signal = True
                play = {"player":[{"state":"play"}, {"path": self.waves.pop(0)}]}
                self.audioplayer_queue.put(play)
                while end_signal:
                    item = self.timer_queue_back.get(block=True, timeout=None)
                    if item["timer"][0]["state"] == "next":
                        self.folio_queue.put(show_next_word)
                    elif item["timer"][0]["state"] == "end":
                        end_signal = False
                self.folio_queue.put(set_folia)
                self.folio_queue.put(reset_word)



screendriver = driver_it8951.IT8951()
screendriver.init(rotate=1, screen="front")

q_audioplay = queue.Queue()
q_folio = queue.Queue()
audioplayer = Audioplayer(q_audioplay)
audioplayer.start()

waves = []
texts = []
stamps = []

#audiotext='Über drei Groschen/Hibiki'
audiotext='Aschenputtel/Dorothea'

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

# print(texts)
generate_foliae = {"folio":[{"state":"generate"}, {"text":texts}]}
#
q_folio.put(generate_foliae)
folio_instance = Audiofolio(q_folio, screendriver, texts, stamps, waves, q_audioplay)
folio_instance.start()
q_folio.put(generate_foliae)

time.sleep(55)
newCoordinator = Coordinator(q_audioplay, q_folio, stamps, waves)
newCoordinator.run_all()
