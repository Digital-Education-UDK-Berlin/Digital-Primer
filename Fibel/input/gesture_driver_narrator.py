import time, os, threading, queue
# from Fibel.input.gesture import gesture
import logging
import importlib.util
import inspect
from pathlib import Path


#make the path failsave

full_path = os.path.dirname(os.path.abspath(__file__))
rootpath = (str(Path(full_path).parents[1]))
spec = importlib.util.spec_from_file_location("gesture", rootpath + str("/Fibel/input/gesture.py"))
gesture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gesture_module)



def consumer(qn):
    while True:
        try:
            item = qn.get(block=True, timeout=None)
            print(item)
        except:
            print("empty")


class gesture_driver(threading.Thread):

    def __init__(self, busno, sensor_queue_input, sensor_queue_output ,logger):
        super(gesture_driver, self).__init__()
        self.dgesture = gesture_module.gesture(busno)
        self.sensor_queue_input = sensor_queue_input
        self.sensor_queue_output = sensor_queue_output
        self.alive = True
        self.logger = logger

    def check_message(self, item):
        if item["gesture"][0]["state"] == "exit":
            self.alive = False

    def run(self):
        self.logger.info('start gesture sensor')
        while self.alive:
            time.sleep(0.05)
            gesturestate = self.dgesture.get_gesture()
            if gesturestate:
                self.sensor_queue_output.put({"gesture":[{"state":1},{"mov":gesturestate}]})
            if not self.sensor_queue_input.empty():
                item = self.sensor_queue_input.get(block=False, timeout=None)
                self.check_message(item)
            # else:
            #     self.sensor_queue.put({"gesture":[{"state":0}]})

if __name__ == "__main__":
    logger = logging.getLogger('simple_example')
    q = queue.Queue()
    p = queue.Queue()
    thread_gesture = gesture_driver(1, q, p, logger)
    a = threading.Thread(target=consumer, args=(p,), daemon=True)
    thread_gesture.start()
    a.start()
    time.sleep(5)
    q.put({"gesture":[{"state":"exit"}]})
