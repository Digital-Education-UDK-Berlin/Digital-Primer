from allimports import *
from pathlib import Path
import requests
import json
import ast
from dotenv import Dotenv


all_audiotexts = os.getenv('all_audiotexts')
path_audiotext = os.getenv('path_audiotext')
audiotexts_dict = ast.literal_eval(all_audiotexts)


def rmdir(directory):
    directory = Path(directory)
    for item in directory.iterdir():
        if item.is_dir():
            rmdir(item)
        else:
            item.unlink()
    directory.rmdir()


def download_all(title, parsed_json,base_path,env_audiotexts,fileextension):
   for key in fileextension:
       new_path = base_path + "/" + str(key)
       os.mkdir(new_path)
   counter = 0
   for i in parsed_json:
       counter = counter + 1
       for key, value in fileextension.items():
           if key in i.keys():
               if type(i[key]) == list:
                   for o in i[key]:
                       new_path = base_path + "/" + str(key) + "/" + o.split("/")[-1]
                       download_file(o,new_path)
               else:
                  new_path = base_path + "/" + str(key) + "/" + title + str(counter) + str(value)
                  download_file(i[key],new_path)
   with open(base_path+'/'+'download_finished.txt', 'w') as fp:
        pass



def get_json(title):
    knotnumber = audiotexts_dict[title]
    build_url = "https://fibel.digital/" + str(knotnumber) + "/audiotext"
    receive = requests.get(build_url)
    url_json = json.loads(receive.text)
    return url_json


def check_and_download(title):
    new_dir = rootpath + path_audiotext + "/" + str(title)
    #is_there = os.path.isdir(new_dir)
    is_there = os.path.isfile(new_dir + "/" + "download_finished.txt")
    if is_there:
        print("path allready there - nothing to download")
    else:
        parsed_json = get_json(title)
        if os.path.isdir(new_dir):
           rmdir(new_dir)
        os.mkdir(new_dir)
        download_all(title,parsed_json,new_dir,all_audiotexts,{"imgs":".jpg","ogg":".ogg"})
        # download_all(parsed_json,ogg_path,all_audiotexts,".ogg")


def download_file(url,filename):
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)
    print("downloaded: "+ str(filename))


# receive = requests.get('https://fibel.digital/7065/audiotext')
# receive = requests.get('https://fibel.digital/4777/audiotext')
# a = json.loads(receive.text)
# print(a)
#
# allogg = []
# alljpg = []
#
# for i in a:
#     if 'ogg' in i.keys():
#        allogg.append(i["ogg"])
#     if 'imgs' in i.keys():
#         #fixme how to handle two dimesnional arrays here ?
#         alljpg.append(i["imgs"][0])
#
#
#
#
# print(alljpg)

#download_file(alljpg[0],"4777.jpg")
    # print(i["ogg"])

# check_and_download("Schneeweißchen und Rosenrot")
