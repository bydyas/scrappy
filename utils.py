from os import system, name, path, getcwd, makedirs


def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def make_photo_dir(username):
    # Get current parent folder
    curr_dir = path.abspath(getcwd())
    dist_dir = username + "_photos"
    # The way to save user message photos
    new_path = rf"{curr_dir}/{dist_dir}"
    # If it does not exist, create it
    if not path.exists(new_path):
        makedirs(new_path)
    return new_path
