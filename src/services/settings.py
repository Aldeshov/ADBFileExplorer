import os

from services.data.managers import FileManager


def default_download_path():
    downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
    if not FileManager.get_device():
        return downloads

    device = FileManager.get_device().replace(':', ' ')
    device = os.path.join(downloads, device)
    if not os.path.isdir(device):
        os.mkdir(device)
    return device
