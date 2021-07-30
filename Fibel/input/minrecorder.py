import time, os, queue
import pyaudio
import wave
import threading
import simpleaudio as sa

#see lesenque for example on how to call

class recorder(threading.Thread):

    def __init__(self,eventqueue,audio_dir,logger):
        super(recorder, self).__init__()
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.channels = 2
        self.fs = 16000
        self.sample_width = 2
        self.stream = None
        self.word = "TESTRECORD"
        self.record = False
        self.device_index = None
        self.eventqueue = eventqueue
        self.audio_dir = audio_dir
        self.last_session_link = audio_dir+'/last'
        self.logger = logger

    def check_event(self, item: dict):
        if item["recorder"][0]["state"] == "new_session":
            last_session=os.path.basename(os.path.realpath(self.last_session_link))
            self.session_id=str(int(last_session)+1)
            new_session_dir=self.audio_dir+self.session_id
            os.mkdir(new_session_dir)
            os.unlink(self.audio_dir+'/last')
            os.symlink(new_session_dir,self.last_session_link,True)
            self.logger.info('new session dir:' + new_session_dir)
        elif item["recorder"][0]["state"] == "start":
            self.start_record()
            self.word = item["recorder"][1]["word"]
            self.append_frames()
        elif item["recorder"][0]["state"] == "stop":
            self.frames.append(self.stream.read(4096))     #fixme
            self.write_audiofile(self.word)
        elif item["recorder"][0]["state"] == "cont":
            self.append_frames()
        # elif item["recorder"][0]["state"] == "cont":
        #     self.append_frames()

    def check_device(self):
     for i in range(self.p.get_device_count()):
         dev=p.get_device_info_by_index(i)
         if dev.name=='seeed-2mic-voicecard':
            self.device_index=dev.index

    def start_record(self):
        self.stream = self.p.open(channels=self.channels,
                                    rate=self.fs,
                                    format=self.p.get_format_from_width(self.sample_width),
                                    input=True,
                                    input_device_index=self.device_index)

    def append_frames(self):
        available_frames = self.stream.get_read_available()
        if available_frames > 0:
            self.frames.append(self.stream.read(available_frames))

    def play_audiofile(self, path: str):
        file_to_play = sa.WaveObject.from_wave_file(path)
        file_to_play.play()

    def write_audiofile(self, word: str):
        self.stream.stop_stream()
        self.stream.close()
        audio_file=self.audio_dir+self.session_id+'/'+word
        self.logger.debug('write audiofile to %s' % audio_file)
        waveFile = wave.open(audio_file,'wb')
        waveFile.setnchannels(self.channels)
        waveFile.setsampwidth(self.p.get_sample_size(self.p.get_format_from_width(self.sample_width)))
        waveFile.setframerate(self.fs)
        waveFile.writeframes(b''.join(self.frames))
        waveFile.close()
        self.play_audiofile(audio_file)
        self.frames = []

    def run(self):
        timeout=0
        self.logger.info('start recorder')
        #self.logger.info(os.getpid())
        while timeout < 3:
            try:
                item = self.eventqueue.get(timeout = 2)
                self.check_event(item)
                self.eventqueue.task_done()
            except:
                self.logger.debug('empty recorder')
                timeout = timeout + 1
        self.logger.error('timeout')
