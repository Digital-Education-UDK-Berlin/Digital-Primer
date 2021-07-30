# Digital Primer

**Intro**

In this repository You will find some necessary software bricks which will allow You to create Your own variant of a digital Primer (DP). DP is a new kind of medium whose raison d'etre is to educate. Its ideal hardware embodiment looks like a book and has multiple properties of a book. Instead of using screens, device uses e-ink displays (mostly using IT8951 controller) to present visual or textual content. Strong emphasis is to be put on speech technologies (automatic speech recognition and speech synthesis) and touchless human-machine interaction. Recommended platform: Raspberry Pi Zero running Raspbian OS.

**Quickstart**

    python3 -m venv .
    source bin/activate
    pip install -r requirements.txt

Start the menu:

    python3 apps/menu/menu.py

Start the reader:

    python3 apps/reader/reader.py

Start the narrator:

    python3 apps/narrator/narrator.py

Please note that reader.py and narrator.py rely on external Data from https://fibel.digital/ . This data has to be aquired.

**Apps**

Currently there are 3 Application which could be run on the fibel: Menu, Reader and Narrator

 1. Menu - This is the smallest Application just acting as a menu to select one of the two core applications.
 2. Reader - This Application generates various Pages based on an input text. The Application shows than the texts on diffrent sites and underlines a word. The user can read the word and than via a gesture select the next word. The application generates an audiofile with integrated timestamps.
 3. Narrator - The Narrator Application generates Pages based on Audiofiles with integrated Timestamps. The generated Pages will be shown synchronously to the related Audio.  Special value here is here placed on the   synchronize the spoken word to the underlining of written word.


**Architecture**

To provide a thread safe communication every thread / class uses a queue. The messaging format for now are dictionary. The syntax of these is up for discussion.

    {"addressee":[{"state":"action"}, {"aditionalkey": "aditionalvalue"}]}
    e.g
    {"player":[{"state":"play"}, {"path": self.waves[self.page]}]}

Since a lot of processes are in need for own threads a lot of thread and timing management need to happen. Processes implement therefore either input / output , only output or only input queues. We can group any process in one of the following categories:

-   producer - a process generating output data without any input data - these are mostly sensors

-   consumer - a process consuming data but not providing any output data - these are mostly device which don't need to provide feedback - e.g a audio interface

-   logic - a process with input and outputs - implementing a logic to compute on inputs and pipe them in consumers - these are the programms of the prototype

**Repository**
The repository contains folders with the following programs:

 - /Fibel - contains drivers, interfaces for running the drivers, utilities and the wittypi interface
 - /apps - contains the main apps Menu, Reader and Narrator
 - /experimental - contains varios functions which need to be implemented - photo function etc
 - /tests - contains mostly functions for testing the hardware - buffertester etc
 - /legacy - contains previosly used code
 - /logs - contains logs


##############################

**screen and buffer considerations**

In the following files one can find varios ways of initalizing and using the screen. They all show diffrent approches:

 - plane.py - when initalized from main it will do a testrun with all diffrent screen directions. this file shows clearly that the bufferadressspace seems to be handled in relation to the initalisation with a certain direction - this means that its seems to be impossible to save smaller than 800*600 files in buffer when initalised with 1 or 3 and display them propperly (to be investigated further)
 - buffertester - using a method of layouting all the words on 800*600 pictures and then just showing specific buffer areas of these files. This approch gets even more confusing since with these bigger files the bufferadressspace seems to be handled in relation to the initalisation and needs manual adjustment for any direction :( - It works for initalisation with 1 and can stack the pictures with best way ((1 * height * width +1 )

##############################


Fibel has a following structure:

Curriculum -> Epoch -> Lection -> Exercise

Curriculum (e.g. "Lesen") and Epoch (e.g. "Tiere") form a topic with specific TOPIC_DIR (e.g. Lesen/Tiere/)

Folios are associated to topics and lessons mix specific folios associated to the topic.

Folio-mixing is attained by means of symlinks.

How to generate folios for a new topic:
1) specify the font (e.g. 'schola'), voice (e.g. 'ask') and drawing (e.g. 'lux') authors
2) populate the Lexicon with Your BMP images and WAV recordings
3) create the "Units" subdir of the TOPIC_DIR populated with files whose names match names of subdirs in the lexicon
4) run python3 generate_foliae.py TOPIC_DIR

How to create new lesson:
1) Generate folios for a new topic (c.f. above)
2) Within the topic dir, create the "Lectiones" subdir (e.g. TOPIC_DIR/Lectiones/)
3) Within the Lectiones subdir, create the lesson subdir whose name is identic to numeric LESSON_ID (e.g. TOPIC_DIR/Lectiones/1)
4) Within the "Deck" subdir of a specific lesson subdir, create symlinks to topic Foliae. Symlink names should be sorted according to the sequence in which You want Folios to get loaded (and potentially also appear)
5) run python3 generate_lesson.py TOPIC_DIR LESSON_ID
