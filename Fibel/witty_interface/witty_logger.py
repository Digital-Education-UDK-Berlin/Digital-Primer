import threading, time, os, csv
import random

b = lambda: random.random()
functions_to_test=[b,b,b]
names_to_test = ["v_in","v_out","cur_out"]

class thread_logger(threading.Thread):
    lock = threading.Lock()
    stopsignal = True

    def __init__(self, path, intervall, functions, value_names):
        threading.Thread.__init__(self)
        self.intervall = intervall
        self.path = path
        self.functions_to_log = functions
        self.value_names = value_names
        self.start_time = time.time()
        #self.addtime()

    def addtime(self):
        self.value_names = self.value_names.append("time")
        #print(self.value_names)

    def run(self):
        self.writeheadercsv()
        while self.stopsignal:
            thread_logger.lock.acquire()
            getallvalues = (list(map(lambda v: v(), self.functions_to_log)))
            self.writecsv(getallvalues)
            thread_logger.lock.release()
            time.sleep(self.intervall)

    def get_time(self):
        return (time.time() - self.start_time)

    def stop(self):
        self.stopsignal = False

    def writeheadercsv(self):
        f = open(self.path, 'w')
        with f:
            writer = csv.DictWriter(f, fieldnames=self.value_names)
            writer.writeheader()

    def writecsv(self, values):
        f = open(self.path, 'a')
        with f:
            dictionary = dict(zip(self.value_names, values))
            writer = csv.DictWriter(f, fieldnames=self.value_names)
            writer.writerow(dictionary)

if __name__ == "__main__":
    print("logging random output in testwrite.csv")
    a = thread_logger('testwrite.csv',3, functions_to_test, names_to_test)
    a.start()
    time.sleep(10)
    a.stop()
