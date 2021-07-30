import json
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

#this needs to be integrated later
#from Fibel.input.minrecorder import recorder


#opusdec --force-wav  aschenputtel1-DOROTHEA-MUELLER-1595607195.ogg test.wav

#folio to do
#layout 10 stept adjustment to fontsize based on characterlenght _> fit all on one screen / no buckets for now :)

testjson = {"id":"w0","w":"	","stop":"593"},{"id":"w1","w":"Es","stop":"735"},{"id":"w2","w":"war","stop":"927"},{"id":"w3","w":"einmal","stop":"1328"},{"id":"w4","w":"eine","stop":"1550"},{"id":"w5","w":"kleine","stop":"1926"},{"id":"w6","w":"Dirne","stop":"2562"},{"id":"w7","w":",","stop":"2612"},{"id":"w8","w":"die","stop":"2745"},{"id":"w9","w":"hatte","stop":"2913"},{"id":"w10","w":"jeder","stop":"3113"},{"id":"w11","w":"lieb","stop":"3282"},{"id":"w12","w":",","stop":"3916"},{"id":"w13","w":"der","stop":"4015"},{"id":"w14","w":"sie","stop":"4132"},{"id":"w15","w":"nur","stop":"4231"},{"id":"w16","w":"ansah","stop":"5118"},{"id":"w17","w":",","stop":"5236"},{"id":"w18","w":"am","stop":"5351"},{"id":"w19","w":"allerliebsten","stop":"5820"},{"id":"w20","w":"aber","stop":"6070"},{"id":"w21","w":"ihre","stop":"6237"},{"id":"w22","w":"Großmutter","stop":"7713"},{"id":"w23","w":",","stop":"7743"},{"id":"w24","w":"die","stop":"7859"},{"id":"w25","w":"wusste","stop":"8109"},{"id":"w26","w":"gar","stop":"8263"},{"id":"w27","w":"nicht","stop":"8609"},{"id":"w28","w":"was","stop":"8775"},{"id":"w29","w":"sie","stop":"8927"},{"id":"w30","w":"alles","stop":"9163"},{"id":"w31","w":"dem","stop":"9396"},{"id":"w32","w":"Kinde","stop":"9729"},{"id":"w33","w":"geben","stop":"10063"},{"id":"w34","w":"sollte","stop":"11101"},{"id":"w35","w":".","stop":"11383"},{"id":"w36","w":"Einmal","stop":"11687"},{"id":"w37","w":"schenkte","stop":"12520"},{"id":"w38","w":"sie","stop":"12670"},{"id":"w39","w":"ihm","stop":"12804"},{"id":"w40","w":"ein","stop":"12938"},{"id":"w41","w":"Käppchen","stop":"13511"},{"id":"w42","w":"von","stop":"13672"},{"id":"w43","w":"rotem","stop":"13945"},{"id":"w44","w":"Samt","stop":"14958"},{"id":"w45","w":"und","stop":"15075"},{"id":"w46","w":"weil","stop":"15227"},{"id":"w47","w":"ihm","stop":"15393"},{"id":"w48","w":"das","stop":"15627"},{"id":"w49","w":"so","stop":"15771"},{"id":"w50","w":"wohl","stop":"16028"},{"id":"w51","w":"stand","stop":"16362"},{"id":"w52","w":"und","stop":"16567"},{"id":"w53","w":"es","stop":"17147"},{"id":"w54","w":"nichts","stop":"17398"},{"id":"w55","w":"anders","stop":"17703"},{"id":"w56","w":"mehr","stop":"17901"},{"id":"w57","w":"tragen","stop":"18283"},{"id":"w58","w":"wollte","stop":"18936"},{"id":"w59","w":",","stop":"19035"},{"id":"w60","w":"hieß","stop":"19269"},{"id":"w61","w":"es","stop":"19371"},{"id":"w62","w":"nur","stop":"19559"},{"id":"w63","w":"das","stop":"19720"},{"id":"w64","w":"Rotkäppchen","stop":"20171"},{"id":"w65","w":".	","stop":"20816"}

dirname = os.path.dirname(__file__)
font = os.path.join(dirname, 'Fonts/schola.otf')

alttesttext= "„Ach,“ dachte sie, „wenn auf den Markt Leute aus meines Vaters Reich kommen, und sehen mich da sitzen und feil halten, wie werden sie mich verspotten!“ Aber es half nichts, sie musste sich fügen, wenn sie nicht Hungers sterben wollten. Das erst Mal gings gut, denn die Leute kauften der Frau, weil sie schön war, gern ihre Waare ab, und bezahlten was sie forderte: ja, viele gaben ihr das Geld, und ließen ihr die Töpfe noch dazu."


class oggparser:

    def __init__(self,audio):
        self.allwords_timestams = {}
        self.parsed = {}
        self.cwd = os.getcwd()
        self.audio = audio
        self.fstring = ""


    def parse(self):
        b = mutagen.File(self.audio)
        try:
            toparse = b["text"]
            new_parse=new_parse.replace(',]',']')
            #print("LALAL"+new_parse+"LLALALA")
            self.parsed = json.loads(new_parse)
        except:
            print("ERROR ENCODING")


    def parsestring(self):
        for i in self.parsed:
            self.fstring = self.fstring + i["w"] + "§"



    def get_timestamps(self):
        ## legacy complicent / re format changed
        counter = 0
        start = 0
        for i in self.parsed:
            self.allwords_timestams[counter] = {"word": i["w"], "start" : start, "end": i["stop"]}
            counter = counter +1


class audioplayer(threading.Thread):

    def __init__(self,eventqueue,audio_path):
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
            #try:
            if 1:
                item = self.eventqueue.get(block=True, timeout=None)
                self.check_event(item)
                self.eventqueue.task_done()
            #except:
                #print("something got seriosly wrong")




#print(inputfolio)

class setzkasten(threading.Thread):

    def __init__(self, setzqueue, drivers, fstring, timestamps):
            super(setzkasten, self).__init__()
            self.setzqueue = setzqueue
            self.screendriver = drivers
            self.generatedfolias = dict()
            self.fstring = fstring
            self.timestamps = timestamps

    def check_event(self, item: dict):
        if item["setzkasten"][0]["state"] == "generate":
            self.fstring = item["setzkasten"][1]["fstring"]
            self.generate_setzkasten()
        elif item["setzkasten"][0]["state"] == "show":
            self.show()
        elif item["setzkasten"][0]["state"] == "jump":
            pass

    def calc_bufferaddress_wh(self, _id, height, width,screendriver):
            return (self.screendriver.img_addr + 480000 + _id * ( 1 * height * width))

    def generate_setzkasten(self):
        global font      #fixme
        setzkasten = {}
        word_pointers = []
        temp_height = 200
        big_height = 800
        id = 0
        word_counter = 0
        buffercounter = 1                  #counts full pages
        for text in self.fstring:
            print("get here")
            print(text)
            text_image = FolioText((600,  big_height), pointers = word_pointers, background=255, mode='L')
            text_image.write_text_box(20,0,text,580,font,font_size=30,justify_last_line=True)
            buffer_address_positiv = self.calc_bufferaddress_wh(buffercounter, big_height, 600,screendriver)
            buffer_address_negativ = self.calc_bufferaddress_wh(buffercounter+1, big_height, 600,screendriver)
            content_image = text_image.image
            invert_image = invert(content_image.convert('L'))
            self.screendriver.load_image(0,0,content_image, img_addr=buffer_address_positiv)
            self.screendriver.load_image(0,0,invert_image, img_addr=buffer_address_negativ)
            self.generatedfolias[buffercounter] = {"buffer_address_positiv":buffer_address_positiv,"buffer_address_negativ":buffer_address_negativ,"word_pointers":text_image.pointers}
            buffercounter = buffercounter+2
            text_image.pointers = []

    def show(self):
        for key in self.generatedfolias:
            print(self.generatedfolias)
            self.screendriver.display_buffer_area(0,0,800,600,2,self.generatedfolias[key]['buffer_address_positiv'])
            wordp = self.generatedfolias[key]['word_pointers']
            counter = 0
            listtimes = []
            #for nextkey in self.timestamps:
            #    print(self.timestamps[nextkey])
            #    listtimes.append(self.timestamps[nextkey]["end"])
            correctfirst = listtimes[1:]
            before_end = 0
            values_int = sorted(list(map(int, listtimes)))
            print(wordp)
            print(self.timestamps)
            for pointer in wordp:
                print(counter)
                screendriver.display_buffer_area(pointer[1],(-1)*pointer[0]+600-pointer[2],pointer[3],pointer[2],2,self.generatedfolias[key]['buffer_address_negativ'])
                current_end = values_int[counter]
                diffrence = current_end - before_end
                time.sleep(diffrence* 10**(-3))
                counter = counter + 1
                time.sleep(2)
                print(counter)
                before_end = current_end
            print("FINISHED")

    def run(self):
        while True:
            item = self.setzqueue.get(block=True, timeout=None)
            print(item)
            self.check_event(item)
            self.setzqueue.task_done()

        #return generatedfolias
    #return [buffer_address_positiv,buffer_address_negativ,text_image.pointers]



# def main():
#     screendriver = driver_it8951.IT8951()
#     screendriver.init(rotate=1, screen="front")
#     setzkasten_buffer = generate_setzkasten(alttesttext,screendriver)
#     screendriver.display_buffer_area(0,0,800,600,2,setzkasten_buffer[0])
#     wordsframes = setzkasten_buffer[2]
#     pointers = wordsframes
#     time.sleep(2)
#     print(pointers)
#     for pointer in pointers:
#         screendriver.display_buffer_area(0,0,800,600,1,setzkasten_buffer[0])
#         screendriver.display_buffer_area(pointer[1],(-1)*pointer[0]+600-pointer[2],pointer[3],pointer[2],2,setzkasten_buffer[1])


#main()

#this is the mainprogramm
# a = buckets(testjson)
# a = [alttesttext]
# screendriver = driver_it8951.IT8951()
# screendriver.init(rotate=1, screen="front")
# setzkasten_buffer = generate_setzkasten(a,screendriver)
# #print(setzkasten_buffer)
# counter = 0
# print(setzkasten_buffer)
# for key in setzkasten_buffer:
#         print(key)
#         screendriver.display_buffer_area(0,0,800,600,2,setzkasten_buffer[key]['buffer_address_positiv'])
#         wordp = setzkasten_buffer[key]['word_pointers']
#         for pointer in wordp:
#             screendriver.display_buffer_area(pointer[1],(-1)*pointer[0]+600-pointer[2],pointer[3],pointer[2],2,setzkasten_buffer[key]['buffer_address_negativ'])
#



#testfilepath = "./recordings/aschenputtel1-DOROTHEA-MUELLER-1595607195.ogg"
testfilepath = "audiotest.ogg"
testfilepath2 = "audiotest.wav"

event_queue = queue.Queue()
setzkasten_queue = queue.Queue()
audioplayer= audioplayer(event_queue,testfilepath2)
audioplayer.start()

a = oggparser(testfilepath)
a.parse()
a.get_timestamps()
a.parsestring()
all_time_stamps = a.allwords_timestams
print(all_time_stamps)

print("____________________")
print(a.fstring)
print("____________________")


b = ["this is a test sentence one","this is a test sentence two","this is a test sentence three"]

play = {"player":[{"state":"play"}, {"path": testfilepath2}]}
generate_setzkasten = {"setzkasten":[{"state":"generate"}, {"fstring": [a.fstring]}]}      #fixme a.fstring is not arry
generate_setzkasten = {"setzkasten":[{"state":"generate"}, {"fstring": b}]}
show_setzkasten = {"setzkasten":[{"state":"show"}]}

subprocess.run(["opusdec", "--force-wav", testfilepath , testfilepath2])

#

screendriver = driver_it8951.IT8951()
screendriver.init(rotate=1, screen="front")

setzkasten_instance = setzkasten(setzkasten_queue, screendriver, [a.fstring], all_time_stamps )
setzkasten_instance.start()

setzkasten_queue.put(generate_setzkasten)
time.sleep(40)
print(setzkasten_instance.generatedfolias)

# setzkasten_queue.put(show_setzkasten)
#event_queue.put(play)



    # def check_event(self, item: dict):
    #     if item["setztkasten"][0]["state"] == "generate":
    #         self.fstring = item["setztkasten"][1]["fstring"]
    #         self.generate_setzkasten()
    #     elif item["setztkasten"][0]["state"] == "start":
    #         self.show()
    #     elif item["setztkasten"][0]["state"] == "jump":
    #         pass




# opusdec --force-wav  aschenputtel1-DOROTHEA-MUELLER-1595607195.ogg test.wav

# Get the data as a NumPy array

# file_to_play = sa.WaveObject.from_wave_file(testfilepath2)
# file_to_play.play()



# print(tempbufferpath)
# setzkasten_buffer = generate_setzkasten([a.fstring],screendriver)
#
# counter = 0

# for key in setzkasten_buffer:
#         #print(key)
#         screendriver.display_buffer_area(0,0,800,600,2,setzkasten_buffer[key]['buffer_address_positiv'])
#         wordp = setzkasten_buffer[key]['word_pointers']
#         for pointer in wordp:
#             screendriver.display_buffer_area(pointer[1],(-1)*pointer[0]+600-pointer[2],pointer[3],pointer[2],2,setzkasten_buffer[key]['buffer_address_negativ'])
#



    #screendriver.display_buffer_area(pointer[1],pointer[0],pointer[3],pointer[2],2,setzkasten_buffer[1])
    # print((-1)*pointer[1]+800)
    # screendriver.display_buffer_area(0,0,90,90,2,setzkasten_buffer[1])
    #screendriver.display_buffer_area(pointer[1],pointer[0],pointer[3],pointer[2],2,setzkasten_buffer[1])
