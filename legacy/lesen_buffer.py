import time, queue, threading
import fibel_logger
from math import sqrt
from Fibel.input.minbutton import fib_button
from Fibel.input.minrecorder import recorder
from Fibel.FolioText import FolioText
from plane import plane

mode='NEUTRAL'
#wordz=['die Birke','die Buche','die Linde','die Eiche','die Tanne','die Fichte','der Apfelbaum','die Pappel','die Haselnuss','der Holunder','der Ahorn']
logger_name = 'lesen'
wordz=['die Birke','die Buche','die Linde','die Eiche','die Tanne','die Fichte','der Apfelbaum']
class lesen():

    def __init__(self, wordz:list, sensor_queue, recorder_queue, screen_queue, logger):
        self.button_state = 0
        self.counter = 0
        self.wordz = wordz
        self.sensor_queue = sensor_queue
        self.recorder_queue = recorder_queue
        self.screen_queue = screen_queue
        self.current_package = {"gesture":[{"state":1},{"mov":"gesturestate"}]}
        self.parser_switcher = {
            "gesture" : self.gesture_parsing,
            "button" : self.button_parsing
            }
        self.logger = logger
        self.logger.info('lesen iniatilzed')    #.format(births)
        self.first_message()


    def button_change(self, old: int, new: int) -> dict:
        if old and new:
            rec = {"recorder":[{"state":"cont"}, {"word":self.wordz[self.counter]}]}
            scr =  {"screen":[{"state":"nil"}]}
            return [rec,scr]
        elif old and not new:
            self.logger.info('button released')
            rec = {"recorder":[{"state":"stop"}, {"word":self.wordz[self.counter]}]}
            self.counter = self.counter + 1
            scr =  {"screen":[{"state":"display_img"},  {"word":self.wordz[self.counter]}, {"factor":3}]}
            return [rec,scr]
        elif not old and not new:
            rec = {"recorder":[{"state":"nil"}, {"word":self.wordz[self.counter]}]}
            scr =  {"screen":[{"state":"nil"}]}
            return [rec,scr]
        elif not old and new:
            self.logger.info('button pressed')
            rec = {"recorder":[{"state":"start"}, {"word":self.wordz[self.counter]}]}
            scr =  {"screen":[{"state":"nil"}]}
            return [rec,scr]

    def button_parsing(self):
        new_button_state = self.current_package["button"]["state"]
        message = self.button_change(self.button_state, new_button_state)
        self.button_state = new_button_state
        return message

    def gesture_parsing(self):
        if self.current_package["gesture"][0]["state"]:
            self.logger.info('recifed swipe')
            self.counter = self.counter + 1
            rec = {"recorder":[{"state":"nil"}, {"word":self.wordz[self.counter]}]}
            scr =  {"screen":[{"state":"display_img"},  {"word":self.wordz[self.counter]}, {"factor":3}]}
            return [rec,scr]

    def package_parsing(self, item: dict) -> int:
        self.current_package = item
        parse = self.parser_switcher.get(list(item.keys())[0],"Invalid Message")
        message = parse()
        return message

    def first_message(self):
        #this needs to be called just one time
        self.screen_queue.put({"screen":[{"state":"display_img"},  {"word":self.wordz[self.counter]}, {"factor":3}]})



    def main_loop(self):
        #self.screen_queue.put({"screen":[{"state":"display_img"},  {"word":self.wordz[self.counter]}, {"factor":3}]})
        while self.counter < len(self.wordz)-1:
            try:
                item = self.sensor_queue.get(timeout=2)
                self.sensor_queue.task_done()
                message = self.package_parsing(item)
                if message:
                    self.recorder_queue.put(message[0])
                    self.screen_queue.put(message[1])
            except queue.Empty:
                self.logger.error('empty sensor_queue')



def prepare_buffer(newplane, wordz):
    newplane.screen.generate_setzkasten(wordz,3)


# def calc_address(int: id, display):
#     return (display.img_addr+id*(2*display.width*display.height+1))

new_logger = fibel_logger.initalize_logger("lesen")
sensor_queue = queue.Queue()
event_queue = queue.Queue()
screen_queue = queue.Queue()
example_path = "/home/fibel/data/sessions/"
a = plane(1, "front", 1, event_queue, sensor_queue, screen_queue, example_path, new_logger)
a.init_screen()
prepare_buffer(a, wordz)
a.init_gesture()
a.init_button()
a.init_audio()
a.buttondriver.start()
a.audiodriver.start()
a.gesturedriver.start()
a.screen.start()
l = lesen(wordz, sensor_queue, event_queue, screen_queue,  new_logger)
while 1:
    l.recorder_queue.put({"recorder":[{"state":"new_session"}]})
    l.main_loop()
    l.counter=0

a.buttondriver.stop()
a.buttondriver.join()
a.audiodriver.join()


# new_height = newplane.screendriver.height
# new_width = newplane.screendriver.width
#
# print(display.img_addr)
# id = 1
# print(display.img_addr+id*(2*display.width*display.height+1))
#print(calc_address(1,display))

# for i in range(0,len(wordz)):
#     individual_pointer = newplane.screendriver.calc_bufferaddress(i)
#     newplane.screendriver.generate_and_load_buffer(wordz[i],3,individual_pointer)
#     buffer_numbers.append(individual_pointer)
#
# newplane.screendriver.display_img_from_buffer(buffer_numbers[5],3)





# word_pointers = []
# folio = FolioText((int(display.height),int(display.width/1)), word_pointers)
# font_size=int(sqrt((30000/len(wordz[0]))))
# folio.write_text_box(0, 0, wordz[0], box_width=560, font_filename=font, font_size=font_size, color=color, place='justify')
# display.load_image(0,0,folio.image,img_addr=calc_address(1,display))
# display.display_buffer_area(0,0,800,600,2,buff_addr=calc_address(1,display))
# #display.img_addr+label_id*(2*label.width*label.height+1)
