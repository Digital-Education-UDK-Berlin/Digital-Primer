import pathlib
import os

class filemanager():

    def __init__(self,subdirectory: str):
        self.path_working_dict = pathlib.Path().absolute()
        self.path_exec_dict = pathlib.Path(__file__).parent.absolute()
        self.path_recordings = self.create_recordings(subdirectory)
        self.path_new_dictionary = ""


    def create_recordings(self, subdirectory: str) -> str:
        new_recording = self.path_working_dict / subdirectory
        if not new_recording.is_dir():
            os.mkdir(new_recording)
        return new_recording

    def create_new_folder(self, name: str)-> str:
        new_path = self.path_recordings / name
        self.path_new_dictionary = new_path
        assert not new_path.is_dir()
        os.mkdir(new_path)
        return new_path

    def create_next(self, name: str)-> str:
        get_list = os.listdir(self.path_recordings)
        generation = len(list(filter(lambda x: bool(name in x), get_list)))
        new_name = name + str(generation + 1)
        new_generation = self.create_new_folder(new_name)
        return new_generation

    def create_new_file(self, name: str)-> str:
        return self.path_new_dictionary / name


if __name__ == "__main__":
    a = filemanager("test_recordings")
    # print(a.create_new_folder("test"))
    print (a.create_next("test"))
    print (a.create_next("test"))
