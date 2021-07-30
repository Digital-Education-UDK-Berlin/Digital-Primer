#!/usr/bin/python3
#Minimalist e-ink polaroid
#Co(d|mb)ed by Prof. Dr. Dr. Daniel Devatman Hromada as a second App of the digital Primer (fibel.digital) project
#Commercial use without explicit consent of the author prohibited
#Where appropriate, CC BY-NC-SA applies, in all other cases mrGPL
#UdK / ECDF / wizzion.com AE5006, June 2020
#Berlin, Deutschland, EU

from io import BytesIO
from time import sleep
from picamera import PiCamera
import Fibel.drivers.it8951 as driver_it8951
from PIL import Image
import RPi.GPIO as GPIO
import time

camera = PiCamera()
camera.color_effects = (128,128)
camera.resolution = (600, 800)
camera.rotation=270

button_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN)

old_button_free=True
while True:
    button_free = GPIO.input(button_pin)
    if button_free:
        if old_button_free==False:
          print('button released! snap!')
          stream = BytesIO()
          camera.capture(stream, format='bmp')
          stream.seek(0)
          camera.start_preview()
          photo = Image.open(stream)
          driver_front=driver_it8951.IT8951()
          driver_front.init(rotate=1)
          pointer_front2=driver_front.img_addr+(2*driver_front.width*driver_front.height+1)
          driver_front.load_image(0,0,photo,img_addr=pointer_front2)
          driver_front.display_buffer_area(0,0,800,600,2,pointer_front2)
          old_button_free=True
        else:
            print('off')
            time.sleep(0.05)
    elif button_free==False:
        if old_button_free:
          print('button pressed!')
        old_button_free=False

