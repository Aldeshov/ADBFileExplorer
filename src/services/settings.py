import os

from services.manager import FileManager


def get_download_folder():
    downloads = os.path.expanduser("~/Downloads")
    if not FileManager.get_device():
        return downloads
    device = f"{downloads}/{FileManager.get_device()}"
    if not os.path.isdir(device):
        os.mkdir(device)
    return device
