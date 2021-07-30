#!/usr/bin/python3
#Minimalist e-ink polaroid
#Co(d|mb)ed by Prof. Dr. Dr. Daniel Devatman Hromada as a second App of the digital Primer (fibel.digital) project
#Commercial use without explicit consent of the author prohibited
#Where appropriate, CC BY-NC-SA applies, in all other cases mrGPL
#UdK / ECDF / wizzion.com AE5006, June 2020
#Berlin, Deutschland, EU

from time import sleep
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (600, 800)
camera.start_preview()
# Camera warm-up time
sleep(2)
camera.capture('foo.jpg')

