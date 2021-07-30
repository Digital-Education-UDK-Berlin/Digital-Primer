from string import *
from random import sample,choice,randint,getrandbits

def randomString(stringLength):
    #letters = string.ascii_letters
    letters=['A','E','I','O','U','M','B','P','R','V','D','m','p','b','r','v','d']
    return ''.join(choice(letters) for i in range(stringLength))


