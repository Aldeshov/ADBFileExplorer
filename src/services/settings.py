import os
import random
import shutil
import tempfile

from services.data.managers import FileManager


def default_download_path():
    downloads = os.path.expanduser("~/Downloads")
    if not FileManager.get_device():
        return downloads

    device = FileManager.get_device().replace(':', ' ')
    device = os.path.join(downloads, device)
    if not os.path.isdir(device):
        os.mkdir(device)
    return device


def temporary_folder():
    root = tempfile.gettempdir()
    if not os.path.isdir(root):
        os.mkdir(root)

    folder = os.path.join(root, ".adb.upload")
    if os.path.isdir(folder):
        if clear_folder(folder):
            return folder
        folder += str(random.randint(1000, 9999))
    os.mkdir(folder)
    return folder


def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
            return False
    return True


def copy_files_to_temp(files):
    destination = temporary_folder()
    for file in files:
        shutil.copy(file, destination)
    destination = os.path.join(destination, '.')
    return destination
