#!/usr/bin/python3 -u
#Digital Primer Lesson 0
#run ./lesson0.py THEMA LESSON_ID

#LESSON INITIALIZE
from Fibel.init import *
init(curriculum='Lesen',thema='Pflanzen',lesson='1',folio_amount=3)
#print(default_voice)
from Fibel.core import *

#FRONTBACKMATTERS
#cover()

#LOAD FOLIOS
load_foliae()

#1st exercise: SPRECHEN : Read & record words
imitate()

g.init()
#2nd exercise: ZUORDNEN : Associate words to images
zuordnen1()

#3rd exercise: ERKENNEN : Berliner digitale Leseprobe ::Distinguish between words and non-words
from Fibel.BDLP import *
BDLP()

