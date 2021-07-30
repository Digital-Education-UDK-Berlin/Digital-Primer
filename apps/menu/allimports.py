import os
from pathlib import Path
import inspect
import importlib.util
import json
import ast
from dotenv import Dotenv

full_path = os.path.dirname(os.path.abspath(__file__))
rootpath = (str(Path(full_path).parents[1]))
font = rootpath + '/Fonts/schola.otf'

spec_gesture = importlib.util.spec_from_file_location("gesture_driver", rootpath + str("/Fibel/input/gesture_driver_narrator.py"))
spec_screendriver = importlib.util.spec_from_file_location("it8951", rootpath + str("/Fibel/drivers/it8951.py"))
spec_narrator = importlib.util.spec_from_file_location("Narrator", rootpath + str("/apps/narrator/narrator.py"))
spec_foliotext = importlib.util.spec_from_file_location("FolioText", rootpath + str("/Fibel/FolioText.py"))
spec_reader = importlib.util.spec_from_file_location("Reader", rootpath + str("/apps/reader/reader.py"))

FolioText_module = importlib.util.module_from_spec(spec_foliotext)
gesture_driver_module = importlib.util.module_from_spec(spec_gesture)
driver_it8951 = importlib.util.module_from_spec(spec_screendriver)
narrator_module = importlib.util.module_from_spec(spec_narrator)
reader_module = importlib.util.module_from_spec(spec_reader)

spec_foliotext.loader.exec_module(FolioText_module)
spec_gesture.loader.exec_module(gesture_driver_module)
spec_screendriver.loader.exec_module(driver_it8951)
spec_narrator.loader.exec_module(narrator_module)
spec_reader.loader.exec_module(reader_module)

dotenv_path = Path(str(rootpath)+ "/" + '.env')
dotenv = Dotenv(dotenv_path)
os.environ.update(dotenv)
