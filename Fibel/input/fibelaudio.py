import RPi.GPIO as GPIO
import time,glob
import pyaudio
import wave
import threading
import simpleaudio as sa
from Fibel.init import *

class fibelaudio:
    p = pyaudio.PyAudio()
    frames = []
    channels=2
    fs=16000
    sample_width=2
    BUTTON = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON, GPIO.IN)
    old_button_free=True
    stream=None
    active_label=""
    label_displayed=''
    stop_recording=False
    last_audiofile=""
    rec_start=None

    def run(self):
        t1 = threading.Thread(target=self.record)
        t1.start()

    def terminate(self):
        self.p.terminate()
        self.stop_recording=True

    def play(self):
        if self.stream:
            self.stream.close()
        self.stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),channels = wave.getnchannels(),rate = wave.getframerate(),output = True)

    def record(self):
       #this should most probably change to use queues
       last_session=os.path.basename(max(glob.glob(os.path.join('/home/fibel/data/sessions/*')), key=os.path.getmtime))
       audio_dir='/home/fibel/data/sessions/'+last_session+'/'

       while True:
            if self.stop_recording:
                break
            self.button_free = GPIO.input(self.BUTTON)
            if self.button_free:
                #print("BUTTON_FREE")
                if self.old_button_free==False:
                  sys.stderr.write('Finishing recording '+self.active_label+'\n')
                  self.stream.stop_stream()
                  self.stream.close()
                  audio_file=audio_dir+self.active_label+'-'+str(int(time.time()))
                  wf = wave.open(audio_file, 'wb')
                  wf.setnchannels(self.channels)
                  wf.setsampwidth(self.p.get_sample_size(self.p.get_format_from_width(self.sample_width)))
                  wf.setframerate(self.fs)
                  wf.writeframes(b''.join(self.frames))
                  self.frames=[]
                  wf.close()
                  wo=sa.WaveObject.from_wave_file(audio_file)
                  self.last_audiofile=audio_file
                  self.last_rec_stop=time.time()
                  self.last_rec_length=self.last_rec_stop-self.last_rec_start
                  #print(audio_file+';'+str(self.last_rec_length))
                  #print(self.active_label+';'+str(self.last_rec_length)+';'+str(self.last_rec_stop-self.label_displayed))
                  po=wo.play()
                  po.wait_done()
                  #self.last_audiofile=audio_file
                  #self.last_rec_length=time.time()-self.last_rec_start
                else:
                    time.sleep(0.05)
                self.old_button_free=True
            elif self.button_free==False:
                print("BUTTON_NONFREE")
                if self.old_button_free:
                  sys.stderr.write("recording "+self.active_label+'\n')
                  self.last_rec_start=time.time()
                  try:
                      sa.stop_all()
                      self.stream = self.p.open(channels=self.channels,rate=self.fs,format=self.p.get_format_from_width(self.sample_width),input=True,input_device_index=2)
                  except:
                      sa.stop_all()
                      time.sleep(3)
                      self.stream.close()
                      time.sleep(2)
                      self.stream = self.p.open(channels=self.channels,rate=self.fs,format=self.p.get_format_from_width(self.sample_width),input=True,input_device_index=2)
                try:
                    self.frames.append(self.stream.read(4096))
                except:
                      self.stream = self.p.open(channels=self.channels,rate=self.fs,format=self.p.get_format_from_width(self.sample_width),input=True,input_device_index=0)
                      self.frames.append(self.stream.read(4096))
                self.old_button_free=False


