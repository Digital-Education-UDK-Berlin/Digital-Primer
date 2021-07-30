import time
from witty_logger import thread_logger as tl
from witty_interface import wpi_interface as wi

wpi = wi()
functions_to_log = [wpi.read_v_in, wpi.read_v_out, wpi.read_cur_out]
variables_to_log = ["v_in","v_out","cur_out"]
timeintervall = 3
path = 'testwrite.csv'

a = tl(path, timeintervall, functions_to_log, variables_to_log)
a.start()
print("here is were other programms would run")
time.sleep(10)
a.stop()
