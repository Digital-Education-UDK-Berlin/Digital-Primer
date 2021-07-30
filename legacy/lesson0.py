#!/usr/bin/python3 -u
#Digital Primer Lesson 0
#run ./lesson0.py THEMA LESSON_ID

#LESSON INITIALIZE
from Fibel import init
init.init()
from Fibel.core import *

#FRONTBACKMATTERS
#cover()

#LOAD FOLIOS
load_foliae(voice="ONO")

#1st exercise: SPRECHEN : Read & record words
imitate(voice="ddh")

g.init()
#2nd exercise: ZUORDNEN : Associate words to images
zuordnen1(title_height=200)

#3rd exercise: ERKENNEN : Berliner digitale Leseprobe ::Distinguish between words and non-words
from Fibel.BDLP import *
BDLP()

