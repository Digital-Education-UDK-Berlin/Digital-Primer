import time, queue
import threading
import RPi.GPIO as GPIO

###only testing

def consumer(qn):
    while True:
        try:
            item = qn.get(timeout=2)
            print(item)
        except:
            print("empty")


class fib_button(threading.Thread):

    def __init__(self, eventqueue, logger):
        super(fib_button, self).__init__()
        self.eventqueue = eventqueue
        self.button = 17
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button, GPIO.IN)
        self.message_on = {"button":{"state":1}}
        self.message_off = {"button":{"state":0}}
        self.killsignal = True
        self.logger = logger

    def stop(self):
        self.killsignal = False

    def run(self):
        self.logger.info('start button')
        while self.killsignal:
            time.sleep(0.05)
            buttonstate = GPIO.input(self.button)
            if buttonstate:
                self.eventqueue.put(self.message_off)
            else:
                self.eventqueue.put(self.message_on)

# if __name__ == "__main__":
#     q = queue.Queue()
#     thread_button = fib_button(q)
#     a = threading.Thread(target=consumer, args=(q,), daemon=True)
#     thread_button.start()
#     a.start()
