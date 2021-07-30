import time
from plane import plane as planeinterface
from Fibel.FolioText import FolioText


mode='NEUTRAL'
wordz=['die Birke','die Buche','die Linde','die Eiche','die Tanne','die Fichte','der Apfelbaum','die Pappel','die Haselnuss','der Holunder','der Ahorn']

class lesen:

    def __init__(self, mode, words, name, plane, session_id):
        self.mode = mode
        self.words = words
        self.name = name
        self.plfin = plane
        self.old_audiofile = ""
        self.counter = 0
        self.pointerwords = dict()
        self.session_id=session_id
        try:
            self.plfin.audiodriver.active_label = self.words[self.counter] + '-' + self.mode + '-' + self.name.upper()
        except:
            print("audiodriver not initalized")

    def test_lesen(self):
        self.plfin.screendriver.write_texttest(self.words[self.counter])
        while True:
            time.sleep(0.2)
            if self.plfin.audiodriver.last_audiofile and self.plfin.audiodriver.last_audiofile!=self.old_audiofile:
                if self.counter<(len(self.words)-1):
                    print(self.counter)
                    self.counter = self.counter + 1
                    self.plfin.audiodriver.label_displayed = time.time()
                    self.plfin.audiodriver.active_label = self.words[self.counter] + '-' + self.mode + '-' + self.name.upper()
                    self.plfin.audiodriver.last_audiofile = ""
                    time.sleep(0.2)
                    pointer = self.plfin.screendriver.generate_and_load(self.words[self.counter],4)
                    self.plfin.screendriver.display_img_from_buffer(pointer)
                else:
                    self.counter=0
                    break


if __name__ == "__main__":
    wordz.insert(0, "Wie heißt du?")
    a = planeinterface(1,"front",1)
    a.init_screen()
    a.init_audio()
    a.audiodriver.run()
    import os,glob
    last_session=os.path.basename(max(glob.glob(os.path.join('/home/fibel/data/pupils/sessions/*')), key=os.path.getmtime))
    session_id=str(int(last_session)+1)
    os.mkdir('/home/fibel/data/pupils/sessions/'+session_id+'/')
    b = lesen(mode,wordz+['Danke!'],str(time.time()),a)
    while True:
        b.test_lesen()
