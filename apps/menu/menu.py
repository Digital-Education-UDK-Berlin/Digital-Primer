import time
import queue
import functools
import logging
from PIL.ImageOps import invert
from PIL import Image
from allimports import *
from download_manager import check_and_download


all_audiotexts = os.getenv('all_audiotexts')
path_audiotext = os.getenv('path_audiotext')
audiotexts_dict = ast.literal_eval(all_audiotexts)

print(audiotexts_dict)

def calc_bufferaddress_wh(screendriver, _id, height, width):
    return screendriver.img_addr + 480000 + _id * (1 * height * width)


def build_list(textarray, font, fontsize):
    word_pointers = []
    text_image = FolioText_module.FolioText((600, 800), pointers=word_pointers, background=255, mode='1')
    text_image.write_list(textarray, 560, font, font_size=fontsize)
    return [text_image.image, text_image.pointers]

# def build_textfolia(textarray, font, fontsize):
#     word_pointers = []
#     text_image = FolioText_module.FolioText((600, 800), pointers=word_pointers, background=255, mode='1')
#     text_image.write_text_box(textarray, 560, font, font_size=fontsize)
#     return [text_image.image, text_image.pointers]


def load_in_buffer(folio, number, screendriver):
    buffer_address_positiv = calc_bufferaddress_wh(screendriver, number, 800, 600)
    print(buffer_address_positiv)
    screendriver.load_image(0, 0, folio, img_addr=buffer_address_positiv)
    return buffer_address_positiv


def make_list(thelist, font):
    fontsize = 40    #this needs a config
    return build_list(thelist, font, fontsize)


def display(buffer_address):
    screendriver.display_buffer_area(0, 0, 800, 600, 2, buffer_address)


def show_files(path):
    files = os.listdir(path)
    return files

def show_point(number,foliaarray):
    currentfolio = foliaarray[1][number]
    buffer_address_negative = foliaarray[0]
    firstelement = currentfolio[0]
    thesum = sum(list(map(lambda x:x[3],currentfolio)))
    screendriver.display_buffer_area(firstelement[1], 0, thesum+10, 600, 2, buffer_address_negative)

def prepare_filelist():
    #filesnarrator = show_files(rootpath+"/data/audiotext/Märchen")
    filesnarrator = list(audiotexts_dict.keys())
    print(filesnarrator)
    ###these are just here for test
    filesnarrator.append("Heute Kann es regnen oder schneien oder vielleicht kann auch die Sonne scheinen")
    # filesnarrator.append("Wolfram - a new science")
    # filesnarrator.append("The Minds new science")
    # filesnarrator.append("Kritik der Reihnen Vernuft")
    newarray = list(map(lambda x: x.replace(" ", "§"),filesnarrator, ))
    b = make_list(newarray, font)
    pointers = b[1]
    a = {}
    for t in pointers:
        for i in filesnarrator:
            if t[4] in i:
                if i in a:
                    a[i].append(t)
                else:
                    a[i] = [t]

    foliaarray = []
    for value in a.values():
        foliaarray.append(value)
    return [b[0],foliaarray]


def positioncheck(position,wordlist):
    #print(wordlist)
    returnbool = False
    if position < len(wordlist[1]) and position >= 0:
        return True
    return returnbool



file_browser_folia = prepare_filelist()

screendriver = driver_it8951.IT8951()
screendriver.init(rotate=1, screen="front")

print("-----------------")
file_browser_folia_inverted = [invert(file_browser_folia[0].convert('RGB')),file_browser_folia[1]]


file_browser_both = [file_browser_folia,file_browser_folia_inverted]
# print(file_browser_both)

menue_words = [["Willkomen"], ["Wähle eine Übung", "lesen <<", "hören>>"], ["Lade Übungen"]]

menue_words_folia = list(map(functools.partial(make_list, font=font), menue_words))
# print(":::::::::::::::")
# print(menue_words_folia)

menue_words_folia.extend(file_browser_both)
# print(menue_words_folia)

all_folio_in_buffer = {}
for i in range(len(menue_words_folia)):
    listbefore = menue_words_folia[i]
    new_buffer_address = load_in_buffer(listbefore[0],i,screendriver)
    listbefore[0] = new_buffer_address
    all_folio_in_buffer[i] = listbefore


print("loaded all in buffer")


logger = logging.getLogger('simple_example')

q_gesture_input = queue.Queue()
q_gesture_output = queue.Queue()
thread_gesture = gesture_driver_module.gesture_driver(1, q_gesture_input, q_gesture_output, logger)
thread_gesture.start()

display(all_folio_in_buffer[0][0])
time.sleep(5)
display(all_folio_in_buffer[1][0])
time.sleep(5)

#
end_signal = True
while end_signal:
    if not q_gesture_output.empty():
        gesture_output = q_gesture_output.get(block=False, timeout=None)
        print(gesture_output)
        if gesture_output["gesture"][1]["mov"] == "U":
            print("hören")
            #q_gesture_input.put({"gesture" : [{"state":"exit"}]})
            end_signal = False
            #display(all_folio_in_buffer[2][0])
            #narrator_module.start_all()
        elif gesture_output["gesture"][1]["mov"] == "D":
            print("lesen")
            q_gesture_input.put({"gesture" : [{"state":"exit"}]})
            end_signal = False
            display(all_folio_in_buffer[2][0])
            reader_module.start_reader()

display(all_folio_in_buffer[3][0])

position = 0
show_point(position,all_folio_in_buffer[4])
end_signal2 = True
while end_signal2:
    if not q_gesture_output.empty():
        gesture_output = q_gesture_output.get(block=False, timeout=None)
        print(gesture_output)
        if gesture_output["gesture"][1]["mov"] == "L":
            if positioncheck(position+1,all_folio_in_buffer[4]):
                position = position + 1
                display(all_folio_in_buffer[3][0])
                show_point(position,all_folio_in_buffer[4])
                print(position)
        elif gesture_output["gesture"][1]["mov"] == "R":
            if positioncheck(position - 1,all_folio_in_buffer[4]):
                position = position - 1
                display(all_folio_in_buffer[3][0])
                show_point(position,all_folio_in_buffer[4])
                print(position)
        elif gesture_output["gesture"][1]["mov"] == "U":
                end_signal = False
                q_gesture_input.put({"gesture" : [{"state":"exit"}]})
                display(all_folio_in_buffer[2][0])
                #narrator_module.start_all()
                # print(all_folio_in_buffer[4][position-1])
                print("______________________________")
                sentence = all_folio_in_buffer[4][1][position]
                b = list(map(lambda x:x[4],sentence))
                full_name = ' '.join(b)
                print("start with "+str(full_name))
                print("______________________________")
                check_and_download(full_name)
                narrator_module.start_all(full_name)
