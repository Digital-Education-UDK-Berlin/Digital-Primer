import queue
import time
import threading
import logging
import os
import simpleaudio as sa
import simpleaudio as sa
import threading
import pyaudio
import wave
import inspect
import importlib.util
from pathlib import Path

full_path = os.path.dirname(os.path.abspath(__file__))
rootpath = (str(Path(full_path).parents[1]))

spec_gesture = importlib.util.spec_from_file_location("gesture_driver", rootpath + str("/Fibel/input/gesture_driver_narrator.py"))
spec_screendriver = importlib.util.spec_from_file_location("it8951", rootpath + str("/Fibel/drivers/it8951.py"))
spec_navigator = importlib.util.spec_from_file_location("navigator", rootpath + str("/apps/narrator/navigator.py"))
spec_filemanager = importlib.util.spec_from_file_location("filemanager", full_path + str("/filemanager.py"))

gesture_driver_module = importlib.util.module_from_spec(spec_gesture)
driver_it8951 = importlib.util.module_from_spec(spec_screendriver)
navigator_module = importlib.util.module_from_spec(spec_navigator)
filemanager_module = importlib.util.module_from_spec(spec_filemanager)

spec_screendriver.loader.exec_module(driver_it8951)
spec_gesture.loader.exec_module(gesture_driver_module)
spec_navigator.loader.exec_module(navigator_module)
spec_filemanager.loader.exec_module(filemanager_module)

class Timer():

    def __init__(self):
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
        elapsed_time += (time.time() - self.start_time)
        return elapsed_time


class recorder(threading.Thread):

    def __init__(self,eventqueue,audio_dir,logger):
        super(recorder, self).__init__()
        self.p = pyaudio.PyAudio()
        self.alive = True
        self.frames = []
        self.channels = 2
        self.fs = 16000
        self.sample_width = 2
        self.stream = None
        self.word = "TESTRECORD"
        self.record = False
        self.device_index = None
        self.eventqueue = eventqueue
        self.logger = logger
        self.filemanager = filemanager_module.filemanager(audio_dir)
        self.filename = "Aschenputtel"
        self.pagecounter = 0

    def check_event(self, item: dict):
        if item["recorder"][0]["state"] == "new_session":
            print("Get here")
            print(self.filemanager.create_next(self.filename))
            self.check_device()
        elif item["recorder"][0]["state"] == "start":
            self.start_record()
            # self.word = item["recorder"][1]["word"]
            self.append_frames()
        elif item["recorder"][0]["state"] == "stop":
            self.frames.append(self.stream.read(4096))     #fixme
            self.write_audiofile()
            self.record = False
        # elif item["recorder"][0]["state"] == "cont":
        #     self.append_frames()

    def start_record(self):
        print("start record")
        self.stream = self.p.open(channels=self.channels,
                                  rate=self.fs,
                                  format=self.p.get_format_from_width(self.sample_width),
                                  input=True,
                                  input_device_index=self.device_index)
        self.record = True

    def check_device(self):
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)
            if dev["name"] == 'seeed-2mic-voicecard: - (hw:0,0)':
                self.device_index = dev['index']
                print("card on input_device_index: " + str(self.device_index))

    def append_frames(self):
        available_frames = self.stream.get_read_available()
        # print("__________________")
        # print(available_frames)
        # print("__________________")
        if available_frames > 0:
            self.frames.append(self.stream.read(available_frames))

    def write_audiofile(self):
        self.stream.stop_stream()
        self.stream.close()
        audio_file = self.filemanager.create_new_file(self.filename + str(self.pagecounter) + str(".wav"))
        print(audio_file)
        self.logger.debug('write audiofile to %s' % audio_file)
        waveFile = wave.open(str(audio_file),'wb')
        waveFile.setnchannels(self.channels)
        waveFile.setsampwidth(self.p.get_sample_size(self.p.get_format_from_width(self.sample_width)))
        waveFile.setframerate(self.fs)
        waveFile.writeframes(b''.join(self.frames))
        waveFile.close()
        self.frames = []
        print("write file")

    def run(self):
        while self.alive:
            if self.record:
                self.append_frames()
            try:
                item = self.eventqueue.get(block=False)
                print(item)
                self.check_event(item)
                self.eventqueue.task_done()
            except:
                pass



test_texts = "Vor einem großen Walde wohnte ein armer Holzhacker mit seiner Frau und seinen zwei Kindern; das Bübchen hieß Hänsel und das Mädchen Gretel. ::: Er hatte wenig zu beißen und zu brechen, und einmal, als große Teuerung ins Land kam, konnte er auch das täglich Brot nicht mehr schaffen. ::: Wie er sich nun Abends im Bette Gedanken machte und sich vor Sorgen herum wälzte, seufzte er und sprach zu seiner Frau „was soll aus uns werden? wie können wir unsere armen Kinder ernähren, da wir für uns selbst nichts mehr haben?“ ::: „Weißt du was, Mann,“ antwortete die Frau, „wir wollen Morgen in aller Frühe die Kinder hinaus in den Wald führen, wo er am dicksten ist: da machen wir ihnen ein Feuer an und geben jedem noch ein Stückchen Brot, dann gehen wir an unsere Arbeit und lassen sie allein. Sie finden den Weg nicht wieder nach Haus und wir sind sie los.“ ::: „Nein, Frau,“ sagte der Mann, „das tue ich nicht; wie sollt ichs übers Herz bringen meine Kinder im Walde allein zu lassen, die wilden Tiere würden bald kommen und sie zerreißen.“ ::: „O du Narr,“ sagte sie, „dann müssen wir alle viere Hungers sterben, du kannst nur die Bretter für die Särge hobelen,“ und ließ ihm keine Ruhe bis er einwilligte. ::: „Aber die armen Kinder dauern mich doch“ sagte der Mann. Die zwei Kinder hatten vor Hunger auch nicht einschlafen können und hatten gehört was die Stiefmutter zum Vater gesagt hatte. ::: Gretel weinte bittere Tränen und sprach zu Hänsel „nun ists um uns geschehen.“ „Still, Gretel,“ sprach Hänsel, „gräme dich nicht, ich will uns schon helfen.“ Und als die Alten eingeschlafen waren, stand er auf, zog sein Röcklein an, machte die Untertüre auf und schlich sich hinaus".replace(" ","§").split(":::")

def start_reader():
    print(test_texts)
    screendriver = driver_it8951.IT8951()
    screendriver.init(rotate=1, screen="front")
    logger = logging.getLogger('simple_example')
    q_folio_input = queue.Queue()
    q_folio_output = queue.Queue()

    folio_instance = navigator_module.Navigator(q_folio_input, q_folio_output, screendriver, test_texts, [])
    folio_instance.start()

    q_gesture_input = queue.Queue()
    q_gesture_output = queue.Queue()
    thread_gesture = gesture_driver_module.gesture_driver(1, q_gesture_input, q_gesture_output, logger)
    thread_gesture.start()


    q_folio_input.put({"folio":[{"state":"init"}, {"data":test_texts}]})
    item = q_folio_output.get(block=True, timeout=None)



    q_audio_input = queue.Queue()
# #
    new_recoder = recorder(q_audio_input, "new_recordings", logger)
    new_recoder.start()
# #
    end_signal = True
    new_timer = Timer()
    page = 0
    new_timer.start_timer()
    last_time_point = [0]
    timestamps = []
#
    q_audio_input.put({"recorder":[{"state":"new_session"}]})
    q_audio_input.put({"recorder":[{"state":"start"}]})
#     q_audio_input.put({"recorder":[{"state":"start"}]})
#     print("get into sleep")
#     time.sleep(4)
#     q_audio_input.put({"recorder":[{"state":"stop"}]})


    while end_signal:
        if len(folio_instance.buffer_slots[page % 8]['word_pointers']) == folio_instance.current_word:
            q_audio_input.put({"recorder":[{"state":"stop"}]})
            new_timer.stop_timer()
            new_timer.reset()
            page = page + 1
            q_folio_input.put({"folio":[{"state":"resetword"}]})
            q_folio_input.put({"folio":[{"state":"nextpage"}]})
            new_timer.start_timer()
            q_audio_input.put({"recorder":[{"state":"start"}]})
        if not q_gesture_output.empty():
            gesture_output = q_gesture_output.get(block=False, timeout=None)
            if gesture_output["gesture"][1]["mov"] == "C":
                q_folio_input.put({"folio":[{"state":"nextword"}]})
                # print(folio_instance.buffer_slots[1 % 8]['word_pointers'])
                print(len(folio_instance.buffer_slots[page % 8]['word_pointers']))
                print("New Datapoint:")
                newtime = new_timer.get_Elapsed_Time()
                lastpoint = last_time_point.pop()
                print(lastpoint,newtime)
                last_time_point.append(newtime)
                new_data_point = {"id":"w"+str(folio_instance.current_word),
                                  "w":str(folio_instance.buffer_slots[folio_instance.current_page % 8]['word_pointers'][folio_instance.current_word][4]),
                                  "start":str(lastpoint),
                                  "stop":str(newtime)}
                print("__________________________")
                print(new_data_point)
                print("__________________________")
 #
    q_folio_input.put({"folio" : [{"state":"exit"}]})
    q_gesture_input.put({"gesture" : [{"state":"exit"}]})


if __name__ == "__main__":
    start_reader()
