import time

class Navigator:

    def __init__(self):
        self.currentpage = 0
        self.buffer_slots = dict()
        self.direction_forward = True
        self.currentsavepoint = 0
        self.stack1 = []

    def generate_next(self):
        self.stack1.append(self.currentpage)
        print("/////////////////////////////////////////")
        print(self.stack1)
        print("/////////////////////////////////////////")
        for i in range(0,4):
            slot = self.currentpage + i
            self.buffer_slots[slot % 8] = { "page_number" : self.currentpage + i , "buffer_address": "None" }


    def generate_previous(self):
        # self.stack.pop()
        self.stack1.pop()
        for i in range(0,4):
            slot = self.currentpage - i
            self.buffer_slots[slot % 8] = { "page_number" : self.currentpage - i , "buffer_address": "None" }



    def next_page(self):
        self.currentpage = self.currentpage + 1
        self.direction_forward = True
        self.test_for_next_load()
        self.display()

    def previous_page(self):
        self.currentpage = self.currentpage - 1
        self.direction_forward = False
        self.test_for_next_load()
        self.display()

    def display(self):
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Page Number" + str(self.currentpage))
        print("show bufferslot  " + str(self.currentpage % 8) + ": " + str(self.buffer_slots[self.currentpage % 8]))
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")

    def test_for_next_load(self):
        print(self.stack1)
        if self.currentpage % 4 == 0:
            if self.direction_forward:
                print("_______________________________")
                print("direction_forward")
                self.generate_next()
                print(a.buffer_slots)
            elif not self.direction_forward and self.stack1[-2]  == self.currentpage:
                print("direction_backward")
                self.generate_previous()
                print(a.buffer_slots)


a = Navigator()

a.generate_next()
for i in range(0,24):
    a.next_page()
    time.sleep(0.5)

print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")


for i in range(0,21):
    a.previous_page()
    time.sleep(0.5)
