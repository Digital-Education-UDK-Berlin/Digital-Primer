from pathlib import Path
import os
import importlib.util
import threading
from typing import List, Dict
from PIL.ImageOps import invert
from PIL import Image

full_path = os.path.dirname(os.path.abspath(__file__))
rootpath = (str(Path(full_path).parents[1]))
spec_foliotext = importlib.util.spec_from_file_location("FolioText", rootpath + str("/Fibel/FolioText.py"))
FolioText_module = importlib.util.module_from_spec(spec_foliotext)
spec_foliotext.loader.exec_module(FolioText_module)

class Navigator(threading.Thread):

    def __init__(self, folioqueue_input, folioqueue_output, drivers, text, timestamps, font=rootpath + '/Fonts/schola.otf'):
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
            text_image = FolioText_module.FolioText((600, 800), pointers=word_pointers, background=255, mode='1')
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
            text_image = FolioText_module.FolioText((600, 800), pointers=word_pointers, background=255, mode='1')
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
