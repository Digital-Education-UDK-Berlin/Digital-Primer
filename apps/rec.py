#!/usr/bin/python3
#Minimalist audio recorder
#Co(d|mb)ded by Prof. Dr. Dr. Daniel Devatman Hromada as a first App of the digital Primer (fibel.digital) project
#Commercial use without explicit consent of the author prohibited
#Where appropriate, CC BY-NC-SA applies, in all other cases mrGPL
#UdK / ECDF / wizzion.com AE5001, January 2020
#Berlin, Deutschland, EU

#PREAMBLE
import time,sys
import RPi.GPIO as GPIO

#I/O
import pyaudio,wave

#INPUT-RELATED
import RPi.GPIO as GPIO
sound_device_index=0
sound_format_width=2
channels=2
sampling_rate=16000
button_pin = 17

#OUTPUT RELATED VARIABLES
rec_file=sys.argv[1]

#PLACEHOLDER VARIABLES
frames = []
old_button_free=True

#SETUP CODE
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN)
p = pyaudio.PyAudio()
rec_start=None

#MAIN LOOP
while True:
    button_free = GPIO.input(button_pin)
    if button_free:
        if old_button_free==False:
          print('Finishing recording')
          break
        else:
            print('off')
            time.sleep(0.05)
    elif button_free==False:
        if old_button_free:
          print('rec')
          rec_start=time.time()
          stream = p.open(channels=channels,rate=sampling_rate,format=p.get_format_from_width(sound_format_width),input=True,input_device_index=sound_device_index)
        data = stream.read(4096)
        frames.append(data)
        old_button_free=False



#TERMINATING OPERATIONS
print('Finished recording, stopping stream.')
stream.stop_stream()
stream.close()
p.terminate()

#KNOWLEDGE SERIALIZATION
wf = wave.open(rec_file, 'wb')
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(p.get_format_from_width(sound_format_width)))
wf.setframerate(sampling_rate)
wf.writeframes(b''.join(frames))
wf.close()
print("sa.WaveObject.from_wave_read(wave.open('"+rec_file+"', 'rb')).play()")
print('time.sleep('+str(round(time.time()-rec_start,2))+')')

