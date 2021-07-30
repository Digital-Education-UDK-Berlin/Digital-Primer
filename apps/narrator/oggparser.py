import mutagen
import json
import os
import re

class Oggparser:

    def __init__(self, audio):
        self.time_stamps = []
        self.parsed = {}
        self.cwd = os.getcwd()
        self.audio = audio
        self.text = ""

    def parse_json(self):
        b = mutagen.File(self.audio)
        toparse = b["text"]
        new_parse = "[" + toparse[0].replace("\t", "") + "]"
        new_parse = new_parse.replace(',]', ']')
        try:
            self.parsed = json.loads(new_parse)
        except:
            try:
               a = re.sub(r'{id:(.*?),w:(.*?),start:(\d+),stop:(\d+)}',r'{"id":"\1","w":"\2","start":"\3","stop":"\4"}',new_parse)
               print(a)
               self.parsed = json.loads(a)
            except:
                print("ENCODING ERROR")


    def get_text(self):
        for i in self.parsed:
            self.text = self.text + i["w"] + "§"
        print(self.text)
        return self.text

    def get_timestamps(self):
        for i in self.parsed:
            self.time_stamps.append({"start" : int(i["start"]), "end": int(i["stop"])})
        return self.time_stamps
