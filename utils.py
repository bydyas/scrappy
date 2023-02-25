from os import system, name
import os


def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def make_photo_dir():
    new_path = rf"{os.path.abspath(os.getcwd())}\msg_photos"
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    return new_path
