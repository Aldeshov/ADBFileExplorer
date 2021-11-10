import os

from services.data.managers import FileManager


def default_download_path():
    downloads = os.path.expanduser("~/Downloads")
    if not FileManager.get_device():
        return downloads
    device = f"{downloads}/{FileManager.get_device()}"
    device = device.replace(':', '_')
    if not os.path.isdir(device):
        os.mkdir(device)
    return device
