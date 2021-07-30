import time, os, threading, queue
from gesture import gesture
import logging


def consumer(qn):
    while True:
        try:
            item = qn.get(timeout=2)
            print(item)
        except:
            print("empty")


class gesture_driver(threading.Thread):

    def __init__(self, busno, sensor_queue, logger):
        super(gesture_driver, self).__init__()
        self.dgesture = gesture(busno)
        self.sensor_queue = sensor_queue
        self.killsignal = True
        self.logger = logger

    def run(self):
        self.logger.info('start gesture sensor')
        while self.killsignal:
            time.sleep(0.05)
            gesturestate = self.dgesture.get_gesture()
            if gesturestate:
                self.sensor_queue.put({"gesture":[{"state":1},{"mov":gesturestate}]})
            else:
                self.sensor_queue.put({"gesture":[{"state":0}]})

if __name__ == "__main__":
    logger = logging.getLogger('simple_example')
    q = queue.Queue()
    thread_gesture = gesture_driver(1, q, logger)
    a = threading.Thread(target=consumer, args=(q,), daemon=True)
    thread_gesture.start()
    a.start()
