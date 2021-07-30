import subprocess, queue
import fibel_logger
from plane import plane as planeinterface

busno_gesture = 3
alligment = 'front'
rotation = 1

## only needed when run as main


def get_wifi_name():
    results = subprocess.check_output(["iwconfig","wlan0"])
    findessid = results.find(b'ESSID:')+6
    wifiname = ((results[findessid:])[:results[findessid:].find(b'\n')]).decode('utf-8')
    return str(wifiname)

def witty_reading(wi):
    vin = wi.read_v_in()
    vout = wi.read_v_in()
    curout = wi.read_cur_out()
    stringreturn = "Vin: " + str(vin) + "\nVout: " + str(vout) + "\nCURout: " + str(curout)
    return (stringreturn)

if __name__ == "__main__":
    new_logger = fibel_logger.initalize_logger("startscreen")
    sensor_queue = queue.Queue()
    event_queue = queue.Queue()
    screen_queue = queue.Queue()
    example_path = "/home/fibel/finalprimer/fibel/testrecordings/"
    a = planeinterface(1, "front", 1, event_queue, sensor_queue, screen_queue, example_path, new_logger)
    a.init_witty()
    wifiname = get_wifi_name()
    wittyreading = witty_reading(a.witty)
    testtext = "Initalized with: " + alligment + " " + '''
     - rotation:''' + str(rotation) + "---- "+"Connected to: "+wifiname +"---- " + wittyreading
    screen_queue.put({"screen":[{"state":"write_textbox"},{"text": testtext},{"factor": 2}]})
    a.init_screen()
    a.screendriver.start()
