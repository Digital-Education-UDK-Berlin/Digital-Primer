import time, queue, threading
import fibel_logger
from Fibel.input.minbutton import fib_button
from Fibel.input.minrecorder import recorder
from plane import plane

mode='NEUTRAL'
wordz=['die Birke','die Buche','die Linde','die Eiche','die Tanne','die Fichte','der Apfelbaum','die Pappel','die Haselnuss','der Holunder','der Ahorn']
logger_name = 'lesen'


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
        self.screen_queue.put({"screen":[{"state":"generate_and_load"}, {"word":self.wordz[self.counter]}, {"factor":3}]})



    def button_change(self, old: int, new: int) -> dict:
        if old and new:
            rec = {"recorder":[{"state":"cont"}, {"word":self.wordz[self.counter]}]}
            scr =  {"screen":[{"state":"nil"}]}
            return [rec,scr]
        elif old and not new:
            self.logger.info('button released')
            rec = {"recorder":[{"state":"stop"}, {"word":self.wordz[self.counter]}]}
            self.counter = self.counter + 1
            scr =  {"screen":[{"state":"generate_and_load"}, {"word":self.wordz[self.counter]}, {"factor":3}]}
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
            scr =  {"screen":[{"state":"generate_and_load"}, {"word":self.wordz[self.counter]}, {"factor":3}]}
            return [rec,scr]

    def package_parsing(self, item: dict) -> int:
        self.current_package = item
        parse = self.parser_switcher.get(list(item.keys())[0],"Invalid Message")
        message = parse()
        return message


    def main_loop(self):
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


new_logger = fibel_logger.initalize_logger("lesen")
sensor_queue = queue.Queue()
event_queue = queue.Queue()
screen_queue = queue.Queue()
example_path = "/home/fibel/data/sessions/"
a = plane(1, "front", 1, event_queue, sensor_queue, screen_queue, example_path, new_logger)

#thread_button = fib_button(sensor_queue)
#l = lesen(wordz, sensor_queue, event_queue, a.screendriver)
a.init_screen()
a.init_gesture()
a.init_button()
a.init_audio()
a.buttondriver.start()
a.audiodriver.start()
a.gesturedriver.start()
a.screendriver.start()
l = lesen(wordz, sensor_queue, event_queue, screen_queue,  new_logger)
while 1:
    l.recorder_queue.put({"recorder":[{"state":"new_session"}]})
    l.main_loop()
    l.counter=0

a.buttondriver.stop()
a.buttondriver.join()
a.audiodriver.join()
