import simpleaudio as sa
import threading

class Audioplayer(threading.Thread):

    def __init__(self, eventqueue, audio_path=""):
        #this needs an implemented input querry to stop :(
        super(Audioplayer, self).__init__()
        self.path = audio_path
        self.q_event = eventqueue
        self.alive = True
        self.current_file_playing = 0

    def check_event(self, item: dict):
        if item["player"][0]["state"] == "play":
            self.path = item["player"][1]["path"]
            self.play_audiofile()
        elif item["player"][0]["state"] == "exit":
            self.alive = False
        elif item["player"][0]["state"] == "stop":
            self.current_file_playing.stop()

    def play_audiofile(self):
        file_to_play = sa.WaveObject.from_wave_file(self.path)
        self.current_file_playing = file_to_play.play()

    def run(self):
        while self.alive:
            try:
                item = self.q_event.get(block=True, timeout=None)
                self.check_event(item)
                self.q_event.task_done()
            except:
                print("something got seriously wrong")
