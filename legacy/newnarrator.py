import os,sys,time,json, queue
import fibel_logger
from PIL import Image, ImageDraw
from PIL.ImageOps import invert
from plane import plane as planeinterface
from Fibel.FolioText import FolioText
from math import sqrt
import wave
import argparse
import simpleaudio as sa

# example: python3 newnarrator.py Books/ABC_Buch/1

parser = argparse.ArgumentParser()
parser.add_argument("path", help="the relative path to the content used",
                    type=str)
args = parser.parse_args()

#home/fibel/minimalprimer/Digital-Primer/

sentences = []
page_dir = "/home/fibel/minimalprimer/Digital-Primer/" + args.path
jsons = []
wavs = []
texts = []

font = 'Fonts/schola.otf'
margin_width = 20
color = 0

plane_instance = 0

# ask here what format this is parsing
def load_variables():
    lines = open(page_dir+'/content','r').readlines()
    for line in lines:
        row = line.split(";")
        texts.append(row[0])
        jsons.append(json.loads('['+(row[1].rstrip())+']'))
        try:
            wavs.append(sa.WaveObject.from_wave_read(wave.open(page_dir+'/'+row[0]+'.wav', 'rb')))
        except:
            wavs.append("")

def initialize_plane(sen,eve,scr):
    example_path = "/home/fibel/finalprimer/fibel/testrecordings/"
    new_logger = fibel_logger.initalize_logger("new_narrator")
    plane_instance = planeinterface(1, "front", 1, sen, eve, scr, example_path, new_logger)
    return plane_instance

sensor_queue = queue.Queue()
event_queue = queue.Queue()
screen_queue = queue.Queue()
load_variables()
newplane = initialize_plane(sensor_queue,event_queue,screen_queue)
print(wavs)
print(jsons)

word_pointers = []
word_pointers.append([])

display = newplane.screendriver.screendriver
new_height = newplane.screendriver.height
new_width = newplane.screendriver.with

print(display.img_addr+id*(2*display.width*display.height+1))

# def pntr(id):
#     global display
#     return display.img_addr+id*(2*display.width*display.height+1)

#print("loading folio "+str(pntr_id))
# display.load_image(0,0,folio.image,img_addr=pntr(1))
# display.load_image(0,0,invert(folio.image.convert('L')),img_addr=pntr(2))
# display.display_buffer_area(0,0,800,600,2,buff_addr=pntr(1))
# print("folio "+str(pntr_id)+" loaded")

# while(True):
#     print(newplane.gesturedriver.get_gesture())
#     time.sleep(0.1)
