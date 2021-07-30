#!/usr/bin/python3 -u
#Digital Primer Lesson 0
#python3 ./lesson.py CURRICULUM EPOCHE LECTION_ID SCREEN_ID IMAGE_AMOUNT

#LESSON INITIALIZE
from Fibel.init import *
init(curriculum=sys.argv[1],thema=sys.argv[2],lesson=sys.argv[3],screen=sys.argv[4],folio_amount=int(sys.argv[5]))
#print(default_voice)
from Fibel.core import *

#FRONTBACKMATTERS
#cover()

#LOAD FOLIOS
load_foliae()

#1st exercise: SPRECHEN : Read & record words
#if sys.argv[4]=="front":
#    imitate()

#g.init()
#2nd exercise: ZUORDNEN : Associate words to images
zuordnen1(variable='down')

#time.sleep(1)
#3rd exercise: ERKENNEN : Berliner digitale Leseprobe ::Distinguish between words and non-words
from Fibel.BDLP import *
BDLP()

#g.paj7620Suspend()
